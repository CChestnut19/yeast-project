"""Numerical models recovered from the root notebooks.

These exploratory equations are distinct from the archived production models.
Functions containing ``literal`` intentionally retain a source inconsistency;
see docs/NOTEBOOK_MIGRATION.md before using them for scientific interpretation.
No files are read and no work is performed on import.
"""
import numpy as np
from scipy.optimize import brentq

from .analysis import response
from .binding import active_dimer_pool


def dimer_response(total_tf, kd, dimer_term, amplitude=1.0, baseline=0.0,
                   linear_term=1.0, *, repressor=False):
    """Reduced mass-balance model used in box and plot6; b is explicit."""
    z = np.asarray(kd) * active_dimer_pool(total_tf, linear_term, dimer_term)
    occupancy = 1 / (1 + z) if repressor else z / (1 + z)
    return baseline + amplitude * occupancy


def monomer_bound_pool(total_tf, association):
    """Hill-1 comparison in box cell 1: K*L/(1+K)."""
    return np.asarray(total_tf) * association / (1 + np.asarray(association))


def quadratic_activation_literal(I, k2, k3):
    """plot4 cell 1's printed scratch expression; I is now an explicit input."""
    weight = (np.asarray(I)*k2)**2+k3
    return weight/(1+weight)


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


def heterodimer_response_pair(total_a, total_b, kd, k1, k2, k3, I,
                              amplitude, baseline_on, baseline_off=None):
    """box cells 4–6: both states use the SAME A*B at K=k2**2*k3.

    I**2 multiplies the induced pool after solving free pools. This is the
    source equation, not the ordinary homodimer response in analysis.py.
    """
    a, b = heterodimer_free_pools(total_a, total_b, k2**2*k3)
    off_baseline = baseline_on if baseline_off is None else baseline_off
    z_on, z_off = kd*k2**2*k3*a*b*np.asarray(I)**2, kd*k1*a*b
    return (baseline_on + amplitude*z_on/(1+z_on),
            off_baseline + amplitude*z_off/(1+z_off))


def two_state_repression(tf, dna_binding, inducer, active_dissociation,
                         inactive_dissociation, allosteric_weight=10.0):
    """box cell 9's literal two-state repression, with explicit parameter names."""
    active = (1 + np.asarray(inducer)/active_dissociation)**2
    inactive = (1 + np.asarray(inducer)/inactive_dissociation)**2
    fraction = active / (active + allosteric_weight*inactive)
    return 1 / (1 + fraction*np.asarray(tf)*dna_binding)


def fixed_induced_root_fold_literal(L, kd, k1, k2, k3, I, amplitude,
                                    baseline=0.001, root_tf=1.0):
    """box cell 10: induced root uses root_tf=1, outside factor still uses L."""
    induced_pool = np.asarray(L)/root_tf * active_dimer_pool(root_tf, 1, k2**2*k3*I**2)
    z = np.asarray(kd)*induced_pool
    on = baseline + amplitude*z/(1+z)
    off = dimer_response(L, kd, k1, amplitude, baseline)
    return on/off


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
                                 delta_epsilon_rd, P, Imax=1.0, beta=1.0/0.6):
    """Imax cancels for a positive reference expression (historical signature)."""
    if np.any(np.asarray(P) <= 0) or Imax <= 0:
        raise ValueError("Fold change requires positive reference expression")
    return (simple_repression_partition_function(0, DBD, N_NS, delta_epsilon_pd,
                                                 delta_epsilon_rd, P, beta) /
            simple_repression_partition_function(R, DBD, N_NS, delta_epsilon_pd,
                                                  delta_epsilon_rd, P, beta))


def rob_phillips_allosteric_dimer_fixed_inducer(R, DBD, N_NS, delta_epsilon_rd,
                                              delta_epsilon_int, K, P,
                                              delta_epsilon_pd, Imax, beta=1.0/0.6):
    """box cell 11's exploratory allosteric expression, source name retained."""
    binding = 2*np.asarray(R)*np.asarray(DBD)/N_NS*np.exp(-beta*delta_epsilon_rd)
    interaction = np.exp(-beta*delta_epsilon_int)
    allosteric = (1+K)**2/(1+K*interaction)**2
    polymerase = P/N_NS*np.exp(-beta*delta_epsilon_pd)
    return Imax*polymerase/(1+polymerase+binding*interaction*allosteric)


def operator_response(L, n, **parameters):
    """Independent n-site activation: baseline + amplitude*(1-(1-p)**n)."""
    n = np.asarray(n)
    if not np.isfinite(n).all() or np.any(n < 1) or np.any(n != np.floor(n)):
        raise ValueError("n must contain positive integers")
    model = dict(parameters)
    amplitude, baseline = model.pop('Imax'), model.pop('I0')
    occupancy = response(L=L, Imax=1.0, I0=0.0, **model)
    with np.errstate(divide='ignore'):
        occupied = -np.expm1(n*np.log1p(-occupancy))
    return baseline + amplitude*occupied


def solve_operator_target(target, n, *, bracket=(1e-5, 100.0), **parameters):
    """Return (TF, multi-site occupancy); unreachable finite target gives NaNs."""
    if not np.isfinite(target) or len(bracket) != 2 or not 0 <= bracket[0] < bracket[1]:
        raise ValueError("Require a finite target and ordered non-negative bracket")
    low = float(operator_response(bracket[0], n, **parameters))-target
    high = float(operator_response(bracket[1], n, **parameters))-target
    if low*high > 0:
        return float('nan'), float('nan')
    value = brentq(lambda L: float(operator_response(L, n, **parameters))-target, *bracket)
    return value, (target-parameters['I0'])/parameters['Imax']


def hybrid_promoter(L_activator, L_repressor, I_activator, I_repressor,
                    activator, repressor, amplitude_activator,
                    amplitude_repressor, baseline):
    """plot7 product gate; activator/repressor mappings hold kd,k1,k2,k3[,kx].

    The two amplitudes multiply; only one baseline is added. This is distinct
    from combinatorial.model's archived promoter conventions.
    """
    a = response(L_activator, I=I_activator, Imax=1., I0=0., **activator)
    r = response(L_repressor, I=I_repressor, Imax=1., I0=0., **repressor)
    return baseline + amplitude_activator*amplitude_repressor*a*(1-r)


def mismatched_tf_crosstalk_literal(L, kd, k1, k21, k22, k31, k32, I,
                                    amplitude=35.84931505, baseline=0.035485714):
    """plot6 cell 12: second root uses kd as TF, but its outside factor uses L."""
    first = response(L, kd, k1, k21, k31, amplitude, baseline, I)
    pool = active_dimer_pool(kd, 1+k22*I, k1+k22**2*k32*I**2)
    # original z=(L/2)*root_ratio*kd = L*pool for kd>0
    z = np.asarray(L)*pool
    second = baseline + amplitude*z/(1+z)
    return second/first
