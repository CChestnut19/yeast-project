# Yeast code

| 位置 | 用途 |
| --- | --- |
| `activator/` | 27 个 Supplementary Note 9 activator 面板的固定参数重算、批次聚合、R² 校验与可选历史对比 |
| `repressor/` | Note 10 的 4 个 repressor、1,141 条测量重算、raw/log10 指标及 35 mm 图 |
| `combinatorial/` | Note 11 的组合模型、216 个均值、12 面板两页图和 log10 指标 |
| `analysis.py` | 原有 notebook 的响应、fold-change 和 Pareto 工具 |
| `binding.py` | 共用的二聚体质量守恒计算 |
| `metrics.py` / `reporting.py` | Note 10/11 共用的严格统计、结果导出和重新计算校验 |

两套输出约定分别保留：activator 使用总上限 `Tmax=35.85`，历史 notebook 使用振幅 `Imax`，其总上限为 `I0+Imax`。共用的是底层质量守恒计算。

Note 10 的 repressor 使用各传感器自己的总输出上限及 `1-(1-p)^2`；Note 11 的组合模型使用 `Tmax=35.85` 及 `p_activator*p^2`。两者沿用各自附件参数及精度。说明见 [repressor](repressor/README.md) 和 [combinatorial](combinatorial/README.md)。

运行方式见 [activator/README.md](activator/README.md)。根目录 `yeast_analysis.py` 是兼容入口，不含重复模型实现。历史 notebooks 中还存在不同实验、不同物种和不同参数集；这些内容不等同于当前 27 面板 activator 流程。
