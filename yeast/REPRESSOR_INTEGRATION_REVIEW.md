# Note 10/11 integration review — 2026-09-16

## 来源与组织

- `repressor_model_scripts(1).zip` → `yeast/repressor/`：4 个 repressor，1,141 条实验测量，35 mm 散点图。
- `Supplementary_Note_11_plot(1).zip` → `yeast/combinatorial/`：216 个实验均值及样本 SD，12 个面板，两页矢量 PDF。
- 附件源代码、数据和资源的 SHA-256 记录在 `REPRESSOR_SOURCE_ARCHIVES.json`。
- 实验输入 CSV 和不可替代的 PDF 底图、坐标/颜色 JSON 纳入版本控制。可重新生成的预测表、指标、输出图、Python 缓存没有重复提交。
- 两套流程统一提供 `check/run/validate` 命令和显式数据/输出路径；数值计算与绘图分离。

## 保留的科学差异

| 项目 | Note 10 | Note 11 |
| --- | --- | --- |
| 调控权重 | `1-(1-p_unbound)^2` | `p_activator*p_unbound^2` |
| 输出上限 | 各传感器自己的 Tmax | 35.85 RPU |
| 参数精度 | 原模型完整小数精度 | 原绘图脚本的舍入参数 |
| 统计单位 | 逐重复测量 | 每个实验条件的均值 |
| 图中指标 | raw R²，明确标为 `R² (raw)` | 每面板 log10 R² |

共用 `yeast/binding.py` 的质量守恒求解，以及新 `metrics.py`、`reporting.py` 的严格指标、导出与重算校验。现有 activator 对非正值/非有限值的敏感性分析省略政策保持独立。

## 修复

- 命令可直接从实验 CSV 运行，不再依赖旧中间预测 CSV。
- 验证字段、重复键、panel/condition 一致性、正 RPU、非负剂量/SD、有限值和常数响应。
- 保存完整预测、raw/log10 指标及源文件/模型参数来源；`validate` 从源 CSV 重算，比较全部行及指标。
- 无论优化模式 `python -O` 是否启用，错误预测仍会被拒绝。
- 校验坐标方向及必要绘图字段，避免错误资源造成实验点和预测曲线错位。
- 绘图依赖缺失时返回退出码 2 并写 FAIL；数值命令无需加载绘图库。
- 保留负 R²。Note 11 A2 的原结果为 −1.073005331220207。
- 修复 Windows 编码造成的图中 R² 标签问题，并验证最终 PDF 中的标签文本及 35 mm 尺寸。

## 验证结果

命令：`python -m unittest discover -s tests -v`。

- 共 **52 项测试通过**：原有 40 项，本次新增 12 项。
- Note 10：逐行对照原预测表的全部 1,141 行及数值列，最大绝对差 **0**；4 个传感器及合并 log10 指标均匹配原包结果。
- Note 10 合并 raw R²：0.8769196761349058；log10 R²：0.8721193770575127。
- Note 11：全部 216 个预测及 12 个面板 log10 R² 与原脚本一致（测试容差 `rtol=1e-13, atol=1e-14`）。
- Note 11 两页 PNG 均为 2481×3508，与附件同名页面 **逐像素一致**；已视觉检查两页。
- 已实际生成 Note 10 的 PDF/SVG/600 dpi PNG，和 Note 11 的两页 PDF、300 dpi 页面/拼接 PNG。
- 独立代码审查发现的坐标方向、依赖缺失状态两项问题已通过失败复现、修复、定向复查闭环。

本地使用 Python 3.9.15、NumPy 1.23.5、Matplotlib 3.6.2；仓库推荐 Python 3.10+，CI 为 Python 3.11。原 notebook 注释块中的无效反斜杠转义仍有一条弃用警告；不影响测试。GitHub CI 的执行结果与本地测试分别记录。

## 范围限制

本次复现使用附件中的实验 CSV；没有独立核对这些整理后的数据与原始工作簿/原始实验记录。未修改参数、重新拟合或改写生物学模型；`PASS` 表示数值重算一致，不代表拟合质量合格。
