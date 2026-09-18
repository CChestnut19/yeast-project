"""Numerical contracts for the pure per-CSV log10-R2 mammalian objective."""

import contextlib
from dataclasses import replace
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mammalian" / "Scripts"))
import model_core as core
import fit_sensor_logr2_floor as floor


def unequal_csv_fixture():
    # At zero TF the unchanged CIC equation predicts T0 for every row.
    # log observations are [0,2] and [0,1,3]; SSTs are 2 and 14/3.
    mappings = [core.SensorMapping(f"{500+i}.csv", f"s{i}", core.ANCHOR_DBD,
                                  core.ANCHOR_DBD, "lbd", True) for i in range(2)]
    layout = core.ParameterLayout(mappings)
    frame = pd.DataFrame({"LBD": np.zeros(5), "inducer": [0, 1, 0, 1, 1],
                          "RPU": [1., 100., 1., 10., 1000.],
                          "csv_index": [0, 0, 1, 1, 1], "lbd_index": np.zeros(5, int),
                          "dbd_index": np.zeros(5, int)})
    data = core.FitData(frame, mappings, frame.LBD.to_numpy(), frame.inducer.to_numpy(),
                        frame.RPU.to_numpy(), np.log10(frame.RPU.to_numpy()),
                        frame.lbd_index.to_numpy(), frame.dbd_index.to_numpy(),
                        frame.csv_index.to_numpy())
    vector = np.zeros(layout.size)
    vector[layout.T0_variant] = 1.
    return data, layout, vector


class LogR2ObjectiveTests(unittest.TestCase):
    def test_constant_log_observations_cannot_acquire_rounding_variance(self):
        data, layout, vector = unequal_csv_fixture()
        observed = np.full(7, 3.)
        constant = replace(data, mappings=data.mappings[:1], observed_rpu=observed,
                           observed_log10=np.log10(observed), csv_index=np.zeros(7, dtype=int))
        with self.assertRaisesRegex(ValueError, "variance"):
            core.objective_row_scales(constant)

    def test_numpy_loss_is_equal_csv_log_r2_without_endpoint_prior(self):
        data, layout, vector = unequal_csv_fixture()
        components = core.objective_components_numpy(data, layout, vector)
        # At T0=1, SSEs are 4 and 10, so macro loss=(4/2+10/(14/3))/2.
        self.assertAlmostEqual(components["objective_total"], 29 / 14, places=13)
        self.assertAlmostEqual(components["data_objective"], 29 / 14, places=13)
        self.assertAlmostEqual(components["macro_R2_log10"], -15 / 14, places=13)
        changed = vector.copy()
        changed[layout.log_Kb] = 4
        # Changing nonidentifiable endpoint kinetics cannot alter this loss.
        self.assertEqual(core.objective_components_numpy(data, layout, changed)["objective_total"],
                         components["objective_total"])

    def test_scipy_optimizes_normalized_macro_log_r2(self):
        data, layout, _ = unequal_csv_fixture()
        fit = core.fit_scipy(data, layout, max_nfev=300, starts=1)
        # Minimizing (2*x^2-4*x+4)/2 + (3*x^2-8*x+10)/(14/3)
        # gives x=log10(T0)=26/23, not the pooled log mean 6/5.
        self.assertAlmostEqual(np.log10(fit.parameter_vector[layout.T0_variant][0]), 26/23, places=6)
        self.assertAlmostEqual(fit.objective_total, 47/46, places=10)

    def test_floor_residuals_use_each_csv_log_sst(self):
        data, layout, vector = unequal_csv_fixture()
        with patch.object(floor, "MAX_REWEIGHT_ROUNDS", 1), patch.object(floor, "WEIGHT_GROWTH", 1), contextlib.redirect_stdout(io.StringIO()):
            fitted, _, _, _ = floor.fit_one_start("normalization", vector, data, layout, 300)
        self.assertAlmostEqual(np.log10(fitted[layout.T0_variant][0]), 26/23, places=6)

    def test_candidate_ranking_prefers_macro_r2_over_global_mse(self):
        a = dict(feasible=True, global_MSE_log10=.01, minimum_R2_log10=.51, mean_R2_log10=.6)
        b = dict(feasible=True, global_MSE_log10=.2, minimum_R2_log10=.55, mean_R2_log10=.8)
        self.assertIs(floor.choose_candidate([a, b]), b)

    @unittest.skipUnless(importlib.util.find_spec("torch"), "optional PyTorch is not installed")
    def test_torch_cic_equation_matches_numpy_at_weak_and_normal_signal(self):
        import torch
        inputs = [np.array([0., .01, 1., 100.]), np.array([1., .5, 3., 1e8]),
                  np.array([1e-16, .003, .003, .003]), .2, .8, 9.15, 0.]
        tensors = [torch.tensor(value, dtype=torch.float64) for value in inputs]
        expected, _ = core.cic_response_numpy(*inputs)
        actual = core.cic_response_torch(*tensors)
        np.testing.assert_allclose(actual.detach().numpy(), expected, rtol=1e-13, atol=0)

    @unittest.skipUnless(importlib.util.find_spec("torch"), "optional PyTorch is not installed")
    def test_torch_pure_log_loss_and_post_step_parameter_match(self):
        data, layout, vector = unequal_csv_fixture()
        with contextlib.redirect_stdout(io.StringIO()):
            fit = core.fit_pytorch(data, layout, 1, .01, 0, 123, vector)
        self.assertLess(fit.objective_total, 29/14)
        self.assertEqual(fit.status, "epoch_budget")
        log_t0 = np.log10(fit.parameter_vector[layout.T0_variant][0])
        expected = .5 * ((2*log_t0**2-4*log_t0+4)/2 + (3*log_t0**2-8*log_t0+10)/(14/3))
        self.assertAlmostEqual(fit.objective_total, expected, places=13)


if __name__ == "__main__":
    unittest.main()
