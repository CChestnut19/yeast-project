# Algorithm-only validation

## Source workbook update 2026-10-16

`data/Source data.xlsx` is now the unchanged author-supplied
`Source data(5).xlsx` (699,800 bytes), SHA-256
`fcbeb334cd553d674ce425dfc69f6dd3778864385117a1f9bee71ea561335e7c`.
The manifest and package metadata identify this version. The older hashes
in the dated records below describe their respective historical workbooks.
No model, fitted parameter, archived numerical CSV or source formula was edited.

- ZIP CRC and all 21 worksheet inventories passed; no uncached formulas were
  found. Comparing cached values and formulas, only `Figure 5` differs from
  the preceding workbook.
- All 1,141 Fig. 5E sensor/observation/prediction pairs exactly match the
  archived Note 10 observations and current predictions as a multiset;
  worksheet row order is not used as an input-condition key. There are
  no negative Fig. 5E predictions. This resolves the earlier prediction-column
  mismatch for the supplied version.
- All 216 Note 11 means, sample SDs and dose conditions match the two-replicate
  source reconstruction. The comparison strips the three trailing-star
  annotations in `K29`, `M32` and `V7`; it does not establish their exclusion policy.
- The 22-test suite passed in Python 3.9.15/Torch 1.13. In the Python 3.12.14
  environment, 21 passed and the optional Torch test was skipped. The
  Note 10/11 demo passed. Independent Decimal checks also reproduced the
  core mass balance and both sets of predictions.
- A synthetic mammalian workflow with 25 CSVs, 13 LBD groups, 11 DBD groups
  and 60 parameters completed with 142 validation checks. This is an
  executable-input check, not an experimental fit or SI-objective validation.
- The mammalian NumPy/Torch parity and gradient checks passed, including
  a real Adam update; both backend result sets passed 37 checks each on
  a separate synthetic fixture. Syntax parsing passed for all 129 tracked
  Python files.
- CIC-Designer/WebDataBase checks covered syntax in 91 Python files and
  selected original functions with transport/database mocks. They were not
  live Flask/Django/database or complete assembly tests.

### Remaining issues reproduced in this review

- The activator parameter reader loads 16 of the current SI Table 3's 19
  named LBDs because its row loop stops early; the required `BjaR180S107R`
  is omitted. Even with an audit-only complete parameter dictionary, 4 of
  27 panels remain blocked by negative actual TF inputs (`Q177`, `Q187`,
  `O198`, `Q258`). The other 23 panels can be computed independently.
  Literal apostrophes in the three starred HKCI measurements parse correctly.
- Mammalian residual scaling and feasible-candidate ranking still differ
  from SI S103/S106. Corrupted derived parameter columns and absent metric
  tables can also escape its numerical validator. Real numerical input
  CSVs, mappings and matched initial vectors are still missing.
- CIC fitting/saving retains a case-mismatched LBD route, missing CSRF
  handling, inducer-reference unit inconsistency and a stale DBD slider
  state. The server also retains machine-specific imports and incomplete
  request-domain checks. A workbook replacement cannot resolve these issues.
- The workbook still contains 58 cached Excel error cells (51 in
  `Supplementary Figure 8`, 3 in `Supplementary Figure 14`, 4 in
  `SI-note repressor`). They are inventoried and preserved, not silently
  repaired or recalculated. Shared-control identity and annotation policies
  remain author decisions.

## Activator source parsing 2026-10-15

The current suite contains 22 tests: 21 passed with one optional Torch skip
in Python 3.12.14; all 22 passed in Python 3.9.15/Torch 1.13. Four new tests
cover literal apostrophes, preserved signed values/star flags, malformed
and nonfinite input rejection, and extraction from the original workbook.

The HKCI84-RpaR179 panel now extracts all 360 records, including `AJ48`,
`AG49` and `AG50`. Their negative measured responses and starred exclusions
are preserved. The workbook SHA-256 remains
`28c095d7796858118591d5a5c1670d2bb56659a75a587687a8170219e55237bf`.
The Note 10/11 demo passed. This checks lexical parsing and HKCI extraction;
it does not establish successful reproduction of the full 27-panel workflow.

## SI naming migration 2026-10-14

The naming migration suite contained 18 checks: 17 passed and
one optional Torch check was skipped in the Python 3.12.14 environment;
all 18 passed in the existing Python 3.9.15/Torch 1.13 environment.
The new tests exercise SI keyword dictionaries, exact inversions, total
ceiling versus amplitude, activator/repressor binding names, original-CSV
normalization, historical parameter adaptation (including distinct hybrid
and comparison-model roles), and SciPy/Torch shared fits.

All 1,141 Note 10 and 216 Note 11 predictions and metrics exactly matched
the pre-migration results. Ordinary/nuclear/activator calculations at 151
inputs, three historical design scans and a parameter-fit result also had
zero numerical difference. Source workbook, archived CSVs and historical
parameter JSON retained identical SHA-256 hashes. The demo passed using
the archived metrics now stored in `submission/reference_metrics.json`.
This verifies the naming migration, not complete SI/model/experiment agreement.

## Historical validation 2026-09-18

The results below record the earlier canonical-formula and log10-R² revision
of draft `0.2.1-draft.1`. They are historical results of the former 102-test
suite, which is absent from baseline `94dd2c0`; they are not the current test count.
Previous raw/mixed-objective and historical-literal checks do not describe
the current fitting behavior.

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

The author-supplied source workbook is now included. Activator parameter TSV, mammalian numerical CSVs/mapping/initial vectors and the former notebooks' private CSVs remain missing. Full experimental fitting, historical GP results, long Adam runs and complete manuscript reproduction were **not** performed. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md). The demo marks missing experimental workflows as `not_run`; synthetic tests are not experimental evidence.

The current [model and objective specification](../docs/MODEL_AND_FITTING.md) supersedes historical raw/mixed fit recipes. Old fitted coefficients have not been relabeled as optimal for the new objective. Mammalian Adam reports its stopping reason; a finite run at an epoch/patience limit does not certify convergence.

The software license was confirmed as MIT on 2026-10-13. Software authors, manuscript mapping and final release metadata still require author confirmation. This is a computationally checked draft, not a statement of journal acceptance.
