"""Shared yeast dose-response and Pareto helpers used by the notebooks.

Here Imax is the response amplitude, so the upper limit is I0 + Imax.
The separate mammalian model fixes its total upper limit to 13.61 RPU.
"""

import numpy as np
from .binding import active_dimer_pool


def response_pair(L, kd, k1, k2, k3, Imax, I0, I, kx1=0.0, kx2=0.0):
    """Return induced and basal responses without subtracting nearly equal roots."""
    L = np.asarray(L, dtype=float)

    def response(b, d):
        effective = active_dimer_pool(L, b, d)
        z = kd * effective
        return I0 + Imax * z / (1.0 + z)

    on = response(1.0 + kx1 + k2 * I * (1.0 + kx2),
                  k1 * (1.0 + kx1**2) + k2**2 * k3 * I**2 * (1.0 + kx2**2))
    off = response(1.0 + kx1, k1 * (1.0 + kx1**2))
    return on, off


def foldchange1(*args):
    on, off = response_pair(*args)
    return np.log10((on / off) * (on - off))


def foldchange2(*args):
    return response_pair(*args)[0]


def foldchange3(*args):
    on, off = response_pair(*args)
    return np.log10(on / off), np.log10(on - off)


def _nuclear_args(L, kd, k1, k2, k3, kx1, kx2, Imax, I0, I):
    return L, kd, k1, k2, k3, Imax, I0, I, kx1, kx2


def nuclear_foldchange1(*args):
    return foldchange1(*_nuclear_args(*args))


def nuclear_foldchange2(*args):
    return foldchange2(*_nuclear_args(*args))


def nuclear_foldchange3(*args):
    return foldchange3(*_nuclear_args(*args))


def fast_pareto_2d(points):
    """Maximize both finite objectives; retain all identical nondominated points."""
    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError("points must be a finite (n, 2) array")
    if len(points) == 0:
        return np.zeros(0, dtype=bool)
    unique, inverse = np.unique(points, axis=0, return_inverse=True)
    order = np.lexsort((-unique[:, 1], -unique[:, 0]))
    y = unique[order, 1]
    best_before = np.concatenate(([-np.inf], np.maximum.accumulate(y)[:-1]))
    mask = np.zeros(len(unique), dtype=bool)
    mask[order] = y > best_before
    return mask[inverse]
