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

Results are written under `--output-dir/scipy_sensor_logR2_floor_0p5/`: parameter tables and vector, observation-level predictions and model intermediates, error metrics, objective components, candidate comparison, optimization trace, fit summary and numerical validation report. If optimization finds no feasible solution, diagnostics remain available and fitting exits with code 2. Initial vectors are never silently taken from another directory.

Running `model_core.py --backend scipy|torch|both` directly uses the original mixed raw/log10 macro-R² objective, which differs from the constrained fitting objective and writes to a different directory. The optional PyTorch backend needs the root `requirements-torch.txt`.

## Validation scope

`validate_results.py` recalculates predictions, model intermediates and per-sensor R² from the experimental CSVs and parameter vector, and checks parameter bounds, saved observation keys, mapping metadata, parameter tables, constraint flags and the fit summary. It writes `numerical_validation_report.md` and needs only numerical inputs and fit outputs.

## Optional dose-response analysis

`model_core.build_dense_curve_outputs(data, layout, vector)` remains available for explicit numerical analysis. It returns sampled model responses and numerical shape measures, including dose values at 10%, 50% and 90% of the sampled response amplitude, transition width in log10 dose, endpoint amplitude and monotonicity. These are sampled-range measures rather than experimentally established asymptotes. Its source labels describe the mixed-objective model's endpoint-only shape prior; when analyzing a floor fit, endpoint-only LBDs were fitted without that prior. The fitter does not automatically generate or export these sampled tables.
