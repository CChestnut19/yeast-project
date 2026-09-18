"""Numerical regressions for the common log10 R-squared fitting contract."""
import importlib.util
import unittest

import numpy as np
from numpy.testing import assert_allclose

from yeast.analysis import response
from yeast import fitting


class LogR2FittingTests(unittest.TestCase):
    def setUp(self):
        self.fixed = {'kd': 2., 'k1': .03, 'k2': .2, 'k3': .7, 'Imax': 20.}

    def test_default_fits_geometric_mean_and_reports_actual_r_squared(self):
        # At zero TF only I0 remains: log SSE has the geometric-mean optimum.
        fit = fitting.fit_response(np.zeros(3), np.zeros(3), [1., 10., 100.],
                                   fixed=self.fixed, initial={'I0': 2.})
        self.assertAlmostEqual(fit['parameters']['I0'], 10., places=5)
        self.assertEqual(fit['scale'], 'log10')
        self.assertAlmostEqual(fit['objective_total'], 1.)
        self.assertAlmostEqual(fit['R2_log10'], 0.)
        self.assertAlmostEqual(fit['SSE'], 2.)
        self.assertTrue(fit['finite'] and fit['success'])

    def test_dataset_normalization_is_invariant_to_repeated_rows_in_one_group(self):
        # A: mean(log y)=1, SST=2. B: mean=2.5, SST=.5.
        # Minimize ((2(c-1)^2+2)/2 + (3(c-2.5)^2+.5)/.5)/2.
        answers = []
        for repeat in (1, 9):
            observed = np.r_[np.tile([1., 100.], repeat), 100., 10**2.5, 1000.]
            groups = ['A']*(2*repeat)+['B']*3
            fit = fitting.fit_response(np.zeros(len(observed)), np.zeros(len(observed)),
                                       observed, fixed=self.fixed, initial={'I0': 10.}, groups=groups)
            self.assertAlmostEqual(np.log10(fit['parameters']['I0']), 16/7, places=5)
            c = 16/7
            expected = ((2*(c-1)**2+2)/2 + (3*(c-2.5)**2+.5)/.5)/2
            self.assertAlmostEqual(fit['objective_total'], expected)
            self.assertAlmostEqual(fit['macro_R2_log10'], 1-expected)
            self.assertEqual(set(fit['group_metrics']), {'A', 'B'})
            answers.append(fit['parameters']['I0'])
        assert_allclose(answers[0], answers[1], rtol=1e-6)

    def test_invalid_log_observations_and_invalid_parameter_domains_are_rejected(self):
        cases = [[1., 1., 1.], [3.]*7, [0., 1., 2.], [-1., 1., 2.], [1., np.nan, 2.], [1., np.inf, 2.]]
        for observed in cases:
            with self.subTest(observed=observed), self.assertRaises(ValueError):
                fitting.fit_response([0.]*len(observed), [0.]*len(observed), observed,
                                     fixed=self.fixed, initial={'I0': 2.})
        for kwargs in ({'scale': 'raw'}, {'bounds': ([-1.], [10.])},
                       {'groups': ['A', 'A', 'B']}, {'groups': ['A', None, 'B']},
                       {'variant': 'torch_epsilon_literal'}, {'variant': 'nuclear_clamped'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                fitting.fit_response([0.]*3, [0.]*3, [1., 10., 100.],
                                     fixed=self.fixed, initial={'I0': 2.}, **kwargs)

    def test_all_notebook_cells_fit_log_response(self):
        L = np.tile([.001, .05, .5, 5., 50.], 6)
        I = np.repeat([0., .01, .1, 1., 10., 100.], 5)
        base = {'k1': .02, 'k2': .3, 'k3': .6}
        fixed = {'kd': 3., 'Imax': 20., 'I0': .002}
        for cell in (0, 1, 2):
            initial = {**base, **({'kx1': .1, 'kx2': .2} if cell == 1 else {})}
            observed = response(L, I=I, **fixed, **initial)*np.tile([.7, 1.4, .9, 1.2, .8], 6)
            fit = fitting.fit_notebook_curve_fit(L, I, observed, cell=cell, fixed=fixed,
                                                initial=initial, maxfev=10000)
            self.assertEqual(fit['scale'], 'log10')
            log_y = np.log10(observed)
            objective = np.sum((np.log10(fit['prediction'])-log_y)**2)/np.sum((log_y-log_y.mean())**2)
            self.assertAlmostEqual(fit['objective_total'], objective)
            reference = fitting.fit_response(L, I, observed, fixed=fixed, initial=initial)
            self.assertLessEqual(fit['objective_total'], reference['objective_total']+1e-6)
            self.assertTrue(fit['success'] and fit['finite'])

    def test_shared_stage_uses_macro_objective_and_canonical_amplitude(self):
        # Recompute shared objective independently from each dataset's log SST.
        common = {'k1': .03, 'k2': .2, 'k3': .7}
        L = np.array([0., .01, .1, 1., 10.])
        I = np.array([0., .1, 1., 10., 100.])
        data = [{'name': name, 'L': L, 'I': I,
                 'observed': response(L, I=I, kd=kd, Imax=20., I0=.1, **common)}
                for name, kd in [('A', 2.), ('B', 5.)]]
        fit = fitting.fit_shared_then_kd(data, initial_shared=common, Imax=20., I0=.1, initial_kd=2.)
        shared = fit['shared']
        manual = []
        for index, dataset in enumerate(data):
            y = np.log10(dataset['observed'])
            prediction = shared['prediction'][index*5:(index+1)*5]
            manual.append(np.sum((np.log10(prediction)-y)**2)/np.sum((y-y.mean())**2))
        self.assertAlmostEqual(shared['objective_total'], np.mean(manual))
        for dataset in data:
            fitted = fit['datasets'][dataset['name']]
            expected = response(L, I=I, Imax=20., I0=.1, **shared['parameters'], **fitted['parameters'])
            assert_allclose(fitted['prediction'], expected, rtol=1e-13)
            self.assertEqual(fitted['prediction'][0], .1)

    def test_exact_M_inversion_recovers_canonical_mass_balance(self):
        estimate_M = getattr(fitting, 'estimate_M', None)
        self.assertIsNotNone(estimate_M, 'Exact mass-balance estimate_M is missing')
        baseline, amplitude, k1, k2, k3, kd, I, L = .01, 2.5, .03, .2, .7, 4., 3., 1.
        maximum = response(L, kd, k1, k2, k3, amplitude, baseline, I)
        self.assertAlmostEqual(estimate_M(baseline, maximum, kd, I, k1=k1, k2=k2), k2*k2*k3)
        for maximum in (baseline, baseline+amplitude*.9, np.nan):
            with self.assertRaises(ValueError):
                estimate_M(baseline, maximum, kd, I, k1=k1, k2=k2)

    def test_exact_inversion_accepts_zero_M_despite_roundoff(self):
        for k1 in (.03, 1., 1e-8):
            maximum = response(1., 4., k1, 1., 0., 2.5, .01, 3.)
            self.assertAlmostEqual(fitting.estimate_M(.01, maximum, 4., 3., k1=k1, k2=1.), 0., places=14)

    def test_raw_diagnostic_underflow_cannot_break_valid_log_fit(self):
        fixed = {**self.fixed, 'I0': 1e-200}
        del fixed['kd']
        fit = fitting.fit_response([0., 0.], [0., 0.], [1e-200, 1e-199],
                                   fixed=fixed, initial={'kd': 2.})
        self.assertTrue(fit['finite'])
        self.assertAlmostEqual(fit['raw_R2'], -1.)

    def test_known_LBD_parameters_give_exact_grouped_initialization(self):
        rows = []
        fixed_lbd = {'X': {'k1': .03, 'k2': .2}, 'Y': {'k1': .08, 'k2': .4}}
        for dbd, kd in [('A', 2.), ('B', 5.)]:
            for lbd, constants in fixed_lbd.items():
                p = dict(constants, k3=.7, kd=kd, Imax=2.5, I0=.01)
                basal, induced = response([1., 1.], I=[0., 3.], **p)
                self.assertAlmostEqual(fitting.estimate_kd(.01, basal, constants['k1']), kd)
                rows.append({'ID': dbd+'-'+lbd, 'I0': .01, 'P0': basal, 'Pmax': induced, 'I': 3.})
        estimate = fitting.estimate_shared_parameters(rows, fixed_lbd=fixed_lbd)
        assert_allclose(estimate['DBD'].set_index('DBD').loc[['A', 'B'], 'kd'], [2., 5.])
        assert_allclose(estimate['LBD'].set_index('LBD').loc[['X', 'Y'], 'M'], [.028, .112])
        with self.assertRaises(ValueError):
            fitting.estimate_shared_parameters(rows, fixed_lbd={'X': fixed_lbd['X']})

    def test_per_observation_kd_and_explicit_curve_fit_bounds(self):
        L = np.tile([.02, .2, 2., 20.], 5)
        I = np.repeat([0., .1, 1., 10., 100.], 4)
        fixed = {'kd': np.tile([1., 2., 4., 8.], 5), 'Imax': 20., 'I0': .02}
        actual = {'k1': .02, 'k2': .3, 'k3': .6}
        observed = response(L, I=I, **fixed, **actual)
        fit = fitting.fit_response(L, I, observed, fixed=fixed,
                                   initial={'k1': .03, 'k2': .2, 'k3': .8})
        assert_allclose(list(fit['parameters'].values()), list(actual.values()), rtol=1e-5)
        bounded = fitting.fit_notebook_curve_fit(
            L, I, observed, cell=0, fixed=fixed, initial={'k1': .01, 'k2': .3, 'k3': .6},
            bounds=([1e-6, 1e-6, 1e-6], [.015, 10., 100.]))
        self.assertLessEqual(bounded['parameters']['k1'], .015)
        self.assertGreater(bounded['objective_total'], 0.)
        self.assertTrue(bounded['success'])


@unittest.skipUnless(importlib.util.find_spec('torch'), 'Torch is optional')
class AdamLogR2Tests(unittest.TestCase):
    def test_untrained_backend_matches_canonical_formula_and_macro_objective(self):
        L = np.array([0., 1e-8, .1, 1., 10.])
        I = np.array([0., 0., .1, 1., 10.])
        for nuclear in (False, True):
            params = {'k1': .03, 'k2': .2, 'k3': .7}
            if nuclear:
                params.update(kx1=.1, kx2=.0001)
            expected = response(L, I=I, kd=2., Imax=20., I0=.1, **params)
            datasets = [{'name': 'A', 'L': L, 'I': I, 'observed': expected*np.array([1., 2., .5, 1., 1.])},
                        {'name': 'B', 'L': np.tile(L, 3), 'I': np.tile(I, 3), 'observed': np.tile(expected*1.3, 3)}]
            fit = fitting.fit_shared_then_kd_adam(datasets, initial_shared=params, Imax=20., I0=.1,
                                                 initial_kd=2., shared_steps=0, kd_steps=0)
            assert_allclose(fit['shared']['prediction'], np.tile(expected, 4), rtol=2e-14, atol=0)
            self.assertEqual(fit['shared']['prediction'][0], .1)
            terms = []
            for data in datasets:
                p = response(data['L'], I=data['I'], kd=2., Imax=20., I0=.1, **params)
                y = np.log10(data['observed'])
                terms.append(np.sum((np.log10(p)-y)**2)/np.sum((y-y.mean())**2))
            self.assertAlmostEqual(fit['shared']['objective_total'], np.mean(terms))
            self.assertTrue(fit['finite'])
            self.assertFalse(fit['shared']['converged'])

    def test_adam_improves_log_objective_with_positive_meaningful_parameters(self):
        L = np.tile([.01, .1, 1., 10.], 3)
        I = np.repeat([0., 1., 10.], 4)
        params = {'k1': .03, 'k2': .2, 'k3': .7}
        target = response(L, I=I, kd=2., Imax=20., I0=.1, **params)
        data = [{'name': 'A', 'L': L, 'I': I, 'observed': target}]
        kwargs = dict(initial_shared={'k1': .06, 'k2': .35, 'k3': 1.}, Imax=20., I0=.1, initial_kd=2.)
        start = fitting.fit_shared_then_kd_adam(data, **kwargs, shared_steps=0, kd_steps=0)
        end = fitting.fit_shared_then_kd_adam(data, **kwargs, shared_steps=200, kd_steps=50, learning_rate=.02)
        self.assertLess(end['shared']['objective_total'], start['shared']['objective_total']/20)
        self.assertTrue(end['finite'])
        self.assertTrue(all(v > 0 for v in end['shared']['parameters'].values()))

    def test_adam_updates_keep_equal_dataset_weight_when_rows_are_repeated(self):
        L = np.array([.01, .1, 1., 10.])
        I = np.array([0., .1, 1., 10.])
        params = {'k1': .03, 'k2': .2, 'k3': .7}
        target = response(L, I=I, kd=2., Imax=20., I0=.1, **params)
        fitted = []
        for repeat in (1, 7):
            datasets = [{'name': 'A', 'L': np.tile(L, repeat), 'I': np.tile(I, repeat),
                         'observed': np.tile(target*[.8, 1.4, .7, 1.2], repeat)},
                        {'name': 'B', 'L': L, 'I': I, 'observed': target*[1.1, .7, 1.5, .8]}]
            fit = fitting.fit_shared_then_kd_adam(datasets, initial_shared=params, initial_kd=2.,
                                                 Imax=20., I0=.1, shared_steps=30, kd_steps=0)
            fitted.append(list(fit['shared']['parameters'].values()))
        assert_allclose(fitted[0], fitted[1], rtol=1e-12, atol=0.)


if __name__ == '__main__':
    unittest.main()
