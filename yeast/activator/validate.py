"""Independently check batch means, predictions and R2, with optional prior-run comparison."""
from __future__ import annotations
from collections import defaultdict
import json
import math
from pathlib import Path
import statistics
from .panels import PANELS
from .source import read_csv, write_csv, write_json, sha256, parse_cell, cell_coordinates, _comparable_values, excel_col
from .model import unit_factor
from .settings import LEXAEC87_KA_OVERRIDE, TMAX_PRIMARY


def require(condition, message):
    if not condition:
        raise ValueError(message)


def as_bool(value):
    text = str(value).strip().casefold()
    if text not in {"true", "false"}:
        raise ValueError(f"Invalid boolean flag: {value!r}")
    return text == "true"


def same_number(left, right, tolerance=1e-10):
    return (math.isnan(left) and math.isnan(right)) or math.isclose(left, right, rel_tol=tolerance, abs_tol=tolerance)


def log10_r2(observed, predicted):
    require(len(observed) == len(predicted), "R2 inputs have different lengths")
    pairs = [(math.log10(y), math.log10(p)) for y, p in zip(observed, predicted)
             if math.isfinite(y) and math.isfinite(p) and y > 0 and p > 0]
    if len(pairs) < 2:
        return math.nan, len(pairs)
    center = statistics.fmean(y for y, _ in pairs)
    denominator = math.fsum((y - center)**2 for y, _ in pairs)
    if denominator == 0:
        return math.nan, len(pairs)
    return 1.0 - math.fsum((y - p)**2 for y, p in pairs) / denominator, len(pairs)


def independent_prediction(row):
    """Scalar mass balance evaluated separately from the NumPy model."""
    tf, dose = float(row["actual_input_rpu"]), float(row["inducer_concentration_uM"])
    ka, kd0, kb, kd1, t0 = (float(row[k]) for k in ("KA", "Kd0", "Kb_per_uM", "Kd1", "T0_variant"))
    ceiling = float(row["Tmax_primary"])
    require(all(math.isfinite(x) for x in (tf, dose, ka, kd0, kb, kd1, t0, ceiling)), "Non-finite model input")
    require(tf >= 0 and dose >= 0 and min(ka, kd0, kb, kd1) > 0 and 0 <= t0 < ceiling,
            "Invalid model input domain")
    a, b = kd0 + kd1 * (kb * dose)**2, 1 + kb * dose
    free_tf = 2 * tf / (b + math.sqrt(b*b + 8*a*tf))
    z = ka * a * free_tf**2
    return t0 + (ceiling - t0) * z / (1 + z)


def _condition_key(row):
    return (row["panel_id"], row["batch_id"], float(row["actual_input_rpu"]),
            float(row["nominal_input_rpu"]), float(row["inducer_concentration_source"]),
            row["inducer_source_unit"], float(row["inducer_concentration_uM"]))


def verify_manifest(output_dir):
    path = output_dir / "02_numeric_reconstruction" / "01_numeric_freeze_manifest.json"
    if not path.is_file():
        raise FileNotFoundError(f"Missing numeric manifest: {path}; rerun reconstruction with this version")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    outputs = manifest.get("outputs", {})
    mandatory = {"01_raw_measurements_long.csv", "01_conditional_means_for_R2.csv",
                 "01_recalculated_statistics.csv", "01_recalculated_parameters.csv",
                 "source_sheet_dump.json", "01_execution_metadata.json"}
    require({f"02_numeric_reconstruction/{name}" for name in mandatory} <= set(outputs),
            "Manifest omits required numeric artifacts")
    for relative, expected in outputs.items():
        target = (output_dir / relative).resolve()
        require(output_dir.resolve() in target.parents, "Manifest path escapes the output directory")
        require(target.is_file() and sha256(target) == expected, f"Artifact checksum mismatch: {relative}")


def source_change_audit(previous_dump, current_dump):
    previous = json.loads(Path(previous_dump).read_text(encoding="utf-8-sig"))
    current = json.loads(Path(current_dump).read_text(encoding="utf-8-sig"))
    old, new = _comparable_values(previous), _comparable_values(current)
    changes = []
    for row, column in sorted(set(old) | set(new)):
        before, after = old.get((row, column)), new.get((row, column))
        if before != after:
            changes.append({"source_cell": f"{excel_col(column)}{row+1}", "previous_value": before,
                            "new_value": after, "previous_starred": parse_cell(before)[1],
                            "new_starred": parse_cell(after)[1]})
    return changes


def validate(output_dir, previous_root=None, panels=PANELS):
    output_dir = Path(output_dir)
    numeric = output_dir / "02_numeric_reconstruction"
    verify_manifest(output_dir)
    raw = read_csv(numeric / "01_raw_measurements_long.csv")
    conditional_all = read_csv(numeric / "01_conditional_means_for_R2.csv")
    conditional = [r for r in conditional_all if r["plot_type"] == "dose_response"]
    stats = [r for r in read_csv(numeric / "01_recalculated_statistics.csv") if r["analysis_id"] == "batch_conditional_log10"]
    params = read_csv(numeric / "01_recalculated_parameters.csv")
    parameter_lookup = {}
    for row in params:
        key = row["panel_id"], row["parameter"]
        require(key not in parameter_lookup, f"Duplicate parameter row: {key}")
        parameter_lookup[key] = float(row["value"])
    snapshot = json.loads((numeric / "source_sheet_dump.json").read_text(encoding="utf-8"))
    metadata = json.loads((numeric / "01_execution_metadata.json").read_text(encoding="utf-8"))
    require(len(raw) == metadata["raw_measurements_exported"]
            and len(conditional_all) == metadata["R2_conditional_means_exported"], "Metadata record counts disagree with numeric tables")
    require(snapshot["source_workbook_sha256"] == metadata["source_workbook_sha256"], "Workbook provenance hashes disagree")
    source_values = _comparable_values(snapshot)
    dose_raw = [row for row in raw if row["plot_type"] == "dose_response"]
    require(bool(dose_raw), "No dose-response measurements")
    groups, by_panel, stats_by_panel = defaultdict(list), defaultdict(list), {}
    seen_source = set()
    for row in dose_raw:
        identity = row["panel_id"], row["source_cell"]
        require(identity not in seen_source, f"Repeated source measurement: {identity}")
        seen_source.add(identity)
        numeric_value, starred = parse_cell(source_values.get(cell_coordinates(row["source_cell"])))
        require(numeric_value is not None and same_number(numeric_value, float(row["response_rpu"])),
                f"Source snapshot mismatch at {row['source_cell']}")
        require(starred == as_bool(row["starred_in_workbook"]), "Saved star flag differs from source cell")
        require(as_bool(row["included_primary"]) == (not starred), "Primary inclusion differs from the trailing-star rule")
        require(same_number(float(row["inducer_concentration_source"]) * unit_factor(row["inducer_source_unit"]),
                            float(row["inducer_concentration_uM"])), "Inducer unit conversion mismatch")
        if not starred:
            groups[_condition_key(row)].append(float(row["response_rpu"]))
    conditional_keys = set()
    for row in conditional:
        key = _condition_key(row)
        require(key not in conditional_keys and key in groups, f"Duplicate or unexpected conditional group: {key}")
        conditional_keys.add(key)
        values = groups[key]
        sd = statistics.stdev(values) if len(values) > 1 else math.nan
        require(int(row["n_included"]) == len(values) and same_number(float(row["mean_response_rpu"]), statistics.fmean(values))
                and same_number(float(row["sd_response_rpu"]), sd), f"Conditional mean/SD mismatch: {key}")
        for field, parameter in (("KA", "KA"), ("T0_variant", "T0_variant"), ("Kd0", "Kd0"),
                                 ("Kb_per_uM", "Kb"), ("Kd1", "Kd1"), ("Tmax_primary", "Tmax_primary")):
            require(same_number(float(row[field]), parameter_lookup[(row["panel_id"], parameter)]),
                    f"Conditional parameter mismatch: {row['panel_id']} {field}")
        require(same_number(float(row["Tmax_primary"]), TMAX_PRIMARY), "Total activator Tmax has changed")
        if row["dbd"].casefold() == "lexaec87":
            require(same_number(float(row["KA"]), LEXAEC87_KA_OVERRIDE), "Archived LexAec87 override has changed")
        require(same_number(float(row["prediction_primary_rpu"]), independent_prediction(row)),
                f"Independent prediction mismatch: {key}")
        by_panel[row["panel_id"]].append(row)
    require(set(groups) == conditional_keys, "Conditional groups do not match the unpooled raw batches")
    for row in stats:
        require(row["panel_id"] not in stats_by_panel, "Duplicate panel statistic")
        stats_by_panel[row["panel_id"]] = row
    expected_panels = {p.panel_id for p in panels}
    require(set(by_panel) == set(stats_by_panel) == expected_panels, "Panel coverage does not match the source mapping")

    previous_rows, previous_counts = {}, defaultdict(int)
    changes = None
    if previous_root is not None:
        previous_root = Path(previous_root)
        old_rows = read_csv(previous_root / "04_quantitative_audit" / "03_R2_three_metrics_batch_specific.csv")
        for row in old_rows:
            require(row["panel_id"] not in previous_rows, "Duplicate prior panel")
            previous_rows[row["panel_id"]] = row
        require(set(previous_rows) == expected_panels, "Previous audit panel coverage does not match")
        for row in read_csv(previous_root / "02_numeric_reconstruction" / "01_raw_measurements_long.csv"):
            if row["plot_type"] == "dose_response" and as_bool(row["starred_in_workbook"]):
                previous_counts[row["panel_id"]] += 1
        changes = source_change_audit(previous_root / "02_numeric_reconstruction" / "source_sheet_dump.json", numeric / "source_sheet_dump.json")

    results = []
    for panel in panels:
        rows = by_panel[panel.panel_id]
        observed = [float(row["mean_response_rpu"]) for row in rows]
        predicted = [float(row["prediction_primary_rpu"]) for row in rows]
        independent, used = log10_r2(observed, predicted)
        reported = stats_by_panel[panel.panel_id]
        require(same_number(independent, float(reported["R2"])), f"Independent log10 R2 mismatch: {panel.panel_id}")
        require(int(reported["n_points_used"]) == used and int(reported["n_points_omitted_nonfinite_or_nonpositive"]) == len(rows)-used,
                f"R2 point accounting mismatch: {panel.panel_id}")
        old = previous_rows.get(panel.panel_id)
        previous_r2 = float(old["log10_R2_1_minus_SSE_over_SST"]) if old else None
        previous_n = int(old["n_batch_specific_conditional_means"]) if old else None
        n_starred = sum(r["panel_id"] == panel.panel_id and as_bool(r["starred_in_workbook"]) for r in dose_raw)
        results.append({"panel_id": panel.panel_id, "construct": panel.construct, "DBD": panel.dbd, "LBD": panel.lbd,
                        "log10_R2_1_minus_SSE_over_SST": independent, "independent_log10_R2_check": independent,
                        "n_batch_specific_conditional_means": len(rows), "n_points_used": used, "n_points_omitted": len(rows)-used,
                        "n_starred_measurements_excluded": n_starred,
                        "previous_log10_R2": previous_r2, "difference_vs_previous": independent-previous_r2 if old else None,
                        "previous_n_batch_specific_conditional_means": previous_n,
                        "difference_in_conditional_means": len(rows)-previous_n if old else None,
                        "previous_n_starred_measurements_excluded": previous_counts[panel.panel_id] if old else None,
                        "newly_starred_measurements_excluded": n_starred-previous_counts[panel.panel_id] if old else None})
    qa = output_dir / "04_qa"
    if changes is not None:
        write_csv(qa / "01_source_data_changed_cells.csv", changes,
                  ["source_cell", "previous_value", "new_value", "previous_starred", "new_starred"])
    write_csv(output_dir / "03_results" / "Supplementary_Note_9_log10_R2_recheck.csv", results)
    summary = {"status": "PASS", "panels_checked": len(results), "conditional_groups_independently_rebuilt": len(groups),
               "dose_response_measurements_total": len(dose_raw), "dose_response_measurements_starred_excluded": sum(as_bool(r["starred_in_workbook"]) for r in dose_raw),
               "conditional_mean_sd_mismatches": 0, "log10_R2_mismatches": 0,
               "panels_with_undefined_log10_R2": sum(not math.isfinite(r["independent_log10_R2_check"]) for r in results),
               "previous_comparison_performed": previous_root is not None, "changed_source_cells": len(changes) if changes is not None else None,
               "metric": "1-SSE/SST after log10; within-batch means; not Pearson r squared",
               "source_sheet": snapshot["sheetName"], "source_sheet_address": snapshot["address"]}
    write_json(qa / "02_log10_R2_QA_summary.json", summary)
    return summary
