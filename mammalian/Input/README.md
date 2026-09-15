# Required source package

这些输入尚未随用户提供的 7 个 Python 文件或 GitHub 仓库提供。请保留原始文件和来源；不要用预测曲线或其他拟合结果代替原始实验观测。

## 拟合与数值验证

- 含 26 个映射条目的原始 README：25 个 Included，`402.csv` 为 Excluded。表列顺序为 `CSV | Sensor name | Source DBD | Canonical DBD | Canonical LBD | Fit status`。
- 25 个映射为 Included 的 CSV，至少包含数值列 `LBD,inducer,RPU`。浓度非负，RPU 正值；缺失值、无穷值和无变异数据会明确报错。全部为空的记录可忽略。
- `pure_log10_initial_parameter_vector.npy`。
- `hybrid_initial_parameter_vector.npy`。

向量顺序由映射中 LBD/DBD 首次出现顺序决定：`log10(Kd0)`, `log10(Kb)`, `log10(Kd1)`, 非 anchor 的 `log10(KA)`, `T0_variant`。原始 13 LBD/11 DBD 对应 60 个自由参数。仅向量长度一致不足以证明映射顺序正确，必须配套使用同一来源的映射和向量。

## 出版图表

- `all_25_sensor_plot_settings.csv`
- `all_25_sensor_30mm_style.json`
- `mammalian_experiment_vs_prediction_plot_settings.json`
- `Supplementary Figure 13_original.pdf`

Figure 13 会保留原图 A-C 并重绘 D-M。原 PDF、零浓度显示约定、样式文件以及 Helvetica 字体均属于复现资料。
