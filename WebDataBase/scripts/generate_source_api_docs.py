"""Generate source-verified API references from the Django URL/view source.

The generator intentionally reports only behavior that can be observed in the
repository. It does not infer deployment-specific authentication guarantees or
invent response schemas that are not explicit in the views.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Route:
    app: str
    route: str
    module: str
    view: str
    name: str


@dataclass
class ViewInfo:
    source: Path
    line: int
    methods: list[str]
    query: list[str]
    form: list[str]
    files: list[str]
    json_fields: list[str]
    response_types: list[str]
    response_keys: list[str]
    statuses: list[int]
    auth_markers: list[str]
    docstring: str


MODULE_FILES = {
    ("WebDatabase", "views"): ROOT / "WebDatabase" / "views.py",
    ("WebDatabase", "account"): ROOT / "WebDatabase" / "account.py",
    ("LabDatabase", "views"): ROOT / "LabDatabase" / "views.py",
    ("LabDatabase", "admin"): ROOT / "LabDatabase" / "admin.py",
    ("LabDatabase", "admin_views"): ROOT / "LabDatabase" / "AdminManage" / "admin_views.py",
    ("LabDatabase", "DNADiagram"): ROOT / "LabDatabase" / "CaculateModule" / "DNADiagram.py",
}


def literal(node: ast.AST | None, default: str = "") -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return default


def dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        left = dotted(node.value)
        return f"{left}.{node.attr}" if left else node.attr
    if isinstance(node, ast.Call):
        return dotted(node.func)
    return ""


def parse_routes(app: str) -> list[Route]:
    source = ROOT / app / "urls.py"
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    routes: list[Route] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or dotted(node.func) != "path" or len(node.args) < 2:
            continue
        route = literal(node.args[0])
        target = dotted(node.args[1])
        if not route or "." not in target:
            continue
        module, view = target.rsplit(".", 1)
        name = ""
        for kw in node.keywords:
            if kw.arg == "name":
                name = literal(kw.value)
        routes.append(Route(app, route, module, view, name))
    return routes


def node_key(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def request_collection(call: ast.Call) -> tuple[str, str] | None:
    if not isinstance(call.func, ast.Attribute) or call.func.attr != "get":
        return None
    owner = dotted(call.func.value)
    if owner in {"request.GET", "request.POST", "request.FILES"} and call.args:
        key = node_key(call.args[0])
        if key:
            return owner.split(".")[-1].lower(), key
    return None


@lru_cache(maxsize=None)
def extract_view(app: str, module: str, view: str) -> ViewInfo | None:
    source = MODULE_FILES.get((app, module))
    if not source or not source.exists():
        return None
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    target: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | None = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == view:
            target = node
            break
    if target is None:
        return None

    methods: set[str] = set()
    query: set[str] = set()
    form: set[str] = set()
    files: set[str] = set()
    json_fields: set[str] = set()
    responses: set[str] = set()
    response_keys: set[str] = set()
    statuses: set[int] = set()
    auth: set[str] = set()

    decorators = [dotted(item) for item in getattr(target, "decorator_list", [])]
    for decorator in decorators:
        low = decorator.lower()
        if "login_required" in low:
            auth.add("login_required")
        if "permission_required" in low or "user_passes_test" in low:
            auth.add(decorator)
        if "require_get" in low:
            methods.add("GET")
        if "require_post" in low:
            methods.add("POST")
        if "csrf_exempt" in low:
            auth.add("csrf_exempt")

    for node in ast.walk(target):
        if isinstance(node, ast.Compare):
            left = dotted(node.left)
            if left == "request.method":
                for comparator in node.comparators:
                    value = literal(comparator).upper()
                    if value in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                        methods.add(value)
        if isinstance(node, ast.Call):
            coll = request_collection(node)
            if coll:
                kind, key = coll
                {"get": query, "post": form, "files": files}[kind].add(key)
            call_name = dotted(node.func).split(".")[-1]
            if call_name in {
                "JsonResponse",
                "HttpResponse",
                "FileResponse",
                "StreamingHttpResponse",
                "render",
                "redirect",
            }:
                responses.add(call_name)
            if call_name == "JsonResponse" and node.args and isinstance(node.args[0], ast.Dict):
                for key_node in node.args[0].keys:
                    key = node_key(key_node) if key_node else None
                    if key:
                        response_keys.add(key)
            for kw in node.keywords:
                if kw.arg == "status" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, int):
                    statuses.add(kw.value.value)
            if isinstance(node.func, ast.Attribute) and node.func.attr == "get" and node.args:
                owner = dotted(node.func.value).lower()
                if owner in {"data", "payload", "body", "json_data", "request_data", "params"}:
                    key = node_key(node.args[0])
                    if key:
                        json_fields.add(key)
        if isinstance(node, ast.Subscript):
            owner = dotted(node.value)
            key = node_key(node.slice)
            if key and owner in {"request.GET", "request.POST", "request.FILES"}:
                {"request.GET": query, "request.POST": form, "request.FILES": files}[owner].add(key)
            if key and owner.lower() in {"data", "payload", "body", "json_data", "request_data", "params"}:
                json_fields.add(key)

    if not methods:
        if query:
            methods.add("GET")
        if form or files or json_fields:
            methods.add("POST")
    if not methods:
        methods.add("GET/POST")

    return ViewInfo(
        source=source,
        line=target.lineno,
        methods=sorted(methods),
        query=sorted(query),
        form=sorted(form),
        files=sorted(files),
        json_fields=sorted(json_fields),
        response_types=sorted(responses) or ["未从源码静态确定"],
        response_keys=sorted(response_keys),
        statuses=sorted(statuses),
        auth_markers=sorted(auth),
        docstring=(ast.get_docstring(target) or "").strip(),
    )


def path_params(route: str) -> list[tuple[str, str]]:
    return [(name, kind) for kind, name in re.findall(r"<(?:(\w+):)?(\w+)>", route)]


def endpoint_kind(info: ViewInfo | None) -> str:
    if not info:
        return "未分类"
    types = set(info.response_types)
    if "FileResponse" in types or "StreamingHttpResponse" in types:
        return "文件下载"
    if "render" in types or "redirect" in types:
        return "页面/跳转"
    if "JsonResponse" in types:
        return "JSON API"
    return "HTTP 接口"


def summary(route: Route) -> str:
    value = route.name or route.view
    spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", value).replace("_", " ")
    return spaced.strip()


def display_source(path: Path, line: int) -> str:
    return f"`{path.relative_to(ROOT).as_posix()}:{line}`"


def curl_example(app: str, route: Route, info: ViewInfo | None) -> str:
    url = f"$BASE_URL/{app}/{route.route}"
    for name, kind in path_params(route.route):
        example = "1" if kind == "int" else f"example-{name}"
        url = re.sub(rf"<(?:\w+:)?{re.escape(name)}>", example, url)
    method = (info.methods[0] if info else "GET").split("/")[0]
    args = [f'curl -i -X {method} "{url}"']
    if info and method != "GET":
        if info.json_fields:
            payload = ", ".join(f'\\"{key}\\": \\"example\\"' for key in info.json_fields[:6])
            args.append('  -H "Content-Type: application/json"')
            args.append('  -H "X-CSRFToken: $CSRF_TOKEN"')
            args.append(f"  -d \"{{{payload}}}\"")
        elif info.files:
            args.append('  -H "X-CSRFToken: $CSRF_TOKEN"')
            for key in info.form[:4]:
                args.append(f'  -F "{key}=example"')
            for key in info.files[:2]:
                args.append(f'  -F "{key}=@./example.dat"')
        else:
            args.append('  -H "X-CSRFToken: $CSRF_TOKEN"')
            for key in info.form[:6]:
                args.append(f'  --data-urlencode "{key}=example"')
    elif info and info.query:
        joiner = "&" if "?" in args[0] else "?"
        query = "&".join(f"{key}=example" for key in info.query[:6])
        args[0] = args[0][:-1] + f"{joiner}{query}\""
    args.append('  -b "sessionid=$SESSION_ID"')
    return " \\\n".join(args)


def python_example(app: str, route: Route, info: ViewInfo | None) -> str:
    url = f'base_url + "/{app}/{route.route}"'
    for name, kind in path_params(route.route):
        example = "1" if kind == "int" else f"example-{name}"
        url = url.replace(f"<{kind}:{name}>", example).replace(f"<{name}>", example)
    method = (info.methods[0] if info else "GET").split("/")[0].lower()
    lines = ["import requests", "", "session = requests.Session()", f"url = {url}"]
    if method == "get":
        if info and info.query:
            items = ", ".join(f'"{key}": "example"' for key in info.query[:6])
            lines.append(f"response = session.get(url, params={{{items}}}, timeout=30)")
        else:
            lines.append("response = session.get(url, timeout=30)")
    else:
        if info and info.json_fields:
            items = ", ".join(f'"{key}": "example"' for key in info.json_fields[:6])
            lines.append(f"response = session.{method}(url, json={{{items}}}, timeout=30)")
        elif info and info.files:
            lines.append('with open("example.dat", "rb") as upload:')
            key = info.files[0]
            lines.append(f'    response = session.{method}(url, files={{"{key}": upload}}, timeout=30)')
        else:
            items = ", ".join(f'"{key}": "example"' for key in (info.form[:6] if info else []))
            lines.append(f"response = session.{method}(url, data={{{items}}}, timeout=30)")
    lines.extend(["response.raise_for_status()", "print(response.text)"])
    return "\n".join(lines)


def parameter_table(route: Route, info: ViewInfo | None) -> str:
    rows = ["| 名称 | 位置 | 类型 | 必需性 |", "|---|---|---|---|"]
    for name, kind in path_params(route.route):
        rows.append(f"| `{name}` | path | {kind or 'string'} | 必需 |")
    if info:
        for key in info.query:
            rows.append(f"| `{key}` | query | string | 由视图逻辑决定 |")
        for key in info.form:
            rows.append(f"| `{key}` | form | string | 由视图逻辑决定 |")
        for key in info.files:
            rows.append(f"| `{key}` | multipart file | binary | 由视图逻辑决定 |")
        for key in info.json_fields:
            rows.append(f"| `{key}` | JSON body | 未从源码静态确定 | 由视图逻辑决定 |")
    if len(rows) == 2:
        rows.append("| — | — | — | 无显式输入参数 |")
    return "\n".join(rows)


def render_app(app: str, routes: list[Route]) -> str:
    title = f"{app} 源码校验 API 文档"
    lines = [
        f"# {title}",
        "",
        "> 本文档由 Django URL 配置与对应视图源码生成并人工约束：只记录仓库中可验证的行为。",
        "> 请求/响应示例为源码推导示例，并非线上抓包结果；部署域名、权限策略和实际数据以运行环境为准。",
        "",
        "## 快速开始",
        "",
        f"- 基础路径：`{{BASE_URL}}/{app}/`",
        "- 示例部署地址（来自项目既有文档）：`http://10.30.76.2:8080`",
        "- 认证方式：Django Session/Cookie。先登录并保留 `sessionid`；源码中的具体权限检查并不完全一致。",
        "- CSRF：启用 Django CSRF 中间件。对未标记 `csrf_exempt` 的状态变更请求，应同时发送 CSRF Cookie 与 `X-CSRFToken`。",
        "- API 版本：URL 未包含版本号，仓库中未发现统一的版本协商机制。",
        "- 限流：源码中未发现统一限流配置。",
        "- 内容类型：依端点使用 query、表单、multipart、JSON 或页面渲染；详见各条目。",
        "",
        "```bash",
        "export BASE_URL=http://10.30.76.2:8080",
        "export SESSION_ID=replace-with-session-id",
        "export CSRF_TOKEN=replace-with-csrf-token",
        "```",
        "",
        "## 通用响应与错误约定",
        "",
        "- `JsonResponse` 端点返回 JSON；`render`/`redirect` 端点返回 HTML 或 3xx；文件端点返回二进制响应。",
        "- 视图大量使用自定义 JSON 字段表达成功/失败，不能仅依赖 HTTP 状态码判断业务结果。",
        "- 可能出现的框架级错误包括 `403 CSRF verification failed`、未登录跳转、`404` 以及未捕获异常导致的 `500`。",
        "- 下列“显式状态码”只列出源码直接写出的 `status=` 数值；未列出不代表只会返回 200。",
        "",
        "## 端点索引",
        "",
        "| # | 方法 | 路径 | 类型 | 视图 |",
        "|---:|---|---|---|---|",
    ]
    infos: list[ViewInfo | None] = []
    for idx, route in enumerate(routes, 1):
        info = extract_view(route.app, route.module, route.view)
        infos.append(info)
        methods = ", ".join(info.methods) if info else "未确定"
        lines.append(
            f"| {idx} | `{methods}` | `/{app}/{route.route}` | {endpoint_kind(info)} | `{route.module}.{route.view}` |"
        )

    lines.extend(["", "## 端点详情", ""])
    for idx, (route, info) in enumerate(zip(routes, infos), 1):
        methods = ", ".join(info.methods) if info else "未确定"
        lines.extend(
            [
                f"### {idx}. `{methods} /{app}/{route.route}`",
                "",
                f"**用途：** {summary(route)}。接口类型：{endpoint_kind(info)}。",
                "",
            ]
        )
        if info:
            lines.append(f"**源码：** {display_source(info.source, info.line)}（`{route.module}.{route.view}`）")
            if info.docstring:
                one_line = " ".join(info.docstring.split())
                lines.append(f"**源码说明：** {one_line}")
            marker = "、".join(f"`{item}`" for item in info.auth_markers) or "无函数级认证/CSRF 装饰器"
            lines.append(f"**函数级安全标记：** {marker}。仍需遵循项目 Session 与 CSRF 约定。")
            lines.append(f"**响应形式：** {', '.join(f'`{item}`' for item in info.response_types)}。")
            lines.append(
                f"**显式状态码：** {', '.join(map(str, info.statuses)) if info.statuses else '源码未显式指定'}。"
            )
        else:
            lines.append("**源码：** 未能静态解析对应视图，请以运行时实现为准。")
        lines.extend(["", parameter_table(route, info), "", "**cURL 示例**", "", "```bash", curl_example(app, route, info), "```", ""])
        lines.extend(
            [
                "**Python 示例**",
                "",
                "```python",
                f'base_url = "http://10.30.76.2:8080"',
                python_example(app, route, info),
                "```",
                "",
                "**响应校验建议**",
                "",
                "- JSON 接口：先检查 HTTP 状态，再检查返回对象中的业务状态/消息字段。",
                "- 页面接口：允许 3xx，并检查最终页面或 `Location`。",
                "- 文件接口：检查 `Content-Type`、`Content-Disposition` 与文件大小。",
                "- 失败测试：至少覆盖缺失必填字段、无效标识符、未登录与 CSRF 缺失。",
                "",
            ]
        )
    lines.extend(
        [
            "## 文档边界与维护",
            "",
            f"- 路由总数：{len(routes)}。",
            "- 参数名称来自 `request.GET`、`request.POST`、`request.FILES` 和常见 JSON payload 的静态提取。",
            "- 动态生成的字段、模型序列化结构和异常分支可能无法通过静态分析完整恢复；相应位置明确标记为“未从源码静态确定”。",
            "- 修改 URL 或视图后，运行 `python scripts/generate_source_api_docs.py` 重新生成。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    outputs = {
        "WebDatabase": ROOT / "WebDatabase.source-api.md",
        "LabDatabase": ROOT / "LabDatabase.source-api.md",
    }
    for app, output in outputs.items():
        routes = parse_routes(app)
        output.write_text(render_app(app, routes), encoding="utf-8")
        unresolved = sum(
            extract_view(route.app, route.module, route.view) is None for route in routes
        )
        duplicate_paths = len(routes) - len({route.route for route in routes})
        print(
            f"{app}: {len(routes)} routes, {unresolved} unresolved, "
            f"{duplicate_paths} duplicate paths -> {output}"
        )


if __name__ == "__main__":
    main()
