"""SI keyword contracts and independent numerical checks for the naming migration."""
import unittest
import importlib.util
import numpy as np
from numpy.testing import assert_allclose

from yeast import analysis, binding, fitting, exploratory_models, notebook_parameters
from yeast.activator import model as activator
from yeast.repressor import model as repressor
from yeast.repressor import pipeline as repressor_pipeline


class SINamesTests(unittest.TestCase):
    def si_call(self, function, **kwargs):
        try:
            return function(**kwargs)
        except (TypeError, KeyError, AttributeError) as error:
            self.fail(f"SI naming contract is unavailable: {error}")

    def test_response_keywords_preserve_mass_balance_and_amplitude(self):
        # Free monomer = 1 at both points; active pools = 1 and 1.75.
        result = self.si_call(analysis.response, c_TF_all=np.array([0., 4., 6.5]),
                              c_I=np.array([0., 1., 2.]), KA=3., Kd0=.75,
                              Kb=1., Kd1=.25, Tmax_minus_T0=10., T0=.2)
        assert_allclose(result, [.2, 7.7, 8.6], rtol=1e-13)

    def test_pool_keywords_keep_active_pool_not_free_monomer(self):
        result = self.si_call(binding.cic_dimer_pool, c_TF_all=np.array([4., 6.5]),
                              c_I=np.array([1., 2.]), Kd0=.75, Kb=1., Kd1=.25)
        assert_allclose(result, [1., 1.75], rtol=1e-13)

    def test_activator_total_ceiling_is_distinct_from_amplitude(self):
        result = self.si_call(activator.model_s32_s47, c_TF_all=np.array([4., 6.5]),
                              c_I=np.array([1., 2.]), KA=3., Kd0=.75,
                              Kb=1., Kd1=.25, T0=.2, Tmax=10.2)
        assert_allclose(result, [7.7, 8.6], rtol=1e-13)

    def test_parameter_fit_accepts_and_exports_si_keys(self):
        result = self.si_call(fitting.fit_response, c_TF_all=np.array([4., 6.5]),
                              c_I=np.array([1., 2.]), observed=np.array([7.7, 8.6]),
                              fixed=dict(Kd0=.75, Kb=1., Kd1=.25,
                                         Tmax_minus_T0=10., T0=.2), initial={'KA': 2.})
        self.assertAlmostEqual(result['parameters']['KA'], 3., places=6)
        self.assertLess(result['objective_total'], 1e-12)

    def test_shared_scipy_fit_consumes_si_dataset_keys(self):
        function = getattr(fitting, 'fit_shared_then_KA', None)
        self.assertIsNotNone(function)
        result = self.si_call(function,
            datasets=[dict(name='one', c_TF_all=[4., 6.5], c_I=[1., 2.], observed=[7.7, 8.6])],
            initial_shared=dict(Kd0=.75, Kb=1., Kd1=.25),
            Tmax_minus_T0=10., T0=.2, initial_KA=3., max_nfev=1)
        self.assertLess(result['shared']['objective_total'], 1e-12)
        self.assertAlmostEqual(result['datasets']['one']['parameters']['KA'], 3., places=12)

    @unittest.skipUnless(importlib.util.find_spec('torch'), 'Optional Torch runtime unavailable')
    def test_shared_adam_fit_consumes_si_dataset_keys(self):
        function = getattr(fitting, 'fit_shared_then_KA_adam', None)
        self.assertIsNotNone(function)
        result = self.si_call(function,
            datasets=[dict(name='one', c_TF_all=[4., 6.5], c_I=[1., 2.], observed=[7.7, 8.6])],
            initial_shared=dict(Kd0=.75, Kb=1., Kd1=.25),
            Tmax_minus_T0=10., T0=.2, initial_KA=3., shared_steps=0, KA_steps=0)
        self.assertLess(result['shared']['objective_total'], 1e-12)
        self.assertAlmostEqual(result['datasets']['one']['parameters']['KA'], 3., places=12)

    def test_basal_inverse_estimates_association_not_dissociation(self):
        function = getattr(fitting, 'estimate_KA', None)
        self.assertIsNotNone(function, 'SI association estimator is missing')
        result = self.si_call(function, T0=.2, basal_output=7.7, Kd0=.75,
                              Tmax_minus_T0=10., c_TF_all=2.5)
        self.assertAlmostEqual(float(result), 4., places=12)

    def test_induced_coefficient_is_not_mistaken_for_free_monomer_or_q(self):
        function = getattr(fitting, 'estimate_Kb2_Kd1', None)
        self.assertIsNotNone(function, 'Induced coefficient estimator is missing')
        result = self.si_call(function, T0=.2, maximum_output=8.6, KA=3., c_I=2.,
                              Kd0=.75, Kb=1., Tmax_minus_T0=10., c_TF_all=6.5)
        self.assertAlmostEqual(float(result), .25, places=12)

    def test_grouped_estimation_uses_si_input_and_output_columns(self):
        table = [{'DBD': 'D', 'LBD': 'R', 'T0': .2, 'T_OFF': 8.2,
                  'T_ON': 7.7, 'c_I': 1.}]
        result = self.si_call(fitting.estimate_shared_parameters, table=table,
                              fixed_lbd={'R': {'Kd0': .75, 'Kb': 1.}},
                              Tmax_minus_T0=10., c_TF_all=4.)
        self.assertAlmostEqual(result['DBD']['KA'].iloc[0], 3., places=12)
        self.assertAlmostEqual(result['LBD']['Kb2_Kd1'].iloc[0], .25, places=12)

    def test_hybrid_uses_ka_for_activator_and_kr_for_repressor(self):
        result = self.si_call(exploratory_models.hybrid_promoter,
                              c_TF_all_activator=4., c_TF_all_repressor=4.,
                              c_I_activator=1., c_I_repressor=1.,
                              activator=dict(KA=3., Kd0=.75, Kb=1., Kd1=.25),
                              repressor=dict(KR=3., Kd0=.75, Kb=1., Kd1=.25),
                              Tmax=10.2, T0=.2, operators=2)
        self.assertAlmostEqual(float(result), .66875, places=12)

    def test_repressor_exports_kr_and_si_kinetics(self):
        settings = repressor.model_settings()
        self.assertIn('Kd0', settings)
        self.assertIn('KR', settings['sensors']['CI94'])
        self.assertAlmostEqual(settings['sensors']['CI94']['KR'], 30.08697891)
        result = self.si_call(repressor.model_components, sensor='CI94',
                              c_TF_all=0., c_I=10.)
        self.assertEqual(result['p_unbound'], 1.)
        self.assertEqual(result['p_permissive'], 1.)
        self.assertAlmostEqual(result['prediction'], 1.62)

    def test_original_csv_is_normalized_to_si_prediction_columns(self):
        rows = repressor_pipeline.read_data(repressor_pipeline.DEFAULT_DATA)
        self.assertEqual(len(rows), 1141)
        self.assertIn('c_TF_all', rows[0])
        self.assertIn('c_I', rows[0])
        predictions = repressor_pipeline.calculate_predictions(rows)
        self.assertTrue(all(np.isfinite(row['prediction_rpu']) for row in predictions))

    def test_historical_parameters_are_adapted_without_overwriting_source(self):
        source = self.si_call(notebook_parameters.load_notebook_parameters,
                              notebook='box.ipynb', cell=0, parameter_names='source')
        modern = notebook_parameters.load_notebook_parameters('box.ipynb', 0)
        self.assertIn('Imax', source['parameters'])
        self.assertEqual(modern['parameters']['Tmax_minus_T0'], source['parameters']['Imax'])

    def test_historical_collections_and_numbered_parameters_use_si_names(self):
        load = notebook_parameters.load_notebook_parameters
        source = load('ec50.ipynb', 2, parameter_names='source')['parameters']
        modern = load('ec50.ipynb', 2)['parameters']
        self.assertEqual(modern['Kd0_by_sensor'], source['sensor_k1'])
        self.assertEqual(modern['Kb_by_sensor'], source['sensor_k2'])
        self.assertEqual(modern['Kd1_by_sensor'], source['sensor_k3'])
        self.assertEqual(modern['c_I_by_sensor'], source['sensor_I'])
        self.assertEqual(modern['Kx1_by_sensor'], source['nuclear_kx1'])
        source = load('plot4.ipynb', 14, parameter_names='source')['parameters']
        modern = load('plot4.ipynb', 14)['parameters']
        self.assertEqual(modern['KA_values'], source['kds'])
        self.assertEqual(modern['T0_values'], source['I0s'])
        source = load('plot6.ipynb', 3, parameter_names='source')['parameters']
        modern = load('plot6.ipynb', 3)['parameters']
        self.assertEqual(modern['KA_1'], source['kd1'])
        self.assertEqual(modern['Kd1'], source['k3'])  # kd1 is operator #1.

    def test_comparison_model_parameters_keep_their_physical_roles(self):
        load = notebook_parameters.load_notebook_parameters
        source = load('box.ipynb', 9, parameter_names='source')['parameters']['LBD_parameters'][0]
        modern = load('box.ipynb', 9)['parameters']['LBD_parameters'][0]
        self.assertEqual(modern['active_dissociation'], source['k2'])
        self.assertEqual(modern['inactive_dissociation'], source['k1'])
        self.assertNotIn('Kb', modern)
        source = load('plot6.ipynb', 0, parameter_names='source')['parameters']
        modern = load('plot6.ipynb', 0)['parameters']
        self.assertEqual(modern['basal_dimer_coefficient'], source['kb'])
        self.assertEqual(modern['induced_dimer_coefficient'], source['kc'])

    def test_historical_hybrid_distinguishes_activator_and_repressor_parameters(self):
        load = notebook_parameters.load_notebook_parameters
        for cell in (1, 2):
            source = load('plot7.ipynb', cell, parameter_names='source')['parameters']['promoter']
            modern = load('plot7.ipynb', cell)['parameters']['promoter']
            self.assertEqual(modern['KA'], source['kd1'])
            self.assertEqual(modern['KR'], source['kd2'])
            self.assertEqual(modern['Kd1_activator'], source['k31'])
            self.assertEqual(modern['Kd1_repressor'], source['k32'])
            self.assertEqual(modern['Tmax_minus_T0_repressor'], source['Imax2'])
            self.assertEqual(modern['T0_activator'], source['I01'])

    def test_historical_enhancement_multiplier_is_not_an_induced_coefficient(self):
        load = notebook_parameters.load_notebook_parameters
        for cell in (0, 1):
            source = load('ec50.ipynb', cell, parameter_names='source')['parameters']
            modern = load('ec50.ipynb', cell)['parameters']
            self.assertEqual(modern['historical_dimer_enhancement_factor'], source['M'])
            self.assertNotIn('Kb2_Kd1', modern)

    def test_historical_design_adapter_drives_si_scan(self):
        receptors, dbds = notebook_parameters.foldchange_design_parameters(cell=3)
        self.assertIn('KA', dbds[0])
        self.assertIn('Tmax_minus_T0', receptors[0])
        rows = analysis.scan_designs(np.array([.3, 1., 3.]), receptors[:1], dbds[:1])
        self.assertTrue(rows)
        self.assertIn('c_TF_all', rows[0])
        self.assertTrue(np.isfinite(rows[0]['RPU']))


if __name__ == '__main__':
    unittest.main()
