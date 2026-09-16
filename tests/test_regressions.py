"""Synthetic regression tests; no manuscript observations are fabricated here."""

import contextlib
from decimal import Decimal, localcontext
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "mammalian" / "Scripts"
sys.path[:0] = [str(ROOT), str(SCRIPTS)]
import model_core as core
import fit_sensor_logr2_floor as floor
import validate_results as validation
import yeast_analysis as yeast


class ModelTests(unittest.TestCase):
    def test_stable_weak_signal_against_decimal_mass_balance(self):
        with localcontext() as context:
            context.prec = 80
            d = Decimal("1e-16")
            effective = d * (2 / ((1 + 8 * d).sqrt() + 1))**2
            expected_p7 = 1 - (1 + Decimal("9.15") * effective)**-7
        output, terms = core.cic_response_numpy(0, 1, 1e-16, 1, 1, 9.15, 0)
        self.assertGreater(output, 0)
        self.assertAlmostEqual(terms["p7"] / float(expected_p7), 1, places=14)

    def test_response_zero_and_saturation(self):
        output, terms = core.cic_response_numpy(np.array([0, 1, 1e8]), 0, .001, 1, 1, 9.15, .01)
        np.testing.assert_array_equal(output, [.01, .01, .01])
        saturated, _ = core.cic_response_numpy(100, 1e8, .001, 1, 1, 9.15, .01)
        self.assertAlmostEqual(float(saturated), core.TMAX)

    def test_normal_signal_matches_original_equation(self):
        inducer = np.geomspace(1e-4, 1e3, 70)
        b = 1 + .2 * inducer
        d = .003 + .2**2 * .8 * inducer**2
        root = np.sqrt(b**2 + 8 * 3 * d)
        z = 9.15 * 1.5 * (root - b) / (root + b)
        expected = .01 + (core.TMAX - .01) * (1 - (1 + z)**-7)
        actual, _ = core.cic_response_numpy(inducer, 3, .003, .2, .8, 9.15, .01)
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)

    def test_floor_candidate_selection(self):
        def candidate(feasible, mse, minimum):
            return dict(feasible=feasible, global_MSE_log10=mse, minimum_R2_log10=minimum, mean_R2_log10=.8)
        bad = candidate(False, .01, .4)
        good = candidate(True, .2, .51)
        best = candidate(True, .1, .55)
        self.assertIs(floor.choose_candidate([bad, good, best]), best)
        with self.assertRaises(ValueError):
            floor.choose_candidate([])
        with self.assertRaises(ValueError):
            floor.choose_candidate([candidate(True, np.nan, .6)])


class FitFixture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.inputs = cls.root / "Input"
        cls.inputs.mkdir()
        cls.readme = cls.root / "README.md"
        mappings = []
        for i in range(25):
            dbd = core.ANCHOR_DBD if i % 11 == 0 else f"dbd{i % 11}"
            mappings.append(core.SensorMapping(f"{500+i}.csv", f"sensor{i}", dbd, dbd, f"lbd{i % 13}", True))
        cls.layout = core.ParameterLayout(mappings)
        cls.vector = np.zeros(cls.layout.size)
        cls.vector[cls.layout.log_Kd0] = -3
        cls.vector[cls.layout.log_Kd1] = -.3
        cls.vector[cls.layout.T0_variant] = .02
        for i, mapping in enumerate(mappings):
            dose = np.tile([0, .01, 1, 10], 3)
            tf = np.repeat([.5, 1, 3], 4)
            ka = core.ANCHOR_KA if mapping.dbd == core.ANCHOR_DBD else 1
            response, _ = core.cic_response_numpy(dose, tf, .001, 1, 10**-.3, ka, .02)
            pd.DataFrame({"LBD": tf, "inducer": dose, "RPU": response}).to_csv(cls.inputs / mapping.csv_name, index=False)
        rows = [f"| {m.csv_name} | {m.sensor_name} | {m.source_dbd} | {m.dbd} | {m.lbd} | Included |" for m in mappings]
        rows.append("| 402.csv | control | control | control | control | Excluded |")
        cls.readme.write_text("\n".join(rows), encoding="utf-8")
        cls.data = core.load_fit_data(cls.inputs, core.read_sensor_mapping(cls.readme))
        table = floor.per_csv_log_metrics(cls.data, cls.layout, cls.vector)
        candidate = dict(label="synthetic_fixture", vector=cls.vector, sensor_weights=np.ones(25), feasible=True,
                         minimum_R2_log10=float(table.R2_log10.min()), mean_R2_log10=float(table.R2_log10.mean()),
                         global_MSE_log10=floor.global_log_mse(cls.data, cls.layout, cls.vector))
        cls.result = floor.write_outputs(candidate, [candidate], [], cls.data, cls.layout, cls.root / "Output", 0)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_roundtrip_independent_validation(self):
        checks = validation.validate_numerical_results(self.inputs, self.readme, self.result)
        self.assertGreater(len(checks), 75)

    def test_tampered_saved_prediction_is_rejected(self):
        path = self.result / "predictions.csv"
        original = path.read_bytes()
        try:
            frame = pd.read_csv(path)
            frame.loc[0, "RPU_predicted"] *= 1.1
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(AssertionError, "predictions are reproduced"):
                validation.validate_numerical_results(self.inputs, self.readme, self.result)
        finally:
            path.write_bytes(original)

    def test_tampered_saved_metric_is_rejected(self):
        path = self.result / "constraint_metrics.csv"
        original = path.read_bytes()
        try:
            frame = pd.read_csv(path)
            frame.loc[0, "R2_log10"] = .99
            frame.to_csv(path, index=False)
            with self.assertRaisesRegex(AssertionError, "independently reproduced"):
                validation.validate_numerical_results(self.inputs, self.readme, self.result)
        finally:
            path.write_bytes(original)

    def test_empty_nonfinite_negative_and_constant_data_rejected(self):
        path = self.inputs / "500.csv"
        original = path.read_bytes()
        mappings = core.read_sensor_mapping(self.readme)
        bad_cases = [("RPU", np.nan), ("RPU", np.inf), ("RPU", 0), ("LBD", -1), ("inducer", -1)]
        try:
            for column, value in bad_cases:
                with self.subTest(column=column, value=value):
                    frame = pd.read_csv(io.BytesIO(original))
                    frame.loc[0, column] = value
                    frame.to_csv(path, index=False)
                    with self.assertRaises(ValueError):
                        core.load_fit_data(self.inputs, mappings)
            for content in ("LBD,inducer,RPU\n", "LBD,inducer,RPU\n1,0,1\n1,1,1\n"):
                path.write_text(content)
                with self.assertRaises(ValueError):
                    core.load_fit_data(self.inputs, mappings)
        finally:
            path.write_bytes(original)

    def test_custom_input_directory_and_invalid_vectors(self):
        with self.assertRaisesRegex(FileNotFoundError, "archived initial parameters"):
            floor.load_start_vectors(self.inputs, self.layout)
        for _, filename in floor.START_FILES:
            np.save(self.inputs / filename, self.vector)
        try:
            starts = floor.load_start_vectors(self.inputs, self.layout)
            np.testing.assert_array_equal(starts[0][1], self.vector)
            for vector in (self.vector[:-1], np.full_like(self.vector, np.inf)):
                with self.assertRaises(ValueError):
                    self.layout.decode_numpy(vector)
        finally:
            for _, filename in floor.START_FILES:
                (self.inputs / filename).unlink()

    def test_scipy_floor_optimizer_step(self):
        initial = self.vector.copy()
        initial[self.layout.T0_variant] = 4
        with patch.object(floor, "MAX_REWEIGHT_ROUNDS", 1), contextlib.redirect_stdout(io.StringIO()):
            result, metrics, trace, weights = floor.fit_one_start("smoke", initial, self.data, self.layout, 2)
        self.assertEqual(len(trace), 2)
        self.assertTrue(np.isfinite(metrics.R2_log10).all())
        self.assertLess(floor.global_log_mse(self.data, self.layout, result), floor.global_log_mse(self.data, self.layout, initial))

    @unittest.skipUnless(importlib.util.find_spec("torch"), "optional PyTorch is not installed")
    def test_torch_numpy_objectives_agree(self):
        with contextlib.redirect_stdout(io.StringIO()):
            fit = core.fit_pytorch(self.data, self.layout, 1, .001, 0, 123, self.vector)
        expected = core.objective_components_numpy(self.data, self.layout, fit.parameter_vector)["objective_total"]
        self.assertAlmostEqual(fit.objective_total, expected, places=13)
        with self.assertRaises(ValueError):
            core.fit_pytorch(self.data, self.layout, 0, .001, 0, 123)


class NotebookTests(unittest.TestCase):

    def test_pareto_matches_quadratic_oracle_with_ties(self):
        rng = np.random.default_rng(20260915)
        points = rng.integers(0, 8, size=(100, 2))
        oracle = np.array([not np.any(np.all(points >= p, axis=1) & np.any(points > p, axis=1)) for p in points])
        np.testing.assert_array_equal(yeast.fast_pareto_2d(points), oracle)
        self.assertEqual(yeast.fast_pareto_2d(np.empty((0, 2))).size, 0)
        with self.assertRaises(ValueError):
            yeast.fast_pareto_2d([[1, np.nan]])

    def test_yeast_equations_match_legacy_for_both_variants(self):
        L = np.geomspace(.3, 10, 40)
        for kx1, kx2 in ((0, 0), (.3, .5)):
            k1, k2, k3, kd, I, imax, i0 = .003, .2, .8, 4, 10, 35.8, .02
            expected = []
            for dose in (I, 0):
                b = 1 + kx1 + k2 * dose * (1 + kx2)
                d = k1 * (1 + kx1**2) + k2**2 * k3 * dose**2 * (1 + kx2**2)
                root = np.sqrt(b**2 + 8 * L * d)
                f = np.log(L / 2) + np.log((root - b) / (root + b)) + np.log(kd)
                expected.append(imax / (1 + np.exp(-f)) + i0)
            actual = yeast.response_pair(L, kd, k1, k2, k3, imax, i0, I, kx1, kx2)
            np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)



class ScriptTests(unittest.TestCase):
    def test_preflight_explains_missing_source_mapping(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "run_pipeline.py"), "--stage", "check"],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Input check failed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_all_script_help(self):
        for script in SCRIPTS.glob("*.py"):
            result = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, f"{script.name}: {result.stderr}")

    def test_supplementary_model_uses_core_and_named_font_weights(self):
        import plot_supplementary_figure13_corrected as supplementary
        import plot_mammalian_experiment_vs_prediction as scatter
        expected = core.cic_response_numpy([0, 1], 1, .001, 1, 1, 9.15, .02)[0]
        np.testing.assert_array_equal(supplementary.model([0, 1], 1, .001, 1, 1, 9.15, .02, core.TMAX), expected)
        self.assertEqual(scatter.font_weight("normal"), 400)
        self.assertEqual(scatter.font_weight("bold"), 700)


if __name__ == "__main__":
    unittest.main()
