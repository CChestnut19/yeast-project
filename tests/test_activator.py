"""Activator regressions use synthetic workbook data, not manuscript observations."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from activator_fixture import make_source_package, write_workbook
from yeast.activator import model
from yeast.activator.aggregation import conditional_means, plot_summaries
from yeast.activator.parameters import read_manuscript_parameters, dbd_parameters_for_panel, normalized_operator
from yeast.activator.panels import PANELS
from yeast.activator.recalculate import run_recalculation
from yeast.activator.source import (parse_cell, read_sheet, load_source_package, read_csv,
                                   write_csv, write_json, sha256, excel_col, cell_coordinates)
from yeast.activator.validate import validate, as_bool, log10_r2, source_change_audit
from yeast import analysis


class ActivatorUnitTests(unittest.TestCase):
    def test_panel_mapping_and_units(self):
        self.assertEqual(len(PANELS), 27)
        self.assertEqual(len({p.panel_id for p in PANELS}), 27)
        self.assertEqual({p.dose_unit for p in PANELS}, {"uM", "nM"})
        self.assertEqual(model.unit_factor("nM"), .001)
        self.assertEqual(model.unit_factor("mM"), 1000)
        with self.assertRaises(ValueError):
            model.unit_factor("unknown")

    def test_starred_values_and_excel_coordinates(self):
        self.assertEqual(parse_cell("RPU= 1.23*"), (1.23, True))
        self.assertEqual(parse_cell(" 4 * "), (4, True))
        self.assertEqual(parse_cell(float("inf")), (None, False))
        self.assertEqual(parse_cell(True), (None, False))
        self.assertEqual(excel_col(74), "BW")
        self.assertEqual(cell_coordinates("$BW$296"), (295, 74))
        with self.assertRaises(ValueError):
            cell_coordinates("A0")

    def test_shared_response_and_total_output_window(self):
        tf, dose, ka, kd0, kb, kd1, t0, ceiling = 2, 10, 2, .001, .1, .5, .016, 35.85
        legacy = analysis.response_pair(tf, ka, kd0, kb, kd1, ceiling-t0, t0, dose)[0]
        self.assertAlmostEqual(float(model.model_s32_s47(tf,dose,ka,kd0,kb,kd1,t0)), float(legacy))
        self.assertAlmostEqual(float(model.model_s32_s47(0,dose,ka,kd0,kb,kd1,t0)), t0)

    def test_model_rejects_invalid_domain(self):
        for bad in (-1, float("nan"), float("inf")):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                model.model_s32_s47(1,bad,2,.001,.1,.5,.016)
        with self.assertRaises(ValueError):
            model.model_s32_s47(1,1,2,.001,.1,.5,40)

    def test_r2_is_not_correlation_squared(self):
        actual = [1, 2, 4, 8]
        predicted = [10, 20, 40, 80]
        r2, count, omitted = model.r2_coefficient(actual, predicted, "log10")
        self.assertLess(r2, 0)
        self.assertAlmostEqual(model.pearson(actual,predicted,"log10")[1], 1)
        independent, used = log10_r2(actual,predicted)
        self.assertAlmostEqual(independent, r2)
        self.assertEqual((count,omitted,used), (4,0,4))
        r2,n,omitted = model.r2_coefficient([0,1,2,np.nan], [1,1,2,1], "log10")
        self.assertEqual((r2,n,omitted), (1,2,2))

    def test_r2_rejects_broadcast_and_zip_truncation(self):
        with self.assertRaises(ValueError):
            model.r2_coefficient([1,2,3],[1],"raw")
        with self.assertRaises(ValueError):
            model.r2_coefficient([1,2],[1,2],"typo")
        with self.assertRaises(ValueError):
            log10_r2([1,2],[1])
        with self.assertRaises(ValueError):
            as_bool("not false")

    def test_imports_and_help_have_no_output_side_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1")
            for arguments in (["-c","import yeast.activator.recalculate, yeast.activator.validate"],
                              ["-m","yeast.activator","--help"]):
                result = subprocess.run([sys.executable,*arguments],cwd=directory,env=env,capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertEqual(list(Path(directory).iterdir()),[])

    def test_workbook_cached_formula_green_fill_and_missing_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/"test.xlsx"
            write_workbook(path,{(1,1):3,(2,2):"4*"},green={(2,2)},formula=((1,1),"1+2",True))
            payload,green=read_sheet(path)
            self.assertEqual(payload["values"][1][1],3)
            self.assertEqual(payload["values"][0],[None,None,None])
            self.assertEqual(payload["formulas"][1][1],"=1+2")
            self.assertEqual(green,{(2,2)})
            write_workbook(path,{(0,0):3},formula=((0,0),"1+2",False))
            with self.assertRaisesRegex(ValueError,"no cached value"):
                read_sheet(path)


class ActivatorWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.temp.name)
        cls.xlsx,cls.tsv=make_source_package(cls.root/"source")
        cls.output=cls.root/"output"
        cls.metadata=run_recalculation(cls.xlsx,cls.tsv,cls.output)
        cls.numeric=cls.output/"02_numeric_reconstruction"
        cls.dbds,cls.lbds=read_manuscript_parameters(cls.tsv)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_27_panels_match_original_archive_reference(self):
        golden=json.loads((ROOT/"tests/fixtures/activator_reference_summary.json").read_text(encoding="utf-8"))
        for filename,count in golden["row_counts"].items():
            if filename == "01_recalculated_statistics.csv":
                # The archived count includes one inconsistent S83 sensitivity per panel.
                count -= 27
            self.assertEqual(len(read_csv(self.numeric/filename)),count,filename)
        rows=[r for r in read_csv(self.numeric/"01_recalculated_statistics.csv") if r["analysis_id"]=="batch_conditional_log10"]
        for row in rows:
            self.assertAlmostEqual(float(row["R2"]),golden["log10_r2"][row["panel_id"]],places=12)
        summary=validate(self.output)
        self.assertEqual(summary["panels_checked"],27)
        self.assertEqual(summary["conditional_groups_independently_rebuilt"],1824)
        self.assertEqual(summary["dose_response_measurements_starred_excluded"],1)
        self.assertFalse(summary["previous_comparison_performed"])

    def test_parameter_override_preserves_source_table(self):
        panel=next(p for p in PANELS if p.dbd=="LexAec87")
        key=normalized_operator(panel.operator)
        original=dict(self.dbds[key])
        selected=dbd_parameters_for_panel(panel,self.dbds)
        self.assertEqual(selected["KA"],.74)
        self.assertEqual(selected["T0_variant"],.016)
        self.assertEqual(self.dbds[key],original)

    def test_source_snapshot_mismatch_is_rejected(self):
        payload,_=read_sheet(self.xlsx)
        path=self.root/"mismatch.json"
        payload["values"][0][0]="wrong source"
        write_json(path,payload)
        with self.assertRaisesRegex(ValueError,"does not match"):
            load_source_package(self.xlsx,path)

    def test_star_and_green_rules_and_batches_remain_separate(self):
        raw=read_csv(self.numeric/"01_raw_measurements_long.csv")
        starred=[r for r in raw if as_bool(r["starred_in_workbook"])]
        self.assertTrue(starred)
        self.assertTrue(all(not as_bool(r["included_primary"]) for r in starred))
        green=[r for r in raw if as_bool(r["green_fill_in_workbook"]) and not as_bool(r["starred_in_workbook"])]
        self.assertTrue(green)
        self.assertTrue(all(as_bool(r["included_primary"]) and not as_bool(r["included_green_exclusion_sensitivity"]) for r in green))
        conditional=read_csv(self.numeric/"01_conditional_means_for_R2.csv")
        groups=[r for r in conditional if r["panel_id"]=="SN9-P1-D" and r["plot_type"]=="dose_response"]
        self.assertEqual(len({r["batch_id"] for r in groups}),12)

    def test_plot_pool_respects_30_percent_input_tolerance(self):
        rows=read_csv(self.numeric/"01_plot_input_30pct_audit.csv")
        self.assertTrue(all(float(r["cluster_max_relative_deviation"])<=.3+1e-12 for r in rows))
        self.assertTrue(all(float(r["batch_relative_deviation_from_cluster_mean"])<=.3+1e-12 for r in rows))

    def test_identical_inputs_in_different_batches_are_not_pooled_for_r2(self):
        template=next(r for r in read_csv(self.numeric/"01_raw_measurements_long.csv")
                      if r["panel_id"]==PANELS[0].panel_id and r["plot_type"]=="dose_response")
        rows=[]
        for batch,responses in (("A",[1,9]),("B",[100,200])):
            for value in responses:
                row=dict(template,batch_id=batch,response_rpu=value,included_primary=True,
                         actual_input_rpu=1,nominal_input_rpu=1,inducer_concentration_source=1,
                         inducer_concentration_uM=1)
                rows.append(row)
        conditional=conditional_means(rows,self.dbds,self.lbds,panels=[PANELS[0]])
        self.assertEqual([r["mean_response_rpu"] for r in conditional],[5,150])
        plotted,_=plot_summaries(rows,self.dbds,self.lbds,panels=[PANELS[0]])
        self.assertEqual(len(plotted),1)
        self.assertEqual(plotted[0]["mean_response_rpu"],77.5)

    def test_workbook_without_starred_observations_is_supported(self):
        xlsx,tsv=make_source_package(self.root/"no_stars_source",starred=False)
        output=self.root/"no_stars_output"
        run_recalculation(xlsx,tsv,output)
        self.assertEqual(validate(output)["dose_response_measurements_starred_excluded"],0)

    def test_non_numeric_response_is_not_silently_dropped(self):
        from yeast.activator.measurements import extract_measurements
        payload,green=load_source_package(self.xlsx)
        payload["values"][147][20]="broken value"
        with self.assertRaisesRegex(ValueError,"Non-numeric response at U148"):
            extract_measurements(payload["values"],green)

    def test_invalid_or_duplicate_parameter_cells_fail(self):
        path=self.root/"bad.tsv"
        original=self.tsv.read_text(encoding="utf-8")
        path.write_text(original+original.splitlines()[1]+"\n",encoding="utf-8")
        with self.assertRaisesRegex(ValueError,"Duplicate manuscript table cell"):
            read_manuscript_parameters(path)

    def test_tampered_artifact_fails_checksum(self):
        path=self.numeric/"01_recalculated_statistics.csv"
        original=path.read_bytes()
        try:
            path.write_bytes(original+b"\n")
            with self.assertRaisesRegex(ValueError,"checksum mismatch"):
                validate(self.output)
        finally:
            path.write_bytes(original)

    def test_independent_prediction_validation_runs_under_python_optimized(self):
        path=self.numeric/"01_conditional_means_for_R2.csv"
        manifest_path=self.numeric/"01_numeric_freeze_manifest.json"
        original,old_manifest=path.read_bytes(),manifest_path.read_bytes()
        try:
            rows=read_csv(path)
            row=next(r for r in rows if r["plot_type"]=="dose_response")
            row["prediction_primary_rpu"]=float(row["prediction_primary_rpu"])*1.5
            write_csv(path,rows)
            manifest=json.loads(old_manifest)
            manifest["outputs"]["02_numeric_reconstruction/"+path.name]=sha256(path)
            write_json(manifest_path,manifest)
            result=subprocess.run([sys.executable,"-O","-m","yeast.activator","validate","--output-dir",str(self.output)],
                                  cwd=ROOT,capture_output=True,text=True,timeout=30)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn("Independent prediction mismatch",result.stderr)
            status=json.loads((self.output/"04_qa/02_log10_R2_QA_summary.json").read_text())
            self.assertEqual(status["status"],"FAIL")
        finally:
            path.write_bytes(original)
            manifest_path.write_bytes(old_manifest)

    def test_previous_audit_is_optional_but_validated_when_requested(self):
        previous=self.root/"previous"
        numeric=previous/"02_numeric_reconstruction"
        numeric.mkdir(parents=True,exist_ok=True)
        (numeric/"source_sheet_dump.json").write_bytes((self.numeric/"source_sheet_dump.json").read_bytes())
        (numeric/"01_raw_measurements_long.csv").write_bytes((self.numeric/"01_raw_measurements_long.csv").read_bytes())
        result=validate(self.output)
        write_csv(previous/"04_quantitative_audit/03_R2_three_metrics_batch_specific.csv",
                  read_csv(self.output/"03_results/Supplementary_Note_9_log10_R2_recheck.csv"))
        compared=validate(self.output,previous)
        self.assertTrue(compared["previous_comparison_performed"])
        self.assertEqual(compared["changed_source_cells"],0)
        with self.assertRaises(FileNotFoundError):
            validate(self.output,self.root/"missing_previous")

    def test_source_change_audit_preserves_cell_addresses(self):
        path=self.root/"changed_dump.json"
        payload=json.loads((self.numeric/"source_sheet_dump.json").read_text())
        payload["values"][0][0]="2*"
        write_json(path,payload)
        changes=source_change_audit(self.numeric/"source_sheet_dump.json",path)
        self.assertEqual(changes,[dict(source_cell="A1",previous_value=None,new_value="2*",previous_starred=False,new_starred=True)])

    def test_check_cli_reads_inputs_without_creating_output(self):
        output=self.root/"check_only"
        result=subprocess.run([sys.executable,"-m","yeast.activator","check","--source-xlsx",str(self.xlsx),
                               "--parameter-table",str(self.tsv),"--output-dir",str(output)],
                              cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
