"""Independent equation and small-workload checks for migrated notebook algorithms."""
import unittest
import warnings

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from yeast.analysis import response, response_pair, scan_designs, fast_pareto_2d
from yeast.activator.model import model_s32_s47
from yeast.exploratory_models import (
    dimer_response, monomer_bound_pool, heterodimer_free_pools,
    heterodimer_response_pair, two_state_repression,
    simple_repression_partition_function, simple_repression_pbound,
    simple_repression_foldchange, rob_phillips_allosteric_dimer_fixed_inducer,
    operator_response, solve_operator_target, hybrid_promoter,
    crosstalk_ratio,
)
from yeast.curve_analysis import (
    get_steep_interval, saturated_fold_approximation, quality_ratio,
    log_fold_range, align_curve, grouped_statistics,
    alignment_statistics, regression_diagnostics,
)
from yeast.optimization import (fit_yield_gp, sample_candidates, select_candidates,
                                pairwise_slice, bounded_round_progress)
from yeast.notebook_parameters import load_notebook_parameters, foldchange_design_parameters


def original_response(L, kd, k1, k2, k3, Imax, I0, I, kx1=0, kx2=0):
    b = 1+k2*I+kx1+kx2*k2*I
    root = np.sqrt(b*b+8*L*(k1+k1*kx1*kx1+k2*k2*k3*I*I*(1+kx2*kx2)))
    z = L/2*(root-b)/(root+b)*kd
    return I0+Imax*z/(1+z)


class ModelMigrationTests(unittest.TestCase):
    def setUp(self):
        self.params = dict(kd=5.374494076, k1=.000268715, k2=.007083518,
                           k3=.760771692, Imax=35.84931505, I0=.01, I=100)

    def test_response_matches_notebook_and_archived_convention(self):
        L = np.logspace(-2, 2, 30)
        for nuclear in ({}, {'kx1':1.1, 'kx2':4.9}):
            p = {**self.params, **nuclear}
            assert_allclose(response(L, **p), original_response(L, **p), rtol=1e-10)
            assert_allclose(response_pair(L, **p)[1], response(L, **{**p, 'I':0}))
        p = self.params
        assert_allclose(response(L, **p), model_s32_s47(
            L, p['I'], p['kd'], p['k1'], p['k2'], p['k3'], p['I0'], p['I0']+p['Imax']))
        self.assertEqual(response(0., **p), p['I0'])
        with self.assertRaises(ValueError):
            response(-1., **p)

    def test_reduced_dimer_equation_and_monomer_comparison(self):
        L = np.array([.01, 1., 100.])
        d, kd = .3, 4.
        root = np.sqrt(1+8*L*d)
        z = L/2*(root-1)/(root+1)*kd
        assert_allclose(dimer_response(L, kd, d), z/(1+z))
        assert_allclose(dimer_response(L, kd, d, repressor=True), 1/(1+z))
        assert_allclose(monomer_bound_pool(L, 3.), .75*L)

    def test_heterodimer_conservation_and_source_state_rules(self):
        m1, m2, k = np.array([0., .1, 3.]), .5, .02
        a, b = heterodimer_free_pools(m1, m2, k)
        assert_allclose(a+k*a*b, m1)
        assert_allclose(b+k*a*b, np.full(3, m2))
        assert_allclose(heterodimer_free_pools(m1, m2, 0)[0], m1)
        p = self.params
        k = p['k2']**2*p['k3']
        root = np.sqrt(1+2*k*(m1+m2)+k*k*(m1-m2)**2)
        a_old, b_old = (-1+k*(m1-m2)+root)/(2*k), (-1-k*(m1-m2)+root)/(2*k)
        z_on = p['kd']*k*a_old*b_old*p['I']**2
        z_off = p['kd']*p['k1']*a_old*b_old
        on, off = heterodimer_response_pair(m1,m2,p['kd'],p['k1'],p['k2'],p['k3'],p['I'],
                                            p['Imax'],.035485714,.01)
        assert_allclose(on, .035485714+p['Imax']*z_on/(1+z_on), atol=1e-10)
        assert_allclose(off, .01+p['Imax']*z_off/(1+z_off), atol=1e-10)

    def test_crosstalk_and_two_state_comparison(self):
        L, kd, k1, k2, I = np.array([.1, 2., 6.]), 4., .02, .3, 10.
        first = original_response(L,kd,k1,k2,.2,35.84931505,.035485714,I)
        second = original_response(L,kd,k1,k2,.02,35.84931505,.035485714,I)
        assert_allclose(crosstalk_ratio(L,kd,k1,k2,k2,.2,.02,I),second/first)
        active, inactive = (1+I/.7)**2, (1+I/.2)**2
        assert_allclose(two_state_repression(L,kd,I,.7,.2),1/(1+active/(active+10*inactive)*L*kd))

    def test_repression_partition_and_allosteric_equations(self):
        R, DBD, N, pd, rd, P, beta = np.array([0.,1.,10.]), 2.,4.6e6,-8.,-15.,100.,1/.6
        rn = P/N*np.exp(-beta*pd)
        tf = 2*R*DBD/(1+DBD)/N*np.exp(-beta*rd)
        z = 1+rn+tf
        assert_allclose(simple_repression_partition_function(R,DBD,N,pd,rd,P),z)
        assert_allclose(simple_repression_pbound(R,DBD,N,pd,rd,P),rn/z)
        assert_allclose(simple_repression_foldchange(R,DBD,N,pd,rd,P,35), (1+rn)/z)
        interaction, K = np.exp(-beta*-5.),100.
        expected = 35*rn/(1+rn+2*R*DBD/N*np.exp(-beta*rd)*interaction*(1+K)**2/(1+K*interaction)**2)
        assert_allclose(rob_phillips_allosteric_dimer_fixed_inducer(R,DBD,N,rd,-5.,K,P,pd,35),expected)

    def test_operator_forward_inverse_and_unreachable_target(self):
        p = {**self.params, 'kx1':.001007507, 'kx2':.001604871}
        for n in (1,2,4):
            target = operator_response(2.3,n,**p)
            L, probability = solve_operator_target(target,n,**p)
            self.assertAlmostEqual(L,2.3,places=10)
            self.assertAlmostEqual(probability,(target-p['I0'])/p['Imax'])
        self.assertTrue(np.isnan(solve_operator_target(100,n,**p)[0]))
        self.assertEqual(operator_response(0,4,**p),p['I0'])
        with self.assertRaises(ValueError):operator_response(1,0,**p)

    def test_hybrid_product_gate(self):
        a = {k:self.params[k] for k in ('kd','k1','k2','k3')}
        r = dict(kd=40.97704697,k1=.000171923,k2=.256016091,k3=225.0817618)
        I1, I2 = np.array([0.,1.,10.]),np.array([10.,1.,0.])
        ap = original_response(10., **a,Imax=1,I0=0,I=I1)
        rp = original_response(10., **r,Imax=1,I0=0,I=I2)
        assert_allclose(hybrid_promoter(10,10,I1,I2,a,r,35.85,baseline=.015930056),
                        (35.85-.015930056)*ap*(1-rp)**2+.015930056,rtol=1e-10)


class AnalysisMigrationTests(unittest.TestCase):
    def test_design_scan_preserves_grid_maxima_and_pareto_ties(self):
        receptors, dbds = foldchange_design_parameters(3)
        L = np.linspace(.3,10,20)
        records = scan_designs(L,receptors[:2],dbds[:2])
        self.assertEqual(len(records),4)
        for r in records:
            receptor = next(x for x in receptors if x['LBD_name']==r['LBD_name'])
            dbd = next(x for x in dbds if x['DBD_name']==r['DBD_name'])
            on,off = response_pair(L,dbd['kd'],receptor['k1'],receptor['k2'],receptor['k3'],receptor['Imax'],dbd['I0'],receptor['I'])
            score = np.log10(on/off*(on-off))
            self.assertEqual(r['L'],L[np.argmax(score)])
            self.assertAlmostEqual(r['score'],score.max())
        assert_array_equal(fast_pareto_2d([[1,2],[1,2],[0,1],[2,1]]),[True,True,False,True])
        frontier = scan_designs(L,receptors[:2],dbds[:2],pareto=True)
        points = np.array([[r['log10_fold'],r['log10_difference']] for r in frontier])
        self.assertTrue(fast_pareto_2d(points).all())

    def test_slope_interval_and_limits(self):
        L = np.logspace(-3,2,200)
        y = .01+20*L**2/(1+L**2)
        gradient = np.gradient(np.log10(y),np.log10(L))
        idx = np.flatnonzero(gradient>.8*gradient.max())
        self.assertEqual(get_steep_interval(L,y),(L[idx[0]],L[idx[-1]]))
        self.assertTrue(np.isnan(get_steep_interval(L,np.ones(len(L)))[0]))
        with self.assertRaises(ValueError):get_steep_interval([0,1],[1,2])
        k1,kd=.02,40.
        root=np.sqrt(1+8*L*k1)
        old=(L*kd/2)/((root-1)/(root+1))/(1+L*kd/2)
        assert_allclose(saturated_fold_approximation(L,k1,kd),old,rtol=1e-10)
        self.assertAlmostEqual(saturated_fold_approximation(0,k1,kd),kd/(4*k1))

    def test_nuclear_quality_and_fold_use_canonical_parameters(self):
        L=np.array([.1,1.,5.]);k1,k2,k3,kd,I,kx1,kx2=.02,.3,.4,5.,10.,2.,.7
        self.assertAlmostEqual(quality_ratio(k1,k2,k3,I),k3*k2**2*I**2/k1)
        self.assertAlmostEqual(quality_ratio(k1,k2,k3,I,kx1=kx1,kx2=kx2),
                               k3*k2**2*I**2*(1+kx2**2)/(k1*(1+kx1**2)))
        on=original_response(L,kd,k1,k2,k3,1.,0.,I,kx1,kx2)
        off=original_response(L,kd,k1,k2,k3,1.,0.,0.,kx1,kx2)
        assert_allclose(log_fold_range(L,k1,k2,k3,kd,I,kx1=kx1,kx2=kx2),
                        np.log10([(on/off).min(),(on/off).max()]))

    def test_alignment_offsets_interpolation_and_statistics(self):
        grid=np.array([1.,2.,3.]); source=2*grid; master=3*grid
        result=align_curve([0.,1.5,4.],[0.,3.,8.],grid,source,master,offset=.2,prediction_policy='clamp')
        assert_allclose(result['corrected'],[.2,4.7,12.2])
        assert_allclose(result['predicted'],[3.,4.5,9.])
        assert_allclose(result['source_residual'],[0.,0.,0.])
        assert_allclose(result['master_residual'],[0.,1.5,4.])
        aligned=align_curve([1.,2.,3.],source,grid,source,master)
        stats=alignment_statistics([aligned,aligned])
        self.assertAlmostEqual(stats['pooled_R2'],1.)
        self.assertAlmostEqual(stats['mean_pearson_r2'],1.)
        grouped=grouped_statistics([1,1,2],[2,4,7])
        assert_allclose(grouped['mean'],[3,7])
        self.assertAlmostEqual(grouped['std'][0],np.sqrt(2))
        self.assertTrue(np.isnan(grouped['std'][1]))
        with self.assertRaises(ValueError):align_curve([1,np.nan],[1,2],grid,source,master)

    def test_regression_direction_and_in_sample_label(self):
        observed=np.array([1.,2.,4.,8.]);predicted=3*observed+2
        result=regression_diagnostics(observed,predicted)
        assert_allclose(result['fitted'],observed)
        self.assertAlmostEqual(result['slope'],1/3)
        self.assertLess(result['raw_R2'],0.)
        result=regression_diagnostics(observed,observed**2,scale='log10',direction='observed_to_predicted')
        assert_allclose(result['fitted'],observed**2)
        self.assertAlmostEqual(result['slope'],2.)
        self.assertLess(result['fitted_in_sample_R2'],0.)

    def test_parameters_are_versioned_and_not_mixed(self):
        one=load_notebook_parameters('ec50.ipynb',3)['parameters']
        two=load_notebook_parameters('ec50.ipynb',4)['parameters']
        self.assertNotEqual(one['sensor_k1']['RpaR'],two['sensor_k1']['RpaR'])
        self.assertEqual(len(foldchange_design_parameters(1)[0]),20)
        self.assertEqual(len(foldchange_design_parameters(2)[0]),5)
        self.assertEqual(len(foldchange_design_parameters(3)[0]),15)


class OptimizationMigrationTests(unittest.TestCase):
    def test_gp_candidate_selection_slicing_and_round_progress(self):
        X=np.array([[0.,0.],[0.,1.],[1.,0.],[1.,1.],[.2,.3],[.7,.8]])
        y=X[:,0]+2*X[:,1]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            gp,scaler=fit_yield_gp(X,y,restarts=0,random_state=2)
        bounds=[[0.,1.],[0.,1.]]
        candidates=sample_candidates(bounds,count=15,random_state=3)
        assert_allclose(candidates,sample_candidates(bounds,count=15,random_state=3))
        result=select_candidates(gp,scaler,candidates,top_k=4,batch_size=3)
        mean=gp.predict(scaler.transform(candidates))
        indices=np.argsort(mean)[-4:]
        assert_array_equal(result['indices'],indices)
        assert_allclose(result['mean'],mean[indices])
        self.assertEqual(select_candidates(gp,scaler,candidates,confidence_threshold=0)['points'].shape,(0,2))
        perturbed=sample_candidates(bounds,previous=[[0,0],[1,1]],random_state=3)
        self.assertEqual(perturbed.shape,(2,2))
        self.assertTrue(((perturbed>=0)&(perturbed<=1)).all())
        sliced=pairwise_slice(gp,scaler,bounds,[.5,.5],(0,1),resolution=3)
        expected=gp.predict(scaler.transform(np.column_stack((sliced['x'].ravel(),sliced['y'].ravel()))))
        assert_allclose(sliced['mean'].ravel(),expected)
        progress=bounded_round_progress([X,np.array([[.5,.5],[2.,2.]])],bounds,(0,1))
        assert_array_equal(progress['counts'],[6,1])
        assert_allclose(progress['distance'],np.linalg.norm(progress['means'][1]-progress['means'][0]))


if __name__ == '__main__':
    unittest.main()
