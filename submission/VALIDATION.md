# Algorithm-only validation

Validation date: **2026-09-18**, draft `0.2.0-draft.1`. These results concern the numerical revision; older PDF tests are not part of this release.

## Environment and commands

A fresh isolated CPython 3.12.14 environment on Windows 11 AMD64 installed the [fixed lock](requirements-lock.txt) in 33.382 seconds using a populated pip cache. `pip check` passed. The environment contains no Matplotlib, seaborn, Plotly, Pillow, pypdf, reportlab, python-docx or fontTools. Full measured details are in [environment.json](environment.json).

```text
python -m pip check
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir Output/demo
```

| Verification | Result |
| --- | --- |
| Complete suite in the working source tree | 75 tests: 73 passed, 2 optional Torch tests skipped; 18.674 seconds |
| Complete suite in an extracted draft archive, without Git metadata | Same 75 tests: 73 passed, 2 optional Torch tests skipped; 18.138 seconds |
| Numerical demo, source / extracted archive | PASS / PASS; 0.400 / 0.394 seconds |
| Both skipped tests in an existing Torch environment | 2 passed; 0.953 seconds |
| Archive contents and SHA-256 validation | All 74 inventoried files verified; no notebooks, figures or document outputs |
| Syntax, local documentation links and production rendering imports | Passed |

Timings describe these small workloads on a 20-logical-CPU machine, not full optimization runtimes. The optional backend check used Python 3.9.15, Torch 1.13.0, NumPy 1.23.5, SciPy 1.10.1 and pandas 1.5.3. It checked the historical Adam models and the separate mammalian NumPy/Torch objective agreement; the full suite was run in the Python 3.12 locked environment.

The GitHub Actions workflow also runs installation, the complete suite, demo and archive build on Windows and Ubuntu. Consult [the exact commit's workflow run](https://github.com/CChestnut19/yeast-project/actions) for remote status; the table above records measured local results.

## Numerical evidence

- Note 10 retains **1,141** supplied replicate measurements, four sensors and all archived sensor metrics. Pooled raw R² is `0.8769196761349058`; pooled log10 R² is `0.8721193770575127`.
- Note 11 retains **216** supplied means across 12 panels, all predictions and archived panel statistics. A2 log10 R² remains `-1.073005331220207`; negative values are not replaced or clipped.
- Activator tests retain grouping, source exclusion annotations, aggregation units, fixed-parameter equations and validation using synthetic workbook fixtures.
- Mammalian tests cover independent mass-balance equations, input rejection, constrained fitting, saved-result tampering and numerical-only pipeline execution on synthetic inputs.
- The [notebook migration inventory](../docs/NOTEBOOK_MIGRATION.md) covers all **59 code cells** from the ten former root notebooks. Cell hashes match the source at `bfd2de5`; 263 statically comparable scientific parameter literals were checked without differences. Eighteen independent source-formula comparisons agreed within floating-point error (maximum absolute difference `2.38e-10`).
- Migration regression tests check operator inversion, model conventions, Pareto ties, alignment residuals, statistics, original SciPy penalties/fallback, fitting from displaced initial values and GP selection. Original Torch classes and the retained Adam backend were also compared for two shared steps and two steps per dataset: maximum prediction difference `2.15e-6`, consistent with float32 expression regrouping. Long-run or bitwise trajectory equivalence is not claimed.
- Default Note 10/11 commands pass with rendering imports actively blocked. Numerical outputs include predictions, metrics, provenance and validation; no rendering flag is needed.

## Limits

Original activator workbook/parameter inputs, mammalian input tables/mapping/initial vectors and the former notebooks' private CSVs are missing. Full experimental fitting, historical GP results, long Adam runs and complete manuscript reproduction were **not** performed. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md). The demo marks missing experimental workflows as `not_run`; synthetic tests are not experimental evidence.

License, software authors, manuscript mapping and final release metadata still require author confirmation. This is a computationally checked draft, not a statement of journal acceptance.
