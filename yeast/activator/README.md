# Yeast activator

整理自用户提供的 `05_scripts(1).zip`。本模块以补充表参数重算 27 个面板，不重新拟合参数。默认分析与模型约定沿用原脚本。

## 安装

在仓库根目录运行，Python 3.10 或以上：

```bash
python -m pip install -r yeast/requirements.txt
python -m yeast.activator --help
```

## 输入

1. 原始 `Source data.xlsx`，含 `SI-note activator` 工作表。原始布局至少覆盖 `A1:BW296`；行列位置对应 `panels.py` 的 27 个面板。
2. 从补充表提取的 `Supplementary_information_tables.tsv`，列为 `table_index,row_index,column_index,text`，以制表符分隔。索引沿用原脚本：Table 1 存 DBD/operator/KA/T0，Table 2 存 LBD/Kd0/Kb/Kd1。
3. 可选的原始 `source_sheet_dump.json`。提供时会核对工作表名称、A1 起点、单元格值与可用的工作簿哈希。

压缩包仅含脚本和 Python 缓存，没有这些真实输入。本仓库的 `tests/activator_fixture.py` 只生成测试用合成数据，不能代替实验数据。

读取器使用 OOXML 的缓存值，保留文本星号和 RGB `A9D18E` 绿色填充，不计算 Excel 公式。遇到无缓存公式或 Excel 错误值会报错；需先在原工作簿中计算并保存。公式信息记录原始 OOXML 内容；共享公式不会由读取器展开或重新计算。

## 常用命令

以下示例中的 `G:/yeast_source` 请替换成真实资料路径；输出目录可自定，建议使用 G 盘。

```bash
# 只检查输入，不创建输出
python -m yeast.activator check --source-xlsx "G:/yeast_source/Source data.xlsx" --parameter-table G:/yeast_source/Supplementary_information_tables.tsv

# 提取缓存值，替代原 00_dump_source_sheet.mjs
python -m yeast.activator dump --source-xlsx "G:/yeast_source/Source data.xlsx" --output-dir G:/codex_outputs/yeast_project/activator

# 一次完成重算与独立校验
python -m yeast.activator run --source-xlsx "G:/yeast_source/Source data.xlsx" --parameter-table G:/yeast_source/Supplementary_information_tables.tsv --output-dir G:/codex_outputs/yeast_project/activator

# 复核已经生成的结果
python -m yeast.activator validate --output-dir G:/codex_outputs/yeast_project/activator
```

`recalculate` 只重算并生成校验清单；结果状态为 `NOT_VALIDATED`，直到独立校验成功。`run` 顺序执行重算与校验。校验失败返回退出码 2，并将 QA 状态更新为 `FAIL`。

历史对比可在 `run` 或 `validate` 后添加 `--previous-root G:/previous_audit`。指定后必须提供下列旧资料，缺失时明确报错；未指定则独立校验当前结果：

```text
previous_audit/
  04_quantitative_audit/03_R2_three_metrics_batch_specific.csv
  02_numeric_reconstruction/01_raw_measurements_long.csv
  02_numeric_reconstruction/source_sheet_dump.json
```

## 保留的分析规则

- 主模型为 S32–S47 质量守恒加 S11，`Tmax=35.85` 为总输出上限，`T0_variant` 来自补充表。
- LexAec87 的 `KA=0.74` 是原压缩包记录的覆盖值；对应 `T0_variant` 继续取表值。
- 带尾随 `*` 的测量先排除。只带绿色填充的值保留在主分析中，并额外计算排除绿色值的敏感性分析。
- R² 的观测单位为同面板、同批次/Run/Day、同实际 TF 输入和同诱导剂浓度下的非星号重复测量算术均值。不同批次不合并计算 R²。
- 绘图汇总另行将实际 TF 输入相近的批次分组，每个非零成员距组均值不超过 30%；该合并不改变 R² 的观测单位。
- 原主指标为 **raw-scale R²**；`batch_conditional_log10` 单独报告 **log10 R²**。两者均为 `1-SSE/SST`，Pearson r² 仅为诊断。
- 保留 `Tmax=35`、统一 `T0=0.035`、去除绿色值、逐重复测量及 literal S83 等原敏感性分析。log10 指标会记录非正值或非有限值的省略数。

## 输出及代码位置

```text
--output-dir/
  02_numeric_reconstruction/  # 7 张数值表、源数据快照、执行信息、哈希清单
  03_results/                 # 27 面板 log10 R² 独立复核表
  04_qa/                     # QA 状态；可选历史源数据变化表
```

数值 CSV 文件名沿用原脚本。清单改为可跨平台的 JSON 格式；QA 表中的历史对比字段在未提供旧包时留空。`validate` 先核对生成文件哈希，再从保存的源快照、原始测量和参数表复核条件均值、预测与 R²；这验证计算一致性，不表示模型拟合优良或原始实验无误。

| 模块 | 内容 |
| --- | --- |
| `source.py` | 工作表缓存值、星号、绿色填充、CSV/JSON 和哈希 |
| `panels.py` / `parameters.py` / `settings.py` | 27 面板布局、补充表解析及原分析默认值 |
| `measurements.py` | 数字表头、ordinal、Run/Day 等批次布局解析 |
| `model.py` | 模型、单位换算、R² 与 Pearson 诊断 |
| `aggregation.py` | 分批条件均值及独立的绘图汇总 |
| `recalculate.py` / `validate.py` | 重算、数值导出与独立复核 |
| `__main__.py` | 统一命令行入口 |

原版对照及测试范围见 [REVIEW.md](REVIEW.md)。
