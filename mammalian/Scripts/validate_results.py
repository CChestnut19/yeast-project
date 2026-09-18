"""Validate saved per-sensor log10-R2-floor results against the original numerical inputs."""

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
    metrics = pd.read_csv(result_dir / "constraint_metrics.csv").set_index("csv")
    require(metrics.index.is_unique and set(metrics.index) == {m.csv_name for m in data.mappings},
            "Constraint metrics cover exactly the mapped sensors", checks)
    recomputed_r2 = []
    for index, mapping in enumerate(data.mappings):
        mask = data.csv_index == index
        raw_r2 = core.r_squared(data.observed_rpu[mask], predicted[mask])
        log_r2 = core.r_squared(data.observed_log10[mask], np.log10(predicted[mask]))
        recomputed_r2.append(log_r2)
        row = metrics.loc[mapping.csv_name]
        require(np.isclose(row["R2_raw"], raw_r2, rtol=1e-10, atol=1e-12)
                and np.isclose(row["R2_log10"], log_r2, rtol=1e-10, atol=1e-12),
                f"{mapping.csv_name} raw/log10 R2 independently reproduced", checks)
        require(bool(log_r2 >= TARGET), f"{mapping.csv_name} meets R2_log10 >= {TARGET}", checks)
        require(str(row["passes_R2_log10_floor"]).lower() == "true"
                and np.isclose(float(row["target_R2_log10"]), TARGET),
                f"{mapping.csv_name} constraint flags match recomputed R2", checks)
    summary = json.loads((result_dir / "fit_summary.json").read_text(encoding="utf-8"))
    constraint = summary["constraint"]
    require(constraint["constraint_satisfied"] is True
            and int(constraint["passing_sensor_count"]) == len(data.mappings)
            and np.isclose(float(constraint["minimum_per_sensor_R2_log10"]), min(recomputed_r2), rtol=1e-10, atol=1e-12),
            "Fit summary agrees with independently recomputed constraints", checks)
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
