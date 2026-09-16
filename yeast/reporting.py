"""Shared portable CSV/JSON output and recomputation checks for Notes 10 and 11."""
import csv
import hashlib
import json
import math
from pathlib import Path


def read_records(path, required):
    with Path(path).open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        if len(columns) != len(set(columns)) or not set(required).issubset(columns):
            raise ValueError(f'{path}: missing or duplicate columns; require {sorted(required)}')
        rows = list(reader)
    if not rows or any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError(f'{path}: empty table or malformed CSV row')
    return rows


def number(value, name, positive=False, integer=False):
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'{name}: invalid number {value!r}') from error
    if isinstance(value, bool) or not math.isfinite(result) or result < 0 or (positive and result == 0):
        raise ValueError(f'{name}: require a finite {"positive" if positive else "non-negative"} number')
    if integer and not result.is_integer():
        raise ValueError(f'{name}: require an integer')
    return int(result) if integer else result


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def write_results(output_dir, rows, metrics, data_path, model_settings):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / 'validation.json', {'status': 'NOT_VALIDATED'})
    with (output_dir / 'predictions.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(output_dir / 'metrics.json', metrics)
    write_json(output_dir / 'provenance.json', {
        'source_path': str(Path(data_path).resolve()), 'source_sha256': sha256(data_path),
        'model_settings': model_settings,
    })


def compare(expected, actual, locator='result'):
    """Compare recomputed rows and metrics, including lengths, identities and finite values."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(expected) != set(actual):
            raise ValueError(f'{locator}: fields differ')
        for key in expected:
            compare(expected[key], actual[key], f'{locator}.{key}')
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            raise ValueError(f'{locator}: row counts differ')
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, f'{locator}[{index}]')
    elif isinstance(expected, (int, float)):
        try:
            value = float(actual)
        except (TypeError, ValueError) as error:
            raise ValueError(f'{locator}: invalid numeric result') from error
        if not math.isfinite(value) or not math.isclose(expected, value, rel_tol=1e-11, abs_tol=1e-13):
            raise ValueError(f'{locator}: saved value differs from recomputation')
    elif expected != actual:
        raise ValueError(f'{locator}: identity or value differs')


def validate_results(output_dir, rows, metrics, data_path, model_settings):
    output_dir = Path(output_dir)
    try:
        actual = read_records(output_dir / 'predictions.csv', rows[0])
        compare(rows, actual, 'predictions')
        compare(metrics, json.loads((output_dir / 'metrics.json').read_text()), 'metrics')
        provenance = json.loads((output_dir / 'provenance.json').read_text())
        compare(model_settings, provenance['model_settings'], 'model_settings')
        compare(sha256(data_path), provenance['source_sha256'], 'source_sha256')
    except (OSError, ValueError, KeyError) as error:
        write_json(output_dir / 'validation.json', {'status': 'FAIL', 'error': str(error)})
        raise
    result = {'status': 'PASS', 'observations': len(rows),
              'scope': 'Recomputed predictions and metrics from supplied CSV and fixed model parameters'}
    write_json(output_dir / 'validation.json', result)
    return result


def validation_data_path(output_dir, requested, default):
    if requested is not None:
        return Path(requested)
    provenance = Path(output_dir) / 'provenance.json'
    if provenance.is_file():
        return Path(json.loads(provenance.read_text())['source_path'])
    return default
