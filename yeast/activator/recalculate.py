"""Reconstruct the supplied activator analyses using fixed manuscript parameters."""
from __future__ import annotations
from pathlib import Path
import platform
import statistics
import sys
from datetime import datetime, timezone
import numpy as np
from .panels import PANELS
from .parameters import dbd_parameters_for_panel
from .settings import TMAX_PRIMARY, TMAX_ALTERNATE
from .model import model_s32_s47, r2_coefficient, pearson, unit_factor
from .source import write_csv, sha256, write_json
from .aggregation import conditional_means, plot_summaries


def reconstruct(raw_rows, dbd_params, lbd_params, output_dir: Path, panels=PANELS):
    """Write numeric tables. No fitting or change to manuscript parameters occurs."""
    output_dir = Path(output_dir)
    OUT = output_dir / "02_numeric_reconstruction"
    OUT.mkdir(parents=True, exist_ok=True)
    condition_rows = conditional_means(raw_rows, dbd_params, lbd_params, panels)
    plot_rows, plot_input_audit_rows = plot_summaries(raw_rows, dbd_params, lbd_params, panels)
    parameter_rows: list[dict] = []
    for panel in panels:
        dp = dbd_parameters_for_panel(panel, dbd_params)
        lp = lbd_params[panel.lbd]
        for name, value, unit, source in [
            ("KA", dp["KA"], "normalized inverse active-pool unit", dp["KA_source_locator"]),
            ("T0_variant", dp["T0_variant"], "RPU", dp["source_locator"]),
            ("Kd0", lp["Kd0"], "dimensionless under manuscript normalization", lp["source_locator"]),
            ("Kb", lp["Kb"], "uM^-1", lp["source_locator"]),
            ("Kd1", lp["Kd1"], "dimensionless", lp["source_locator"]),
            ("Tmax_primary", TMAX_PRIMARY, "RPU", "Supplementary Note 8.1 paragraphs 402-404"),
            ("Tmax_sensitivity", TMAX_ALTERNATE, "RPU", "Former continuity value retained as sensitivity"),
        ]:
            parameter_rows.append({
                "panel_id": panel.panel_id,
                "construct": panel.construct,
                "component_type": "DBD" if name in {"KA", "T0_variant"} else ("LBD" if name in {"Kd0", "Kb", "Kd1"} else "global"),
                "component_name": panel.dbd if name in {"KA", "T0_variant"} else (panel.lbd if name in {"Kd0", "Kb", "Kd1"} else "promoter output window"),
                "parameter": name,
                "value": value,
                "unit": unit,
                "source_locator": source,
                "role": "primary" if name != "Tmax_sensitivity" else "predeclared sensitivity",
            })

    stats_rows: list[dict] = []
    for panel in panels:
        cond = [r for r in condition_rows if r["panel_id"] == panel.panel_id and r["plot_type"] == "dose_response"]
        raw = [r for r in raw_rows if r["panel_id"] == panel.panel_id and r["plot_type"] == "dose_response" and r["included_primary"]]
        raw_no_green = [r for r in raw if r["included_green_exclusion_sensitivity"]]
        y_cond = np.array([r["mean_response_rpu"] for r in cond], float)
        y_raw = np.array([r["response_rpu"] for r in raw], float)
        dp = dbd_parameters_for_panel(panel, dbd_params)
        lp = lbd_params[panel.lbd]
        raw_pred = model_s32_s47(
            np.array([r["input_rpu"] for r in raw]),
            np.array([r["inducer_concentration_uM"] for r in raw]),
            dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], dp["T0_variant"], TMAX_PRIMARY,
        )
        no_green_groups: dict[tuple[str, float, float], list[dict]] = {}
        for row in raw_no_green:
            no_green_groups.setdefault(
                (row["batch_id"], row["actual_input_rpu"], row["inducer_concentration_uM"]), []
            ).append(row)
        no_green_y = []
        no_green_pred = []
        for (_batch_id, ctf, dose_uM), group in sorted(no_green_groups.items()):
            no_green_y.append(statistics.fmean(float(r["response_rpu"]) for r in group))
            no_green_pred.append(float(model_s32_s47(ctf, dose_uM, dp["KA"], lp["Kd0"], lp["Kb"], lp["Kd1"], dp["T0_variant"], TMAX_PRIMARY)))
        variants = [
            ("primary", "within_batch_conditional_means", "raw", y_cond, np.array([r["prediction_primary_rpu"] for r in cond]), "S32-S47+S11; T0,variant; Tmax=35.85; different batches not averaged"),
            ("batch_conditional_log10", "within_batch_conditional_means", "log10", y_cond, np.array([r["prediction_primary_rpu"] for r in cond]), "Sensitivity only; same conditional means as primary, evaluated after log10 response transformation"),
            ("replicate_log10", "raw_replicates", "log10", y_raw, raw_pred, "S32-S47+S11; T0,variant; Tmax=35.85"),
            ("replicate_raw_scale", "raw_replicates", "raw", y_raw, raw_pred, "S32-S47+S11; T0,variant; Tmax=35.85"),
            ("Tmax35_sensitivity", "within_batch_conditional_means", "raw", y_cond, np.array([r["prediction_Tmax35_rpu"] for r in cond]), "S32-S47+S11; T0,variant; Tmax=35"),
            ("global_T0_sensitivity", "within_batch_conditional_means", "raw", y_cond, np.array([r["prediction_global_T0_0_035_rpu"] for r in cond]), "S32-S47+S11; T0=0.035; Tmax=35.85"),
            ("green_excluded_sensitivity", "within_batch_conditional_means_without_green_fill", "raw", np.asarray(no_green_y, float), np.asarray(no_green_pred, float), "Primary raw-scale model; trailing-star and green-filled source values excluded; batches not pooled"),
        ]
        for analysis_id, aggregation, scale, y, pred, model_note in variants:
            value, n_used, n_omitted = r2_coefficient(y, pred, scale)
            r, r_sq, n_pearson = pearson(y, pred, scale)
            stats_rows.append({
                "panel_id": panel.panel_id,
                "page": panel.page,
                "construct": panel.construct,
                "analysis_id": analysis_id,
                "metric": "coefficient_of_determination_1_minus_SSE_over_SST",
                "aggregation": aggregation,
                "response_scale": scale,
                "R2": value,
                "n_points_used": n_used,
                "n_points_omitted_nonfinite_or_nonpositive": n_omitted,
                "exclude_starred": True,
                "exclude_green_fill": analysis_id == "green_excluded_sensitivity",
                "inducer_model_unit": "uM",
                "model_note": model_note,
                "pearson_r_diagnostic": r,
                "pearson_r_squared_diagnostic_not_R2": r_sq,
                "pearson_n": n_pearson,
            })

    unit_rows = []
    for panel in panels:
        panel_doses = sorted({r["inducer_concentration_source"] for r in raw_rows if r["panel_id"] == panel.panel_id and r["plot_type"] == "dose_response"})
        panel_uM = sorted({r["inducer_concentration_uM"] for r in raw_rows if r["panel_id"] == panel.panel_id and r["plot_type"] == "dose_response"})
        unit_rows.append({
            "panel_id": panel.panel_id,
            "construct": panel.construct,
            "source_header_unit": panel.dose_unit,
            "conversion_factor_to_uM": unit_factor(panel.dose_unit),
            "source_dose_values": ";".join(f"{v:.12g}" for v in panel_doses),
            "model_dose_values_uM": ";".join(f"{v:.12g}" for v in panel_uM),
            "evidence": f"Source data.xlsx / SI-note activator block beginning row {panel.block_row}",
        })

    raw_path = OUT / "01_raw_measurements_long.csv"
    data_path = OUT / "01_recalculated_source_data.csv"
    conditional_path = OUT / "01_conditional_means_for_R2.csv"
    plot_input_audit_path = OUT / "01_plot_input_30pct_audit.csv"
    param_path = OUT / "01_recalculated_parameters.csv"
    stats_path = OUT / "01_recalculated_statistics.csv"
    units_path = OUT / "01_concentration_unit_conversion.csv"
    write_csv(raw_path, raw_rows)
    write_csv(data_path, sorted(plot_rows, key=lambda r: (r["page"], r["panel_order"], r["plot_type"], r["input_rpu"], r["inducer_concentration_uM"])))
    write_csv(conditional_path, sorted(condition_rows, key=lambda r: (r["page"], r["panel_order"], r["plot_type"], r["input_rpu"], r["inducer_concentration_uM"], r["batch_id"])))
    write_csv(plot_input_audit_path, sorted(plot_input_audit_rows, key=lambda r: (int(r["page"]), r["panel_id"], float(r["plot_input_cluster_mean_rpu"]), r["batch_id"])))
    write_csv(param_path, parameter_rows)
    write_csv(stats_path, stats_rows)
    write_csv(units_path, unit_rows)


    return {
        "panels": len(panels),
        "panels_with_source_measurements": len({r["panel_id"] for r in raw_rows if r["plot_type"] == "dose_response"}),
        "raw_measurements_exported": len(raw_rows),
        "R2_conditional_means_exported": len(condition_rows),
        "plot_summaries_exported": len(plot_rows),
    }


def run_recalculation(source_xlsx, parameter_table, output_dir, source_dump=None):
    from .source import load_source_package
    from .parameters import read_manuscript_parameters
    from .measurements import extract_measurements

    workbook, green_cells = load_source_package(source_xlsx, source_dump)
    dbd_params, lbd_params = read_manuscript_parameters(parameter_table)
    for panel in PANELS:
        dp = dbd_parameters_for_panel(panel, dbd_params)
        if dp["T0_variant"] is None or panel.lbd not in lbd_params:
            raise ValueError(f"Missing manuscript parameters for {panel.panel_id}")
    raw_rows = extract_measurements(workbook["values"], green_cells)
    found = {row["panel_id"] for row in raw_rows if row["plot_type"] == "dose_response"}
    missing = {p.panel_id for p in PANELS} - found
    if missing:
        raise ValueError(f"Missing dose-response measurements for panels: {sorted(missing)}")
    output_dir = Path(output_dir)
    numeric = output_dir / "02_numeric_reconstruction"
    write_json(output_dir / "04_qa" / "02_log10_R2_QA_summary.json",
               {"status": "NOT_VALIDATED", "reason": "Reconstruction is being updated; run validate after completion"})
    counts = reconstruct(raw_rows, dbd_params, lbd_params, output_dir)
    dump_path = numeric / "source_sheet_dump.json"
    write_json(dump_path, workbook)
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
        "source_workbook": str(Path(source_xlsx).resolve()),
        "source_workbook_sha256": sha256(source_xlsx),
        "parameter_table_sha256": sha256(parameter_table),
        "source_dump_sha256": sha256(dump_path),
        "source_sheet": workbook["sheetName"], "source_sheet_address": workbook["address"],
        "primary_R2": "within-batch conditional means; raw scale; 1-SSE/SST; starred cells excluded; green-only cells included",
        "primary_model": "S32-S47 + S11; total Tmax=35.85; T0_variant; LexAec87 KA=0.74",
        "plot_aggregation": "separate plotting pool; every nonzero input within 30% of cluster arithmetic mean",
        **counts,
    }
    write_json(numeric / "01_execution_metadata.json", metadata)
    files = [numeric / name for name in (
        "01_raw_measurements_long.csv", "01_recalculated_source_data.csv",
        "01_conditional_means_for_R2.csv", "01_plot_input_30pct_audit.csv",
        "01_recalculated_parameters.csv", "01_recalculated_statistics.csv",
        "01_concentration_unit_conversion.csv",
    )] + [dump_path, numeric / "01_execution_metadata.json"]
    manifest = {"outputs": {path.relative_to(output_dir).as_posix(): sha256(path) for path in files},
                "source_workbook_sha256": sha256(source_xlsx),
                "parameter_table_sha256": sha256(parameter_table),
                "code": {path.name: sha256(path) for path in sorted(Path(__file__).parent.glob("*.py"))},
                "shared_binding_sha256": sha256(Path(__file__).resolve().parents[1] / "binding.py")}
    write_json(numeric / "01_numeric_freeze_manifest.json", manifest)
    return metadata
