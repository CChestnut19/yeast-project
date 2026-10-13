"""Export MySQL schema metadata and ER diagram sources without business data."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pymysql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "database_structure"


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def safe_mermaid_type(column_type: str) -> str:
    return (
        column_type.replace(" ", "_")
        .replace("(", "_")
        .replace(")", "")
        .replace(",", "_")
        .replace("'", "")
        .replace('"', "")
    )


def sql_literal(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def main() -> None:
    env = {**load_env(PROJECT_ROOT / ".env"), **os.environ}
    config = {
        "host": env.get("DB_HOST", "localhost"),
        "port": int(env.get("DB_PORT", "3306")),
        "user": env.get("DB_USER", "root"),
        "password": env.get("DB_PASSWORD", ""),
        "database": env.get("DB_NAME", "labdnadata"),
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
    }
    connection = pymysql.connect(**config)
    schema = config["database"]

    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION() AS version")
        version = cursor.fetchone()["version"]

        cursor.execute(
            """
            SELECT TABLE_NAME, TABLE_TYPE, ENGINE, TABLE_ROWS, TABLE_COLLATION,
                   TABLE_COMMENT
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
            """,
            (schema,),
        )
        tables = cursor.fetchall()

        cursor.execute(
            """
            SELECT TABLE_NAME, ORDINAL_POSITION, COLUMN_NAME, COLUMN_TYPE,
                   DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_KEY, EXTRA,
                   CHARACTER_SET_NAME, COLLATION_NAME, COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, ORDINAL_POSITION
            """,
            (schema,),
        )
        columns = cursor.fetchall()

        cursor.execute(
            """
            SELECT TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME,
                   COLLATION, CARDINALITY, SUB_PART, INDEX_TYPE
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
            """,
            (schema,),
        )
        indexes = cursor.fetchall()

        cursor.execute(
            """
            SELECT kcu.CONSTRAINT_NAME, kcu.TABLE_NAME, kcu.COLUMN_NAME,
                   kcu.REFERENCED_TABLE_NAME, kcu.REFERENCED_COLUMN_NAME,
                   rc.UPDATE_RULE, rc.DELETE_RULE
            FROM information_schema.KEY_COLUMN_USAGE kcu
            JOIN information_schema.REFERENTIAL_CONSTRAINTS rc
              ON rc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
             AND rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
             AND rc.TABLE_NAME = kcu.TABLE_NAME
            WHERE kcu.CONSTRAINT_SCHEMA = %s
              AND kcu.REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY kcu.TABLE_NAME, kcu.CONSTRAINT_NAME, kcu.ORDINAL_POSITION
            """,
            (schema,),
        )
        foreign_keys = cursor.fetchall()

        create_statements: list[dict[str, str]] = []
        for table in tables:
            table_name = table["TABLE_NAME"]
            cursor.execute(f"SHOW CREATE TABLE `{table_name.replace('`', '``')}`")
            create_row = cursor.fetchone()
            create_sql = create_row.get("Create Table") or create_row.get("Create View")
            create_statements.append({"table": table_name, "sql": create_sql})

    connection.close()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    exported_at = datetime.now().astimezone().isoformat(timespec="seconds")

    metadata = {
        "database": schema,
        "mysql_version": version,
        "exported_at": exported_at,
        "summary": {
            "table_count": len(tables),
            "column_count": len(columns),
            "index_entry_count": len(indexes),
            "foreign_key_count": len(foreign_keys),
        },
        "tables": tables,
        "columns": columns,
        "indexes": indexes,
        "foreign_keys": foreign_keys,
    }
    (OUTPUT_DIR / "schema_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )

    sql_lines = [
        f"-- Structure-only export for `{schema}`",
        f"-- MySQL version: {version}",
        f"-- Exported at: {exported_at}",
        "-- Contains no table data.",
        "",
        "SET FOREIGN_KEY_CHECKS=0;",
        "",
    ]
    for item in create_statements:
        sql_lines.extend(
            [
                f"-- Table structure for `{item['table']}`",
                f"DROP TABLE IF EXISTS `{item['table'].replace('`', '``')}`;",
                item["sql"] + ";",
                "",
            ]
        )
    sql_lines.append("SET FOREIGN_KEY_CHECKS=1;")
    (OUTPUT_DIR / "schema_only.sql").write_text(
        "\n".join(sql_lines) + "\n", encoding="utf-8"
    )

    columns_by_table: dict[str, list[dict[str, object]]] = defaultdict(list)
    for column in columns:
        columns_by_table[column["TABLE_NAME"]].append(column)
    foreign_by_column = {
        (fk["TABLE_NAME"], fk["COLUMN_NAME"]): fk for fk in foreign_keys
    }

    mermaid = [
        "---",
        f"title: {schema} database ER diagram",
        "---",
        "erDiagram",
    ]
    for table in tables:
        table_name = table["TABLE_NAME"]
        mermaid.append(f"    {table_name} {{")
        for column in columns_by_table[table_name]:
            markers = []
            if column["COLUMN_KEY"] == "PRI":
                markers.append("PK")
            if (table_name, column["COLUMN_NAME"]) in foreign_by_column:
                markers.append("FK")
            if column["COLUMN_KEY"] == "UNI":
                markers.append("UK")
            marker = " " + ",".join(markers) if markers else ""
            comment_parts = []
            if column["IS_NULLABLE"] == "NO":
                comment_parts.append("NOT NULL")
            if column["COLUMN_DEFAULT"] is not None:
                comment_parts.append(f"default={column['COLUMN_DEFAULT']}")
            if column["COLUMN_COMMENT"]:
                comment_parts.append(str(column["COLUMN_COMMENT"]).replace('"', "'"))
            comment = f' "{"; ".join(comment_parts)}"' if comment_parts else ""
            mermaid.append(
                f"        {safe_mermaid_type(column['COLUMN_TYPE'])} "
                f"{column['COLUMN_NAME']}{marker}{comment}"
            )
        mermaid.append("    }")
    for fk in foreign_keys:
        label = (
            f"{fk['CONSTRAINT_NAME']}: "
            f"{fk['COLUMN_NAME']}→{fk['REFERENCED_COLUMN_NAME']}"
        ).replace('"', "'")
        mermaid.append(
            f"    {fk['REFERENCED_TABLE_NAME']} ||--o{{ "
            f"{fk['TABLE_NAME']} : \"{label}\""
        )
    (OUTPUT_DIR / "er_diagram.mmd").write_text(
        "\n".join(mermaid) + "\n", encoding="utf-8"
    )

    summary = [
        f"# `{schema}` 数据库结构导出",
        "",
        f"- 导出时间：{exported_at}",
        f"- MySQL 版本：{version}",
        f"- 基础表数量：{len(tables)}",
        f"- 字段数量：{len(columns)}",
        f"- 数据库外键约束数量：{len(foreign_keys)}",
        "- 本目录不包含业务数据或数据库密码。",
        "",
        "## 文件说明",
        "",
        "- `er_diagram.mmd`：Mermaid ER 图源码，可导入 Mermaid Live Editor 或支持 Mermaid 的 Markdown 工具。",
        "- `schema_metadata.json`：表、字段、索引和外键的机器可读元数据。",
        "- `schema_only.sql`：MySQL 仅结构建表 SQL，不含数据。",
        "",
        "## 外键关系",
        "",
    ]
    if foreign_keys:
        summary.extend(
            [
                "| 约束名 | 子表.字段 | 父表.字段 | 更新规则 | 删除规则 |",
                "|---|---|---|---|---|",
            ]
        )
        for fk in foreign_keys:
            summary.append(
                f"| {fk['CONSTRAINT_NAME']} | {fk['TABLE_NAME']}.{fk['COLUMN_NAME']} "
                f"| {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']} "
                f"| {fk['UPDATE_RULE']} | {fk['DELETE_RULE']} |"
            )
    else:
        summary.append(
            "数据库中没有声明外键约束；ER 图会展示各表字段，但不会臆测代码层面的关系。"
        )
    (OUTPUT_DIR / "README.md").write_text(
        "\n".join(summary) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "output_dir": str(OUTPUT_DIR),
                "database": schema,
                "tables": len(tables),
                "columns": len(columns),
                "foreign_keys": len(foreign_keys),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
