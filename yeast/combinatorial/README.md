# Yeast activator + repressor: Supplementary Note 11

Recalculate the 216 supplied experimental means across 12 panels (A1-C4). Sample SD values remain in the input table as experimental metadata; they do not weight fitting.

```text
python -m yeast.combinatorial check
python -m yeast.combinatorial run --output-dir Output/combinatorial
python -m yeast.combinatorial validate --output-dir Output/combinatorial
```

Use the [fixed environment](../../submission/REPRODUCIBILITY.md), or install NumPy via `yeast/requirements.txt`. `--data` selects a CSV with columns `panel,condition,x_value_uM,series_value_uM,mean_RPU,sample_SD_RPU`. Panel suffix and condition must agree. Doses/SDs must be nonnegative, means positive, and panel/x/series keys unique. All 12 panels must occur. Invalid or nonfinite inputs cause errors.

`check` writes no files. `run` writes `predictions.csv`, `metrics.json`, `provenance.json` and `validation.json`, and independently checks the result. `validate` accepts `--data` for an identical relocated source. Rendering options, PDF layouts, palettes and coordinates have been removed.

## Fixed model conventions

- Activator TF inputs: 0.49 / 8.12; repressor TF inputs: 0.21 / 4.56.
- `Tmax=35.85`, repressor `T0=0.01`, two repressor operators.
- Output weight: `p_activator*p_unbound^2`; original parameter precision remains distinct from Note 10.
- Conditions 1/2 vary activator inducer; 3/4 vary repressor inducer.
- Each panel uses experimental means to calculate log10 R². A2 remains `-1.073005331220207`.

Equations are in `model.py`, input validation in `data.py`, and numerical execution in `pipeline.py`. The retained CSV filename reflects the supplied archive's naming; no drawing is performed. Supplied means have not been independently reconciled with the original workbook.
