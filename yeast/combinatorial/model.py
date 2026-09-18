"""Note 11: activator occupancy times the probability BOTH operators are unbound."""
from dataclasses import asdict, dataclass
import numpy as np
from yeast.binding import cic_dimer_pool

TMAX_RPU = 35.85
REPRESSOR_OPERATOR_COUNT = 2
REPRESSOR_T0_RPU = {'LexAbs94-LasR177': .01, 'LexAxa101-LasR177': .01}
LBD_PARAMETERS = {
    'RpaR179': {'Kd0': 2.69e-4, 'Kb': 7.08e-3, 'Kd1': 7.61e-1},
    'ER282-595': {'Kd0': 3.40e-5, 'Kb': 9.08, 'Kd1': 1.01},
    'LasR177': {'Kd0': 1.72e-4, 'Kb': 2.56e-1, 'Kd1': 225.08},
}
FIXED_CTF_ALL = {1: (.49, .21), 2: (8.12, .21), 3: (.49, 4.56), 4: (8.12, 4.56)}


@dataclass(frozen=True)
class Architecture:
    label: str
    activator_lbd: str
    activator_ka: float
    repressor_dbd: str
    repressor_lbd: str
    repressor_kr: float

    @property
    def repressor(self):
        return f'{self.repressor_dbd}-{self.repressor_lbd}'


ARCHITECTURES = {
    'A': Architecture('A', 'RpaR179', 1.67, 'LexAbs94', 'LasR177', 40.98),
    'B': Architecture('B', 'ER282-595', 1.13, 'LexAbs94', 'LasR177', 40.98),
    'C': Architecture('C', 'ER282-595', 1.13, 'LexAxa101', 'LasR177', 1.45),
}
PANELS = tuple(f'{letter}{condition}' for letter in 'ABC' for condition in range(1, 5))


def effective_pool(c_tf, inducer_uM, parameters):
    dose = np.asarray(inducer_uM, dtype=float)
    if not np.isfinite(dose).all() or np.any(dose < 0):
        raise ValueError('Inducer concentration must be finite and non-negative')
    kd0, kb, kd1 = (parameters[name] for name in ('Kd0', 'Kb', 'Kd1'))
    return cic_dimer_pool(c_tf, dose, kd0, kb, kd1)


def predicted_rpu(panel, condition, x_uM, series_uM):
    if panel not in PANELS or condition != int(panel[1]) or isinstance(condition, bool):
        raise ValueError(f'Panel and condition must agree: {panel!r}, {condition!r}')
    architecture = ARCHITECTURES[panel[0]]
    c_activator, c_repressor = FIXED_CTF_ALL[condition]
    activator_dose, repressor_dose = (x_uM, series_uM) if condition in (1, 2) else (series_uM, x_uM)
    activator = effective_pool(c_activator, activator_dose, LBD_PARAMETERS[architecture.activator_lbd])
    repressor = effective_pool(c_repressor, repressor_dose, LBD_PARAMETERS[architecture.repressor_lbd])
    z = architecture.activator_ka * activator
    p_activator = z / (1 + z)
    p_unbound = 1 / (1 + architecture.repressor_kr * repressor)
    t0 = REPRESSOR_T0_RPU[architecture.repressor]
    result = t0 + (TMAX_RPU - t0) * p_activator * p_unbound**REPRESSOR_OPERATOR_COUNT
    return float(result) if np.ndim(result) == 0 else result


def model_settings():
    return {'Tmax': TMAX_RPU, 'T0': REPRESSOR_T0_RPU, 'operators': REPRESSOR_OPERATOR_COUNT,
            'lbds': LBD_PARAMETERS, 'tf_inputs': {str(k): list(v) for k, v in FIXED_CTF_ALL.items()},
            'architectures': {key: asdict(value) for key, value in ARCHITECTURES.items()},
            'operator_rule': 'p_activator * p_unbound**n'}
