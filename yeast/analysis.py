"""Shared canonical yeast dose-response and Pareto helpers.

Here Tmax_minus_T0 is the response amplitude, so the upper limit is T0 + Tmax_minus_T0.
The separate mammalian model fixes its total upper limit to 13.61 RPU.
"""

import numpy as np
from .binding import cic_dimer_pool


def response(c_TF_all, KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1=0.0, Kx2=0.0):
    """Notebook response with an amplitude Tmax_minus_T0 (total ceiling T0 + Tmax_minus_T0).

    All inputs broadcast, including per-observation KA and inducer concentration c_I.
    This convention is deliberately separate from activator.model's total Tmax.
    """
    KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1, Kx2 = (
        np.asarray(value, dtype=float)
        for value in (KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1, Kx2))
    if any(not np.isfinite(value).all() or np.any(value < 0)
           for value in (KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1, Kx2)):
        raise ValueError("Response parameters must be finite and non-negative")
    c_TF_eff = cic_dimer_pool(c_TF_all, c_I, Kd0, Kb, Kd1, Kx1, Kx2)
    z = KA * c_TF_eff
    return T0 + Tmax_minus_T0 * z / (1.0 + z)


def response_pair(c_TF_all, KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1=0.0, Kx2=0.0):
    """Return induced and basal responses without subtracting nearly equal roots."""
    return (response(c_TF_all, KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1, Kx2),
            response(c_TF_all, KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, 0.0, Kx1, Kx2))


def foldchange1(*args):
    on, off = response_pair(*args)
    return np.log10((on / off) * (on - off))


def foldchange2(*args):
    return response_pair(*args)[0]


def foldchange3(*args):
    on, off = response_pair(*args)
    return np.log10(on / off), np.log10(on - off)


def _nuclear_args(c_TF_all, KA, Kd0, Kb, Kd1, Kx1, Kx2, Tmax_minus_T0, T0, c_I):
    return c_TF_all, KA, Kd0, Kb, Kd1, Tmax_minus_T0, T0, c_I, Kx1, Kx2


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


def scan_designs(c_TF_all, receptors, dbds, *, pareto=False):
    """Scan caller-supplied receptor/DBD records; return numerical result records.

    receptors need LBD_name, Kd0/Kb/Kd1/Tmax_minus_T0/c_I and optional Kx1/Kx2;
    dbds need DBD_name, KA, T0. The DBD T0 overrides any receptor T0,
    as in new_foldchange. Invalid logarithmic objectives are excluded explicitly.
    pareto=False keeps the first grid maximum per pair; True returns the global
    nondominated records, retaining tied points, in log10(fold) order.
    """
    c_TF_all = np.asarray(c_TF_all, dtype=float)
    if c_TF_all.ndim != 1 or not len(c_TF_all) or not np.isfinite(c_TF_all).all() or np.any(c_TF_all < 0):
        raise ValueError("c_TF_all must be a nonempty finite non-negative vector")
    dbds = list(dbds)
    records = []
    for receptor in receptors:
        for dbd in dbds:
            on, off = response_pair(
                c_TF_all, dbd['KA'], receptor['Kd0'], receptor['Kb'], receptor['Kd1'],
                receptor['Tmax_minus_T0'], dbd['T0'], receptor['c_I'],
                receptor.get('Kx1', 0.0), receptor.get('Kx2', 0.0))
            valid = (on > off) & (off > 0) & np.isfinite(on) & np.isfinite(off)
            indices = np.flatnonzero(valid)
            if not len(indices):
                continue
            f1, f2 = np.log10(on[valid] / off[valid]), np.log10(on[valid] - off[valid])
            selected = range(len(indices)) if pareto else [int(np.argmax(f1 + f2))]
            for j in selected:
                idx = indices[j]
                records.append({'LBD_name': receptor['LBD_name'],
                                'DBD_name': dbd['DBD_name'], 'c_TF_all': float(c_TF_all[idx]),
                                'score': float(f1[j] + f2[j]), 'RPU': float(on[idx]),
                                'log10_fold': float(f1[j]), 'log10_difference': float(f2[j])})
    if pareto and records:
        mask = fast_pareto_2d([[r['log10_fold'], r['log10_difference']] for r in records])
        records = sorted((r for r, keep in zip(records, mask) if keep),
                         key=lambda r: r['log10_fold'])
    return records
