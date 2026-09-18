"""Archived activator equations and metrics; Tmax is the TOTAL output ceiling."""
from __future__ import annotations
import numpy as np
from yeast.binding import cic_dimer_pool
from .settings import TMAX_PRIMARY


def unit_factor(unit: str) -> float:
    try:
        return {"nM": 1e-3, "uM": 1.0, "mM": 1e3}[unit]
    except KeyError as error:
        raise ValueError(f"Unsupported inducer unit: {unit!r}") from error


def _validate_parameters(c_tf, c_i_uM, ka, kd0, kb, kd1, t0, tmax):
    for name, value in (("c_tf", c_tf), ("c_i_uM", c_i_uM), ("KA", ka),
                        ("Kd0", kd0), ("Kb", kb), ("Kd1", kd1), ("T0", t0), ("Tmax", tmax)):
        array = np.asarray(value, dtype=float)
        if not np.isfinite(array).all() or np.any(array < 0):
            raise ValueError(f"{name} must be finite and non-negative")
    if np.any(np.asarray(tmax) <= 0) or np.any(np.asarray(t0) >= tmax):
        raise ValueError("Require 0 <= T0 < Tmax")


def model_s32_s47(c_tf, c_i_uM, ka, kd0, kb, kd1, t0, tmax=TMAX_PRIMARY):
    _validate_parameters(c_tf, c_i_uM, ka, kd0, kb, kd1, t0, tmax)
    dose = np.asarray(c_i_uM, dtype=float)
    active_pool = cic_dimer_pool(c_tf, dose, kd0, kb, kd1)
    z = ka * active_pool
    return t0 + (tmax - t0) * z / (1.0 + z)


def _metric_pairs(y, predicted, scale):
    if scale not in {"raw", "log10"}:
        raise ValueError("scale must be 'raw' or 'log10'")
    y, predicted = np.asarray(y, dtype=float), np.asarray(predicted, dtype=float)
    if y.ndim != 1 or predicted.shape != y.shape:
        raise ValueError("Observed and predicted data must be one-dimensional arrays of equal length")
    mask = np.isfinite(y) & np.isfinite(predicted)
    if scale == "log10":
        mask &= (y > 0) & (predicted > 0)
    omitted = int(len(y) - mask.sum())
    y, predicted = y[mask], predicted[mask]
    if scale == "log10":
        y, predicted = np.log10(y), np.log10(predicted)
    return y, predicted, omitted


def r2_coefficient(y, pred, scale: str):
    y, pred, omitted = _metric_pairs(y, pred, scale)
    if len(y) < 2:
        return float("nan"), len(y), omitted
    denominator = float(np.sum((y - np.mean(y))**2))
    if denominator == 0:
        return float("nan"), len(y), omitted
    return float(1.0 - np.sum((y - pred)**2) / denominator), len(y), omitted


def pearson(y, pred, scale: str):
    y, pred, _ = _metric_pairs(y, pred, scale)
    if len(y) < 2 or np.std(y) == 0 or np.std(pred) == 0:
        return float("nan"), float("nan"), len(y)
    r = float(np.corrcoef(y, pred)[0, 1])
    return r, r * r, len(y)
