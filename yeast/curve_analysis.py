"""Array-based slope, historical quality, alignment and regression calculations."""
import numpy as np
from scipy.interpolate import interp1d
from scipy.stats import linregress

from .activator.model import r2_coefficient, pearson


def _paired(x, y, *, minimum=2):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.ndim != 1 or x.shape != y.shape or len(x) < minimum:
        raise ValueError("Require equal-length one-dimensional paired arrays")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Inputs must be finite; remove missing rows jointly")
    return x, y


def get_steep_interval(L, P, threshold_ratio=0.8):
    """box cell 0: first/last grid points above a fraction of maximum log slope.

    A flat/decreasing curve has no positive steep interval and returns NaNs.
    The interval encloses all qualifying points, even when disjoint.
    """
    L, P = _paired(L, P)
    if np.any(L <= 0) or np.any(P <= 0) or np.any(np.diff(L) <= 0):
        raise ValueError("Require positive response and increasing positive TF grid")
    if not 0 <= threshold_ratio < 1:
        raise ValueError("threshold_ratio must lie in [0, 1)")
    slope = np.gradient(np.log10(P), np.log10(L))
    indices = np.flatnonzero((slope > threshold_ratio*np.max(slope)) & (slope > 0))
    return (float(L[indices[0]]), float(L[indices[-1]])) if indices.size else (np.nan, np.nan)


def saturated_fold_approximation(L, k1, kd):
    """ec50 cells 0–1's approximate fold, including its finite L=0 limit."""
    L, k1, kd = np.asarray(L, float), np.asarray(k1, float), np.asarray(kd, float)
    if np.any(L < 0) or np.any(k1 <= 0) or np.any(kd < 0):
        raise ValueError("Require L>=0, k1>0, kd>=0")
    root = np.sqrt(1+8*L*k1)
    return kd*(root+1)**2/(16*k1*(1+L*kd/2))


def quality_ratio(k1, k2, k3, I, *, kx1=None, kx2=None):
    """ec50 cells 3–5: induced/basal coefficient ratio (not an EC50)."""
    result = np.asarray(k3)*np.asarray(k2)**2*np.asarray(I)**2/np.asarray(k1)
    if (kx1 is None) != (kx2 is None):
        raise ValueError("Supply both nuclear parameters or neither")
    return result if kx1 is None else result*np.asarray(kx2)**2/np.asarray(kx1)**2


def log_fold_range_literal(L, k1, k2, k3, kd, I, *, is_nuclear=False, kx1=0, kx2=0):
    """ec50 cell 2, including the historical nuclear 'subtract 1' convention.

    Stable algebra for the same equation; retains the source's nan/inf sentinel
    mapping and positive-only range policy. I is explicit because the cell used
    a stale global I instead of its own sensor_I table.
    """
    L = np.asarray(L, float)
    basal_d, induced_d, b = k1, k2**2*k3*I**2, 1.0
    if is_nuclear:
        basal_d *= 1+kx1**2
        induced_d *= 1+kx2**2
        b = 1+kx1
    roots = [np.sqrt(b*b+8*L*d) for d in (basal_d, induced_d)]
    # (root-1)/(root+1), not (root-b)/(root+b).
    y1, y2 = [(b*b-1+8*L*d)/(r+1)**2 for d, r in zip((basal_d, induced_d), roots)]
    with np.errstate(divide='ignore', invalid='ignore'):
        fold = ((1/y1)+L*kd/2)/((1/y2)+L*kd/2)
    fold = np.nan_to_num(fold, nan=1e-6, posinf=1e6, neginf=1e-6)
    positive = np.asarray(fold).reshape(-1)
    positive = positive[positive > 0]
    if not len(positive):
        return 0., 0.
    return float(np.log10(positive.min())), float(np.log10(positive.max()))


def align_curve(x, observed, grid, source_curve, master_curve, *, offset=0.0,
                prediction_policy='extrapolate'):
    """Apply master-minus-source linear interpolation plus an explicit offset.

    Correction extrapolates as in plot6. 'clamp' reproduces cell 10's np.interp
    prediction at out-of-grid points; 'extrapolate' reproduces earlier cells.
    Returns paired arrays with both uncorrected residuals and corrected data.
    """
    x, observed = _paired(x, observed, minimum=0)
    grid, source = _paired(grid, source_curve)
    _, master = _paired(grid, master_curve)
    if np.any(np.diff(grid) <= 0):
        raise ValueError("Interpolation grid must be strictly increasing")
    difference = interp1d(grid, master-source, fill_value='extrapolate')(x)
    if prediction_policy == 'clamp':
        predicted = np.interp(x, grid, master)
    elif prediction_policy == 'extrapolate':
        predicted = interp1d(grid, master, fill_value='extrapolate')(x)
    else:
        raise ValueError("prediction_policy must be 'clamp' or 'extrapolate'")
    return {'x': x.copy(), 'corrected': observed+difference+offset,
            'predicted': predicted, 'shift': difference+offset,
            'source_residual': interp1d(grid, source, fill_value='extrapolate')(x)-observed,
            'master_residual': interp1d(grid, master, fill_value='extrapolate')(x)-observed}


def grouped_statistics(x, values):
    """Sorted means and sample standard deviations (ddof=1), as pandas groupby."""
    x, values = _paired(x, values, minimum=0)
    unique = np.unique(x)
    groups = [values[x == value] for value in unique]
    return {'x': unique, 'mean': np.array([g.mean() for g in groups]),
            'std': np.array([g.std(ddof=1) if len(g)>1 else np.nan for g in groups]),
            'count': np.array([len(g) for g in groups], dtype=int)}


def alignment_statistics(aligned):
    """Separate per-dataset Pearson r², its unweighted mean and pooled raw R²."""
    aligned = list(aligned)
    correlations = np.array([pearson(a['corrected'], a['predicted'], 'raw')[1]
                             for a in aligned])
    if not aligned:
        return {'pearson_r2': correlations, 'mean_pearson_r2': np.nan, 'pooled_R2': np.nan}
    observed = np.concatenate([a['corrected'] for a in aligned])
    predicted = np.concatenate([a['predicted'] for a in aligned])
    return {'pearson_r2': correlations, 'mean_pearson_r2': float(np.mean(correlations)),
            'pooled_R2': r2_coefficient(observed, predicted, 'raw')[0]}


def regression_diagnostics(observed, predicted, *, scale='raw', direction='predicted_to_observed'):
    """Retain the distinct historical in-sample calibration directions.

    raw predicted_to_observed: plot4 cell 11 (observed ~ predicted).
    log10 observed_to_predicted: plot7 cell 0 / fitting cell 5 (predicted ~ observed).
    The latter's fitted values use the observations and are not new predictions.
    Returns raw R², Pearson r², line coefficients and in-sample fitted R².
    """
    observed, predicted = _paired(observed, predicted)
    omitted = 0
    if scale == 'log10':
        valid = (observed > 0) & (predicted > 0)
        omitted = int((~valid).sum())
        observed, predicted = observed[valid], predicted[valid]
        if len(observed) < 2:
            raise ValueError("Need at least two positive paired observations")
        a, b = np.log10(observed), np.log10(predicted)
    elif scale == 'raw':
        a, b = observed, predicted
    else:
        raise ValueError("scale must be 'raw' or 'log10'")
    if direction == 'predicted_to_observed':
        x, y = b, a
    elif direction == 'observed_to_predicted':
        x, y = a, b
    else:
        raise ValueError("Unknown regression direction")
    result = linregress(x, y)
    fitted = result.slope*x+result.intercept
    fitted = 10**fitted if scale == 'log10' else fitted
    return {'slope': float(result.slope), 'intercept': float(result.intercept),
            'pearson_r2': float(result.rvalue**2), 'p_value': float(result.pvalue),
            'stderr': float(result.stderr), 'fitted': fitted, 'omitted': omitted,
            'raw_R2': r2_coefficient(observed, predicted, 'raw')[0],
            'fitted_in_sample_R2': r2_coefficient(observed, fitted, 'raw')[0]}
