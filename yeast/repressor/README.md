# Yeast repressor: Supplementary Note 10

Recalculate 1,141 supplied experimental measurements for four sensors without refitting. The source table is `data/experiment_data.csv`.

```text
python -m yeast.repressor check
python -m yeast.repressor run --output-dir Output/repressor
python -m yeast.repressor validate --output-dir Output/repressor
```

Use the [fixed environment](../../submission/REPRODUCIBILITY.md), or install NumPy via `yeast/requirements.txt`. `--data` selects a CSV with columns `sensor,tf_input_rpu,inducer_um,replicate,experiment_rpu`. All four sensors (CI94, CI43470, LexAgs91, LexAbs94) must be present; concentrations must be nonnegative, observations positive and replicate identifiers positive integers. Duplicate keys and nonfinite/missing values cause errors.

`check` does not write files. `run` writes `predictions.csv`, `metrics.json`, `provenance.json` and `validation.json`, then validates results. `validate` uses the recorded input path unless `--data` specifies an identical relocated source. No plotting options or graphics dependencies remain.

## Model and statistics

Original K1/K2/K3 and sensor parameter precision are preserved. The output weight is `1-(1-p_unbound)^2`, with sensor-specific total ceiling and `T0=0.01`. It differs from Note 11's two-operator rule. Mass balance uses `yeast.binding.active_dimer_pool`.

Individual replicates remain the observation unit. Raw and log10 R², SSE, SST and RMSE are reported per sensor and pooled. R² means `1-SSE/SST`, not squared correlation; negative values are retained. Pooled raw/log10 R² are `0.8769196761349058` / `0.8721193770575127`.

Validation recalculates predictions and metrics from source data and checks hashes/model parameters. It establishes computational consistency, not experimental validity. Original archive hashes remain in [REPRESSOR_SOURCE_ARCHIVES.json](../REPRESSOR_SOURCE_ARCHIVES.json).
