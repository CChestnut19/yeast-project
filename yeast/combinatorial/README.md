# 酵母 activator + repressor：Supplementary Note 11

来自 `Supplementary_Note_11_plot(1).zip`。保留 216 个实验均值及样本 SD、12 个面板、两页 PDF 底图、坐标位置和 CMYK 调色板。

## 运行

在仓库根目录执行，推荐 Python 3.10+：

```bash
python -m pip install -r yeast/requirements-plotting.txt
python -m yeast.combinatorial check
python -m yeast.combinatorial run --output-dir G:/codex_outputs/yeast_project/combinatorial
python -m yeast.combinatorial validate --output-dir G:/codex_outputs/yeast_project/combinatorial
```

PNG 导出沿用 Poppler 的 `pdftoppm`，需在 `PATH` 中可用。添加 `--pdf-only` 只生成矢量 PDF；添加 `--no-plot` 只生成数值结果，且只需 `yeast/requirements.txt` 中的 NumPy。

- `--data`：替代实验均值 CSV。
- `--resources-dir`：含坐标、几何、颜色 JSON 和 PDF 底图的目录。
- `--layout`：单独指定相同坐标体系的两页 A4 底图。
- `--dpi`：PNG 分辨率，默认 300。
- `check` 检查数据、指标及绘图资源，不写输出；`check --no-plot` 仅检查数值输入。

输入列：`panel,condition,x_value_uM,series_value_uM,mean_RPU,sample_SD_RPU`。必须覆盖 A1–C4；panel 后缀与 condition 一致。剂量和 SD 非负，均值为正；每个 panel/x/series 仅有一个均值。错误和非有限值直接报错。

## 固定模型约定

- activator TF：0.49 / 8.12；repressor TF：0.21 / 4.56。
- `Tmax=35.85`，两种 repressor 的 `T0=0.01`，operator 数为 2。
- 输出权重为 `p_activator * p_unbound^2`；保留 Note 11 原参数精度，不与 Note 10 的完整精度参数强行统一。
- 条件 1/2 的 x 轴为 activator 诱导剂；条件 3/4 的 x 轴为 repressor 诱导剂。
- 每个面板使用实验均值计算 log10 R²，SD 仅用于误差棒，不用于加权拟合。
- 原附件 A2 的 log10 R² 约为 **−1.073005**；整合后保留该结果。

数值计算在 `model.py`，输入校验在 `data.py`，图形代码在 `plotting.py`。底图和坐标资源绑定于原始版式；替代数据应使用原剂量范围和已有 series 颜色，若要改变图的范围，须同时更新资源。

## 输出与校验

```text
--output-dir/
  predictions.csv
  metrics.json
  provenance.json
  validation.json
  Supplementary_Note_11.pdf
  Supplementary_Note_11_page_1.png
  Supplementary_Note_11_page_2.png
  Supplementary_Note_11.png
```

PDF 保留两页矢量版式，另输出单页及拼接 PNG。`validate` 默认使用 provenance 中记录的源 CSV，也可用 `--data` 指定内容相同的新位置；它重新计算预测及指标，不依赖已保存的预测进行自证。检查不需要绘图库，也不将绘图文件的存在视为数值正确的证据。附件仅提供整理后的实验均值，未独立复核它们与原始工作簿的对应关系。
