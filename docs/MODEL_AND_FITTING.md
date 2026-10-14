# Model consistency and fitting objective

## Shared CIC equation

The yeast modules use `yeast.binding.cic_dimer_pool`. Ordinary and nuclear CIC calculations use the same mass balance:

```text
b = 1 + Kx1 + Kb*c_I*(1+Kx2)
d = Kd0*(1+Kx1²) + Kb²*Kd1*c_I²*(1+Kx2²)
c_TF = 2*c_TF_all / (b + sqrt(b² + 8*d*c_TF_all))
c_TF_eff = d*c_TF²
z = KA*c_TF_eff
p_bound = z/(1+z)
p_unbound = 1/(1+z)
```

Set `Kx1=Kx2=0` for the ordinary model. The rationalized root avoids cancellation and gives exactly zero active pool at zero TF. The mammalian NumPy and differentiable Torch implementations use the same ordinary mass balance, verified by cross-backend numerical tests.

| Numerical API name | Manuscript/module name | Meaning |
| --- | --- | --- |
| `c_TF_all` | c_TF,all | Total TF concentration in calibrated RPU |
| `c_I` | c_I | Inducer concentration in µM |
| `KA` | `KA` | Operator association coefficient |
| `Kd0` | `Kd0` | Basal dimerization coefficient |
| `Kb` | `Kb` | Inducer association coefficient |
| `Kd1` | `Kd1` | Inducer-dependent dimerization coefficient |
| `T0` | `T0` | Baseline response |
| `Tmax_minus_T0` | `Tmax-T0` | Response amplitude |

`analysis.response` uses the explicit amplitude `Tmax_minus_T0`. To reproduce
`activator.model_s32_s47(..., T0, Tmax)`, supply that same `T0` and
`Tmax_minus_T0=Tmax-T0`. Array APIs use the supplied parameter units; the
activator workbook workflow converts its source doses to µM explicitly.
See [SI variable names](SI_VARIABLE_NAMES.md) for keyword and export changes.

`Kx1/Kx2` retain the historical nuclear-transport model. They are not aliases
for the newer apparent-model parameters `Λ(I)` or `n_app`.

Different operator architectures retain their established output rules:

| Model | Output |
| --- | --- |
| Yeast activator | `T0 + (Tmax-T0)*p_bound` |
| Note 10 repressor | `T0 + (Tmax-T0)*(1-(1-p_unbound)**n)` |
| Note 11 combined model | `T0 + (Tmax-T0)*p_bound_activator*p_unbound_repressor**2` |
| Mammalian CIC | `T0 + (13.61-T0)*(1-(1-p_bound)**7)` |

The generic `hybrid_promoter` now uses the Note 11 rule with a total `Tmax`, one T0 and an explicit operator count (default 2). Heterodimer, monomer and allosteric comparison functions describe different model assumptions; they are not alternative CIC fitting equations.

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
- `fit_shared_then_KA` / `fit_shared_then_KA_adam`: fit shared receptor parameters across groups, then each dataset's KA. SciPy and optional Torch use the canonical response and log10 objective.
- Mammalian `model_core.fit_scipy` / `fit_pytorch`: equal-weight per-CSV log10 R² objective and the established shared-parameter hierarchy.
- Mammalian `fit_sensor_logr2_floor.py`: the same macro log10 objective, subject to the existing requirement that every included sensor reaches `R2_log10 >= 0.5`. Adaptive weights help reach feasibility; final feasible candidates are ranked by macro log10 R². Reported feasibility is checked independently.

The fixed-parameter activator/repressor/combinatorial reconstruction commands do not fit parameters. Their original raw/log10 evaluation tables remain available and are not optimization objectives. Gaussian-process candidate search is a separate experimental-design algorithm, not a CIC parameter fitter.

## Corrections to the initial notebook migration

The earlier `037e500` revision preserved some inconsistent historical expressions. This revision corrects the same-model calculations:

- Both crosstalk curves use the supplied TF concentration; KA is never substituted for TF.
- Fold ranges use the complete shared induced/basal response, including the correct nuclear terms.
- Nuclear coefficient diagnostics use `(1+Kx2²)/(1+Kx1²)`. They report the inducer-dependent contribution relative to the basal contribution, not the full response fold change.
- Basal KA and induced `Kb2_Kd1=Kb²*Kd1` estimation use exact mass-balance inverses with the necessary fixed Kd0/Kb inputs. Grouped estimates are initial summaries, not objective-optimized fits.
- The asymmetric epsilon/clamped fitting variants, fixed-TF root helper, disconnected quadratic scratch expression and incompatible literal S83 response are removed. Their source remains in Git history.

The notebook parameter JSON preserves original source constants and hashes as provenance. Any `historical_fit` entries describe the source and do not configure the current optimizers. Original experimental inputs remain incomplete; these changes require fresh fitting when those inputs become available. Old fitted parameters are not silently relabeled as log10-optimal.
