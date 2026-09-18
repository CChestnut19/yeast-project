"""Reproduce the supplied Note 10/11 datasets and check their reference metrics."""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def check_outputs(output_dir):
    reference = json.loads((ROOT / 'tests/fixtures/repressor_reference.json').read_text(encoding='utf-8'))
    note10 = json.loads((output_dir / 'note10/metrics.json').read_text(encoding='utf-8'))
    note11 = json.loads((output_dir / 'note11/metrics.json').read_text(encoding='utf-8'))
    for sensor, expected in reference['note10']['per_sensor'].items():
        for key, value in expected.items():
            if not math.isclose(note10['log10']['per_sensor'][sensor][key], value, rel_tol=1e-10, abs_tol=1e-12):
                raise ValueError(f'Note 10 reference mismatch: {sensor}/{key}')
    for key, value in reference['note10']['pooled'].items():
        if not math.isclose(note10['log10']['pooled'][key], value, rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError(f'Note 10 pooled reference mismatch: {key}')
    if set(note11) != set(reference['note11']['log10_r2']):
        raise ValueError('Note 11 panel set differs from the reference')
    for panel, expected in reference['note11']['log10_r2'].items():
        if not math.isclose(note11[panel]['R2'], expected, rel_tol=1e-10, abs_tol=1e-12):
            raise ValueError(f'Note 11 reference mismatch: {panel}')
    counts = {}
    for name, expected in [('note10', 1141), ('note11', 216)]:
        with (output_dir / name / 'predictions.csv').open(encoding='utf-8-sig', newline='') as stream:
            count = sum(1 for _ in csv.DictReader(stream))
        if count != expected:
            raise ValueError(f'{name} observation count differs: {count}')
        counts[f'{name}_observations'] = count
    return {**counts, 'note10_pooled_log10_r2': note10['log10']['pooled']['R2'],
            'note11_panels': {panel: note11[panel]['R2'] for panel in sorted(note11)}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report_path = output / 'demo_report.json'
    report = {'status': 'RUNNING', 'python': platform.python_version(), 'platform': platform.platform(),
              'not_run': {'activator_experimental': 'Source workbook and parameter TSV not supplied',
                          'mammalian_experimental': 'Experimental CSVs, mapping and initial vectors not supplied'},
              'commands': [], 'scope': 'numerical_algorithms'}
    started = time.perf_counter()
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    env = {**os.environ, 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1'}
    try:
        for package, name in [('repressor', 'note10'), ('combinatorial', 'note11')]:
            command = [sys.executable, '-m', 'yeast.' + package, 'run', '--output-dir', str(output / name)]
            step_start = time.perf_counter()
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
            report['commands'].append({'command': command[1:], 'seconds': time.perf_counter() - step_start,
                                       'exit_code': result.returncode})
            (output / f'{name}.log').write_text(result.stdout + result.stderr, encoding='utf-8')
            if result.returncode:
                raise ValueError(f'{name} failed; see {output / (name + ".log")}')
        report['checks'] = check_outputs(output)
        report['status'] = 'PASS'
    except (OSError, ValueError, KeyError) as error:
        report['status'] = 'FAIL'
        report['error'] = str(error)
    report['elapsed_seconds'] = time.perf_counter() - started
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report['status'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
