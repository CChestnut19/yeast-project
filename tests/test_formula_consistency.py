"""Cross-module response checks; expected expressions do not call model helpers."""
import unittest
import numpy as np
from numpy.testing import assert_allclose

from yeast import analysis, curve_analysis, exploratory_models
from yeast.activator.model import model_s32_s47
from yeast.combinatorial import model as combinatorial


def reference_response(L, I, kd, k1, k2, k3, amplitude=1., baseline=0., kx1=0., kx2=0.):
    b = 1 + k2*I + kx1 + kx2*k2*I
    d = k1*(1+kx1**2) + k2**2*k3*I**2*(1+kx2**2)
    monomer = 2*L/(b+np.sqrt(b*b+8*d*L))
    z = kd*d*monomer**2
    return baseline+amplitude*z/(1+z)


class FormulaConsistencyTests(unittest.TestCase):
    def test_crosstalk_uses_same_tf_in_both_curves(self):
        L = np.array([.2, 1., 7.])
        first = reference_response(L, 3., 5., .02, .3, .4, 10., .03)
        second = reference_response(L, 3., 5., .02, .1, .8, 10., .03)
        actual = exploratory_models.crosstalk_ratio(
            L, 5., .02, .3, .1, .4, .8, 3., amplitude=10., baseline=.03)
        assert_allclose(actual, second/first, rtol=1e-12)

    def test_nuclear_fold_range_uses_complete_mass_balance(self):
        L = np.array([.1, 1., 4.])
        on = reference_response(L, 10., 5., .02, .3, .4, kx1=2., kx2=.7)
        off = reference_response(L, 0., 5., .02, .3, .4, kx1=2., kx2=.7)
        actual = curve_analysis.log_fold_range(
            L, .02, .3, .4, 5., 10., kx1=2., kx2=.7)
        assert_allclose(actual, [np.log10(on/off).min(), np.log10(on/off).max()], rtol=1e-12)

    def test_nuclear_coefficient_ratio_reduces_to_ordinary_at_zero_transport(self):
        actual = curve_analysis.quality_ratio(.02,.3,.4,10.,kx1=0.,kx2=0.)
        self.assertAlmostEqual(float(actual),180.)

    def test_coefficient_diagnostic_rejects_invalid_model_parameters(self):
        for bad in (-1., np.nan, np.inf):
            for position in range(4):
                arguments = [.02,.3,.4,10.]
                arguments[position] = bad
                with self.subTest(position=position,bad=bad), self.assertRaises(ValueError):
                    curve_analysis.quality_ratio(*arguments)
            with self.assertRaises(ValueError):
                curve_analysis.quality_ratio(.02,.3,.4,10.,kx1=bad,kx2=.7)

    def test_ordinary_response_matches_activator_total_ceiling(self):
        L = np.array([0., .2, 3., 1e5])
        I = np.array([0., .1, 3., 100.])
        expected = reference_response(L,I,5.,.02,.3,.4,34.85,1.)
        assert_allclose(analysis.response(L,5.,.02,.3,.4,34.85,1.,I), expected)
        assert_allclose(model_s32_s47(L,I,5.,.02,.3,.4,1.,35.85), expected)

    def test_hybrid_gate_matches_note11_parameters_and_operator_count(self):
        activator = dict(kd=1.67,k1=2.69e-4,k2=7.08e-3,k3=.761)
        repressor = dict(kd=40.98,k1=1.72e-4,k2=.256,k3=225.08)
        doses = np.array([0.,.1,1.,10.])
        actual = exploratory_models.hybrid_promoter(
            .49,.21,doses,1.,activator,repressor,35.85,baseline=.01,operators=2)
        expected = combinatorial.predicted_rpu('A1',1,doses,1.)
        assert_allclose(actual,expected,rtol=1e-12)


if __name__ == '__main__':
    unittest.main()
