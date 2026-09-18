# Algorithm-only validation

Validation date: **2026-09-18**, draft `0.2.1-draft.1`. These results concern the canonical-formula and log10-R² revision. Previous raw/mixed-objective and historical-literal checks do not describe the current fitting behavior.

## Environment and commands

A fresh isolated CPython 3.12.14 environment on Windows 11 AMD64 installed the [fixed lock](requirements-lock.txt) in 33.382 seconds using a populated pip cache. `pip check` passed. The environment contains no Matplotlib, seaborn, Plotly, Pillow, pypdf, reportlab, python-docx or fontTools. Full measured details are in [environment.json](environment.json).

```text
python -m pip check
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir Output/demo
```

| Verification | Result |
| --- | --- |
| Complete suite in the working source tree | 102 tests: 96 passed, 6 optional Torch tests skipped; 20.870 seconds |
| Fitting/backend suite in an existing Torch environment | 21 passed, including all 6 skipped tests; 1.564 seconds |
| Numerical demo | PASS; 0.441 seconds |
| Archive construction, inventory and integrity tests | Passed for 78 inventoried files, deterministic archives, extracted manifests and tampering rejection |
| Syntax, local documentation links and production rendering imports | Passed |

Timings describe these small workloads on a 20-logical-CPU machine, not full optimization runtimes. The optional backend suite used Python 3.9.15, Torch 1.13.0, NumPy 1.23.5, SciPy 1.10.1 and pandas 1.5.3. It checked canonical yeast/mammalian models, log10 objectives and real Adam updates; the full suite was run in the Python 3.12 locked environment. The existing locked environment was reused without changing its dependencies.

The GitHub Actions workflow also runs installation, the complete suite, demo and archive build on Windows and Ubuntu. Consult [the exact commit's workflow run](https://github.com/CChestnut19/yeast-project/actions) for remote status; the table above records measured local results.

## Numerical evidence

- Note 10 retains **1,141** supplied replicate measurements, four sensors and all archived sensor metrics. Pooled raw R² is `0.8769196761349058`; pooled log10 R² is `0.8721193770575127`.
- Note 11 retains **216** supplied means across 12 panels, all predictions and archived panel statistics. A2 log10 R² remains `-1.073005331220207`; negative values are not replaced or clipped.
- Activator tests retain grouping, source exclusions, aggregation units and all 27 reference log10 metrics using synthetic workbook fixtures. Removing the inconsistent S83 sensitivity removes 27 secondary statistic rows; the original reference fixture remains unchanged as provenance.
- Mammalian tests cover the pure per-CSV log10 objective, removal of raw/prior terms, feasible-candidate ranking, saved-objective tampering, formula parity and the final Adam update's objective/parameter pairing. An already-feasible initial vector still undergoes objective optimization.
- The [notebook migration inventory](../docs/NOTEBOOK_MIGRATION.md) still covers all **59 code cells**. Original cell hashes and parameter literals remain provenance; corrected formulas are intentionally not asserted to equal the inconsistent historical expressions.
- Cross-module tests verify CIC mass balance, amplitude/total-ceiling conversion, canonical nuclear folds and crosstalk, and the Note 11 hybrid operator rule. Independent review checked 1,000 randomized mass balances with maximum relative residual `5.87e-16` and a 64-case exact-inversion grid without failures.
- Biased-data tests distinguish raw from log fitting: the simple raw optimum is 37 and the log optimum is 10; the current fitter returns 10. Unequal-size/variance groups and repeated rows verify equal-dataset weighting. Actual Adam updates retain that weighting.
- Tests reject zero, negative, nonfinite and constant observations, including a seven-row constant dataset whose floating-point SST is spuriously nonzero. They also check exact parameter inversions, per-row kd, bounds, Pareto ties, alignment statistics and GP selection. These are computational checks, not real-data fitting results.
- Default Note 10/11 commands pass with rendering imports actively blocked. Numerical outputs include predictions, metrics, provenance and validation; no rendering flag is needed.

## Limits

Original activator workbook/parameter inputs, mammalian input tables/mapping/initial vectors and the former notebooks' private CSVs are missing. Full experimental fitting, historical GP results, long Adam runs and complete manuscript reproduction were **not** performed. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md). The demo marks missing experimental workflows as `not_run`; synthetic tests are not experimental evidence.

The current [model and objective specification](../docs/MODEL_AND_FITTING.md) supersedes historical raw/mixed fit recipes. Old fitted coefficients have not been relabeled as optimal for the new objective. Mammalian Adam reports its stopping reason; a finite run at an epoch/patience limit does not certify convergence.

License, software authors, manuscript mapping and final release metadata still require author confirmation. This is a computationally checked draft, not a statement of journal acceptance.
