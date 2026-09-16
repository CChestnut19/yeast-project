# Yeast models

Run commands from the repository root. Start with the [reproduction guide](../submission/REPRODUCIBILITY.md) for a pinned environment and the combined Note 10/11 demo.

| Module | Scope |
| --- | --- |
| [activator](activator/README.md) | Fixed-parameter reconstruction, batch aggregation and R² validation for 27 Supplementary Note 9 panels; original inputs still required |
| [repressor](repressor/README.md) | Supplementary Note 10: four sensors, 1,141 supplied measurements, raw/log10 metrics and a 35 mm plot |
| [combinatorial](combinatorial/README.md) | Supplementary Note 11: 216 supplied means, 12 panels, a two-page figure and log10 metrics |
| `analysis.py` | Response, fold-change and Pareto utilities used by the historical notebooks |
| `binding.py` | Shared dimer mass-balance calculation |
| `metrics.py` / `reporting.py` | Strict statistics, result export and recomputation checks shared by Notes 10 and 11 |

## Model conventions

The activator workflow uses a total ceiling `Tmax=35.85`. Historical notebooks use an amplitude `Imax`, with total ceiling `I0+Imax`. Only the underlying mass-balance calculation is shared.

Note 10 uses sensor-specific total ceilings and the weight `1-(1-p_unbound)^2`. Note 11 uses `Tmax=35.85` and `p_activator*p_unbound^2`. Each retains its supplied parameter values and precision; they are distinct model conventions.

The root `yeast_analysis.py` is a compatibility import without a duplicate model implementation. Historical notebooks contain different experiments, species and parameter sets, and are not interchangeable with the 27-panel activator workflow. Their mapping to final manuscript figures remains to be confirmed.
