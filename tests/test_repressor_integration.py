"""Scientific and CLI regressions against the two user-supplied archives."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REFERENCE = json.loads((ROOT / 'tests/fixtures/repressor_reference.json').read_text())


def write_rows(path, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class RepressorIntegrationTests(unittest.TestCase):
    def test_note10_reproduces_all_supplied_sensor_statistics(self):
        from yeast.repressor.pipeline import read_data, calculate_predictions, summarize
        rows = read_data(ROOT / 'yeast/repressor/data/experiment_data.csv')
        result = summarize(calculate_predictions(rows))
        self.assertEqual(len(rows), 1141)
        for sensor, expected in REFERENCE['note10']['per_sensor'].items():
            for key, value in expected.items():
                self.assertAlmostEqual(result['log10']['per_sensor'][sensor][key], value, places=11)
        for key, value in REFERENCE['note10']['pooled'].items():
            self.assertAlmostEqual(result['log10']['pooled'][key], value, places=11)

    def test_models_preserve_different_operator_rules_and_mass_balance(self):
        from yeast.repressor.model import model_components, predict
        from yeast.combinatorial.model import predicted_rpu
        result = model_components('CI94', np.array([0., 1., 3.]), 4.)
        np.testing.assert_allclose((1 + .256016091 * 4) * result['free_monomer'] + 2 * result['active_pool'], [0, 1, 3], rtol=1e-13)
        np.testing.assert_allclose(result['p_two'], 2 * result['p_r'] - result['p_r']**2, rtol=1e-13)
        self.assertEqual(predict('CI94', 0, 0), 1.62)
        self.assertGreater(predict('CI94', 1, 0), predict('CI94', 1, 100))
        self.assertAlmostEqual(predicted_rpu('A1', 1, 0, 0), REFERENCE['note11']['predictions'][0], places=14)

    def test_note11_all_predictions_and_panel_r2_match_archive(self):
        from yeast.combinatorial.data import read_data
        from yeast.combinatorial.model import predicted_rpu
        from yeast.combinatorial.pipeline import summarize
        rows = read_data(ROOT / 'yeast/combinatorial/data/Supplementary_Note_11_plot_data.csv')
        predicted = [predicted_rpu(r['panel'], r['condition'], r['x_value_uM'], r['series_value_uM']) for r in rows]
        np.testing.assert_allclose(predicted, REFERENCE['note11']['predictions'], rtol=1e-13, atol=1e-14)
        stats = summarize(rows)
        for panel, expected in REFERENCE['note11']['log10_r2'].items():
            self.assertAlmostEqual(stats[panel]['R2'], expected, places=12)
        self.assertLess(stats['A2']['R2'], 0)  # Negative R2 must not be clipped or hidden.

    def test_model_domains_and_panel_condition_consistency(self):
        from yeast.repressor.model import predict
        from yeast.combinatorial.model import predicted_rpu
        for bad in [-1, float('nan'), float('inf')]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                predict('CI94', 1, bad)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                predicted_rpu('A1', 1, bad, 0)
        for panel, condition in [('A1', 2), ('Z1', 1), ('A1', 1.5)]:
            with self.assertRaises(ValueError):
                predicted_rpu(panel, condition, 0, 0)
        with self.assertRaises(ValueError):
            predict('unknown', 1, 1)

    def test_metrics_reject_invalid_pairs_instead_of_silently_omitting(self):
        from yeast.metrics import regression_metrics
        for actual, predicted in [([], []), ([1, 2], [1]), ([[1], [2]], [[1], [2]]),
                                  ([1, 0], [1, 2]), ([1, float('nan')], [1, 2]), ([1, 1], [1, 2])]:
            with self.subTest(actual=actual), self.assertRaises(ValueError):
                regression_metrics(actual, predicted, scale='log10')
        self.assertAlmostEqual(regression_metrics([1, 10, 100], [10, 100, 1000], 'log10')['R2'], -.5)

    def test_csv_rejects_unknown_sensors_duplicates_and_nonfinite_values(self):
        from yeast.repressor.pipeline import read_data
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.csv'
            base = {'sensor':'CI94', 'tf_input_rpu':1, 'inducer_um':0, 'replicate':1, 'experiment_rpu':1}
            for change in [{'sensor':'Other'}, {'experiment_rpu':'nan'}, {'tf_input_rpu':-1}, {'replicate':1.5}]:
                write_rows(path, [{**base, **change}])
                with self.subTest(change=change), self.assertRaises(ValueError):
                    read_data(path)
            write_rows(path, [base, base])
            with self.assertRaises(ValueError):
                read_data(path)

    def test_note11_csv_rejects_wrong_condition_negative_sd_and_duplicates(self):
        from yeast.combinatorial.data import read_data
        with (ROOT / 'yeast/combinatorial/data/Supplementary_Note_11_plot_data.csv').open(encoding='utf-8-sig', newline='') as stream:
            source = list(csv.DictReader(stream))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'bad.csv'
            for change in [{'condition':2}, {'sample_SD_RPU':-1}, {'mean_RPU':0}, {'x_value_uM':'inf'}]:
                rows = [dict(r) for r in source]
                rows[0].update(change)
                write_rows(path, rows)
                with self.subTest(change=change), self.assertRaises(ValueError):
                    read_data(path)
            write_rows(path, source + [source[0]])
            with self.assertRaises(ValueError):
                read_data(path)

    def test_both_clis_help_check_and_numeric_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            for package in ('repressor', 'combinatorial'):
                target = Path(directory) / package
                for args in (['--help'], ['check', '--output-dir', str(target)]):
                    result = subprocess.run([sys.executable, '-m', 'yeast.' + package, *args], cwd=ROOT, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertFalse(target.exists())
                result = subprocess.run([sys.executable, '-m', 'yeast.' + package, 'run', '--output-dir', str(target)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([sys.executable, '-O', '-m', 'yeast.' + package, 'validate', '--output-dir', str(target)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                predictions = target / 'predictions.csv'
                with predictions.open(encoding='utf-8-sig', newline='') as stream:
                    rows = list(csv.DictReader(stream))
                rows[0]['prediction_rpu'] = float(rows[0]['prediction_rpu']) * 1.1
                write_rows(predictions, rows)
                result = subprocess.run([sys.executable, '-O', '-m', 'yeast.' + package, 'validate', '--output-dir', str(target)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(json.loads((target / 'validation.json').read_text())['status'], 'FAIL')




if __name__ == '__main__':
    unittest.main()
