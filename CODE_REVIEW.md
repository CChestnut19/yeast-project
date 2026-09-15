# Code review — 2026-09-15

Base: `a2bf257a511cf73101fcfce7eb6dcb342ebd5e58` (upstream `main`).

## Changes

- Added the seven supplied Python scripts under the independent `mammalian/Scripts/` module, plus a pipeline entry point, dependency files, input documentation and regression tests.
- Fixed archived initial vectors ignoring `--input-dir`; missing or malformed vectors now fail explicitly.
- Shared the mammalian NumPy equation between fitting and Supplementary Figure 13. Rationalized mass balance and `log1p`/`expm1` preserve weak responses; PyTorch uses the corresponding stable expressions.
- Rejected partial/non-finite observations, negative concentrations, non-positive RPU, zero-variance sensors, malformed parameter vectors and invalid optimizer limits.
- Made the hybrid SciPy/PyTorch command-line entry point usable. Infeasible constrained fits now exit with code 2 while retaining diagnostics.
- Added paths to publication and validation CLIs, fixed named font weights, preserved curve identifiability metadata and rejected duplicate Word parameter rows.
- Numerical validation now reloads original observations, checks source-row alignment, recomputes predictions and raw/log10 R², and compares saved parameter tables and summaries. It can run independently of publication PDFs.
- Extracted 10 repeated notebook functions into `yeast_analysis.py`; removed 37 unused imports. Model variants and parameter sets were retained.
- Corrected Pareto filtering for equal objective values and duplicate nondominated points. Corrected two-metric CSV column headers.
- Applied a common missing-row mask to historical PyTorch notebook inputs to prevent independently dropped columns from becoming misaligned. Normalized executable Windows path literals to forward slashes.
- Cleared saved notebook execution output and counts. Total notebook size changed from 3,627,149 bytes to 269,927 bytes (about 93% smaller); original outputs remain recoverable in Git history.

## Validation

`python -m unittest discover -s tests -v`

18 regression tests passed locally, including the optional PyTorch check. Coverage includes high-precision weak-signal comparison, normal-range equivalence to original equations, finite/bounded responses, input rejection, custom archived-vector paths, SciPy optimization, PyTorch/NumPy objective agreement, numerical write/read validation, rejection of altered predictions and R², all eight mammalian CLI help commands, missing-input preflight, notebook syntax, a reduced-grid execution of the fold-change notebook, rectangular CSV exports and a quadratic reference for Pareto filtering.

Local numerical runtime: NumPy 1.23.5, pandas 1.5.3, SciPy 1.10.1, Matplotlib 3.6.2, PyTorch 1.13.0. CLI checks used pypdf 6.0.0, python-docx 1.2.0 and reportlab 4.4.3 in an isolated test dependency directory. GitHub Actions installs the declared dependencies on Python 3.11; its result is separate from local validation.

## Remaining source-data requirements

The supplied material did not include the original 25-sensor observations, six-column mapping, archived parameter vectors, publication settings or original Figure 13 PDF. These were not fabricated or replaced with prediction exports. Real-data refitting, the 953-observation manuscript assertions and final PDF/Word visual reproduction have therefore not been verified.

Historical notebooks that load external files still need their original data and local paths. The other notebooks were checked for syntax and cleaned, not fully executed or scientifically revalidated. One commented-out triple-quoted block retains a legacy invalid-escape deprecation warning; it does not affect the tested calculations.
