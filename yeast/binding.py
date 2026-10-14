"""Mass conservation shared by yeast models with different response windows."""
import numpy as np


def active_dimer_pool(c_TF_all, linear_term, dimer_term):
    """Return d*m**2 for c_TF_all = b*m + 2*d*m**2, without cancellation."""
    c_TF_all, linear_term, dimer_term = np.broadcast_arrays(
        np.asarray(c_TF_all, dtype=float), np.asarray(linear_term, dtype=float),
        np.asarray(dimer_term, dtype=float))
    if (not all(np.isfinite(x).all() for x in (c_TF_all, linear_term, dimer_term))
            or np.any(c_TF_all < 0) or np.any(linear_term <= 0) or np.any(dimer_term < 0)):
        raise ValueError("Mass-balance inputs must be finite: TF >= 0, b > 0, d >= 0")
    root = np.sqrt(linear_term**2 + 8.0 * dimer_term * c_TF_all)
    return dimer_term * np.square(2.0 * c_TF_all / (linear_term + root))


def cic_dimer_pool(c_TF_all, c_I, Kd0, Kb, Kd1, Kx1=0.0, Kx2=0.0):
    """Canonical CIC pool using the SI coefficients Kd0, Kb and Kd1.

    Historical nuclear transport adds Kx1/Kx2 terms; zero transport gives the ordinary model.
    Concentrations must use the units associated with the selected parameters.
    """
    c_I, Kd0, Kb, Kd1, Kx1, Kx2 = (
        np.asarray(value, dtype=float) for value in (c_I, Kd0, Kb, Kd1, Kx1, Kx2))
    if any(not np.isfinite(value).all() or np.any(value < 0)
           for value in (c_I, Kd0, Kb, Kd1, Kx1, Kx2)):
        raise ValueError('CIC parameters and c_I must be finite and non-negative')
    return active_dimer_pool(
        c_TF_all, 1.0 + Kx1 + Kb * c_I * (1.0 + Kx2),
        Kd0 * (1.0 + Kx1**2) + Kb**2 * Kd1 * c_I**2 * (1.0 + Kx2**2))
