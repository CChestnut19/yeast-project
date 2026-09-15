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
