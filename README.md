# yeast-project

酵母传感器分析 notebooks，以及独立的哺乳动物 CIC 拟合模块。

## 目录

- 根目录 10 个 `.ipynb`：保留各实验和模型变体。许多历史单元格仍使用 `E:/Desktop/...` 数据路径，运行前需按自己的实验目录修改；原始数据没有随仓库提供。
- `yeast_analysis.py`：`new_foldchange.ipynb` 共用的响应、折叠变化和二维 Pareto 筛选。酵母 `Imax` 表示振幅，总输出上限为 `I0 + Imax`。
- `mammalian/Scripts/`：7 个原始脚本经检查后的版本，以及 `run_pipeline.py`。该模型的总输出上限固定为 13.61 RPU，与酵母模型分开维护。
- `tests/`：合成数据回归测试、notebook 语法检查、命令行入口检查。合成测试结果不代表真实实验拟合已复现。
- `tools/clean_notebooks.py`：清理 notebook 的执行输出和未使用导入。

## 安装与测试

Python 3.10 或以上。在仓库根目录运行：

```bash
python -m pip install -r mammalian/Scripts/requirements-main-supp-n7.txt
python -m unittest discover -s tests -v
```

PyTorch 是可选依赖；使用 Adam 后端或历史 PyTorch notebook 单元格时，另安装 `requirements-torch.txt`。未安装 PyTorch 时仅跳过对应后端测试。

## 使用

酵母分析：从仓库根目录打开 notebooks；`new_foldchange.ipynb` 导入同目录的 `yeast_analysis.py`。各单元格保留不同的参数集，运行完整 notebook 时按原顺序执行。

哺乳动物流程见 [mammalian/README.md](mammalian/README.md)。当前仓库尚未包含实验 CSV、原始映射、初始向量及出版绘图资源；预检查会明确报告缺少的输入。

生成结果写入明确指定的输出目录；请优先使用 G 盘目录。不要把生成的 notebook 图像、缓存和拟合结果重复提交到源码仓库。

本次修改和验证范围见 [CODE_REVIEW.md](CODE_REVIEW.md)。
