"""Mass conservation shared by yeast models with different response windows."""
import numpy as np


def active_dimer_pool(total_tf, linear_term, dimer_term):
    """Return d*m**2 for total_tf = b*m + 2*d*m**2, without cancellation."""
    total_tf, linear_term, dimer_term = np.broadcast_arrays(
        np.asarray(total_tf, dtype=float), np.asarray(linear_term, dtype=float),
        np.asarray(dimer_term, dtype=float))
    if (not all(np.isfinite(x).all() for x in (total_tf, linear_term, dimer_term))
            or np.any(total_tf < 0) or np.any(linear_term <= 0) or np.any(dimer_term < 0)):
        raise ValueError("Mass-balance inputs must be finite: TF >= 0, b > 0, d >= 0")
    root = np.sqrt(linear_term**2 + 8.0 * dimer_term * total_tf)
    return dimer_term * np.square(2.0 * total_tf / (linear_term + root))


def cic_dimer_pool(total_tf, inducer, k1, k2, k3, kx1=0.0, kx2=0.0):
    """Canonical CIC pool; k1/k2/k3 correspond to Kd0/Kb/Kd1.

    Nuclear transport adds kx terms; zero transport gives the ordinary model.
    Concentrations must use the units associated with the selected parameters.
    """
    inducer, k1, k2, k3, kx1, kx2 = (
        np.asarray(value, dtype=float) for value in (inducer, k1, k2, k3, kx1, kx2))
    if any(not np.isfinite(value).all() or np.any(value < 0)
           for value in (inducer, k1, k2, k3, kx1, kx2)):
        raise ValueError('CIC parameters and inducer must be finite and non-negative')
    return active_dimer_pool(
        total_tf, 1.0 + kx1 + k2 * inducer * (1.0 + kx2),
        k1 * (1.0 + kx1**2) + k2**2 * k3 * inducer**2 * (1.0 + kx2**2))
