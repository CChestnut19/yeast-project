# Mammalian CIC algorithms (n = 7)

This algorithm-only workflow fits 25 CIC sensors and validates numerical results. `402.csv` is an excluded control. LBDs share `Kd0/Kb/Kd1`, DBDs share `KA/T0_variant`, `KA_lexAec87=9.15`, and the total output ceiling is `Tmax=13.61`.

**Original experimental inputs are not included.** See [Input/README.md](Input/README.md). The source README must contain the real six-column sensor mapping, and the two initial parameter vectors must use that mapping's order. Synthetic tests do not establish experimental reproduction.

## Run

Install the numerical dependencies and run from the repository root, replacing `path/to/source` with the original package location:

```bash
python -m pip install -r mammalian/Scripts/requirements-main-supp-n7.txt
python mammalian/Scripts/run_pipeline.py --stage check --readme path/to/source/README.md --input-dir path/to/source/Input
python mammalian/Scripts/run_pipeline.py --stage fit --readme path/to/source/README.md --input-dir path/to/source/Input --output-dir Output/mammalian
python mammalian/Scripts/validate_results.py --readme path/to/source/README.md --input-dir path/to/source/Input --result-dir Output/mammalian/scipy_sensor_logR2_floor_0p5
```

`check` checks the observed data, mapping and archived initial vectors. `fit` performs constrained fitting with log10 R² >= 0.5 for every sensor, then validates the saved numerical results. `all` runs the same complete algorithm workflow. Plot settings, PDFs and fonts are not inputs.

## Fitting objective

All fitting paths minimize the equal-CSV objective

```text
z_ij = log10(RPU_observed_ij)
SST_j = sum_i (z_ij - mean_i(z_ij))^2
R2_log10_j = 1 - sum_i (log10(RPU_predicted_ij) - z_ij)^2 / SST_j
objective_total = mean_j (1 - R2_log10_j)
```

Each CSV contributes equally, regardless of its number of observations or log-scale variance. Least-squares residuals are divided by `sqrt(number_of_CSVs * SST_j)`. Raw-scale R² and global log10 MSE are diagnostic metrics. There is no shape-prior term. Observed RPU must be finite, strictly positive and nonconstant on the log10 scale in every CSV; invalid observations are rejected without clipping.

The floor fitter first optimizes this objective from each archived start, then uses adaptive CSV weights to seek the additional constraint `R2_log10_j >= 0.5` for every sensor. It retains evaluated candidates and selects the feasible candidate with the largest unweighted mean per-CSV log10 R². The adaptive weighted search loss is recorded separately from `objective_total`. This numerical search does not guarantee a global constrained optimum. Archived initial-vector filenames retain their historical names; they do not select the fitting objective.

Results are written under `--output-dir/scipy_sensor_logR2_floor_0p5/`: parameter tables and vector, observation-level predictions and model intermediates, error metrics, objective components, candidate comparison, optimization trace, fit summary and numerical validation report. If optimization finds no feasible solution, diagnostics remain available and fitting exits with code 2. Initial vectors are never silently taken from another directory.

Running `model_core.py --backend scipy|torch|both` directly uses the same pure macro log10-R² objective, without the per-sensor 0.5 floor. It writes to `scipy_curve_fit_macro_log10_r2` and/or `pytorch_adam_macro_log10_r2`; the comparison is `backend_comparison_macro_log10_r2.csv`. The optional PyTorch backend needs the root `requirements-torch.txt` and is imported only when requested.

Adam status records `epoch_budget` or `patience` as its stopping reason; neither certifies convergence. The returned objective is recomputed from the saved best parameter vector, including consideration of the final update.

## Validation scope

`validate_results.py` recalculates predictions, model intermediates, per-sensor R² and the macro log10-R² objective from the experimental CSVs and parameter vector. It checks parameter bounds, saved observation keys, mapping metadata, parameter tables, objective components and the fit summary. For floor results it also checks per-sensor SSE/SST, constraint flags and selected-candidate metrics. The saver rejects inconsistent supplied objectives or candidate feasibility before writing output. Validation accepts either a floor result directory or a direct SciPy/Torch result directory; it writes `numerical_validation_report.md` and needs only numerical inputs and fit outputs.

## Optional dose-response analysis

`model_core.build_dense_curve_outputs(data, layout, vector)` remains available for explicit numerical analysis. It returns sampled model responses and numerical shape measures, including dose values at 10%, 50% and 90% of the sampled response amplitude, transition width in log10 dose, endpoint amplitude and monotonicity. These are sampled-range measures rather than experimentally established asymptotes. Endpoint-only LBDs are labeled `endpoint_only_unregularized` with limited curve-shape identifiability. The fitter does not automatically generate or export these sampled tables.
