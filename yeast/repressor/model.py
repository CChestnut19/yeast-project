"""Note 10: output scales with at least one repressor operator being unbound."""
import numpy as np
from yeast.binding import cic_dimer_pool

Kd0, Kb, Kd1 = 0.000171923, 0.256016091, 225.0817618
PARAMETERS = {
    'CI94': {'KR': 30.08697891, 'Tmax': 1.62, 'T0': .01, 'n': 2},
    'CI43470': {'KR': 6.216347694, 'Tmax': 2.2, 'T0': .01, 'n': 2},
    'LexAgs91': {'KR': .343528478, 'Tmax': 1.06, 'T0': .01, 'n': 2},
    'LexAbs94': {'KR': 40.97704697, 'Tmax': .66, 'T0': .01, 'n': 2},
}
SENSORS = tuple(PARAMETERS)


def model_components(sensor, c_TF_all, c_I):
    if sensor not in PARAMETERS:
        raise ValueError(f'Unknown repressor sensor: {sensor!r}')
    parameter = PARAMETERS[sensor]
    dose = np.asarray(c_I, dtype=float)
    if not np.isfinite(dose).all() or np.any(dose < 0):
        raise ValueError('Inducer concentration must be finite and non-negative')
    d = Kd0 + Kb**2 * Kd1 * dose**2
    c_TF_eff = cic_dimer_pool(c_TF_all, dose, Kd0, Kb, Kd1)
    c_TF = np.sqrt(c_TF_eff / d)
    p_unbound = 1.0 / (1.0 + parameter['KR'] * c_TF_eff)
    p_permissive = 1.0 - (1.0 - p_unbound)**parameter['n']
    prediction = parameter['T0'] + p_permissive * (parameter['Tmax'] - parameter['T0'])
    return {'c_TF': c_TF, 'c_TF_eff': c_TF_eff,
            'p_unbound': p_unbound, 'p_permissive': p_permissive, 'prediction': prediction}


def predict(sensor, c_TF_all, c_I):
    value = model_components(sensor, c_TF_all, c_I)['prediction']
    return float(value) if np.ndim(value) == 0 else value


def model_settings():
    return {'Kd0': Kd0, 'Kb': Kb, 'Kd1': Kd1, 'sensors': PARAMETERS,
            'operator_rule': '1 - (1 - p_unbound)**n'}
