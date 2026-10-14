"""Numerical models recovered from the root notebooks.

Homodimer helpers reuse the canonical CIC model. Heterodimer and allosteric
comparison models have distinct physical assumptions and are not CIC fit backends.
No files are read and no work is performed on import.
"""
import numpy as np
from scipy.optimize import brentq

from .analysis import response
from .binding import active_dimer_pool, cic_dimer_pool


def dimer_response(c_TF_all, KA, dimer_term, Tmax_minus_T0=1.0, T0=0.0,
                   linear_term=1.0, *, repressor=False):
    """Reduced mass-balance model used in box and plot6; b is explicit."""
    z = np.asarray(KA) * active_dimer_pool(c_TF_all, linear_term, dimer_term)
    occupancy = 1 / (1 + z) if repressor else z / (1 + z)
    return T0 + Tmax_minus_T0 * occupancy


def monomer_bound_pool(c_TF_all, association):
    """Hill-1 comparison in box cell 1: K*c_TF_all/(1+K)."""
    return np.asarray(c_TF_all) * association / (1 + np.asarray(association))


def heterodimer_free_pools(total_a, total_b, association):
    """Solve A_total=A+K*A*B and B_total=B+K*A*B stably."""
    a, b, k = np.broadcast_arrays(np.asarray(total_a, float),
                                  np.asarray(total_b, float), np.asarray(association, float))
    if any(not np.isfinite(v).all() or np.any(v < 0) for v in (a, b, k)):
        raise ValueError("Heterodimer inputs must be finite and non-negative")
    delta = k * (a - b)
    root = np.sqrt(1 + 2 * k * (a + b) + delta**2)
    # Rationalize separately to preserve each source free-pool root.
    return 2*a / (root + 1 - delta), 2*b / (root + 1 + delta)


def heterodimer_response_pair(total_a, total_b, KA, Kd0, Kb, Kd1, c_I,
                              Tmax_minus_T0, T0_on, T0_off=None):
    """box cells 4–6: both states use the SAME A*B at K=Kb**2*Kd1.

    c_I**2 multiplies the induced pool after solving free pools. This is the
    source equation, not the ordinary homodimer response in analysis.py.
    """
    a, b = heterodimer_free_pools(total_a, total_b, Kb**2*Kd1)
    off_baseline = T0_on if T0_off is None else T0_off
    z_on, z_off = KA*Kb**2*Kd1*a*b*np.asarray(c_I)**2, KA*Kd0*a*b
    return (T0_on + Tmax_minus_T0*z_on/(1+z_on),
            off_baseline + Tmax_minus_T0*z_off/(1+z_off))


def two_state_repression(tf, dna_binding, c_I, active_dissociation,
                         inactive_dissociation, allosteric_weight=10.0):
    """box cell 9's literal two-state repression, with explicit parameter names."""
    active = (1 + np.asarray(c_I)/active_dissociation)**2
    inactive = (1 + np.asarray(c_I)/inactive_dissociation)**2
    fraction = active / (active + allosteric_weight*inactive)
    return 1 / (1 + fraction*np.asarray(tf)*dna_binding)


def simple_repression_partition_function(R, DBD, N_NS, delta_epsilon_pd,
                                         delta_epsilon_rd, P, beta=1.0/0.6):
    """box cell 12 partition function; effective R=R*DBD/(1+DBD)."""
    rnap = (np.asarray(P)/N_NS)*np.exp(-beta*delta_epsilon_pd)
    effective_r = np.asarray(R)*np.asarray(DBD)/(1+np.asarray(DBD))
    repressor = 2*effective_r/N_NS*np.exp(-beta*delta_epsilon_rd)
    return 1 + rnap + repressor


def simple_repression_pbound(R, DBD, N_NS, delta_epsilon_pd,
                             delta_epsilon_rd, P, beta=1.0/0.6):
    z = simple_repression_partition_function(R, DBD, N_NS, delta_epsilon_pd,
                                             delta_epsilon_rd, P, beta)
    return (np.asarray(P)/N_NS)*np.exp(-beta*delta_epsilon_pd)/z


def simple_repression_foldchange(R, DBD, N_NS, delta_epsilon_pd,
                                 delta_epsilon_rd, P, Tmax_minus_T0=1.0, beta=1.0/0.6):
    """Tmax_minus_T0 cancels for a positive reference expression (historical signature)."""
    if np.any(np.asarray(P) <= 0) or Tmax_minus_T0 <= 0:
        raise ValueError("Fold change requires positive reference expression")
    return (simple_repression_partition_function(0, DBD, N_NS, delta_epsilon_pd,
                                                 delta_epsilon_rd, P, beta) /
            simple_repression_partition_function(R, DBD, N_NS, delta_epsilon_pd,
                                                  delta_epsilon_rd, P, beta))


def rob_phillips_allosteric_dimer_fixed_inducer(R, DBD, N_NS, delta_epsilon_rd,
                                              delta_epsilon_int, K, P,
                                              delta_epsilon_pd, Tmax_minus_T0, beta=1.0/0.6):
    """box cell 11's exploratory allosteric expression, source name retained."""
    binding = 2*np.asarray(R)*np.asarray(DBD)/N_NS*np.exp(-beta*delta_epsilon_rd)
    interaction = np.exp(-beta*delta_epsilon_int)
    allosteric = (1+K)**2/(1+K*interaction)**2
    polymerase = P/N_NS*np.exp(-beta*delta_epsilon_pd)
    return Tmax_minus_T0*polymerase/(1+polymerase+binding*interaction*allosteric)


def operator_response(c_TF_all, n, **parameters):
    """Independent n-site activation: T0 + Tmax_minus_T0*(1-(1-p)**n)."""
    n = np.asarray(n)
    if not np.isfinite(n).all() or np.any(n < 1) or np.any(n != np.floor(n)):
        raise ValueError("n must contain positive integers")
    model = dict(parameters)
    Tmax_minus_T0, T0 = model.pop('Tmax_minus_T0'), model.pop('T0')
    occupancy = response(c_TF_all=c_TF_all, Tmax_minus_T0=1.0, T0=0.0, **model)
    with np.errstate(divide='ignore'):
        occupied = -np.expm1(n*np.log1p(-occupancy))
    return T0 + Tmax_minus_T0*occupied


def solve_operator_target(target, n, *, bracket=(1e-5, 100.0), **parameters):
    """Return (TF, multi-site occupancy); unreachable finite target gives NaNs."""
    if not np.isfinite(target) or len(bracket) != 2 or not 0 <= bracket[0] < bracket[1]:
        raise ValueError("Require a finite target and ordered non-negative bracket")
    low = float(operator_response(bracket[0], n, **parameters))-target
    high = float(operator_response(bracket[1], n, **parameters))-target
    if low*high > 0:
        return float('nan'), float('nan')
    value = brentq(lambda c_TF_all: float(operator_response(c_TF_all, n, **parameters))-target, *bracket)
    return value, (target-parameters['T0'])/parameters['Tmax_minus_T0']


def hybrid_promoter(c_TF_all_activator, c_TF_all_repressor, c_I_activator, c_I_repressor,
                    activator, repressor, Tmax, T0=.01, operators=2):
    """Note 11 gate: T0 + (Tmax-T0)*p_activator*p_unbound**operators.

    Activator holds KA and repressor holds KR; both hold Kd0/Kb/Kd1.
    Optional Kx1/Kx2 retain the historical transport model. Tmax is the total
    ceiling, not the product of two historical notebook amplitudes.
    """
    if (not np.isfinite(Tmax) or not np.isfinite(T0) or not 0 <= T0 < Tmax
            or isinstance(operators, bool) or operators < 1 or int(operators) != operators):
        raise ValueError('Require 0 <= T0 < Tmax and a positive integer operator count')
    a = response(c_TF_all_activator, c_I=c_I_activator, Tmax_minus_T0=1., T0=0., **activator)
    r = dict(repressor)
    KR = r.pop('KR')
    if not np.isfinite(KR) or KR < 0:
        raise ValueError('Repressor KR must be finite and non-negative')
    pool = cic_dimer_pool(c_TF_all_repressor, c_I_repressor, **r)
    unbound = 1/(1+KR*pool)
    return T0 + (Tmax-T0)*a*unbound**operators


def crosstalk_ratio(c_TF_all, KA, Kd0, Kb_1, Kb_2, Kd1_1, Kd1_2, c_I,
                    Tmax_minus_T0=35.84931505, T0=0.035485714):
    """Second/first canonical response at the same TF and c_I concentrations."""
    first = response(c_TF_all, KA, Kd0, Kb_1, Kd1_1, Tmax_minus_T0, T0, c_I)
    second = response(c_TF_all, KA, Kd0, Kb_2, Kd1_2, Tmax_minus_T0, T0, c_I)
    if np.any(first <= 0):
        raise ValueError('Crosstalk ratio requires a positive reference response')
    return second/first
