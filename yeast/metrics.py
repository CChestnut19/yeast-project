"""Strict regression metrics for the complete Note 10/11 observation tables.

Activator sensitivity analyses keep their separate, documented omission policy.
"""
import numpy as np


def regression_metrics(observed, predicted, scale='log10'):
    observed, predicted = np.asarray(observed, float), np.asarray(predicted, float)
    if observed.ndim != 1 or predicted.shape != observed.shape or observed.size < 2:
        raise ValueError('Metrics require equal-length 1D arrays with at least two observations')
    if not np.isfinite(observed).all() or not np.isfinite(predicted).all():
        raise ValueError('Metrics require finite observations and predictions')
    if scale == 'log10':
        if np.any(observed <= 0) or np.any(predicted <= 0):
            raise ValueError('Log10 metrics require positive observations and predictions')
        observed, predicted = np.log10(observed), np.log10(predicted)
    elif scale != 'raw':
        raise ValueError("Metric scale must be 'raw' or 'log10'")
    sse = float(np.sum((observed - predicted)**2))
    sst = float(np.sum((observed - np.mean(observed))**2))
    if sst <= 0:
        raise ValueError('R2 is undefined for constant observations')
    return {'n': int(observed.size), 'SSE': sse, 'SST': sst,
            'R2': float(1 - sse / sst), 'RMSE': float(np.sqrt(sse / observed.size))}
