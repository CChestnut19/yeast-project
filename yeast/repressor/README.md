# Yeast repressor: Supplementary Note 10

Adapted from `repressor_model_scripts(1).zip`, which supplies 1,141 experimental measurements for four sensors. The integrated workflow recalculates predictions directly from `data/experiment_data.csv`, without a separate intermediate-CSV step or parameter refitting.

## Environment and commands

For submission reproduction, use the pinned Python 3.12 environment in [Reproducibility](../../submission/REPRODUCIBILITY.md). The entry points require Python 3.10 or later. To install the workflow's numerical and plotting dependencies separately, run the following from the repository or extracted package root:

```bash
python -m pip install -r yeast/requirements-plotting.txt
python -m yeast.repressor --help
python -m yeast.repressor check
python -m yeast.repressor run --output-dir Output/repressor
python -m yeast.repressor validate --output-dir Output/repressor
```

The examples explicitly write results to `Output/repressor`; use `--output-dir` to choose another location.

- `--data path/to/source/experiment_data.csv` selects another experimental CSV with the same schema. The supplied table is used by default.
- `run --no-plot` generates and validates numerical results without loading plotting libraries. Only NumPy from `yeast/requirements.txt` is required for this mode.
- `check` validates the data and metrics without creating output files.
- `validate` uses the source-file path recorded in the output provenance by default. Pass `--data` to use an identical copy at a new location.

## Input rules

The CSV columns are `sensor,tf_input_rpu,inducer_um,replicate,experiment_rpu`.

The table must contain all four sensors: CI94, CI43470, LexAgs91 and LexAbs94. TF inputs and inducer concentrations must be nonnegative, experimental RPU values must be positive, and replicate identifiers must be positive integers. Duplicate sensor/TF/dose/replicate keys, missing fields and nonfinite values cause an error; rows are not silently discarded.

## Model and statistics

- `model.py` preserves the full precision of the original K1/K2/K3 constants and sensor parameters.
- Mass balance is calculated by `yeast.binding.active_dimer_pool`.
- The model's output weight is `1 - (1 - p_unbound)^2`. This is retained separately from the `p_unbound^2` rule in Note 11.
- `Tmax` is the sensor-specific total output ceiling, and `T0=0.01`.
- Individual replicate measurements remain the observation unit. `metrics.json` reports per-sensor and pooled R², SSE, SST and RMSE on both raw and log10 scales.
- The original scatter plot reports **raw R²**, although its axes are logarithmic. The integrated plot explicitly labels this as `R² (raw)`.
- Log10 R² uses `1-SSE/SST`. It is not replaced by squared correlation, and negative values are not clipped to zero.

## Outputs and validation scope

```text
Output/repressor/
  predictions.csv
  metrics.json
  provenance.json
  validation.json
  pdf/experiment_vs_prediction_35mm.pdf
  svg/experiment_vs_prediction_35mm.svg
  png/experiment_vs_prediction_35mm_600dpi.png
```

The scatter plot remains 35 mm × 35 mm. The three figure files are omitted when `--no-plot` is used.

`validate` recalculates results from the experimental CSV and checks every prediction row, the metrics, the source-file hash and model parameters. `PASS` means that these calculations are consistent. It does not independently establish the validity of the experimental measurements or model fit.

The original prediction table, generated figures and Python caches are not duplicated in the source tree. Prediction tables and figures can be regenerated with the commands above. Original-file hashes are recorded in [REPRESSOR_SOURCE_ARCHIVES.json](../REPRESSOR_SOURCE_ARCHIVES.json).
