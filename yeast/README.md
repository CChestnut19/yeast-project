# Yeast numerical algorithms

Run commands from the repository root using the [fixed environment](../submission/REPRODUCIBILITY.md).

| Module | Scope |
| --- | --- |
| [activator](activator/README.md) | 27-panel fixed-parameter reconstruction, batch aggregation and R² validation; original workbook/table required |
| [repressor](repressor/README.md) | Four sensors, 1,141 supplied measurements and raw/log10 statistics |
| [combinatorial](combinatorial/README.md) | 216 supplied means, 12 panels and log10 statistics |
| `binding.py` | Shared stable dimer mass balance |
| `analysis.py` | Response, fold-change and Pareto algorithms consolidated from root notebooks |
| `metrics.py` / `reporting.py` | Strict statistics, numerical export and independent result checks |

Additional historical algorithms and preserved parameter variants are documented in the [notebook migration inventory](../docs/NOTEBOOK_MIGRATION.md). Import functions from `yeast` modules; the redundant root `yeast_analysis.py` alias has been removed.

## Preserve distinct conventions

Activator uses total ceiling `Tmax=35.85`. Historical responses use amplitude `Imax`, with total ceiling `I0+Imax`. Note 10 uses sensor-specific total ceilings and `1-(1-p_unbound)^2`; Note 11 uses `Tmax=35.85` and `p_activator*p_unbound^2`. Sharing mass balance does not make these response equations interchangeable.

All entry points produce numerical outputs only. Existing source fields such as activator `plot_type` and the Note 11 filename `Supplementary_Note_11_plot_data.csv` retain their original data-schema/provenance names; they do not invoke rendering.

All parameter-fitting entry points optimize log10 R². The [formula and fitting specification](../docs/MODEL_AND_FITTING.md) explains shared mass balance, output-window conversion, equal dataset weights and corrections to inconsistent historical expressions.
