"""Validate the per-sensor log10-R2-floor fit and corrected Figure 13 PDF."""

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
TMAX = 13.61


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


def validate_publication(input_dir: Path, result_dir: Path, numerical_checks=()) -> None:
    from pypdf import PdfReader

    BACKEND = result_dir
    required = (
        "fit_summary.json",
        "constraint_metrics.csv",
        "candidate_comparison.csv",
        "optimization_trace.csv",
        "objective_components.csv",
        "metrics.csv",
        "macro_metrics.csv",
        "parameters_lbd.csv",
        "parameters_dbd.csv",
        "parameter_vector.npy",
        "predictions.csv",
        "curves_dense.csv",
        "curve_shape_metrics.csv",
        "all_25_sensor_curves_30mm_axes.pdf",
        "all_25_sensor_curves_30mm_axes_plot_settings_used.csv",
        "all_25_sensor_curves_30mm_axes_style_used.json",
        "Supplementary Figure 13_corrected.pdf",
        "corrected_pdf_panel_metrics.csv",
        "corrected_pdf_style_spec.json",
    )
    missing = [name for name in required if not (BACKEND / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing output files: {missing}")

    checks: list[str] = list(numerical_checks)
    summary = json.loads((BACKEND / "fit_summary.json").read_text(encoding="utf-8"))
    constraint = pd.read_csv(BACKEND / "constraint_metrics.csv")
    predictions = pd.read_csv(BACKEND / "predictions.csv")
    dbd = pd.read_csv(BACKEND / "parameters_dbd.csv")
    lbd = pd.read_csv(BACKEND / "parameters_lbd.csv")
    input_549 = pd.read_csv(input_dir / "549.csv")
    plot_settings_path = input_dir / "all_25_sensor_plot_settings.csv"
    if not plot_settings_path.is_file():
        raise FileNotFoundError(f"Missing plot settings input: {plot_settings_path}")
    plot_settings = pd.read_csv(plot_settings_path)
    used_plot_settings_path = (
        BACKEND / "all_25_sensor_curves_30mm_axes_plot_settings_used.csv"
    )
    used_atlas_style_path = (
        BACKEND / "all_25_sensor_curves_30mm_axes_style_used.json"
    )

    require(
        len(constraint) == 25
        and constraint["csv"].nunique() == 25
        and "402.csv" not in set(constraint["csv"]),
        "Exactly 25 CIC CSVs are constrained and 402.csv is excluded",
        checks,
    )
    require(
        bool((constraint["R2_log10"] >= TARGET).all())
        and bool(constraint["passes_R2_log10_floor"].all()),
        "Every included sensor has log10-scale R2 >= 0.5",
        checks,
    )
    require(
        "R2_raw" in constraint.columns
        and bool(np.isfinite(constraint["R2_raw"].to_numpy(float)).all()),
        "Per-sensor raw and log10 R2 values are both saved",
        checks,
    )
    minimum_r2 = float(constraint["R2_log10"].min())
    require(
        np.isclose(
            minimum_r2,
            float(summary["constraint"]["minimum_per_sensor_R2_log10"]),
            rtol=1e-12,
            atol=1e-12,
        ),
        "Saved minimum per-sensor log10 R2 is independently reproduced",
        checks,
    )
    require(
        summary["constraint"]["constraint_satisfied"]
        and int(summary["constraint"]["passing_sensor_count"]) == 25,
        "fit_summary records a feasible 25/25 solution",
        checks,
    )
    require(
        int(summary["operator_number"]) == 7
        and np.isclose(float(summary["Tmax"]), TMAX)
        and np.isclose(float(summary["anchor_KA"]), 9.15),
        "operator_number=7, Tmax=13.61, and KA_lexAec87=9.15 are fixed",
        checks,
    )
    require(
        len(lbd) == 13 and len(dbd) == 11,
        "The shared hierarchy contains 13 LBD and 11 DBD parameter groups",
        checks,
    )
    anchor = dbd.loc[dbd["canonical_dbd"] == "lexAec87"].iloc[0]
    require(
        bool(anchor["KA_fixed"]) and np.isclose(float(anchor["KA"]), 9.15),
        "The lexAec87 parameter row is fixed at KA=9.15",
        checks,
    )
    require(
        len(predictions) == 953 and predictions["csv"].nunique() == 25,
        "Predictions contain all 953 observations from 25 CSVs",
        checks,
    )
    require(
        len(plot_settings) == 25
        and plot_settings["csv"].nunique() == 25
        and set(plot_settings["csv"]) == set(constraint["csv"]),
        "Plot settings contain exactly one row for every included sensor",
        checks,
    )
    minimum_by_csv = predictions.groupby("csv")["inducer"].min()
    recorded_minimum = plot_settings.set_index("csv")["saved_off_input_um"]
    require(
        all(
            np.isclose(
                float(recorded_minimum.loc[csv_name]),
                float(minimum_by_csv.loc[csv_name]),
                rtol=1e-10,
                atol=1e-15,
            )
            for csv_name in minimum_by_csv.index
        ),
        "Plot settings saved_off_input_um matches every saved fitted input",
        checks,
    )
    require(
        bool((plot_settings["visible_zero_label"].astype(float) == 0.0).all())
        and bool(plot_settings["zero_slot_minor_ticks"].astype(str).str.lower().eq("true").all())
        and bool((plot_settings["tick_direction"].astype(str) == "in").all())
        and bool(plot_settings["plot_only"].astype(str).str.lower().eq("true").all())
        and bool(np.isclose(plot_settings["model_zero_um"].astype(float), 0.0).all()),
        "All plot rows require label 0, zero-slot minor ticks, inward ticks, plot-only scope, and mathematical model zero",
        checks,
    )
    require(
        plot_settings_path.read_bytes() == used_plot_settings_path.read_bytes(),
        "Output archives the exact validated plot settings used for the atlas",
        checks,
    )
    require(
        len(input_549) == 18
        and int(np.isclose(input_549["inducer"], 0.0).sum()) == 9
        and int(np.isclose(input_549["inducer"], 10.0).sum()) == 9,
        "549.csv contains nine 0-uM OFF and nine 10-uM ON observations",
        checks,
    )
    predictions_549 = predictions.loc[predictions["csv"] == "549.csv"]
    require(
        len(predictions_549) == 18
        and int(np.isclose(predictions_549["inducer"], 0.0).sum()) == 9,
        "Saved 549.csv predictions were recomputed at mathematical inducer=0",
        checks,
    )
    p1 = predictions["p1"].to_numpy(float)
    p7 = predictions["p7"].to_numpy(float)
    require(
        np.allclose(p7, 1.0 - np.power(1.0 - p1, 7), rtol=1e-10, atol=1e-12),
        "p7 = 1 - (1 - p1)^7 is reproduced for every observation",
        checks,
    )
    t0_lookup = dbd.set_index("canonical_dbd")["T0_variant"]
    t0 = predictions["canonical_dbd"].map(t0_lookup).to_numpy(float)
    expected_output = t0 + (TMAX - t0) * p7
    require(
        np.allclose(
            predictions["RPU_predicted"].to_numpy(float),
            expected_output,
            rtol=1e-10,
            atol=1e-12,
        ),
        "T(x) = T0_variant + (Tmax - T0_variant) p7 is reproduced",
        checks,
    )

    pdf_path = BACKEND / "Supplementary Figure 13_corrected.pdf"
    pdf = PdfReader(str(pdf_path))
    require(len(pdf.pages) == 1, "Corrected PDF contains one page", checks)
    page = pdf.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    require(
        np.isclose(width, 595.276, atol=0.01)
        and np.isclose(height, 841.89, atol=0.01),
        "Corrected PDF retains the A4 reference page size",
        checks,
    )

    atlas = PdfReader(str(BACKEND / "all_25_sensor_curves_30mm_axes.pdf"))
    atlas_text = "\n".join(page.extract_text() or "" for page in atlas.pages)
    require(
        len(atlas.pages) == 5
        and all(csv_name in atlas_text for csv_name in constraint["csv"]),
        "All-sensor atlas contains five pages and all 25 CSV labels",
        checks,
    )
    atlas_style = json.loads(used_atlas_style_path.read_text(encoding="utf-8"))
    require(
        np.isclose(float(atlas_style["axis_length_mm"]), 30.0)
        and np.isclose(float(atlas_style["symbol_diameter_multiplier"]), 1.25),
        "Accepted all-sensor atlas uses 30 mm square axes and the final 1.25 symbol-size multiplier",
        checks,
    )

    style = json.loads(
        (BACKEND / "corrected_pdf_style_spec.json").read_text(encoding="utf-8")
    )
    require(
        style["font"]["family"] == "Helvetica"
        and style["font"]["panel_letter"]["size_pt"] == 8
        and style["font"]["title_axis_tick_base"]["size_pt"] == 6
        and style["font"]["tick_exponent"]["size_pt"] == 4,
        "Helvetica 8/6/4 pt hierarchy matches Supplementary Figure 13",
        checks,
    )
    require(
        style["y_axis"]["scale"] == "log10"
        and style["y_axis"]["limits"] == [0.001, 100.0],
        "All D-M panels use the reference log10 y-axis range 1e-3 to 1e2",
        checks,
    )
    require(
        style["x_axis"]["scale"] == "zero slot plus broken log10 axis"
        and style["x_axis"]["break_mark_centers_axis_fraction"]
        == [0.0403, 0.0589],
        "The reference zero slot and broken-axis geometry are recorded",
        checks,
    )
    geometry = style["panel_axis_geometry_pt"]
    require(
        len(geometry) == 10
        and all(
            np.isclose(spec["x1"] - spec["x0"], 85.039, atol=0.01)
            and np.isclose(spec["bottom"] - spec["top"], 85.039, atol=0.01)
            for spec in geometry.values()
        ),
        "All ten corrected D-M panel boxes retain the measured reference geometry",
        checks,
    )
    panel_metrics = pd.read_csv(BACKEND / "corrected_pdf_panel_metrics.csv")
    require(
        len(panel_metrics) == 10 and bool(panel_metrics["passes_0p5"].astype(str).str.lower().eq("true").all())
        and bool((panel_metrics["R2_log10_with_source_zero_plot_positions"] >= TARGET).all()),
        "All ten corrected D-M panels remain above log10 R2=0.5 after source-zero plot restoration",
        checks,
    )

    report = [
        "# Validation report",
        "",
        f"Result: PASS ({len(checks)} checks)",
        "",
        f"Minimum per-sensor log10 R2: {minimum_r2:.9f}",
        f"Passing sensors: {int((constraint['R2_log10'] >= TARGET).sum())}/25",
        "",
        "## Checks",
        "",
        *[f"- PASS: {check}" for check in checks],
        "",
    ]
    (BACKEND / "validation_report.md").write_text(
        "\n".join(report), encoding="utf-8"
    )
    print(f"PASS ({len(checks)} checks); minimum log10 R2={minimum_r2:.9f}")
    print(BACKEND / "validation_report.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=PROJECT / "Input")
    parser.add_argument("--readme", type=Path, default=PROJECT / "README.md")
    parser.add_argument("--result-dir", type=Path, default=BACKEND)
    parser.add_argument("--numerical-only", action="store_true", help="Validate fit data without requiring publication PDFs")
    args = parser.parse_args()
    checks = validate_numerical_results(args.input_dir, args.readme, args.result_dir)
    if args.numerical_only:
        report = "# Numerical validation\n\nPASS\n\n" + "\n".join(f"- {check}" for check in checks) + "\n"
        (args.result_dir / "numerical_validation_report.md").write_text(report, encoding="utf-8")
        print(f"PASS ({len(checks)} numerical checks); publication layout not checked")
    else:
        validate_publication(args.input_dir, args.result_dir, checks)


if __name__ == "__main__":
    main()
