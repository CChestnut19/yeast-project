# Model consistency and fitting objective

## Shared CIC equation

The yeast modules use `yeast.binding.cic_dimer_pool`. Ordinary and nuclear CIC calculations use the same mass balance:

```text
b = 1 + kx1 + k2*I*(1+kx2)
d = k1*(1+kx1²) + k2²*k3*I²*(1+kx2²)
m = 2*L / (b + sqrt(b² + 8*d*L))
active_pool = d*m²
z = kd*active_pool
p_bound = z/(1+z)
p_unbound = 1/(1+z)
```

Set `kx1=kx2=0` for the ordinary model. The rationalized root avoids cancellation and gives exactly zero active pool at zero TF. The mammalian NumPy and differentiable Torch implementations use the same ordinary mass balance, verified by cross-backend numerical tests.

| Numerical API name | Manuscript/module name | Meaning |
| --- | --- | --- |
| `L` | `c_tf`, `ctf_all` | Total TF concentration |
| `I` | `c_i_uM`, `inducer` | Inducer concentration in the selected parameter units |
| `kd` | `KA` | Operator association coefficient |
| `k1` | `Kd0` | Basal dimerization coefficient |
| `k2` | `Kb` | Inducer association coefficient |
| `k3` | `Kd1` | Inducer-dependent dimerization coefficient |
| `I0` | `T0` | Baseline response |
| `Imax` | `Tmax-T0` | Response amplitude, not total ceiling |

`analysis.response` retains explicit amplitude arguments. Therefore, to reproduce `activator.model_s32_s47(..., t0, tmax)`, supply `I0=t0` and `Imax=tmax-t0`. Do not pass the total ceiling as an amplitude. Concentration units are not inferred or automatically converted by array APIs; the activator workbook workflow retains its explicit source-unit conversion.

Different operator architectures retain their established output rules:

| Model | Output |
| --- | --- |
| Yeast activator | `T0 + (Tmax-T0)*p_bound` |
| Note 10 repressor | `T0 + (Tmax-T0)*(1-(1-p_unbound)**n)` |
| Note 11 combined model | `T0 + (Tmax-T0)*p_bound_activator*p_unbound_repressor**2` |
| Mammalian CIC | `T0 + (13.61-T0)*(1-(1-p_bound)**7)` |

The generic `hybrid_promoter` now uses the Note 11 rule with a total `tmax`, one baseline and an explicit operator count (default 2). Heterodimer, monomer and allosteric comparison functions describe different model assumptions; they are not alternative CIC fitting equations.

## One fitting objective: log10 R²

For dataset `g`, transform observations and predictions:

```text
u_i = log10(observed_i)
v_i = log10(predicted_i)
SST_g = sum((u_i - mean(u_g))²)
R2_log10_g = 1 - sum((u_i-v_i)²)/SST_g
```

Parameter fitting minimizes:

```text
objective_total = mean_g(1-R2_log10_g)
residual_i = (v_i-u_i)/sqrt(number_of_groups*SST_g)
```

The sum of squared residuals equals the objective. A single dataset reduces to maximizing its log10 R². Multiple datasets sharing parameters contribute equally; their different sample counts, ranges and numerical scales do not silently change the objective into pooled log SSE. With fixed grouping, repeating all observations of one dataset does not increase that dataset's weight.

This metric is **R² of log10-transformed responses**. It is neither `log10(R²)` nor squared Pearson correlation. Negative R² values remain meaningful. Raw R² and log MSE can be exported as diagnostics but do not enter the fitting objective. Raw/log mixtures and endpoint shape-prior penalties have been removed.

Observed responses must be finite, strictly positive and nonconstant within every fitted group. Invalid observations raise an error; they are not omitted, replaced or clipped to make log10 R² defined. Predictions must also remain finite and strictly positive. A finite objective does not imply optimizer convergence; inspect returned convergence/status fields.

### Fitting entry points

- `yeast.fitting.fit_response`: SciPy least-squares fitting; optional `groups` identifies equal-weight datasets.
- `fit_notebook_curve_fit`: SciPy curve_fit with source-cell initialization/bounds and the same normalized log10 objective. Historical raw losses and invalid-domain fallback are superseded.
- `fit_shared_then_kd` / `fit_shared_then_kd_adam`: fit shared receptor parameters across groups, then each dataset's kd. SciPy and optional Torch use the canonical response and log10 objective.
- Mammalian `model_core.fit_scipy` / `fit_pytorch`: equal-weight per-CSV log10 R² objective and the established shared-parameter hierarchy.
- Mammalian `fit_sensor_logr2_floor.py`: the same macro log10 objective, subject to the existing requirement that every included sensor reaches `R2_log10 >= 0.5`. Adaptive weights help reach feasibility; final feasible candidates are ranked by macro log10 R². Reported feasibility is checked independently.

The fixed-parameter activator/repressor/combinatorial reconstruction commands do not fit parameters. Their original raw/log10 evaluation tables remain available and are not optimization objectives. Gaussian-process candidate search is a separate experimental-design algorithm, not a CIC parameter fitter.

## Corrections to the initial notebook migration

The earlier `037e500` revision preserved some inconsistent historical expressions. This revision corrects the same-model calculations:

- Both crosstalk curves use the supplied TF concentration; kd is never substituted for TF.
- Fold ranges use the complete shared induced/basal response, including the correct nuclear terms.
- Nuclear coefficient diagnostics use `(1+kx2²)/(1+kx1²)`. They report the inducer-dependent contribution relative to the basal contribution, not the full response fold change.
- Basal kd and induced `M=k2²*k3` estimation use exact mass-balance inverses with the necessary fixed k1/k2 inputs. Grouped estimates are initial summaries, not objective-optimized fits.
- The asymmetric epsilon/clamped fitting variants, fixed-TF root helper, disconnected quadratic scratch expression and incompatible literal S83 response are removed. Their source remains in Git history.

The notebook parameter JSON preserves original source constants and hashes as provenance. Any `historical_fit` entries describe the source and do not configure the current optimizers. Original experimental inputs remain incomplete; these changes require fresh fitting when those inputs become available. Old fitted parameters are not silently relabeled as log10-optimal.
