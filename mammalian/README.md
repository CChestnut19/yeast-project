# Mammalian CIC model (n = 7)

This independent workflow fits 25 CIC sensors. `402.csv` is an excluded control. LBDs share `Kd0/Kb/Kd1`, DBDs share `KA/T0_variant`, `KA_lexAec87=9.15`, and the total output ceiling is `Tmax=13.61`.

**Original experimental inputs are not included.** See [Input/README.md](Input/README.md). The source README must contain the real six-column sensor mapping, and the two initial parameter vectors must use that mapping's order. Synthetic tests do not establish experimental reproduction.

## Run

Install the [pinned submission environment](../submission/REPRODUCIBILITY.md). Run from the repository root, replacing `path/to/source` with the original package location:

```bash
python mammalian/Scripts/run_pipeline.py --stage check --readme path/to/source/README.md --input-dir path/to/source/Input
python mammalian/Scripts/run_pipeline.py --stage fit --readme path/to/source/README.md --input-dir path/to/source/Input --output-dir Output/mammalian
python mammalian/Scripts/run_pipeline.py --stage figures --readme path/to/source/README.md --input-dir path/to/source/Input --output-dir Output/mammalian
```

`fit` performs constrained fitting with log10 R² >= 0.5 for every sensor and numerical validation. `figures` uses saved parameters for all 25 curves, corrected Figure 13, experiment-versus-prediction plots and Word parameter tables. `all` runs both stages. `check` checks the inputs, mapping, vector shapes and figure resources; font availability and layout are checked during plotting.

Results are written under `--output-dir/scipy_sensor_logR2_floor_0p5/`. If optimization finds no feasible solution, diagnostics remain available and the command exits with code 2 before figure generation. Initial vectors are never silently taken from another directory.

Running `model_core.py --backend scipy|torch|both` directly uses the original mixed raw/log10 macro-R² objective, which differs from the constrained fitting objective and writes to a different directory. The optional PyTorch backend needs `requirements-torch.txt` and is outside the pinned submission demo.

## Validation scope

`validate_results.py --numerical-only` recalculates predictions, model intermediates and per-sensor R² from the experimental CSVs and parameter vector, and checks the parameter tables and summary. Full validation also requires the manuscript-specific counts (953 observations and the zero-dose convention for `549.csv`), publication PDFs and style resources.

Publication plotting requires locally available, legally usable and embeddable Helvetica regular and bold fonts. Fonts are not distributed here, and publication fonts are not silently substituted.
