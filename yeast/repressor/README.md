# 酵母 repressor：Supplementary Note 10

来自 `repressor_model_scripts(1).zip`，包含 4 个传感器的 1,141 条实验测量。整合后直接从 `data/experiment_data.csv` 重算预测，无需先生成中间 CSV，也不重新拟合参数。

## 运行

在仓库根目录执行，推荐 Python 3.10+：

```bash
python -m pip install -r yeast/requirements-plotting.txt
python -m yeast.repressor check
python -m yeast.repressor run --output-dir G:/codex_outputs/yeast_project/repressor
python -m yeast.repressor validate --output-dir G:/codex_outputs/yeast_project/repressor
```

`--data` 可指定其他相同结构的实验 CSV；默认使用附件数据。`run --no-plot` 仅生成数值结果，只需 `yeast/requirements.txt` 中的 NumPy。`check` 验证数据与指标、不创建输出。`validate` 默认读取输出记录的源文件路径，也可用 `--data` 指向内容相同的新位置。

输入列：`sensor,tf_input_rpu,inducer_um,replicate,experiment_rpu`。必须包含 CI94、CI43470、LexAgs91、LexAbs94；TF 和诱导剂浓度非负，实验 RPU 为正，重复编号为正整数。重复的 sensor/TF/dose/replicate 键、缺失字段及非有限值会报错，不静默删除行。

## 模型和统计

- `model.py` 保留原包 K1/K2/K3 和各传感器参数的完整精度。
- 质量守恒调用 `yeast.binding.active_dimer_pool`。
- 原模型的输出权重为 `1 - (1 - p_unbound)^2`，与 Note 11 的 `p_unbound^2` 分别保留。
- `Tmax` 是各传感器的总输出上限，`T0=0.01`。
- 保留逐重复测量口径；`metrics.json` 同时输出逐传感器及合并的 raw/log10 R²、SSE、SST、RMSE。
- 原散点图标注的是 **raw R²**，虽然坐标轴为对数；整合后的标注明确写为 `R² (raw)`。
- log10 R² 使用 `1-SSE/SST`，不替换成相关系数平方，也不把负值裁为零。

## 输出

```text
--output-dir/
  predictions.csv
  metrics.json
  provenance.json
  validation.json
  pdf/experiment_vs_prediction_35mm.pdf
  svg/experiment_vs_prediction_35mm.svg
  png/experiment_vs_prediction_35mm_600dpi.png
```

散点图尺寸仍为 35 mm × 35 mm。`validate` 从实验 CSV 重新计算，检查完整预测行、指标、源文件哈希及模型参数；`PASS` 只代表这些计算一致。附件的旧预测表、输出图和 `.pyc` 未重复纳入源码，可通过命令重新生成。原文件哈希见 `../REPRESSOR_SOURCE_ARCHIVES.json`。
