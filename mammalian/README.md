# Mammalian CIC model (n = 7)

独立保存哺乳动物工作流。默认拟合对象为 25 个 CIC CSV；`402.csv` 为排除对照。LBD 共享 `Kd0/Kb/Kd1`，DBD 共享 `KA/T0_variant`，`KA_lexAec87=9.15`，`Tmax=13.61`。

## 所需原始资料

见 [Input/README.md](Input/README.md)。本文件不提供虚构的映射表；请用 `--readme` 指向配套资料中含真实六列表格的 README。两个 `.npy` 初始向量的顺序必须与该映射一致。

## 运行

从仓库根目录执行；下例路径请替换成真实输入位置。

```bash
python mammalian/Scripts/run_pipeline.py --stage check --readme G:/mammalian_source/README.md --input-dir G:/mammalian_source/Input
python mammalian/Scripts/run_pipeline.py --stage fit --readme G:/mammalian_source/README.md --input-dir G:/mammalian_source/Input --output-dir G:/codex_outputs/yeast_project/mammalian
python mammalian/Scripts/run_pipeline.py --stage figures --readme G:/mammalian_source/README.md --input-dir G:/mammalian_source/Input --output-dir G:/codex_outputs/yeast_project/mammalian
```

`fit` 执行带每传感器 log10 R²≥0.5 约束的拟合与数值复核；`figures` 使用已保存参数生成 25 传感器曲线、校正 Figure 13、实验-预测图和 Word 参数表。`all` 顺序执行两阶段。`check` 检查输入数据、映射、向量形状和绘图文件是否存在；字体可用性和布局在绘图阶段检查。

结果目录为 `--output-dir/scipy_sensor_logR2_floor_0p5/`。优化没有找到可行解时仍保留诊断，但以退出码 2 终止，不继续生成正式图表。初始向量不会从其他目录静默读取。

单独运行 `model_core.py --backend scipy|torch|both` 可使用原有混合 raw/log10 macro-R² 目标；它与约束拟合目标不同，输出目录也不同。PyTorch 需要额外依赖。

## 验证范围

`validate_results.py --numerical-only` 从原始 CSV 与参数向量重算预测、模型中间量和逐传感器 R²，并检查参数表与汇总一致性。默认完整验证还要求论文数据的固定计数（953 条观测、549.csv 的零浓度约定）、出版 PDF 和样式资料。

参考字体 Helvetica 需要本机安装合法可用且支持 PDF 嵌入的常规体和粗体。仓库不随附字体，也不会静默替换出版字体。
