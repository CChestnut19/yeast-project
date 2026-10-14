# SI variable names

The yeast numerical interfaces use the notation of the current Supplementary
Information, particularly Notes 3, 6 and 8. This naming migration preserves
model equations, parameter values, fitting objectives and observation order.

| Python name | SI meaning | Former API name |
| --- | --- | --- |
| `c_TF_all` | Total calibrated TF abundance, RPU | `L`, `total_tf`, `c_tf` |
| `c_I` | Inducer concentration, µM | `I`, `inducer`, `c_i_uM` |
| `KA` | Activator/operator association coefficient | `kd`, `ka` |
| `KR` | Repressor/operator association coefficient | Repressor `kd` |
| `Kd0` | Basal dimerization coefficient | `k1`, `K1` |
| `Kb` | Inducer association coefficient | `k2`, `K2` |
| `Kd1` | Induced dimerization coefficient | `k3`, `K3` |
| `T0` | Basal reporter output, RPU | `I0`, `baseline`, `t0` |
| `Tmax` | Total reporter-output ceiling, RPU | `tmax` |
| `Tmax_minus_T0` | Explicit response amplitude, RPU | `Imax`, `amplitude` |
| `c_TF` | Free TF monomer | `monomer`, `free_monomer` |
| `c_TF_eff` | DNA-binding competent TF pool | `active_pool` |

`KA` and `KR` are association weights in these implementations; the migration
does not take reciprocals. `Imax` was an amplitude and is renamed to
`Tmax_minus_T0`, preserving its value. It must not be passed as a total `Tmax`.

```python
from yeast.analysis import response

T0, Tmax = 0.2, 10.2
output = response(c_TF_all=4.0, c_I=1.0, KA=3.0,
                  Kd0=0.75, Kb=1.0, Kd1=0.25,
                  Tmax_minus_T0=Tmax-T0, T0=T0)
# output = 7.7 RPU
```

## Fitting and derived quantities

Parameter dictionaries use the same SI keys. Dataset dictionaries for shared
fitting use `c_TF_all`, `c_I` and `observed`. The shared fitting functions are
`fit_shared_then_KA` and `fit_shared_then_KA_adam`, with `initial_KA` and, for
Adam, `KA_steps`.

`estimate_KA` estimates the operator association coefficient.
`estimate_Kb2_Kd1` estimates `Kb**2 * Kd1`; its former name `estimate_M` could
be confused with the free monomer in the SI. This induced coefficient is
not `Q_LBD`: the ordinary-model definition is `Q_LBD=Kb**2*Kd1/Kd0`.
The separate `M` constant in historical ec50 cells 0/1 is an enhancement
multiplier and is exposed as `historical_dimer_enhancement_factor`; it is
neither the free monomer nor `Kb**2*Kd1`.
The `quality_ratio` diagnostic additionally multiplies that ratio by `c_I**2`
and includes transport factors when the historical model is selected.

`Kx1/Kx2` describe the historical nuclear-transport model. They do not represent
the newer apparent-model parameters `Λ(I)` or `n_app`.

## Source data and exports

Original workbook, CSV and notebook JSON files remain unchanged. Note 10's
original `tf_input_rpu` and `inducer_um` CSV headers are read into `c_TF_all`
and `c_I`. Activator normalized records use those same names and `Kb`;
`inducer_name` identifies the chemical separately from its numeric dose.
Repressor model settings expose `KR`, and hybrid architectures expose both
`KA` and `KR`.

Existing callers must update keyword arguments and model-result field names.
Positional parameter order and amplitude semantics remain unchanged. Newly
written result directories must be validated with this revision's validator.

`load_notebook_parameters(notebook, cell)` returns SI-named parameters and grids
with the original values, source hashes and historical recipes. To inspect the
unchanged source record, pass `parameter_names='source'`. The design adapter
returns SI-named receptor and DBD records suitable for `scan_designs`.

Collections use suffixes such as `Kd0_values`, `KA_values` and `Kd0_by_sensor`.
Numbered operator weights such as source `kd1` become `KA_1`, not `Kd1`.
The historical two-state and reduced comparison models receive descriptive
names for their distinct physical roles: `active_dissociation`,
`inactive_dissociation`, `basal_dimer_coefficient` and `induced_dimer_coefficient`.
The archived `k_params` vector is exposed as `LBD_coefficients`, retaining its
`[Kd0, Kb, Kd1]` order. Source metadata and historical fitting recipes are
preserved verbatim.
Historical hybrid records use `KA` for activation, `KR` for repression and
suffixes `_activator`/`_repressor` for kinetics, doses and output constants.
Crosstalk parameters use numbered names such as `Kb_1`, `Kd1_2` and `Kx2_2`.

## Naming reference

The author-supplied `Supplementary information.docx`, last modified
2026-10-13, was checked on 2026-10-14. Its SHA-256 is
`b231da78c442abf86a62f44698807e16fec182beef1c6d3c182c4c8aa75e1c10`.
