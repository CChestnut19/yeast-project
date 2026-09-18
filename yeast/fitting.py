"""Explicit-data historical parameter estimation and least-squares fitting.

The notebook amplitude convention applies even to its historical mammalian
parameter sets. This module does not alter mammalian/Scripts/model_core.py.
"""
import numpy as np
from scipy.optimize import curve_fit, least_squares

from .analysis import response
from .binding import active_dimer_pool


def estimate_kd(baseline, basal_output, k1, *, amplitude=2.5, total_tf=1.0):
    """Invert basal occupancy; parameters_estimate cell 1's solve_kd."""
    fraction = (np.asarray(basal_output)-np.asarray(baseline))/amplitude
    pool = active_dimer_pool(total_tf, 1., k1)
    if np.any((fraction < 0) | (fraction >= 1)) or np.any(pool <= 0):
        raise ValueError("Require a nonsaturated basal fraction and positive basal pool")
    return fraction/(pool*(1-fraction))


def estimate_M_literal(baseline, maximum_output, kd, inducer, *, amplitude=2.5, total_tf=1.0):
    """Retain the notebook's M formula (not an exact mass-balance inversion).

    Algebraically equals fraction/(1-fraction)/kd/(L/2)/I**2. In particular
    this is not k2**2*k3 inferred from the complete response equation.
    """
    fraction = (np.asarray(maximum_output)-np.asarray(baseline))/amplitude
    if (np.any((fraction < 0) | (fraction >= 1)) or np.any(np.asarray(kd) <= 0)
            or np.any(np.asarray(inducer) <= 0) or total_tf <= 0):
        raise ValueError("Require nonsaturated output, kd>0, I>0, total_tf>0")
    return fraction/(1-fraction)/np.asarray(kd)/(total_tf/2)/np.asarray(inducer)**2


def estimate_shared_parameters(table, *, amplitude=2.5, total_tf=1.0):
    """Three-stage grouped heuristic from parameters_estimate (pandas in/out).

    Required columns: ID='DBD-LBD', I0, P0, Pmax, I; or explicit DBD and LBD.
    Returns {'DBD': table, 'LBD': table, 'observations': merged table}.
    """
    import pandas as pd
    data = pd.DataFrame(table).copy()
    if not {'DBD', 'LBD'}.issubset(data.columns):
        split = data['ID'].astype(str).str.split('-', expand=True)
        if split.shape[1] != 2 or split.isna().any().any():
            raise ValueError("ID must contain exactly one '-' or supply DBD and LBD")
        data[['DBD', 'LBD']] = split
    numeric = data[['I0', 'P0', 'Pmax', 'I']].to_numpy(float)
    if not np.isfinite(numeric).all() or amplitude <= 0 or total_tf <= 0:
        raise ValueError("Require finite complete observations and positive amplitude/TF")
    lbds = []
    for name, group in data.groupby('LBD'):
        fraction = (group['P0'].mean()-group['I0'].mean())/amplitude
        if not 0 < fraction < 1 or fraction == .5:
            raise ValueError("Historical k1 estimate is singular or nonphysical for this basal fraction")
        k1 = abs(((1+2*fraction)/(1-2*fraction))**2-1)/(8*total_tf)
        lbds.append({'LBD': name, 'k1': k1})
    lbd = pd.DataFrame(lbds)
    data = data.merge(lbd, on='LBD', validate='many_to_one')
    data['kd'] = estimate_kd(data['I0'], data['P0'], data['k1'],
                              amplitude=amplitude, total_tf=total_tf)
    dbd = data.groupby('DBD', as_index=False)['kd'].mean()
    data = data.drop(columns='kd').merge(dbd, on='DBD', validate='many_to_one')
    data['M'] = estimate_M_literal(data['I0'], data['Pmax'], data['kd'], data['I'],
                                    amplitude=amplitude, total_tf=total_tf)
    lbd = lbd.merge(data.groupby('LBD', as_index=False)['M'].mean(), on='LBD')
    data = data.drop(columns='M').merge(lbd[['LBD', 'M']], on='LBD', validate='many_to_one')
    return {'DBD': dbd, 'LBD': lbd, 'observations': data}


def epsilon_response_literal(L, kd, k1, k2, k3, Imax, I0, I, epsilon=1e-9):
    """NumPy translation of the exact asymmetric epsilon Torch formula, cell 3."""
    L, I = np.asarray(L, float), np.asarray(I, float)
    b = 1+k2*I
    root = np.sqrt(b*b+8*L*(k1+k2**2*k3*I**2)+epsilon)
    numerator = (L/2+epsilon)*((root-b+epsilon)/(root+b)+epsilon)*(kd+epsilon)
    denominator = 1+(L/2+epsilon)*((root-b+epsilon)/(root+b+epsilon)+epsilon)*(kd+epsilon)
    return I0+Imax*numerator/denominator


def _predict(L, I, parameters, variant):
    if variant == 'standard':
        return response(L=L, I=I, **parameters)
    if variant == 'torch_epsilon_literal':
        return epsilon_response_literal(L=L, I=I, **parameters)
    if variant == 'nuclear_clamped':
        parameters = {k: abs(v) if k in {'k1', 'k2', 'k3', 'kd', 'kx1', 'kx2'} else v
                      for k, v in parameters.items()}
        parameters['kx2'] = max(parameters['kx2'], .001)
        return response(L=L, I=I, **parameters)
    raise ValueError("Unknown model variant")


def fit_response(L, I, observed, *, fixed, initial, scale='raw', bounds=None,
                 variant='standard', max_nfev=10000):
    """Fit any selected parameters, with per-observation fixed kd supported.

    scale='raw' minimizes raw SSE (same minimizer as the Torch MSE); log10
    minimizes log10 SSE as shared fixed-kd cell 2. Initial parameter order is
    mapping insertion order; bounds must follow that order. Positive bounds
    replace the notebook's discontinuous 1e10 penalty and invalid-domain fallback.
    Return parameters, predictions, SSE/MSE, Jacobian covariance estimate,
    convergence status and the SciPy result. A failed fit is never hidden.
    """
    L, I, observed = np.asarray(L, float), np.asarray(I, float), np.asarray(observed, float)
    if (L.ndim != 1 or I.shape != L.shape or observed.shape != L.shape or not len(L)
            or not all(np.isfinite(x).all() for x in (L, I, observed))):
        raise ValueError("Require finite equal-length 1D L, I and observed arrays")
    if np.any(L < 0) or np.any(I < 0):
        raise ValueError("Concentrations must be non-negative")
    if scale not in {'raw', 'log10'} or (scale == 'log10' and np.any(observed <= 0)):
        raise ValueError("Use raw or log10 scale, with positive observations for log10")
    if not initial or set(fixed) & set(initial):
        raise ValueError("Supply fitted parameters distinct from fixed parameters")
    names = list(initial)
    x0 = np.asarray([initial[name] for name in names], float)
    if bounds is None:
        bounds = (np.full(len(names), 1e-30), np.full(len(names), np.inf))
    target = np.log10(observed) if scale == 'log10' else observed

    def evaluate(values):
        return _predict(L, I, {**fixed, **dict(zip(names, values))}, variant)

    def residual(values):
        predicted = evaluate(values)
        if scale == 'log10':
            if np.any(predicted <= 0):
                raise ValueError("Log fit produced a nonpositive prediction")
            predicted = np.log10(predicted)
        return predicted-target

    result = least_squares(residual, x0, bounds=bounds, x_scale='jac', max_nfev=max_nfev)
    sse = float(result.fun @ result.fun)
    dof = len(observed)-len(names)
    covariance = (np.linalg.pinv(result.jac.T @ result.jac)*sse/dof
                  if dof > 0 else np.full((len(names), len(names)), np.nan))
    return {'parameters': dict(zip(names, result.x)), 'prediction': evaluate(result.x),
            'SSE': sse, 'MSE': sse/len(observed), 'scale': scale,
            'covariance': covariance, 'success': bool(result.success),
            'message': result.message, 'optimizer': result}


def fit_shared_then_kd(datasets, *, initial_shared, Imax, I0, initial_kd=10.0,
                       variant='standard', max_nfev=10000, warm_start=True):
    """Torch cells 3/4's two-stage objective, using SciPy and explicit dataset IDs.

    First fit shared receptor parameters at fixed kd=initial_kd on all rows;
    then freeze them and fit kd separately in input order. warm_start=True
    retains the notebook's previous-dataset kd initialization. Optimizer paths
    and unconstrained Adam iterates are not claimed to be bitwise reproduced.
    """
    datasets = list(datasets)
    if not datasets or len({d['name'] for d in datasets}) != len(datasets):
        raise ValueError("Provide datasets with distinct names")
    shared = fit_response(np.concatenate([d['L'] for d in datasets]),
                          np.concatenate([d['I'] for d in datasets]),
                          np.concatenate([d['observed'] for d in datasets]),
                          fixed={'kd': initial_kd, 'Imax': Imax, 'I0': I0},
                          initial=initial_shared, variant=variant, max_nfev=max_nfev)
    per_dataset = {}
    kd = initial_kd
    for data in datasets:
        fit = fit_response(data['L'], data['I'], data['observed'],
                           fixed={**shared['parameters'], 'Imax': Imax, 'I0': I0},
                           initial={'kd': kd}, variant=variant, max_nfev=max_nfev)
        per_dataset[data['name']] = fit
        if warm_start:
            kd = fit['parameters']['kd']
    return {'shared': shared, 'datasets': per_dataset,
            'success': shared['success'] and all(f['success'] for f in per_dataset.values())}


def fit_notebook_curve_fit(L, I, observed, *, cell, fixed, initial=None,
                           bounds=None, maxfev=None, fallback_maxfev=9000000000):
    """Preserve parameters_fitting cells 0/1/2's original SciPy procedures.

    cell=0: raw response, k1<10 and k1/k2/k3>0 penalty, bounded curve_fit,
    then unbounded fallback on an exception. cell=1: nuclear raw response,
    positive-parameter penalty, unbounded curve_fit. cell=2: bounded log10
    response with caller-provided fixed kd (scalar or per-observation array).
    Never infer fixed kd from filesystem/glob order. Defaults are original
    initialization, bounds and evaluation limits, which can be expensive.
    """
    L, I, observed = np.asarray(L, float), np.asarray(I, float), np.asarray(observed, float)
    if (L.ndim != 1 or I.shape != L.shape or observed.shape != L.shape or not len(L)
            or not all(np.isfinite(v).all() for v in (L, I, observed))):
        raise ValueError("Require finite paired observation vectors")
    defaults = {
        0: (['k1','k2','k3'], [.1,.1,.1],
            ([1e-20,1e-15,1e-15],[1000,1e12,1e23]), 1000000000),
        1: (['k1','k2','k3','kx1','kx2'], [.001,1,1000000,10,10],
            (-np.inf,np.inf), 1000000000),
        2: (['k1','k2','k3'], [1,1,.1],
            ([1e-17,1e-8,1e-6],[1e12,1e10,1e11]), 500000000),
    }
    if cell not in defaults:
        raise ValueError("Choose historical fitting cell 0, 1 or 2")
    names, p0, source_bounds, source_limit = defaults[cell]
    if set(names) & set(fixed):
        raise ValueError("Fixed and fitted parameters must be distinct")
    if cell == 2 and np.any(observed <= 0):
        raise ValueError("Historical log10 fit requires positive observations")
    p0 = p0 if initial is None else [initial[name] for name in names]
    chosen_bounds = source_bounds if bounds is None else bounds
    chosen_limit = source_limit if maxfev is None else maxfev
    target = np.log10(observed) if cell == 2 else observed

    def forward(x, *values):
        if cell in (0,1) and (any(v <= 0 for v in values) or (cell == 0 and values[0] >= 10)):
            return np.ones_like(x[0])*1e10
        predicted = response(L=x[0], I=x[1], **fixed, **dict(zip(names,values)))
        return np.log10(predicted) if cell == 2 else predicted

    fallback = False
    try:
        parameters,covariance = curve_fit(forward,(L,I),target,p0=p0,
                                           bounds=chosen_bounds,maxfev=chosen_limit)
    except Exception:
        if cell != 0:
            raise
        fallback = True
        parameters,covariance = curve_fit(forward,(L,I),target,p0=p0,maxfev=fallback_maxfev)
    fitted = forward((L,I),*parameters)
    sse = float(np.sum((target-fitted)**2))
    return {'parameters':dict(zip(names,parameters)), 'covariance':covariance,
            'prediction':10**fitted if cell == 2 else fitted,
            'SSE':sse, 'MSE':sse/len(L), 'scale':'log10' if cell == 2 else 'raw',
            'used_unbounded_fallback':fallback}


def fit_shared_then_kd_adam(datasets, *, initial_shared, Imax, I0, initial_kd=10.0,
                            variant='torch_epsilon_literal', shared_steps=100000,
                            kd_steps=150000, learning_rate=.001, max_gradient_norm=5.0):
    """Optional Torch backend preserving source cells 3/4's optimization semantics.

    Requires torch only when called. Uses float32, original epsilon/abs/clamp,
    fixed-kd shared stage, then each dataset's kd stage with warm starts and
    a fresh Adam optimizer. Exactly as the source, zero_grad only clears the
    selected optimizer's parameters and gradient clipping covers ALL model
    parameters; unselected gradients therefore accumulate. This historical
    quirk affects updates and is intentionally retained, not recommended as a
    new fitting method. Algebraic regrouping may change float32 rounding; no
    bitwise trajectory equivalence is claimed. Returned loss is recomputed
    after the final step.
    """
    import torch
    datasets = list(datasets)
    if not datasets or len({d['name'] for d in datasets}) != len(datasets):
        raise ValueError("Provide datasets with distinct names")
    expected = {'k1','k2','k3'} | ({'kx1','kx2'} if variant == 'nuclear_clamped' else set())
    if variant not in {'torch_epsilon_literal','nuclear_clamped'} or set(initial_shared) != expected:
        raise ValueError("Use a source variant and its exact shared parameter names")
    if (int(shared_steps) != shared_steps or int(kd_steps) != kd_steps
            or shared_steps < 0 or kd_steps < 0):
        raise ValueError("Iteration counts must be non-negative integers")
    parameters = {name: torch.nn.Parameter(torch.tensor([float(value)],dtype=torch.float32))
                  for name,value in {**initial_shared,'kd':initial_kd}.items()}
    converted = []
    for data in datasets:
        arrays = [np.asarray(data[key],float) for key in ('L','I','observed')]
        if (arrays[0].ndim != 1 or not len(arrays[0])
                or any(a.shape != arrays[0].shape or not np.isfinite(a).all() for a in arrays)):
            raise ValueError("Require complete paired vectors in each dataset")
        converted.append((data['name'],*(torch.tensor(a,dtype=torch.float32) for a in arrays)))

    def forward(L,I):
        p = parameters
        if variant == 'torch_epsilon_literal':
            b = 1+p['k2']*I
            root = torch.sqrt(b*b+8*L*(p['k1']+p['k2']**2*p['k3']*I**2)+1e-9)
            numerator=(L/2+1e-9)*((root-b+1e-9)/(root+b)+1e-9)*(p['kd']+1e-9)
            denominator=1+(L/2+1e-9)*((root-b+1e-9)/(root+b+1e-9)+1e-9)*(p['kd']+1e-9)
        else:
            k1,k2,k3,kx1,kx2,kd=(torch.abs(p[name]) for name in ('k1','k2','k3','kx1','kx2','kd'))
            kx2=torch.clamp(kx2,min=.001)
            b=1+k2*I+kx1+kx2*k2*I
            root=torch.sqrt(b*b+8*L*(k1+k1*kx1*kx1+k2*k2*k3*I*I*(1+kx2*kx2)))
            numerator=L/2*(root-b)/(root+b)*kd
            denominator=1+numerator
        return I0+Imax*numerator/denominator

    def train(L,I,observed,names,steps):
        optimizer=torch.optim.Adam([parameters[name] for name in names],lr=learning_rate)
        for _ in range(int(steps)):
            optimizer.zero_grad()
            loss=torch.nn.functional.mse_loss(forward(L,I),observed)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(list(parameters.values()),max_norm=max_gradient_norm)
            optimizer.step()
        with torch.no_grad():
            predicted=forward(L,I)
            loss=torch.nn.functional.mse_loss(predicted,observed)
        return {'prediction':predicted.numpy().copy(), 'MSE':float(loss),
                'raw_parameters':{k:float(v.detach()[0]) for k,v in parameters.items()},
                'finite':bool(torch.isfinite(loss))}

    shared=train(*(torch.cat([d[i] for d in converted]) for i in (1,2,3)),
                 list(initial_shared),shared_steps)
    results={name:train(L,I,observed,['kd'],kd_steps) for name,L,I,observed in converted}
    return {'shared':shared,'datasets':results,'variant':variant,
            'finite':shared['finite'] and all(r['finite'] for r in results.values())}
