# Validation record

Date: **2026-09-16**. Scope: the code accompanying draft `0.1.0-draft.1`, tested from the repository and an independently extracted precommit archive. This is computational reproduction of the supplied data, not validation of the complete manuscript.

## Environment

The exact dependency lock installed successfully into a fresh isolated CPython 3.12.14 environment on Windows 11 (AMD64), on an Intel processor with 20 logical CPUs. No GPU or system Python packages were used. `PYTHONPATH` was cleared and user site packages disabled. See [environment.json](environment.json) for the full package and machine record.

Installation took **38.905 seconds**, including virtual-environment creation and dependency installation, with a populated pip cache and internet index access. `python -m pip check` reported `No broken requirements found.` This measured time is not an estimate for an uncached download.

## Completed checks

| Check | Result | Measured time |
| --- | --- | --- |
| Repository: `python -m unittest discover -s tests -v` | 58 tests: 57 passed, 1 optional PyTorch test skipped | 18.692 s reported by unittest; 19.708 s process wall time |
| Extracted draft: same test command | 56 tests: 55 passed, 1 optional PyTorch test skipped; the two notebook-dependent tests are deliberately absent | 28.028 s reported by unittest; 29.111 s process wall time |
| Default demo from the source tree | PASS; Note 10 PDF/SVG/PNG and Note 11 PDF generated | 6.743 s |
| Default demo from the extracted draft | PASS; same reference counts and metrics | 3.480 s |
| Archive inventory and SHA-256 verification | PASS; 78 listed files plus `PACKAGE_MANIFEST.json`, no notebooks or generated results | Not timed separately |
| Figure inspection | Note 10 scatter and both Note 11 PDF pages rendered and visually checked for layout/labels | Not timed separately |

Test coverage includes independent model equations, supplied-data reference predictions, input rejection, altered-output rejection, CLI execution, figure dimensions, package inventory/hash checks and a demo invoked from another working directory. The demo tampering check rejects an altered Note 11 A2 R².

## Numerical reference checks

| Result | Value |
| --- | --- |
| Note 10 observations / sensors | 1,141 / 4 |
| Note 10 pooled raw R² | `0.8769196761349058` |
| Note 10 pooled log10 R² | `0.8721193770575127` |
| Note 11 means / panels | 216 / 12 |
| Note 11 A2 log10 R² | `-1.073005331220207` |

All 12 Note 11 panel references were checked, including negative values. Model equations, parameters and numerical reference fixtures were unchanged by this submission preparation.

## Limits and diagnostics

- PyTorch is optional and absent from this isolated environment; its NumPy/Torch agreement test was skipped. These results do not validate that backend under the submission lock.
- Activator and mammalian experimental reproduction remain unrun because the original inputs are missing. Their synthetic tests do not replace real-data validation. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md).
- The supplied Note 10/11 tables have not been independently reconciled against primary workbooks.
- The local platform tested here is Windows. GitHub Actions is configured for Windows/Linux; consult the run for the exact commit for remote results. No local Linux or macOS run is claimed.
- A historical notebook emits a Python 3.12 invalid-escape warning for a legacy path. Notebook syntax checks pass; notebooks remain outside the draft archive.
- The pinned pypdf 6.18.1 emits a deprecation warning during Note 11 PDF construction; generation and page checks pass. Do not assume compatibility with pypdf 7 without updating and revalidating the drawing code.
- Poppler preview rendering reports missing display-font aliases for `Symbol` and `ArialUnicode` in the supplied layout. The pages were inspected; no exact cross-platform pixel match or font portability is claimed. Poppler is not needed by the default PDF demo.

The executed commands and per-workflow durations are also recorded in generated `demo_report.json` files. Runtime files and local machine paths are excluded from version control and the draft archive.
