"""Gaussian-process fitting, bounded search and slices from optimal_plot.ipynb."""
import numpy as np


def _bounds(bounds):
    bounds = np.asarray(bounds, float)
    if (bounds.ndim != 2 or bounds.shape[1] != 2 or not np.isfinite(bounds).all()
            or np.any(bounds[:, 1] <= bounds[:, 0])):
        raise ValueError("Bounds must be finite (n_features, 2) increasing intervals")
    return bounds


def fit_yield_gp(X, y, *, anisotropic=False, alpha=1e-3, restarts=50, random_state=None):
    """Standardize X; fit ConstantKernel*RBF with the historical kernel bounds."""
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF, ConstantKernel
    from sklearn.preprocessing import StandardScaler
    X, y = np.asarray(X, float), np.asarray(y, float)
    if (X.ndim != 2 or len(X) < 2 or y.shape != (len(X),)
            or not np.isfinite(X).all() or not np.isfinite(y).all()):
        raise ValueError("Require a finite feature matrix and paired response vector")
    length = np.ones(X.shape[1]) if anisotropic else 1.0
    kernel = ConstantKernel(1., (1e-6, 1e6))*RBF(length, (1e-6, 1e4 if anisotropic else 1e2))
    scaler = StandardScaler().fit(X)
    gp = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=restarts,
                                   alpha=alpha, random_state=random_state)
    gp.fit(scaler.transform(X), y)
    return gp, scaler


def sample_candidates(bounds, *, count=50000, previous=None, perturbation=.1, random_state=None):
    """Uniform candidates or one clipped perturbation per previous point.

    In the local case count is deliberately ignored, as in source cell 2:
    its num_samples=20000 was unused and it generated one row per previous row.
    """
    bounds = _bounds(bounds)
    rng = np.random.default_rng(random_state)
    if previous is None:
        if isinstance(count, bool) or int(count) != count or count < 1:
            raise ValueError("count must be a positive integer")
        return rng.uniform(bounds[:, 0], bounds[:, 1], size=(int(count), len(bounds)))
    previous = np.asarray(previous, float)
    if (previous.ndim != 2 or previous.shape[1] != len(bounds)
            or not np.isfinite(previous).all() or not np.isfinite(perturbation) or perturbation < 0):
        raise ValueError("Invalid previous points or perturbation")
    return np.clip(previous+rng.uniform(-perturbation, perturbation, previous.shape),
                   bounds[:, 0], bounds[:, 1])


def select_candidates(gp, scaler, candidates, *, top_k=64, confidence_threshold=None, batch_size=1000):
    """Rank GP means after the optional strict sigma<threshold filter.

    Return selected rows in ascending predicted yield, matching argsort[-k:].
    Empty selections retain correct shapes; prediction batches include std.
    """
    points = np.asarray(candidates, float)
    if (points.ndim != 2 or not np.isfinite(points).all() or top_k < 1
            or batch_size < 1 or int(top_k) != top_k or int(batch_size) != batch_size):
        raise ValueError("Require finite candidate matrix and positive integer sizes")
    means, stds = [], []
    for start in range(0, len(points), int(batch_size)):
        mean, std = gp.predict(scaler.transform(points[start:start+int(batch_size)]), return_std=True)
        means.append(mean)
        stds.append(std)
    mean = np.concatenate(means) if means else np.empty(0)
    std = np.concatenate(stds) if stds else np.empty(0)
    valid = np.ones(len(points), dtype=bool) if confidence_threshold is None else std < confidence_threshold
    indices = np.flatnonzero(valid)
    indices = indices[np.argsort(mean[indices])[-int(top_k):]]
    return {'points': points[indices], 'mean': mean[indices], 'std': std[indices],
            'indices': indices, 'eligible_count': int(valid.sum())}


def pairwise_slice(gp, scaler, bounds, fixed_values, dimensions, *, resolution=50):
    """Numeric two-coordinate GP slice, with other features fixed to supplied means."""
    bounds, fixed = _bounds(bounds), np.asarray(fixed_values, float)
    i, j = dimensions
    if (fixed.shape != (len(bounds),) or not np.isfinite(fixed).all()
            or i == j or min(i, j) < 0 or max(i, j) >= len(bounds) or resolution < 2):
        raise ValueError("Invalid fixed vector, dimensions or resolution")
    x, y = np.meshgrid(np.linspace(*bounds[i], resolution), np.linspace(*bounds[j], resolution))
    points = np.tile(fixed, (x.size, 1))
    points[:, i], points[:, j] = x.ravel(), y.ravel()
    mean, std = gp.predict(scaler.transform(points), return_std=True)
    return {'x': x, 'y': y, 'mean': mean.reshape(x.shape), 'std': std.reshape(x.shape)}


def bounded_round_progress(rounds, bounds, dimensions):
    """Per-round means and Euclidean changes after filtering just two coordinates."""
    bounds = _bounds(bounds)
    indices = list(dimensions)
    means, counts = [], []
    for points in rounds:
        points = np.asarray(points, float)
        if points.ndim != 2 or points.shape[1] != len(bounds):
            raise ValueError("Round feature shape does not match bounds")
        pair = points[:, indices]
        valid = np.all((pair >= bounds[indices, 0]) & (pair <= bounds[indices, 1]), axis=1)
        counts.append(int(valid.sum()))
        means.append(pair[valid].mean(axis=0) if valid.any() else np.full(len(indices), np.nan))
    means = np.asarray(means)
    return {'means': means, 'counts': np.asarray(counts),
            'distance': np.linalg.norm(np.diff(means, axis=0), axis=1)}
