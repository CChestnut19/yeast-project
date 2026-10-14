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
    KA: float
    repressor_dbd: str
    repressor_lbd: str
    KR: float

    @property
    def repressor(self):
        return f'{self.repressor_dbd}-{self.repressor_lbd}'


ARCHITECTURES = {
    'A': Architecture('A', 'RpaR179', 1.67, 'LexAbs94', 'LasR177', 40.98),
    'B': Architecture('B', 'ER282-595', 1.13, 'LexAbs94', 'LasR177', 40.98),
    'C': Architecture('C', 'ER282-595', 1.13, 'LexAxa101', 'LasR177', 1.45),
}
PANELS = tuple(f'{letter}{condition}' for letter in 'ABC' for condition in range(1, 5))


def effective_pool(c_TF_all, c_I, parameters):
    dose = np.asarray(c_I, dtype=float)
    if not np.isfinite(dose).all() or np.any(dose < 0):
        raise ValueError('Inducer concentration must be finite and non-negative')
    Kd0, Kb, Kd1 = (parameters[name] for name in ('Kd0', 'Kb', 'Kd1'))
    return cic_dimer_pool(c_TF_all, dose, Kd0, Kb, Kd1)


def predicted_rpu(panel, condition, c_I_x, c_I_series):
    if panel not in PANELS or condition != int(panel[1]) or isinstance(condition, bool):
        raise ValueError(f'Panel and condition must agree: {panel!r}, {condition!r}')
    architecture = ARCHITECTURES[panel[0]]
    c_TF_all_activator, c_TF_all_repressor = FIXED_CTF_ALL[condition]
    c_I_activator, c_I_repressor = (c_I_x, c_I_series) if condition in (1, 2) else (c_I_series, c_I_x)
    activator = effective_pool(c_TF_all_activator, c_I_activator, LBD_PARAMETERS[architecture.activator_lbd])
    repressor = effective_pool(c_TF_all_repressor, c_I_repressor, LBD_PARAMETERS[architecture.repressor_lbd])
    z = architecture.KA * activator
    p_activator = z / (1 + z)
    p_unbound = 1 / (1 + architecture.KR * repressor)
    T0 = REPRESSOR_T0_RPU[architecture.repressor]
    result = T0 + (TMAX_RPU - T0) * p_activator * p_unbound**REPRESSOR_OPERATOR_COUNT
    return float(result) if np.ndim(result) == 0 else result


def model_settings():
    return {'Tmax': TMAX_RPU, 'T0': REPRESSOR_T0_RPU, 'operators': REPRESSOR_OPERATOR_COUNT,
            'lbds': LBD_PARAMETERS, 'c_TF_all': {str(k): list(v) for k, v in FIXED_CTF_ALL.items()},
            'architectures': {key: asdict(value) for key, value in ARCHITECTURES.items()},
            'operator_rule': 'p_activator * p_unbound**n'}
