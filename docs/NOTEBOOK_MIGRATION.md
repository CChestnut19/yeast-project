# Root notebook algorithm migration

Source: repository commit `bfd2de5`, ten root notebooks, **59 code cells**.
Cell numbers below are the original zero-based notebook indices, including
markdown cells. `yeast/notebook_parameters.json` records every code cell's
SHA-256 and its literal scientific parameters, with separate source-cell keys.
This migration removes notebook execution, plots, colors, figure geometry,
personal filesystem paths and automatic CSV writes. Functions return numerical
arrays, records or tables; callers can write those results to CSV/JSON.

## Shared interfaces and model conventions

- `yeast.binding.active_dimer_pool` remains the single ordinary homodimer
  mass-balance implementation. `yeast.analysis.response` and `response_pair`
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
  allosteric, operator and hybrid models. Functions ending in `literal` retain
  suspicious source equations instead of substituting a different model.
- `yeast.curve_analysis` handles slopes, historical quality measures, alignment
  and regression. It reuses the existing activator R²/Pearson implementations.
  `yeast.fitting` handles estimation/fitting and `yeast.optimization` the GP work.

Use `load_notebook_parameters('ec50.ipynb', 3)` to select one parameter version.
The result separates `parameters`, optional `grids`, `fit` and `alignment`
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
| 10 | `fixed_induced_root_fold_literal`: induced square root uses TF=1 while its outside factor uses varying L. Actual baseline .001 overrides unused I0. |
| 11 | `rob_phillips_allosteric_dimer_fixed_inducer`; compute expression/no-TF expression for fold. Retains source's product R*DBD, interaction and fixed allosteric factor. |
| 12 | `simple_repression_partition_function`, `simple_repression_pbound`, `simple_repression_foldchange`; retain effective R=R*DBD/(1+DBD). State contributions are 1/Z, RNAP/Z, TF/Z. |

### ec50.ipynb — 6 cells

Despite its filename this notebook contains **no EC50 calculation or dose-root
search**. Its distinct computations are quality ratios and fold ranges.

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `saturated_fold_approximation`; other computed response curves reuse `dimer_response`. The source `np.arange(.000109651,.387876109)` has default step 1 and contains only one k1, recorded in grid metadata. |
| 1 | Same approximate fold with separately preserved acVHH/RpaR coefficients; ordinary multiplication gives the L*k1 coordinate. |
| 2 | `log_fold_range_literal`; nuclear root/ratio mismatch retained. Uses explicit I, because original loop ignores sensor_I and inherits I=10 from earlier cells. All parameter tables retained separately. |
| 3 | `quality_ratio`, optionally multiplied by kx2²/kx1² for names present in both nuclear tables. Yeast-era parameter set retained. |
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
| 1 | `estimate_shared_parameters`: group-mean k1 heuristic by LBD, rowwise `estimate_kd` then mean by DBD, `estimate_M_literal` then mean by LBD, merge onto observation table. Explicit amplitude=2.5 and total_tf=1 defaults. `calc_f` is the shared basal dimer pool after substituting its root. |

### parameters_fitting.ipynb — 6 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `fit_notebook_curve_fit(cell=0)`: raw objective, original k1<10 and positive-k penalty, original bounded fit, unbounded fallback on exception. Caller supplies fixed kd/I0/amplitude. |
| 1 | `fit_notebook_curve_fit(cell=1)`: five-parameter nuclear model, raw objective, positive-value penalty, unbounded curve_fit. |
| 2 | `fit_notebook_curve_fit(cell=2)`: bounded three-shared-parameter log10 objective; fixed per-observation kd is explicit. Historical indices 0→10.56826129, 1→9.152591138, later→2.09409 retained as metadata. No unknown glob order is reconstructed. |
| 3 | `epsilon_response_literal` and optional `fit_shared_then_kd_adam(variant='torch_epsilon_literal')`; raw MSE, ordinary three-shared-parameter stage at kd=10, followed by warm-started per-dataset kd stages. SciPy `fit_shared_then_kd` is an additional alternative, not a claim of Adam equivalence. |
| 4 | Same optional Adam scheduler with `variant='nuclear_clamped'`; five shared parameters, absolute values and kx2 floor .001. Original float32, learning rate .001, 100,000 shared steps, 150,000 kd steps and gradient clip 5 are configurable defaults. |
| 5 | `regression_diagnostics(scale='log10', direction='observed_to_predicted')`; positive paired mask, log Pearson r², line coefficients and raw predictive R². |

### plot4.ipynb — 11 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 1 | `quadratic_activation_literal` retains the printed ((I*k2)²+k3)/(1+(I*k2)²+k3). Original I is used before assignment and k1 is undefined; unused x2 discarded. Interface requires I explicitly. |
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
| 12 | `mismatched_tf_crosstalk_literal`: second square root uses m2 (labelled kd) as TF, while outer factor is m1. Parameters remain distinct. Undefined scatter x_subset/y_subset removed. |
| 13 | Two calls to nuclear `response`, separate k3/kx2/dose values; return second/first for crosstalk. Personal CSV scatter selection is not a model input. |

### plot7.ipynb — 3 cells

| Cell | Retained computation / disposition |
| --- | --- |
| 0 | `regression_diagnostics(scale='log10', direction='observed_to_predicted')`; retains positive mask, log-space regression, raw R² and in-sample fitted R². The fitted quantity depends on observed values and is labelled accordingly. |
| 1 | `hybrid_promoter` with varying TF concentrations, fixed inducer doses=10. Preserve amplitude pair 35.84931505/.85546578 and baseline .006969286. Source axis labels say inducer although actual variables are TF. |
| 2 | Same hybrid interface with fixed TF=10, varying inducer doses, amplitude pair 35.84931505/.687512595 and baseline .015930056; shared raw R². Unused I02 does not contribute. |

## Known scientific and execution limits

1. Stable rationalized mass-balance expressions replace subtractive cancellation.
   Zero-TF baseline is defined exactly; the original logarithmic forms emitted
   NaNs at zero. Existing finite-domain equations agree within floating-point
   tolerance. The steep-interval function returns NaNs if no positive interval
   exists instead of indexing an empty result.
2. `box` heterodimer states deliberately share A*B. Its unused C/D equations
   contain k2² where a basal k1² might be expected, but do not affect any output.
   The fixed-root, mismatched-TF and nuclear subtract-1 variants are explicitly
   retained as literal models; they are not silently “corrected.”
3. The grouped estimate's k1 heuristic and `estimate_M_literal` are preserved
   even though the latter is not the inverse of the complete inducer model.
   Singular/nonphysical inputs now raise an error instead of generating invalid
   downstream parameters. These are historical estimates, not fit guarantees.
4. Historical SciPy fit defaults retain original penalties and fallback. The
   optional Adam backend preserves selected-optimizer zero_grad and clipping
   **all** parameters, including accumulating gradients on parameters outside
   that optimizer. This is a source quirk with numerical consequences. Algebraic
   regrouping can change float32 rounding; bitwise optimizer trajectories are
   not claimed. The separate least_squares interface uses positive bounds and
   explicitly reports convergence; it is an additional supported workflow.
5. No original private CSVs used by these root notebooks are included in the
   repository's two public CSV inputs. The activator workbook workflow and
   public Note 10/11 tables have their own established pipelines. Their values
   are not substituted for missing notebook CSVs. Historical original-data
   fits, GP optima and corrected experimental R² therefore cannot be rerun here.
   Missing measurements are not synthesized.
6. Array APIs require paired rows; they reject missing values rather than
   repeating independent dropna calls that can mismatch L, dose and response.
   GP random sampling accepts an explicit seed; source runs had none, so old
   candidate rows cannot be reconstructed bit-for-bit. GPs retain their original
   standardization, kernels, alpha, ranking and standard-deviation filters.
7. No concentration-unit conversion is inferred. Supply each API's inputs in
   the units associated with its selected source parameters; historical cells
   do not establish a single shared unit convention.

## Validation

`python -m unittest discover -s tests -p test_notebook_algorithms.py -v` verifies original finite
response equations (including distinct literal variants), model ceiling
conversion, conservation, operator inversion/unreachable targets, source grid
maxima/Pareto ties, quality ratios, alignment residuals/offsets/boundaries,
grouped statistics, calibration direction, parameter-set separation, grouped
estimation, raw/log fits from displaced initial values, original curve_fit
penalties/fallback, two-stage fits and small GP selection/slices.

On 2026-09-18, the minimal NumPy/Pandas/SciPy/scikit-learn environment passed
**18 tests**, with the optional Torch test skipped. The existing Torch environment
separately passed both historical forward variants and a two-step shared plus
two-step per-dataset Adam smoke test. No plotting package is required.
