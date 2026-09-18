"""Note 10: output scales with at least one repressor operator being unbound."""
import numpy as np
from yeast.binding import cic_dimer_pool

K1, K2, K3 = 0.000171923, 0.256016091, 225.0817618
PARAMETERS = {
    'CI94': {'kd': 30.08697891, 'Tmax': 1.62, 'T0': .01, 'n': 2},
    'CI43470': {'kd': 6.216347694, 'Tmax': 2.2, 'T0': .01, 'n': 2},
    'LexAgs91': {'kd': .343528478, 'Tmax': 1.06, 'T0': .01, 'n': 2},
    'LexAbs94': {'kd': 40.97704697, 'Tmax': .66, 'T0': .01, 'n': 2},
}
SENSORS = tuple(PARAMETERS)


def model_components(sensor, total_tf, inducer_um):
    if sensor not in PARAMETERS:
        raise ValueError(f'Unknown repressor sensor: {sensor!r}')
    parameter = PARAMETERS[sensor]
    dose = np.asarray(inducer_um, dtype=float)
    if not np.isfinite(dose).all() or np.any(dose < 0):
        raise ValueError('Inducer concentration must be finite and non-negative')
    d = K1 + K2**2 * K3 * dose**2
    active_pool = cic_dimer_pool(total_tf, dose, K1, K2, K3)
    free_monomer = np.sqrt(active_pool / d)
    p_r = 1.0 / (1.0 + parameter['kd'] * active_pool)
    p_two = 1.0 - (1.0 - p_r)**parameter['n']
    prediction = parameter['T0'] + p_two * (parameter['Tmax'] - parameter['T0'])
    return {'free_monomer': free_monomer, 'active_pool': active_pool,
            'p_r': p_r, 'p_two': p_two, 'prediction': prediction}


def predict(sensor, total_tf, inducer_um):
    value = model_components(sensor, total_tf, inducer_um)['prediction']
    return float(value) if np.ndim(value) == 0 else value


def model_settings():
    return {'K1': K1, 'K2': K2, 'K3': K3, 'sensors': PARAMETERS,
            'operator_rule': '1 - (1 - p_unbound)**n'}
