"""Canonical yeast inversions and log10 R-squared parameter fitting.

Imax is an amplitude: the total ceiling is I0 + Imax. All optimizers minimize
an equal-dataset mean of 1 - R2(log10 response). Notebook values are provenance.
"""
import numpy as np
from scipy.optimize import curve_fit, least_squares

from .analysis import response
from .binding import active_dimer_pool


def _fraction(baseline, output, amplitude):
    baseline, output, amplitude = np.broadcast_arrays(
        np.asarray(baseline, float), np.asarray(output, float), np.asarray(amplitude, float))
    if (not all(np.isfinite(v).all() for v in (baseline, output, amplitude))
            or np.any(baseline < 0) or np.any(amplitude <= 0)):
        raise ValueError('Require finite nonnegative baseline and positive amplitude')
    fraction = (output-baseline)/amplitude
    if np.any((fraction < 0) | (fraction >= 1)):
        raise ValueError('Output must lie between baseline and the unsaturated ceiling')
    return fraction


def estimate_kd(baseline, basal_output, k1, *, amplitude=2.5, total_tf=1.0):
    """Exactly invert basal occupancy for known k1 and no nuclear partitioning."""
    fraction = _fraction(baseline, basal_output, amplitude)
    pool = active_dimer_pool(total_tf, 1., k1)
    if np.any(pool <= 0):
        raise ValueError('Require a positive basal dimer pool')
    return fraction/(pool*(1-fraction))


def estimate_M(baseline, maximum_output, kd, inducer, *, k1, k2,
               amplitude=2.5, total_tf=1.0):
    """Invert the full mass balance for M = k2**2 * k3, without nuclear terms.

    Known k1 and k2 are required. The inferred pool must be below L/2 and
    the resulting dimer term must be at least k1.
    """
    fraction = _fraction(baseline, maximum_output, amplitude)
    kd, inducer, k1, k2, total_tf = (np.asarray(v, float) for v in (kd, inducer, k1, k2, total_tf))
    if (not all(np.isfinite(v).all() for v in (kd, inducer, k1, k2, total_tf))
            or any(np.any(v <= 0) for v in (kd, inducer, k2, total_tf)) or np.any(k1 < 0)):
        raise ValueError('Require finite kd, I, k2, TF > 0 and k1 >= 0')
    pool = fraction/(kd*(1-fraction))
    if np.any(2*pool >= total_tf):
        raise ValueError('Output requires an unreachable dimer pool at this total TF')
    monomer = (total_tf-2*pool)/(1+k2*inducer)
    M = (pool/monomer**2-k1)/inducer**2
    # Baseline subtraction can amplify rounding when the induced pool is tiny.
    # An output indistinguishable (within eight ULPs) from the exact k3=0
    # boundary represents M=0; materially lower outputs remain invalid.
    zero_output = response(total_tf, kd, k1, k2, 0., amplitude, baseline, inducer)
    boundary_tolerance = 8*np.spacing(np.maximum(np.abs(maximum_output), np.abs(zero_output)))
    M = np.where(np.abs(np.asarray(maximum_output)-zero_output) <= boundary_tolerance, 0., M)
    if not np.isfinite(M).all() or np.any(M < 0):
        raise ValueError('Output is incompatible with a nonnegative induced dimer term')
    return M


def estimate_shared_parameters(table, *, fixed_lbd, amplitude=2.5, total_tf=1.0):
    """Summarize exact inversions as initialization, not an optimized fit.

    table requires I0, P0, Pmax, I and either DBD/LBD or ID='DBD-LBD'.
    fixed_lbd maps each LBD to known {'k1': value, 'k2': value}. Basal kd
    inversions are averaged by DBD, then exact M inversions by LBD. Averages
    need not reproduce noisy observations; use a fitting API for that.
    """
    import pandas as pd
    data = pd.DataFrame(table).copy()
    if not {'DBD', 'LBD'}.issubset(data.columns):
        split = data['ID'].astype(str).str.split('-', expand=True)
        if split.shape[1] != 2 or split.isna().any().any() or (split == '').any().any():
            raise ValueError("ID must contain exactly one '-' or supply DBD and LBD")
        data[['DBD', 'LBD']] = split
    if data.empty or data[['DBD', 'LBD']].isna().any().any():
        raise ValueError('Require nonempty observations with explicit dataset identities')
    numeric = data[['I0', 'P0', 'Pmax', 'I']].to_numpy(float)
    if not np.isfinite(numeric).all():
        raise ValueError('Require finite complete observations')
    rows = []
    for name in data['LBD'].unique():
        if name not in fixed_lbd or set(fixed_lbd[name]) != {'k1', 'k2'}:
            raise ValueError('Supply known k1 and k2 for every LBD')
        rows.append({'LBD': name, **fixed_lbd[name]})
    lbd = pd.DataFrame(rows)
    data = data.merge(lbd, on='LBD', validate='many_to_one')
    data['kd'] = estimate_kd(data['I0'], data['P0'], data['k1'], amplitude=amplitude, total_tf=total_tf)
    dbd = data.groupby('DBD', as_index=False)['kd'].mean()
    data = data.drop(columns='kd').merge(dbd, on='DBD', validate='many_to_one')
    data['M'] = estimate_M(data['I0'], data['Pmax'], data['kd'], data['I'],
                          k1=data['k1'], k2=data['k2'], amplitude=amplitude, total_tf=total_tf)
    lbd = lbd.merge(data.groupby('LBD', as_index=False)['M'].mean(), on='LBD')
    data = data.drop(columns='M').merge(lbd[['LBD', 'M']], on='LBD', validate='many_to_one')
    return {'DBD': dbd, 'LBD': lbd, 'observations': data}


def _observations(L, I, observed, groups=None):
    L, I, observed = (np.asarray(v, float) for v in (L, I, observed))
    if (L.ndim != 1 or I.shape != L.shape or observed.shape != L.shape or len(L) < 2
            or not all(np.isfinite(v).all() for v in (L, I, observed))
            or np.any(L < 0) or np.any(I < 0) or np.any(observed <= 0)):
        raise ValueError('Require finite paired vectors, nonnegative L/I and positive observations')
    labels = np.zeros(len(L), dtype=int) if groups is None else np.asarray(groups, dtype=object)
    if labels.shape != L.shape:
        raise ValueError('groups must supply one dataset identity per observation')
    indices = {}
    for index, label in enumerate(labels):
        if (label is None or not isinstance(label, (str, int, float, np.integer, np.floating))
                or (not isinstance(label, str) and not np.isfinite(label))):
            raise ValueError('Dataset identities must be nonmissing strings or finite numbers')
        indices.setdefault(label, []).append(index)
    target = np.log10(observed)
    groups_info = {}
    weights = np.empty(len(L))
    for label, index_list in indices.items():
        index = np.asarray(index_list)
        values = target[index]
        sst = float(np.sum((values-values.mean())**2))
        if len(index) < 2 or np.ptp(values) == 0 or not np.isfinite(sst) or sst <= 0:
            raise ValueError('Every dataset needs at least two nonconstant log10 observations')
        groups_info[label] = (index, sst)
        weights[index] = 1/np.sqrt(len(indices)*sst)
    return L, I, observed, target, weights, groups_info


def _metrics(observed, prediction, groups_info):
    prediction = np.asarray(prediction, float)
    if prediction.shape != observed.shape or not np.isfinite(prediction).all() or np.any(prediction <= 0):
        raise ValueError('Log10 fitting requires finite positive predictions')
    target = np.log10(observed)
    errors = np.log10(prediction)-target
    sse = float(errors @ errors)
    group_metrics = {}
    for label, (index, sst) in groups_info.items():
        group_sse = float(errors[index] @ errors[index])
        group_metrics[label] = {'n': len(index), 'SSE_log10': group_sse, 'SST_log10': sst,
                                'R2_log10': 1-group_sse/sst}
    objective = float(np.mean([v['SSE_log10']/v['SST_log10'] for v in group_metrics.values()]))
    # Common rescaling preserves raw R2 while avoiding squared-value underflow.
    raw_scale = float(np.max(observed))
    raw_observed = observed/raw_scale
    raw_sst = float(np.sum((raw_observed-raw_observed.mean())**2))
    with np.errstate(over='ignore', invalid='ignore'):
        raw_r2 = 1-float(np.sum((prediction/raw_scale-raw_observed)**2))/raw_sst
    return {'prediction': prediction, 'scale': 'log10', 'objective_total': objective,
            'R2_log10': 1-sse/float(np.sum((target-target.mean())**2)),
            'macro_R2_log10': 1-objective, 'group_metrics': group_metrics,
            'SSE': sse, 'MSE': sse/len(observed),
            'raw_R2': raw_r2,
            'finite': bool(np.isfinite(objective))}


def _parameters(fixed, initial, bounds=None, variant='standard'):
    if variant != 'standard':
        raise ValueError("Only variant='standard' is supported; supply kx1/kx2 for the nuclear model")
    required = {'kd', 'k1', 'k2', 'k3', 'Imax', 'I0'}
    supplied = set(fixed) | set(initial)
    if (not initial or set(fixed) & set(initial) or not required.issubset(supplied)
            or supplied-required-{'kx1', 'kx2'}):
        raise ValueError('Supply distinct fixed/fitted parameters of the canonical response')
    names = list(initial)
    x0 = np.asarray([initial[name] for name in names], float)
    if x0.shape != (len(names),) or not np.isfinite(x0).all() or np.any(x0 < 0):
        raise ValueError('Initial fitted parameters must be finite nonnegative scalars')
    for value in fixed.values():
        array = np.asarray(value, float)
        if not np.isfinite(array).all() or np.any(array < 0):
            raise ValueError('Fixed parameters must be finite and nonnegative')
    bounds = (0., np.inf) if bounds is None else bounds
    lower, upper = (np.broadcast_to(np.asarray(v, float), x0.shape).copy() for v in bounds)
    if (not np.isfinite(lower).all() or np.isnan(upper).any() or np.any(lower < 0)
            or np.any(upper <= lower) or np.any(x0 < lower) or np.any(x0 > upper)):
        raise ValueError('Bounds must preserve nonnegative parameter meanings and contain the initial values')
    return names, x0, (lower, upper)


def fit_response(L, I, observed, *, fixed, initial, scale='log10', bounds=None,
                 groups=None, variant='standard', max_nfev=10000):
    """Fit selected parameters by minimizing mean_dataset(1 - R2_log10).

    groups identifies each observation's dataset; None means one dataset.
    Each dataset has equal weight regardless of its row count or log variance.
    SSE/MSE are unweighted log10 diagnostics; raw_R2 is diagnostic only.
    R2_log10 is pooled, while macro_R2_log10 equals 1-objective_total.
    Bounds follow initial's insertion order. A failed fit is never hidden.
    """
    if scale != 'log10':
        raise ValueError("Parameter fitting only supports scale='log10'")
    L, I, observed, target, weights, groups_info = _observations(L, I, observed, groups)
    names, x0, bounds = _parameters(fixed, initial, bounds, variant)

    def evaluate(values):
        predicted = response(L=L, I=I, **fixed, **dict(zip(names, values)))
        if not np.isfinite(predicted).all() or np.any(predicted <= 0):
            raise ValueError('Log10 fitting requires finite positive predictions')
        return predicted

    def residual(values):
        return (np.log10(evaluate(values))-target)*weights

    result = least_squares(residual, x0, bounds=bounds, x_scale='jac', max_nfev=max_nfev)
    metrics = _metrics(observed, evaluate(result.x), groups_info)
    dof = len(observed)-len(names)
    covariance = (np.linalg.pinv(result.jac.T @ result.jac)*metrics['objective_total']/dof
                  if dof > 0 else np.full((len(names), len(names)), np.nan))
    return {**metrics, 'parameters': dict(zip(names, result.x)), 'covariance': covariance,
            'success': bool(result.success and metrics['finite']), 'message': result.message,
            'optimizer': result}


def _datasets(datasets):
    datasets = list(datasets)
    if not datasets or len({d['name'] for d in datasets}) != len(datasets):
        raise ValueError('Provide datasets with distinct names')
    normalized = []
    for data in datasets:
        L, I, y, _, _, _ = _observations(data['L'], data['I'], data['observed'])
        normalized.append({'name': data['name'], 'L': L, 'I': I, 'observed': y})
    return normalized


def fit_shared_then_kd(datasets, *, initial_shared, Imax, I0, initial_kd=10.0,
                       variant='standard', max_nfev=10000, warm_start=True):
    """Fit shared receptor parameters with fixed kd, then each dataset's kd.

    Both stages use the canonical response and log10 R-squared objective.
    The shared stage averages per-dataset normalized errors equally.
    """
    datasets = _datasets(datasets)
    shared = fit_response(np.concatenate([d['L'] for d in datasets]),
                          np.concatenate([d['I'] for d in datasets]),
                          np.concatenate([d['observed'] for d in datasets]),
                          fixed={'kd': initial_kd, 'Imax': Imax, 'I0': I0},
                          initial=initial_shared, variant=variant, max_nfev=max_nfev,
                          groups=[d['name'] for d in datasets for _ in d['L']])
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
            'finite': shared['finite'] and all(f['finite'] for f in per_dataset.values()),
            'success': shared['success'] and all(f['success'] for f in per_dataset.values())}


def fit_notebook_curve_fit(L, I, observed, *, cell, fixed, initial=None,
                           bounds=None, groups=None, maxfev=None):
    """Use SciPy curve_fit with the canonical log10 R-squared objective.

    Cell 0/2 select k1/k2/k3; cell 1 also fits kx1/kx2. Notebook starts and
    valid finite lower bounds are retained; invalid penalties and unbounded
    fallbacks are removed. sigma implements equal per-dataset normalization.
    """
    defaults = {
        0: (['k1', 'k2', 'k3'], [.1, .1, .1], ([1e-20, 1e-15, 1e-15], [1000, 1e12, 1e23])),
        1: (['k1', 'k2', 'k3', 'kx1', 'kx2'], [.001, 1, 1000000, 10, 10], (0., np.inf)),
        2: (['k1', 'k2', 'k3'], [1, 1, .1], ([1e-17, 1e-8, 1e-6], [1e12, 1e10, 1e11])),
    }
    if cell not in defaults:
        raise ValueError('Choose fitting cell 0, 1 or 2')
    names, p0, source_bounds = defaults[cell]
    initial = dict(zip(names, p0)) if initial is None else initial
    if set(initial) != set(names):
        raise ValueError('Initial parameters must match the selected fitting cell')
    initial = {name: initial[name] for name in names}
    names, p0, bounds = _parameters(fixed, initial, source_bounds if bounds is None else bounds)
    L, I, observed, target, weights, groups_info = _observations(L, I, observed, groups)

    def forward(x, *values):
        prediction = response(L=x[0], I=x[1], **fixed, **dict(zip(names, values)))
        if not np.isfinite(prediction).all() or np.any(prediction <= 0):
            raise ValueError('Log10 fitting requires finite positive predictions')
        return np.log10(prediction)

    parameters, covariance, info, message, status = curve_fit(
        forward, (L, I), target, p0=p0, bounds=bounds, sigma=1/weights,
        maxfev=10000 if maxfev is None else maxfev, x_scale='jac', full_output=True)
    prediction = response(L=L, I=I, **fixed, **dict(zip(names, parameters)))
    metrics = _metrics(observed, prediction, groups_info)
    return {**metrics, 'parameters': dict(zip(names, parameters)), 'covariance': covariance,
            'success': bool(status in (1, 2, 3, 4) and metrics['finite']),
            'message': message, 'optimizer': 'scipy.optimize.curve_fit', 'optimizer_info': info}


def fit_shared_then_kd_adam(datasets, *, initial_shared, Imax, I0, initial_kd=10.0,
                            variant='standard', shared_steps=100000, kd_steps=150000,
                            learning_rate=.001, max_gradient_norm=5.0, warm_start=True,
                            gradient_tolerance=1e-7):
    """Optional float64 Adam fitting of the same canonical log10 objective.

    Positive parameters are represented by their natural logarithms; returned
    parameters retain their physical meanings. No epsilon, abs or clamp
    changes the response. Only active-stage parameters receive gradients.
    finite reports numerical validity; success requires gradient convergence,
    and exhausting a step budget is explicitly reported as non-convergence.
    """
    import torch
    datasets = _datasets(datasets)
    names, initial, _ = _parameters({'kd': initial_kd, 'Imax': Imax, 'I0': I0},
                                    initial_shared, variant=variant)
    if (np.any(initial <= 0) or not np.isfinite(initial_kd) or initial_kd <= 0
            or any(not np.isfinite(v) or v <= 0 for v in (learning_rate, max_gradient_norm, gradient_tolerance))):
        raise ValueError('Adam initial parameters, kd, learning rate and tolerances must be positive')
    if not all(isinstance(v, (int, np.integer)) and v >= 0 for v in (shared_steps, kd_steps)):
        raise ValueError('Iteration counts must be nonnegative integers')
    parameters = {name: torch.nn.Parameter(torch.tensor(np.log(float(value)), dtype=torch.float64))
                  for name, value in {**initial_shared, 'kd': initial_kd}.items()}

    def values():
        return {name: torch.exp(value) for name, value in parameters.items()}

    def forward(L, I):
        p = values()
        kx1, kx2 = p.get('kx1', 0.), p.get('kx2', 0.)
        b = 1+kx1+p['k2']*I*(1+kx2)
        d = p['k1']*(1+kx1**2)+p['k2']**2*p['k3']*I**2*(1+kx2**2)
        monomer = 2*L/(b+torch.sqrt(b*b+8*d*L))
        z = p['kd']*d*monomer**2
        return I0+Imax*z/(1+z)

    def train(L, I, observed, active, steps, groups=None):
        L, I, observed, target, weights, groups_info = _observations(L, I, observed, groups)
        L, I, target, weights = (torch.tensor(v, dtype=torch.float64) for v in (L, I, target, weights))
        for name, parameter in parameters.items():
            parameter.requires_grad_(name in active)
            parameter.grad = None
        selected = [parameters[name] for name in active]
        optimizer = torch.optim.Adam(selected, lr=learning_rate)
        updates = 0
        converged = False
        gradient_norm = np.inf
        for step in range(steps+1):
            optimizer.zero_grad(set_to_none=True)
            predicted = forward(L, I)
            loss = torch.sum(((torch.log10(predicted)-target)*weights)**2)
            if not bool(torch.isfinite(loss)) or not bool(torch.all(predicted > 0)):
                raise FloatingPointError('Adam produced a nonfinite log10 objective or invalid response')
            loss.backward()
            gradient_norm = float(torch.linalg.vector_norm(torch.stack([p.grad.detach() for p in selected])))
            if not np.isfinite(gradient_norm):
                raise FloatingPointError('Adam produced a nonfinite gradient')
            if gradient_norm <= gradient_tolerance:
                converged = True
                break
            if step == steps:
                break
            torch.nn.utils.clip_grad_norm_(selected, max_norm=max_gradient_norm)
            optimizer.step()
            updates += 1
        metrics = _metrics(observed, predicted.detach().numpy().copy(), groups_info)
        fitted = {name: float(value.detach()) for name, value in values().items()}
        metrics['finite'] = metrics['finite'] and all(np.isfinite(v) and v > 0 for v in fitted.values())
        return {**metrics, 'parameters': {name: fitted[name] for name in active},
                'model_parameters': fitted, 'converged': converged,
                'success': bool(converged and metrics['finite']), 'steps': updates,
                'gradient_norm': gradient_norm,
                'message': 'Gradient tolerance reached' if converged else 'Step budget exhausted'}

    shared = train(*(np.concatenate([d[key] for d in datasets]) for key in ('L', 'I', 'observed')),
                   names, shared_steps, groups=[d['name'] for d in datasets for _ in d['L']])
    results = {}
    for data in datasets:
        if not warm_start:
            with torch.no_grad():
                parameters['kd'].fill_(np.log(initial_kd))
        results[data['name']] = train(data['L'], data['I'], data['observed'], ['kd'], kd_steps)
    return {'shared': shared, 'datasets': results, 'variant': 'standard',
            'finite': shared['finite'] and all(r['finite'] for r in results.values()),
            'success': shared['success'] and all(r['success'] for r in results.values())}
