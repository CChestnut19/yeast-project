# Root notebook algorithm migration

Source: repository commit `bfd2de5`, ten root notebooks, **59 code cells**.
Cell numbers below are the original zero-based notebook indices, including
markdown cells. `yeast/notebook_parameters.json` records every code cell's
SHA-256 and its literal scientific parameters, with separate source-cell keys.
The initial migration at `037e500` preserved historical equations. The current
revision applies the author's formula-consistency and log10-R² corrections;
see [the current model and fitting specification](MODEL_AND_FITTING.md).
Source hashes and constants remain provenance, not a claim that corrected
algorithms reproduce the inconsistent source expressions.

This migration removes notebook execution, plots, colors, figure geometry,
personal filesystem paths and automatic CSV writes. Functions return numerical
arrays, records or tables; callers can write those results to CSV/JSON.

## Shared interfaces and model conventions

- `yeast.binding.cic_dimer_pool` supplies the canonical ordinary/nuclear
  coefficients and calls the shared stable `active_dimer_pool` solver. `yeast.analysis.response` and `response_pair`
  now serve ordinary and nuclear historical dose-response calculations.
- Historical `Imax` is an **amplitude**: ceiling = `I0 + Imax`. The existing
  activator model uses a **total** `Tmax`: amplitude = `Tmax - T0`. They coincide
  only after that explicit conversion. Historical mammalian parameter sets in
  these notebooks retain their amplitude convention; the mammalian model is
  unchanged.
- `foldchange1/2/3`, nuclear wrappers and `fast_pareto_2d` remain shared.
  `scan_designs` replaces the repeated search/export loops and preserves first
  grid maxima and tied Pareto points. Undefined log objectives are excluded
  explicitly; a pair without any valid objective produces no result record.
- `yeast.exploratory_models` holds distinct reduced, heterodimer,
  allosteric, operator and hybrid models. Same-model historical inconsistencies have been corrected or removed;
  comparison models retain explicitly distinct physical assumptions.
- `yeast.curve_analysis` handles slopes, historical quality measures, alignment
  and regression. It reuses the existing activator R²/Pearson implementations.
  `yeast.fitting` handles estimation/fitting and `yeast.optimization` the GP work.

Use `load_notebook_parameters('ec50.ipynb', 3)` to select one parameter version.
The result separates `parameters`, optional `grids`, `historical_fit` and `alignment`
recipes. `foldchange_design_parameters(cell=1|2|3)` converts that notebook's
receptor/DBD tables to `scan_designs` input. No parameter sets are merged by
sensor name: the same name has different coefficients and doses in different
cells. Constant snapshots retain source variable names; unused constants do
not become implicit model inputs.

```python
import numpy as np
from yeast.analysis import scan_designs
from yeast.notebook_parameters import foldchange_design_parameters

receptors, dbds = foldchange_design_parameters(cell=3)
maxima = scan_designs(np.linspace(.3, 10, 2000), receptors, dbds)
front = scan_designs(np.linspace(.3, 10, 2000), receptors, dbds, pareto=True)
```

## Per-cell disposition

Every row removes figure construction, styling, display/save calls and personal
path I/O where present. “Reuse” means the numerical expression is represented
by the named shared interface, rather than copied into another module.

### box.ipynb — 13 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | Reuse `response_pair`; `curve_analysis.get_steep_interval` retains gradient of log10(P) against log10(L), threshold 0.8 and first/last qualifying indices. |
| 1 | Reuse `binding.active_dimer_pool(L, 1, d)` for the two Hill-2 pools; `exploratory_models.monomer_bound_pool` retains Hill-1 pools. Ratios are ordinary array division. |
| 2 | `exploratory_models.dimer_response` with d=k2²k3I² or k1, b=1; activator on/off and repressor off/on occupancy ratios, varying kd. |
| 3 | Same parameterized reduced model as cell 2, varying L, fixed kd=40. |
| 4 | `heterodimer_free_pools` and `heterodimer_response_pair`; retain log10(on/off), I=1000 and both actual baselines .01. Unused C/D roots, n, f2 and color-map function removed. |
| 5 | Same heterodimer interface with total_b=.5 and varying kd; both actual baselines .01. Unused C/D and style removed. |
| 6 | Same heterodimer interface with total_b=1, I=100, baseline_on=.035485714, baseline_off=.01; return on response. Type-III comparison reuses `response`. |
| 7 | Cell 2 reduced activator ratio on a TF/kd grid; no new response implementation. |
| 8 | Cell 2 reduced repressor off/on ratio on a TF/kd grid. |
| 9 | `two_state_repression`; x1=(1+I/active_dissociation)², x2=(1+I/inactive_dissociation)², active weight x1/(x1+10*x2). Source passes the value named k2 as active_dissociation and k1 as inactive_dissociation. Imax/I0 are unused. |
| 10 | Induced/basal fold now uses `analysis.response_pair` at the same supplied L in both states. Removed the inconsistent fixed-TF root helper; the source equation remains in Git history. |
| 11 | `rob_phillips_allosteric_dimer_fixed_inducer`; compute expression/no-TF expression for fold. Retains source's product R*DBD, interaction and fixed allosteric factor. |
| 12 | `simple_repression_partition_function`, `simple_repression_pbound`, `simple_repression_foldchange`; retain effective R=R*DBD/(1+DBD). State contributions are 1/Z, RNAP/Z, TF/Z. |

### ec50.ipynb — 6 cells

Despite its filename this notebook contains **no EC50 calculation or dose-root
search**. Its distinct computations are quality ratios and fold ranges.

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `saturated_fold_approximation`; other computed response curves reuse `dimer_response`. The source `np.arange(.000109651,.387876109)` has default step 1 and contains only one k1, recorded in grid metadata. |
| 1 | Same approximate fold with separately preserved acVHH/RpaR coefficients; ordinary multiplication gives the L*k1 coordinate. |
| 2 | `log_fold_range` uses the complete canonical response_pair, including the nuclear linear/dimer terms, explicit I and optional Imax/I0. Removed the subtract-1 mismatch and fabricated NaN/Inf sentinel fold values. |
| 3 | `quality_ratio` reports the inducer-dependent dimer coefficient contribution relative to basal; nuclear multiplier corrected to (1+kx2²)/(1+kx1²). Source parameters remain separate. |
| 4 | Same ratio interface with a different historical mammalian parameter set and inducer doses. |
| 5 | Exact numerical duplicate of cell 4; reuse same interface. Parameters retain a distinct source pointer; tick formatting removed. |

### new_foldchange.ipynb — 3 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 1 | `scan_designs` with `foldchange_design_parameters(1)`: 20 receptor versions × 14 DBDs, grid [.3,10], 2000 points. DBD I0 overrides any receptor I0. Returns optimum L, score, output, log fold and log difference. |
| 2 | Same scan with `foldchange_design_parameters(2)`: five nuclear receptors and their kx1/kx2. |
| 3 | Same scan with `foldchange_design_parameters(3)`: 15 receptors; `pareto=True` retains global two-objective frontier and sensor labels. Shared `fast_pareto_2d`; CSV/color loops removed. |

### operator.ipynb — 2 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `operator_response` and `solve_operator_target`: n-site occupancy 1-(1-p_bound)^n, Brent inversion on [1e-5,100], unreachable targets return (NaN,NaN). This is distinct from Note 10's unbound-operator rule. |
| 1 | Same forward model over dose/L/operator count; preserves the distinct amplitude 10.84931505 and inherited I0=.035485714 in its recipe. |

### optimal_plot.ipynb — 4 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `fit_yield_gp` (standardized X, isotropic constant×RBF, alpha=.001, 50 restarts), `sample_candidates`, `select_candidates`; 50,000 bounded candidates, top 64 predicted means, batches of 1000. |
| 1 | Same interfaces with strict predictive-standard-deviation filter sigma<.2 before ranking. |
| 2 | Fit on caller-concatenated old/new observations; perturb previous candidates by uniform [-.1,.1], clip to bounds, sigma<.15, top 64. Source num_samples=20000 was unused: local sampling still produces one point per previous row. |
| 3 | `fit_yield_gp(anisotropic=True)` keeps separate length scales and upper bound 1e4. `pairwise_slice` predicts two-feature grids with other features fixed at caller-supplied training means; `bounded_round_progress` retains filtering, round means and Euclidean movements. |

### parameters_estimate.ipynb — 1 cell

| Cell | Retained computation / disposition |
| --- | --- |
| 1 | `estimate_kd` and `estimate_M` exactly invert canonical mass balance. `estimate_shared_parameters` requires explicit fixed LBD k1/k2 and groups inversions as initialization; removed the unsupported k1 heuristic and incomplete M inversion. |

### parameters_fitting.ipynb — 6 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `fit_notebook_curve_fit(cell=0)` retains source initialization/bounds where valid and minimizes normalized log10 residuals. Raw objective, discontinuous penalties and invalid-domain unbounded fallback are superseded. |
| 1 | `fit_notebook_curve_fit(cell=1)` fits the five canonical nuclear parameters with nonnegative bounds and the same log10 R² objective. |
| 2 | `fit_notebook_curve_fit(cell=2)` fits three shared parameters, explicit per-observation kd and optional dataset groups; each group is normalized by its own log10 SST. Source glob-order constants are provenance only. |
| 3 | `fit_shared_then_kd` and optional `fit_shared_then_kd_adam` fit the canonical response, first shared parameters at fixed kd then per-dataset kd; all stages optimize log10 R². Removed the asymmetric epsilon equation and raw MSE. |
| 4 | Same two-stage APIs with explicit kx1/kx2. The nuclear model matches analysis.response; no extra kx2 floor or absolute-value model variant. Optional Adam uses positive parametrization and float64; only selected gradients are optimized. |
| 5 | `regression_diagnostics(scale='log10', direction='observed_to_predicted')`; positive paired mask, log Pearson r², line coefficients and raw predictive R². |

### plot4.ipynb — 11 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 1 | Removed the disconnected quadratic scratch expression and undefined-variable fragments; use analysis.response for a CIC response with explicit TF and model parameters. |
| 6 | Nuclear `response` with the cell's MR coefficients. |
| 7 | Ordinary `response`, shared raw/log10 R² calculations. Historical mammalian amplitude convention retained. |
| 8 | Nuclear `response` with distinct ER/DHB crosstalk coefficients; shared raw R². |
| 9 | Ordinary `response` with distinct RpaR/DBD coefficients; shared raw R². |
| 10 | Remove unlabelled scalar scratch sum 3000+5500+16610+16548+4856.58=46514.58; no model, inputs or downstream use. |
| 11 | Ordinary `response`; `regression_diagnostics(scale='raw', direction='predicted_to_observed')` retains affine in-sample calibration and distinguishes it from raw predictive R². |
| 12 | Two ordinary responses at different L/kd values; parameter records retained, no distinct model. |
| 14 | Ordinary `response_pair` broadcast/scanned over DBD records. Preserve this cell's different LexAs17/RecApact/CI values instead of replacing by another table. |
| 15 | Ordinary `response_pair` over listed receptor records; upper I_ranges endpoint is each induced dose. |
| 16 | Nuclear `response_pair`; its receptor parameter versions and dose endpoints remain separate. |

### plot6.ipynb — 10 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `dimer_response` at d=kb and d=I*kc, plus dimer-pool ratio as the approximate fold. This induced coefficient is linear in I, unlike k2²k3I². |
| 3 | Reuse `response`; `align_curve` with explicit source→master mapping and offsets; `grouped_statistics` of **master_residual**=master(x)-raw observation for P1P2/P1P9/P1P11; `alignment_statistics` per-dataset Pearson r² and unweighted mean. Both historically selected dataset subsets are retained in JSON. Unused response duplicate `func` and overwritten ddg expression removed. |
| 4 | `response` with varying kd; `align_curve` with identical source/master can provide interpolated predictions; shared Pearson metric. Original datasets actually select LBD, despite comments/axis saying kd: caller must choose the coordinate explicitly. |
| 5 | Reuse response/profiles/alignment primitives. Source contains `[.01,-.00697,...][i]`: Ellipsis and insufficient offsets make its workflow unexecutable. Preserve known parameter records; require explicit offsets instead of inventing the missing values. Its sequential difference mapping also differs from cell 3. |
| 6 | Reuse response, align_curve and alignment_statistics. Rounded kd/baseline parameters retained. Original `calculate_statistics` is `pass`; no hidden numerical algorithm. Implicit zip alignment and swallowed file-read errors are replaced by explicit paired input arrays. |
| 8 | `regression_diagnostics(scale='raw', direction='predicted_to_observed')`; retains Pearson r² and line fit on supplied prediction/observation columns. |
| 9 | `response` + `align_curve`: induced offset=-I0[i], basal offset=.027-2*I0[i]; `grouped_statistics` of **source_residual**=source(x)-raw observation. Source/master baseline=.01 and master kd=6.216347694. |
| 10 | Same corrections, `prediction_policy='clamp'` retains np.interp master-prediction boundary behavior while correction extrapolates. `alignment_statistics` supplies pooled raw R² by dose. Numerical output arrays retained; RGB/hex export removed. |
| 12 | `crosstalk_ratio` now evaluates two canonical responses with the same supplied L. Removed the substitution of kd for TF and undefined scatter variables. |
| 13 | Two calls to nuclear `response`, separate k3/kx2/dose values; return second/first for crosstalk. Personal CSV scatter selection is not a model input. |

### plot7.ipynb — 3 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `regression_diagnostics(scale='log10', direction='observed_to_predicted')`; retains positive mask, log-space regression, raw R² and in-sample fitted R². The fitted quantity depends on observed values and is labelled accordingly. |
| 1 | `hybrid_promoter` now uses the Note 11 total-ceiling convention and p_activator*p_unbound**operators (default 2). Source amplitude constants remain archived; callers explicitly supply tmax/baseline/operator count. |
| 2 | Same corrected hybrid interface, with fixed TF and varying inducer doses; shared diagnostic R². Multiplication of two historical amplitudes is no longer the output rule. |

## Current scope and limits

1. Same-model response, folds, crosstalk and fitting use the canonical mass
   balance described in [MODEL_AND_FITTING.md](MODEL_AND_FITTING.md). Historical
   Imax is still an amplitude and must be converted explicitly to total Tmax.
2. All CIC parameter optimizers maximize log10 R². Shared fits equally weight
   each dataset using its own log10 SST. Raw R², Pearson r² and calibration
   regressions remain diagnostic calculations, not fitting objectives.
3. Heterodimer, monomer, reduced limiting and allosteric comparison functions
   have different assumptions. They are not interchangeable CIC fit backends.
4. Source parameter constants and cell hashes are preserved independently.
   `historical_fit` describes an old source recipe, not current optimizer
   settings. Old fitted coefficients must be refitted before claiming that
   they optimize the corrected objective.
5. The original notebooks' private CSVs are missing. The included Note 10/11
   tables are not substituted for those inputs. Original-data fits, GP optima
   and historical corrected experimental R² cannot be reproduced here.
6. Array APIs require finite paired rows. Fitting additionally requires
   strictly positive, nonconstant responses per group; invalid observations
   are rejected. No concentration-unit conversion is inferred by array APIs.
7. The optional Adam backend uses canonical float64 equations and positive
   parameters. Historical epsilon, abs/clamp and accumulating-gradient quirks
   are superseded; historical optimizer trajectories are not reproduced.

## Validation

```text
python -m unittest discover -s tests -v
```

Tests compare canonical equations across modules, source parameter separation,
operator rules, fitting objectives on biased data, group weighting, invalid
inputs, exact inversions and optional NumPy/Torch parity. The source-cell
inventory still covers all 59 original code cells. Current measured results
and data limitations are in [VALIDATION.md](../submission/VALIDATION.md).
