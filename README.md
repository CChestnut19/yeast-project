# Yeast and mammalian regulatory algorithms

**Algorithm-only manuscript draft — `0.2.0-draft.1`.** This repository contains numerical models, parameter estimation/fitting, response analysis and validation. It writes numerical CSV/JSON results. Figure rendering and document generation have been removed.

## Code layout

| Directory | Purpose |
| --- | --- |
| `yeast/activator/` | Supplementary Note 9 fixed-parameter reconstruction and batch-specific statistics |
| `yeast/repressor/` | Supplementary Note 10 predictions and raw/log10 statistics for four sensors |
| `yeast/combinatorial/` | Supplementary Note 11 combined-model predictions and log10 statistics |
| `yeast/analysis.py`, `yeast/binding.py` | Shared response, fold-change, Pareto and mass-balance algorithms |
| Other `yeast/` numerical modules | Distinct calculations consolidated from the ten former root notebooks; see the migration inventory below |
| `mammalian/Scripts/` | Independent CIC model, constrained fitting, numerical diagnostics and validation |
| `tests/` | Reference calculations, input validation and regression tests |
| `tools/` | Numerical demo and optional traceable draft archive |

Root notebook code has been compared with subfolder implementations and consolidated into reusable modules. The [cell-by-cell migration inventory](docs/NOTEBOOK_MIGRATION.md) records shared implementations, distinct models, parameter variants and discarded rendering/incomplete exploratory fragments. The former notebooks and figures remain retrievable from Git history at commit `bfd2de5`.

## Install and run

Use Python 3.12 from the repository root:

```text
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` in Windows PowerShell or `. .venv/bin/activate` on Linux/macOS, then:

```text
python -m pip install -r submission/requirements-lock.txt
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir Output/demo
```

The fixed environment contains NumPy, SciPy, pandas and scikit-learn with their dependencies. No graphics libraries or GPU are required. PyTorch is optional for the mammalian backend and historical notebook Adam fitting. `Output/` is ignored by Git.

The demo checks 1,141 Note 10 measurements and 216 Note 11 means across 12 conditions/panels. It produces predictions, metrics, provenance, validation reports and execution timings. Missing-data workflows are explicitly marked `not_run`.

## Scientific scope

- Note 10 pooled raw R²: `0.8769196761349058`; pooled log10 R²: `0.8721193770575127`.
- Note 11 A2 log10 R²: `-1.073005331220207`. Negative values are retained.
- Note 10 uses `1-(1-p_unbound)^2`; Note 11 uses `p_activator*p_unbound^2`. Their parameters and observation units remain distinct.
- Original activator and mammalian experimental inputs are incomplete. Their synthetic tests do not establish experimental reproduction.
- Historical notebook variants are exploratory algorithms, not verified replacements for the manuscript models.

## Documentation

- [Reproduction commands](submission/REPRODUCIBILITY.md) and [validation evidence](submission/VALIDATION.md)
- [Analysis mapping](submission/ANALYSIS_MAP.md) and [required data](submission/DATA_REQUIREMENTS.md)
- [Yeast algorithms](yeast/README.md) and [mammalian algorithms](mammalian/README.md)
- [Release checklist](submission/RELEASE_CHECKLIST.md), [Code availability draft](submission/CODE_AVAILABILITY.md), [citation](submission/CITATION_GUIDANCE.md), [license status](submission/LICENSE_STATUS.md)

The license, software authors, final manuscript mapping and missing-data arrangements remain pending author confirmation. This draft does not claim complete manuscript reproduction or journal acceptance.
