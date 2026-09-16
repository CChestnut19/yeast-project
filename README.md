# yeast-project

酵母 activator、repressor、组合调控数值计算与绘图、历史分析 notebooks，以及独立的哺乳动物 CIC 拟合模块。

## 目录

- 根目录 10 个 `.ipynb`：保留各实验和模型变体。许多历史单元格仍使用 `E:/Desktop/...` 数据路径，运行前需按自己的实验目录修改；原始数据没有随仓库提供。
- `yeast/activator/`：来自 `05_scripts(1).zip` 的 27 面板 activator 工作流，按数据读取、面板、参数、模型、聚合、重算和校验分模块；入口为 `python -m yeast.activator`。
- `yeast/repressor/`：Supplementary Note 10 的 4 个 repressor、1,141 条测量及 35 mm 散点图；入口为 `python -m yeast.repressor`。
- `yeast/combinatorial/`：Supplementary Note 11 的 activator/repressor 组合模型、216 个实验均值、12 面板两页图；入口为 `python -m yeast.combinatorial`。
- `yeast/analysis.py`：历史 notebook 共用的响应、折叠变化和二维 Pareto 筛选。根目录 `yeast_analysis.py` 保留兼容导入。
- `yeast/binding.py`：酵母模型共用的质量守恒计算。历史 notebook 的 `Imax` 表示振幅；activator 的 `Tmax=35.85` 表示总输出上限。
- `mammalian/Scripts/`：7 个原始脚本经检查后的版本，以及 `run_pipeline.py`。该模型的总输出上限固定为 13.61 RPU，与酵母模型分开维护。
- `tests/`：合成数据回归测试、notebook 语法检查、命令行入口检查。合成测试结果不代表真实实验拟合已复现。
- `tools/clean_notebooks.py`：清理 notebook 的执行输出和未使用导入。

## 安装与测试

Python 3.10 或以上。在仓库根目录运行：

```bash
python -m pip install -r mammalian/Scripts/requirements-main-supp-n7.txt
python -m pip install -r yeast/requirements-plotting.txt
python -m unittest discover -s tests -v
```

PyTorch 是可选依赖；使用 Adam 后端或历史 PyTorch notebook 单元格时，另安装 `requirements-torch.txt`。未安装 PyTorch 时仅跳过对应后端测试。

## 使用

酵母 activator 的输入格式、运行命令和分析规则见 [yeast/activator/README.md](yeast/activator/README.md)。只运行该工作流时安装 `yeast/requirements.txt` 即可，不需要 Node、Excel 应用或专用 artifact-tool 运行库。

本次新增的 [repressor](yeast/repressor/README.md) 和 [组合调控](yeast/combinatorial/README.md) 已包含附件中的实验 CSV，可直接运行：

```bash
python -m yeast.repressor run --output-dir G:/codex_outputs/yeast_project/repressor
python -m yeast.combinatorial run --output-dir G:/codex_outputs/yeast_project/combinatorial --pdf-only
```

去掉 `--pdf-only` 可导出 Note 11 PNG，需要 Poppler `pdftoppm`。两套模型共用质量守恒与严格的统计计算，保留不同的 operator 公式、参数精度及实验聚合口径。

历史酵母分析：从仓库根目录打开 notebooks；`new_foldchange.ipynb` 的原导入方式继续可用。各单元格保留不同的参数集与模型变体，不能因为名称相近就替换成 activator 的结果。

哺乳动物流程见 [mammalian/README.md](mammalian/README.md)。当前仓库尚未包含实验 CSV、原始映射、初始向量及出版绘图资源；预检查会明确报告缺少的输入。

生成结果写入明确指定的输出目录；请优先使用 G 盘目录。不要把生成的 notebook 图像、缓存和拟合结果重复提交到源码仓库。

最初整理记录见 [CODE_REVIEW.md](CODE_REVIEW.md)，本次 activator 整理与原版对照记录见 [yeast/activator/REVIEW.md](yeast/activator/REVIEW.md)。
