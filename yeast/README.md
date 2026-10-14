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

Activator uses total ceiling `Tmax=35.85`. Historical responses use amplitude
`Tmax_minus_T0`, with total ceiling `T0+Tmax_minus_T0`. Note 10 uses sensor-specific
total ceilings and `1-(1-p_unbound)^2`; Note 11 uses `Tmax=35.85` and
`p_activator*p_unbound^2`. Sharing mass balance does not make these response
equations interchangeable.

## SI variable names

Numerical APIs use `c_TF_all`, `c_I`, `KA`/`KR`, `Kd0`, `Kb`, `Kd1`, `T0` and
`Tmax` or its explicit amplitude `Tmax_minus_T0`. The free monomer and active
pool use `c_TF` and `c_TF_eff`. Concentrations entering the manuscript workflows
are calibrated RPU for TF and µM for inducer; `inducer_name` stores chemical
identity separately. See [the migration guide](../docs/SI_VARIABLE_NAMES.md).

Archived CSVs and notebook JSON preserve their original headers and names.
Readers adapt them to the SI API; newly exported model inputs use SI names.

All entry points produce numerical outputs only. Existing source fields such as activator `plot_type` and the Note 11 filename `Supplementary_Note_11_plot_data.csv` retain their original data-schema/provenance names; they do not invoke rendering.

All parameter-fitting entry points optimize log10 R². The [formula and fitting specification](../docs/MODEL_AND_FITTING.md) explains shared mass balance, output-window conversion, equal dataset weights and corrections to inconsistent historical expressions.
