"""CIC design search with the same ordinary response and equal-weight score as yeast."""
import csv
import numpy as np
from Entity import DBD, LBD


DEFAULT_IMAX = 35.84931505  # Amplitude, not the total response ceiling.


def response(L, kd, k1, k2, k3, Imax, I0, I, kx1=0.0, kx2=0.0):
    """Stable mass balance, implemented locally; no dependency on yeast."""
    L, kd, k1, k2, k3, Imax, I0, I, kx1, kx2 = (
        np.asarray(value, dtype=float)
        for value in (L, kd, k1, k2, k3, Imax, I0, I, kx1, kx2))
    if any(not np.isfinite(value).all() or np.any(value < 0)
           for value in (L, kd, k1, k2, k3, Imax, I0, I, kx1, kx2)):
        raise ValueError('Response parameters must be finite and non-negative')
    b = 1.0 + kx1 + k2 * I * (1.0 + kx2)
    d = k1 * (1.0 + kx1**2) + k2**2 * k3 * I**2 * (1.0 + kx2**2)
    if not np.isfinite(b).all() or not np.isfinite(d).all():
        raise ValueError('Mass-balance coefficients must be finite')
    root = np.sqrt(b**2 + 8.0 * d * L)
    active_pool = d * np.square(2.0 * L / (b + root))
    z = kd * active_pool
    return I0 + Imax * z / (1.0 + z)


def _scores(on, off):
    on, off = np.broadcast_arrays(on, off)
    score = np.full(on.shape, np.nan)
    valid = (on > off) & (off > 0) & np.isfinite(on) & np.isfinite(off)
    with np.errstate(divide='ignore', invalid='ignore', over='ignore'):
        score[valid] = np.log10(on[valid] / off[valid]) + np.log10(on[valid] - off[valid])
    score[~np.isfinite(score)] = np.nan
    return score


def foldchange1(L, kd, k1, k2, k3, Imax, I0, I):
    """Equal-weight log10 ratio + log10 difference; invalid candidates are NaN."""
    on = response(L, kd, k1, k2, k3, Imax, I0, I)
    off = response(L, kd, k1, k2, k3, Imax, I0, 0.0)
    return _scores(on, off)


def foldchange2(L, kd, k1, k2, k3, Imax, I0, I):
    return response(L, kd, k1, k2, k3, Imax, I0, I)


def scan_designs(concentrations, receptors, dbds):
    """Return the first grid maximum per valid pair, as yeast's default scan does."""
    concentrations = np.asarray(concentrations, dtype=float)
    if (concentrations.ndim != 1 or not len(concentrations)
            or not np.isfinite(concentrations).all() or np.any(concentrations < 0)):
        raise ValueError('L must be a nonempty finite non-negative vector')
    dbds = list(dbds)
    records = []
    for receptor in receptors:
        for dbd in dbds:
            args = (concentrations, dbd['kd'], receptor['k1'], receptor['k2'],
                    receptor['k3'], receptor['Imax'], dbd['I0'])
            nuclear = {'kx1': receptor.get('kx1', 0.0), 'kx2': receptor.get('kx2', 0.0)}
            on = response(*args, receptor['I'], **nuclear)
            off = response(*args, 0.0, **nuclear)
            score = _scores(on, off)
            indices = np.flatnonzero(np.isfinite(score))
            if not len(indices):
                continue
            index = indices[np.argmax(score[indices])]
            records.append({
                'LBD_name': receptor['LBD_name'], 'DBD_name': dbd['DBD_name'],
                'L': float(concentrations[index]), 'score': float(score[index]),
                'RPU': float(on[index]),
                'log10_fold': float(np.log10(on[index] / off[index])),
                'log10_difference': float(np.log10(on[index] - off[index])),
            })
    return records


def ReadExcelLBDValue(api_url, session):
    menu = LBD.GetLBDDimerMenu(api_url, session)
    if not menu:
        raise ValueError('No LBD parameters returned by WebDatabase/GetLBDDimerMenu')
    return [{'LBD_name': name, 'k1': values[0], 'k2': values[1], 'k3': values[2],
             'Imax': DEFAULT_IMAX, 'I': values[3]} for name, values in menu.items()]


def ReadExcelDBDValue(api_url, session):
    # Name, baseline and kd must come from the same database record.
    menu = DBD.GetDBDMenu(api_url, session)
    if not menu:
        raise ValueError('No DBD parameters returned by WebDatabase/GetDBDMenu')
    return [{'DBD_name': name, 'I0': values[0], 'kd': values[1]}
            for name, values in menu.items()]


def normalize_optional_name(value):
    if value is None:
        return None
    value = str(value).strip()
    return None if value.lower() in ('', 'none', 'null', 'undefined') else value


def same_name(left, right):
    return str(left).strip().lower() == str(right).strip().lower()


def HtmlReturn(api_url, session, LBD=None, DBD=None, *, concentrations=None):
    base = api_url.rstrip('/')
    if base.lower().endswith('/webdatabase'):
        base = base[:-len('/WebDatabase')]
    receptors = ReadExcelLBDValue(base, session)
    dbds = ReadExcelDBDValue(base, session)
    fixed_lbd, fixed_dbd = normalize_optional_name(LBD), normalize_optional_name(DBD)
    if fixed_lbd:
        receptors = [r for r in receptors if same_name(r['LBD_name'], fixed_lbd)]
        if not receptors:
            raise ValueError(f'LBD not found: {fixed_lbd}')
    if fixed_dbd:
        dbds = [d for d in dbds if same_name(d['DBD_name'], fixed_dbd)]
        if not dbds:
            raise ValueError(f'DBD not found: {fixed_dbd}')
    grid = np.linspace(0.3, 10, 2000) if concentrations is None else concentrations
    records = scan_designs(grid, receptors, dbds)
    if not records:
        raise ValueError('No valid candidates: require finite output with induced > basal > 0')
    best = max(records, key=lambda record: record['score'])
    lookup = {(r['LBD_name'], r['DBD_name']): r for r in records}
    # Keep historical export filenames; the first contains scores, not raw fold change.
    for filename, field in [('new_foldchange_max_values.csv', 'score'),
                            ('new_max_L_values.csv', 'L'), ('new_output.csv', 'RPU')]:
        with open(filename, 'w', newline='', encoding='utf-8') as output:
            writer = csv.writer(output)
            writer.writerow(['LBD_name'] + [d['DBD_name'] for d in dbds])
            for receptor in receptors:
                writer.writerow([receptor['LBD_name']] + [
                    lookup.get((receptor['LBD_name'], d['DBD_name']), {}).get(field, '')
                    for d in dbds])
    return [best['score'], best['LBD_name'], best['DBD_name'], best['L'], best['RPU']]
