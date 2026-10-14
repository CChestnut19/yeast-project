"""Load explicitly selected historical parameter sets; never mix source cells."""
import json
from pathlib import Path


_SOURCE_NAMES = {
    'L': 'c_TF_all', 'I': 'c_I', 'kd': 'KA', 'k1': 'Kd0',
    'k2': 'Kb', 'k3': 'Kd1', 'I0': 'T0', 'Imax': 'Tmax_minus_T0',
    'kx1': 'Kx1', 'kx2': 'Kx2',
    'L1': 'c_TF_all_1', 'I1': 'c_I_1', 'I2': 'c_I_2', 'I3': 'c_I_3',
    'I0s': 'T0_values', 'kds': 'KA_values', 'KD_VALUES': 'KA_values',
    'k1s': 'Kd0_values', 'k2s': 'Kb_values', 'k3s': 'Kd1_values',
    'kx1s': 'Kx1_values', 'kx2s': 'Kx2_values',
    'sensor_k1': 'Kd0_by_sensor', 'sensor_k2': 'Kb_by_sensor',
    'sensor_k3': 'Kd1_by_sensor', 'sensor_I': 'c_I_by_sensor',
    'nuclear_kx1': 'Kx1_by_sensor', 'nuclear_kx2': 'Kx2_by_sensor',
    'k_params': 'LBD_coefficients',
    **{f'kd{i}': f'KA_{i}' for i in range(1, 15)},
}
# Separate comparison models reuse source symbols with different physical roles.
_HYBRID_NAMES = {
    'k11': 'Kd0_activator', 'k21': 'Kb_activator', 'k31': 'Kd1_activator',
    'kd1': 'KA', 'k12': 'Kd0_repressor', 'k22': 'Kb_repressor',
    'k32': 'Kd1_repressor', 'kd2': 'KR',
    'Imax1': 'Tmax_minus_T0_activator', 'Imax2': 'Tmax_minus_T0_repressor',
    'I01': 'T0_activator', 'I02': 'T0_repressor',
    'I1': 'c_I_activator', 'I2': 'c_I_repressor',
    'L1': 'c_TF_all_activator', 'L2': 'c_TF_all_repressor',
}
_CELL_NAMES = {
    'box.ipynb:9': {'k1': 'inactive_dissociation', 'k2': 'active_dissociation'},
    'ec50.ipynb:0': {'M': 'historical_dimer_enhancement_factor'},
    'ec50.ipynb:1': {'M': 'historical_dimer_enhancement_factor'},
    'plot6.ipynb:0': {'kb': 'basal_dimer_coefficient', 'kc': 'induced_dimer_coefficient'},
    'plot6.ipynb:12': {'k21': 'Kb_1', 'k22': 'Kb_2', 'k31': 'Kd1_1', 'k32': 'Kd1_2'},
    'plot6.ipynb:13': {'k31': 'Kd1_1', 'k32': 'Kd1_2', 'kx21': 'Kx2_1', 'kx22': 'Kx2_2'},
    'plot7.ipynb:1': _HYBRID_NAMES,
    'plot7.ipynb:2': _HYBRID_NAMES,
}


def _si_key(key, aliases):
    for old, new in aliases.items():
        if key == old or key.startswith(old + '_'):
            return new + key[len(old):]
    return key


def _si_parameters(value, aliases):
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            renamed = _si_key(key, aliases)
            if renamed in result:
                raise ValueError(f'Conflicting source parameter aliases: {key}')
            result[renamed] = _si_parameters(item, aliases)
        return result
    if isinstance(value, list):
        return [_si_parameters(item, aliases) for item in value]
    return value


def load_notebook_parameters(notebook, cell, *, parameter_names='si'):
    """Return SI parameter names with unchanged values and source provenance.

    ``cell`` is the zero-based index in the original notebook, including markdown
    cells. historical_fit is provenance, not a current optimizer configuration.
    parameter_names='source' returns the original archived names. The JSON
    archive and historical fitting recipes are never rewritten. Kx1/Kx2
    describe the historical transport model, not the new apparent model.
    Filesystem access occurs only on this explicit call.
    """
    path = Path(__file__).with_name('notebook_parameters.json')
    with path.open(encoding='utf-8') as stream:
        data = json.load(stream)
    key = f'{notebook}:{cell}'
    if key not in data['cells']:
        raise ValueError(f'Unknown historical parameter source: {key}')
    if parameter_names not in {'si', 'source'}:
        raise ValueError("parameter_names must be 'si' or 'source'")
    record = data['cells'][key]
    if parameter_names == 'source':
        return record
    aliases = {**_SOURCE_NAMES, **_CELL_NAMES.get(key, {})}
    return {**record, 'parameters': _si_parameters(record['parameters'], aliases),
            **({'grids': _si_parameters(record['grids'], aliases)} if 'grids' in record else {})}


def foldchange_design_parameters(cell=3):
    """Return (receptors, dbds) for scan_designs from one new_foldchange cell."""
    if cell not in (1, 2, 3):
        raise ValueError('Choose new_foldchange code cell 1, 2 or 3')
    values = load_notebook_parameters('new_foldchange.ipynb', cell)['parameters']
    baselines = values.get('T0_dict', values.get('T0_values'))
    dbds = [{'DBD_name': name, 'KA': KA, 'T0': baselines[name]}
            for name, KA in zip(values['KA_labels'], values['KA_values'])]
    return values['LBD_parameters'], dbds
