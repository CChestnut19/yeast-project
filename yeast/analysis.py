"""Shared canonical yeast dose-response and Pareto helpers.

Here Imax is the response amplitude, so the upper limit is I0 + Imax.
The separate mammalian model fixes its total upper limit to 13.61 RPU.
"""

import numpy as np
from .binding import cic_dimer_pool


def response(L, kd, k1, k2, k3, Imax, I0, I, kx1=0.0, kx2=0.0):
    """Notebook response with an amplitude Imax (total ceiling I0 + Imax).

    All inputs broadcast, including per-observation kd and inducer dose I.
    This convention is deliberately separate from activator.model's total Tmax.
    """
    kd, k1, k2, k3, Imax, I0, I, kx1, kx2 = (
        np.asarray(value, dtype=float)
        for value in (kd, k1, k2, k3, Imax, I0, I, kx1, kx2))
    if any(not np.isfinite(value).all() or np.any(value < 0)
           for value in (kd, k1, k2, k3, Imax, I0, I, kx1, kx2)):
        raise ValueError("Response parameters must be finite and non-negative")
    effective = cic_dimer_pool(L, I, k1, k2, k3, kx1, kx2)
    z = kd * effective
    return I0 + Imax * z / (1.0 + z)


def response_pair(L, kd, k1, k2, k3, Imax, I0, I, kx1=0.0, kx2=0.0):
    """Return induced and basal responses without subtracting nearly equal roots."""
    return (response(L, kd, k1, k2, k3, Imax, I0, I, kx1, kx2),
            response(L, kd, k1, k2, k3, Imax, I0, 0.0, kx1, kx2))


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


def scan_designs(L, receptors, dbds, *, pareto=False):
    """Scan caller-supplied receptor/DBD records; return numerical result records.

    receptors need LBD_name, k1/k2/k3/Imax/I and optional kx1/kx2;
    dbds need DBD_name, kd, I0. The DBD baseline overrides any receptor I0,
    as in new_foldchange. Invalid logarithmic objectives are excluded explicitly.
    pareto=False keeps the first grid maximum per pair; True returns the global
    nondominated records, retaining tied points, in log10(fold) order.
    """
    L = np.asarray(L, dtype=float)
    if L.ndim != 1 or not len(L) or not np.isfinite(L).all() or np.any(L < 0):
        raise ValueError("L must be a nonempty finite non-negative vector")
    dbds = list(dbds)
    records = []
    for receptor in receptors:
        for dbd in dbds:
            on, off = response_pair(
                L, dbd['kd'], receptor['k1'], receptor['k2'], receptor['k3'],
                receptor['Imax'], dbd['I0'], receptor['I'],
                receptor.get('kx1', 0.0), receptor.get('kx2', 0.0))
            valid = (on > off) & (off > 0) & np.isfinite(on) & np.isfinite(off)
            indices = np.flatnonzero(valid)
            if not len(indices):
                continue
            f1, f2 = np.log10(on[valid] / off[valid]), np.log10(on[valid] - off[valid])
            selected = range(len(indices)) if pareto else [int(np.argmax(f1 + f2))]
            for j in selected:
                idx = indices[j]
                records.append({'LBD_name': receptor['LBD_name'],
                                'DBD_name': dbd['DBD_name'], 'L': float(L[idx]),
                                'score': float(f1[j] + f2[j]), 'RPU': float(on[idx]),
                                'log10_fold': float(f1[j]), 'log10_difference': float(f2[j])})
    if pareto and records:
        mask = fast_pareto_2d([[r['log10_fold'], r['log10_difference']] for r in records])
        records = sorted((r for r, keep in zip(records, mask) if keep),
                         key=lambda r: r['log10_fold'])
    return records
