"""Load explicitly selected historical parameter sets; never mix source cells."""
import json
from pathlib import Path


def load_notebook_parameters(notebook, cell):
    """Return original parameters, source hash and historical recipes for one cell.

    ``cell`` is the zero-based index in the original notebook, including markdown
    cells. historical_fit is provenance, not a current optimizer configuration.
    Filesystem access occurs only on this explicit call.
    """
    path = Path(__file__).with_name('notebook_parameters.json')
    with path.open(encoding='utf-8') as stream:
        data = json.load(stream)
    key = f'{notebook}:{cell}'
    if key not in data['cells']:
        raise ValueError(f'Unknown historical parameter source: {key}')
    return data['cells'][key]


def foldchange_design_parameters(cell=3):
    """Return (receptors, dbds) for scan_designs from one new_foldchange cell."""
    if cell not in (1, 2, 3):
        raise ValueError('Choose new_foldchange code cell 1, 2 or 3')
    values = load_notebook_parameters('new_foldchange.ipynb', cell)['parameters']
    baselines = values.get('I0_dict', values.get('I0_values'))
    dbds = [{'DBD_name': name, 'kd': kd, 'I0': baselines[name]}
            for name, kd in zip(values['kd_labels'], values['kd_values'])]
    return values['LBD_parameters'], dbds
