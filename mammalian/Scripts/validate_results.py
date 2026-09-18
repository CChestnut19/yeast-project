"""Validate saved macro log10-R2 fits and optional per-sensor floor constraints."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import model_core as core


PROJECT = Path(__file__).resolve().parent.parent
BACKEND = PROJECT / "Output" / "scipy_sensor_logR2_floor_0p5"
TARGET = 0.5


def require(condition: bool, message: str, checks: list[str]) -> None:
    if not condition:
        raise AssertionError(message)
    checks.append(message)


def validate_numerical_results(input_dir: Path, readme: Path, result_dir: Path) -> list[str]:
    """Recompute saved predictions and R2 from original observations and parameters."""
    data = core.load_fit_data(input_dir, core.read_sensor_mapping(readme))
    layout = core.ParameterLayout(data.mappings)
    vector = np.load(result_dir / "parameter_vector.npy", allow_pickle=False)
    parameters = layout.decode_numpy(vector)
    lower, upper = layout.bounds()
    checks = []
    require(bool(((vector >= lower) & (vector <= upper)).all()), "Parameter vector is within model bounds", checks)
    predicted, terms = core.predict_rpu_numpy(data, layout, vector)
    require(bool(np.isfinite(predicted).all() and (predicted > 0).all()),
            "Predictions are finite and strictly positive for log10 R2", checks)
    saved = pd.read_csv(result_dir / "predictions.csv")
    keys = ["csv", "source_row"]
    require(not saved.duplicated(keys).any(), "Saved observation keys are unique", checks)
    expected_keys = pd.MultiIndex.from_frame(data.frame[keys])
    saved = saved.set_index(keys)
    require(len(saved) == len(data.frame) and set(saved.index) == set(expected_keys),
            "Saved observation keys exactly match the original inputs", checks)
    saved = saved.loc[expected_keys]
    for column in ("sensor_name", "canonical_lbd", "canonical_dbd", "source_dbd"):
        require(saved[column].tolist() == data.frame[column].tolist(), f"Saved {column} matches mapping", checks)
    for column in core.REQUIRED_COLUMNS:
        require(np.allclose(saved[column], data.frame[column], rtol=1e-12, atol=1e-15),
                f"Saved {column} matches original observations", checks)
    require(np.allclose(saved["RPU_predicted"], predicted, rtol=1e-10, atol=1e-12),
            "Saved predictions are reproduced from the parameter vector", checks)
    for column, values in {
        "log10_RPU_observed": data.observed_log10,
        "log10_RPU_predicted": np.log10(predicted),
        "residual_raw": data.observed_rpu - predicted,
        "residual_log10": data.observed_log10 - np.log10(predicted),
    }.items():
        require(np.allclose(saved[column], values, rtol=1e-10, atol=1e-12),
                f"Saved {column} is independently reproduced", checks)
    for column, values in terms.items():
        require(np.allclose(saved[column], values, rtol=1e-10, atol=1e-12),
                f"Saved model term {column} is reproduced", checks)
    for filename, key, names, columns in (
        ("parameters_lbd.csv", "canonical_lbd", layout.lbd_names,
         {"Kd0": parameters.Kd0, "Kb_uM_inverse": parameters.Kb, "Kd1": parameters.Kd1}),
        ("parameters_dbd.csv", "canonical_dbd", layout.dbd_names,
         {"KA": parameters.KA, "T0_variant": parameters.T0_variant}),
    ):
        table = pd.read_csv(result_dir / filename).set_index(key)
        require(table.index.is_unique and set(table.index) == set(names), f"{filename} has the exact parameter groups", checks)
        for column, values in columns.items():
            require(np.allclose(table.loc[names, column], values, rtol=1e-10, atol=1e-12),
                    f"{filename} {column} matches the parameter vector", checks)
        if key == "canonical_dbd":
            ordered = table.loc[names]
            expected_fixed = [str(name == core.ANCHOR_DBD).lower() for name in names]
            require(ordered["KA_fixed"].astype(str).str.lower().tolist() == expected_fixed
                    and np.allclose(ordered["Tmax"], core.TMAX)
                    and (ordered["operator_number"] == core.OPERATOR_NUMBER).all(),
                    "DBD fixed-parameter metadata agrees with the model", checks)
    summary = json.loads((result_dir / "fit_summary.json").read_text(encoding="utf-8"))
    has_floor = summary["backend"] == BACKEND.name
    require(has_floor or summary["backend"] in {core.SCIPY_BACKEND, core.TORCH_BACKEND},
            "Saved backend declares a supported macro log10 R2 objective", checks)
    if has_floor:
        metrics = pd.read_csv(result_dir / "constraint_metrics.csv").set_index("csv")
        require(metrics.index.is_unique and set(metrics.index) == {m.csv_name for m in data.mappings},
                "Constraint metrics cover exactly the mapped sensors", checks)
    recomputed_r2 = []
    recomputed_raw_r2 = []
    normalized_log_sse = []
    for index, mapping in enumerate(data.mappings):
        mask = data.csv_index == index
        observed = data.observed_log10[mask]
        sse_log = float(np.sum((observed - np.log10(predicted[mask]))**2))
        sst_log = float(np.sum((observed - observed.mean())**2))
        raw = data.observed_rpu[mask]
        sse_raw = float(np.sum((raw - predicted[mask])**2))
        sst_raw = float(np.sum((raw - raw.mean())**2))
        raw_r2 = 1.0 - sse_raw / sst_raw
        log_r2 = 1.0 - sse_log / sst_log
        recomputed_r2.append(log_r2)
        recomputed_raw_r2.append(raw_r2)
        normalized_log_sse.append(sse_log / sst_log)
        if not has_floor:
            continue
        row = metrics.loc[mapping.csv_name]
        require(np.isclose(row["R2_raw"], raw_r2, rtol=1e-10, atol=1e-12)
                and np.isclose(row["R2_log10"], log_r2, rtol=1e-10, atol=1e-12),
                f"{mapping.csv_name} raw/log10 R2 independently reproduced", checks)
        require(bool(log_r2 >= TARGET), f"{mapping.csv_name} meets R2_log10 >= {TARGET}", checks)
        require(str(row["passes_R2_log10_floor"]).lower() == "true"
                and np.isclose(float(row["target_R2_log10"]), TARGET),
                f"{mapping.csv_name} constraint flags match recomputed R2", checks)
        expected_sensor = {"SSE_log10": sse_log, "TSS_log10": sst_log,
                           "normalized_SSE_log10": sse_log / sst_log,
                           "SSE_raw": sse_raw, "TSS_raw": sst_raw,
                           "normalized_SSE_raw": sse_raw / sst_raw, "n": int(mask.sum())}
        require(all(np.isclose(float(row[key]), value, rtol=1e-10, atol=1e-12)
                    for key, value in expected_sensor.items()),
                f"{mapping.csv_name} saved SSE and SST independently reproduced", checks)

    loss = float(np.mean(normalized_log_sse))
    expected_components = {"objective_total": loss, "data_objective": loss,
                           "macro_log10_1_minus_R2": loss,
                           "macro_R2_log10": float(np.mean(recomputed_r2)),
                           "macro_R2_raw": float(np.mean(recomputed_raw_r2))}
    require(summary["objective"] == core.OBJECTIVE_DESCRIPTION
            and np.isclose(float(summary["objective_total"]), loss, rtol=1e-10, atol=1e-12),
            "Fit summary objective independently reproduced as macro per-CSV log10 R2 loss", checks)
    require(np.isclose(float(summary["macro_metrics"]["R2_log10"]), np.mean(recomputed_r2), rtol=1e-10, atol=1e-12)
            and np.isclose(float(summary["macro_metrics"]["R2_raw"]), np.mean(recomputed_raw_r2), rtol=1e-10, atol=1e-12),
            "Fit summary diagnostic macro R2 independently reproduced", checks)
    if has_floor:
        expected_constraint = {
            "global_unweighted_MSE_log10": float(np.mean((data.observed_log10 - np.log10(predicted))**2)),
            "minimum_per_sensor_R2_log10": min(recomputed_r2),
            "mean_per_sensor_R2_log10": float(np.mean(recomputed_r2)),
            "target_R2_log10": TARGET, "passing_sensor_count": len(data.mappings),
            "included_sensor_count": len(data.mappings), "constraint_satisfied": True,
        }
        constraint = summary["constraint"]
        require(set(constraint) == set(expected_constraint)
                and constraint["constraint_satisfied"] is True
                and all(np.isclose(float(constraint[key]), value, rtol=1e-10, atol=1e-12)
                        for key, value in expected_constraint.items()),
                "Fit summary agrees with independently recomputed constraints", checks)
        expected_components.update(expected_constraint)
        comparison = pd.read_csv(result_dir / "candidate_comparison.csv")
        selected = comparison.loc[comparison["selected"].astype(str).str.lower() == "true"]
        require(len(selected) == 1, "Candidate comparison has exactly one selected fit", checks)
        chosen = selected.iloc[0]
        require(chosen["start"] == summary["selected_start"]
                and str(chosen["feasible"]).lower() == "true"
                and all(np.isclose(float(chosen[key]), value, rtol=1e-10, atol=1e-12)
                        for key, value in {"objective_total": loss,
                                           "minimum_R2_log10": min(recomputed_r2),
                                           "mean_R2_log10": np.mean(recomputed_r2),
                                           "global_MSE_log10": expected_constraint["global_unweighted_MSE_log10"]}.items()),
                "Selected candidate objective and constraints independently reproduced", checks)
        feasible = comparison.loc[comparison["feasible"].astype(str).str.lower() == "true"]
        require(float(chosen["mean_R2_log10"]) >= float(feasible["mean_R2_log10"].max()) - 1e-12,
                "Selected candidate maximizes reported feasible macro log10 R2", checks)

    components = pd.read_csv(result_dir / "objective_components.csv")
    require(len(components) == 1 and set(components.columns) == set(expected_components),
            "Saved objective components have exactly the expected fields", checks)
    for source, values in (("CSV", components.iloc[0]), ("summary", summary["objective_components"])):
        require(set(values.keys()) == set(expected_components)
                and all(np.isclose(float(values[key]), value, rtol=1e-10, atol=1e-12)
                        for key, value in expected_components.items()),
                f"Saved {source} objective components independently reproduced", checks)
    return checks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=PROJECT / "Input")
    parser.add_argument("--readme", type=Path, default=PROJECT / "README.md")
    parser.add_argument("--result-dir", type=Path, default=BACKEND)
    args = parser.parse_args()
    checks = validate_numerical_results(args.input_dir, args.readme, args.result_dir)
    report = "# Numerical validation\n\nPASS\n\n" + "\n".join(f"- {check}" for check in checks) + "\n"
    report_path = args.result_dir / "numerical_validation_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"PASS ({len(checks)} numerical checks)")
    print(report_path)


if __name__ == "__main__":
    main()
