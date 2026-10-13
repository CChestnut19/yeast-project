"""Fit one LBD using SciPy curve_fit while keeping DBD kd fixed."""

import numpy as np
from scipy.optimize import curve_fit


def _model(inputs, k1, k2, k3):
    L, inducer, Imax, kd, I0 = inputs
    x1 = np.sqrt(
        (k2 * inducer + 1) ** 2
        + 8 * L * (k2**2 * k3 * inducer**2 + k1)
    )
    ratio = (x1 - (k2 * inducer + 1)) / (x1 + (k2 * inducer + 1))
    occupied = (L / 2) * ratio * kd
    return Imax * occupied / (1 + occupied) + I0


def _array(dataframe, column, default=None):
    if column in dataframe.columns:
        series = dataframe[column]
        if default is not None:
            series = series.fillna(default)
        return series.to_numpy(dtype=float)
    if default is None:
        raise ValueError(f"Fitting data is missing column {column}")
    return np.full(len(dataframe), default, dtype=float)


def cal(LBDName, SperLBDData, I0_val, Imax_val):
    if SperLBDData.empty:
        raise ValueError(f"No fitting rows for LBD {LBDName}")

    inputs = (
        _array(SperLBDData, "LBD"),
        _array(SperLBDData, "inducer"),
        _array(SperLBDData, "Imax", Imax_val),
        _array(SperLBDData, "kd"),
        _array(SperLBDData, "I0", I0_val),
    )
    target = _array(SperLBDData, "RPU")
    params, _ = curve_fit(
        _model,
        inputs,
        target,
        p0=(0.1, 0.1, 0.1),
        bounds=(1e-12, np.inf),
        maxfev=500000,
    )
    return params.tolist()
