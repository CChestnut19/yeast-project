#!/usr/bin/env python3
"""Plot all 25 refitted mammalian sensors from saved outputs.

The script reads the saved fitted parameter vector and observed-point tables.
It writes a five-page PDF with six square panels per page (the final page has
one panel). Every panel uses the same Supplementary Figure 13 coordinate rule:
a finite graphical slot labelled 0, a measured double-slash break, and a
positive log10-dose axis. The finite zero coordinates are plot-only mappings;
they never change the input CSVs, fitted parameters, predictions, or R2 values.
Model curves are evaluated linearly in true concentration across the zero slot
and logarithmically over the positive-dose range.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from matplotlib.ticker import (
    FixedFormatter,
    FixedLocator,
    LogFormatterMathtext,
    LogLocator,
    NullFormatter,
)
import numpy as np
import pandas as pd

import model_core as core


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = PACKAGE_ROOT / "Input"
DEFAULT_RESULT_DIR = PACKAGE_ROOT / "Output" / "scipy_sensor_logR2_floor_0p5"
DEFAULT_OUTPUT_PDF = DEFAULT_RESULT_DIR / "all_25_sensor_curves_30mm_axes.pdf"
DEFAULT_PLOT_SETTINGS = DEFAULT_INPUT_DIR / "all_25_sensor_plot_settings.csv"
USED_PLOT_SETTINGS_NAME = "all_25_sensor_curves_30mm_axes_plot_settings_used.csv"
DEFAULT_30MM_STYLE_SETTINGS = DEFAULT_INPUT_DIR / "all_25_sensor_30mm_style.json"

Y_MIN = 1.0e-3
Y_MAX = 1.0e2
PANELS_PER_PAGE = 6
COLORS = ("#2474B5", "#E3A72F", "#2D9B56")
MARKER = "o"
MM_PER_INCH = 25.4
REFERENCE_AXIS_LENGTH_MM = 3.24 * MM_PER_INCH
REFERENCE_MARKER_DIAMETER_PT = 5.0
REQUIRED_PLOT_SETTING_COLUMNS = {
    "csv",
    "sensor_name",
    "saved_off_input_um",
    "graphical_zero_x_um",
    "positive_log_min_um",
    "positive_log_max_um",
    "visible_zero_label",
    "zero_slot_minor_ticks",
    "tick_direction",
    "break_geometry",
    "plot_only",
    "model_zero_um",
}
EXPECTED_BREAK_GEOMETRY = "Supplementary Figure 13 generic D-L double slash"


def numeric_csv_key(csv_name: str) -> int:
    return int(Path(csv_name).stem)


def parse_boolean(value: object, field: str, csv_name: str) -> bool:
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise ValueError(f"{csv_name}: {field} must be true/false, found {value!r}")


def load_display_spec(
    plot_settings_path: Path,
    metrics: pd.DataFrame,
    predictions: pd.DataFrame,
) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    """Read and validate the relative plot-only settings input table."""

    settings = pd.read_csv(plot_settings_path)
    missing_columns = sorted(REQUIRED_PLOT_SETTING_COLUMNS - set(settings.columns))
    if missing_columns:
        raise ValueError(f"Plot settings are missing columns: {missing_columns}")
    if len(settings) != 25 or settings["csv"].nunique() != 25:
        raise ValueError("Plot settings must contain exactly one row for each of 25 CSVs")

    expected_csvs = set(metrics["csv"].astype(str))
    configured_csvs = set(settings["csv"].astype(str))
    if configured_csvs != expected_csvs:
        raise ValueError(
            "Plot settings CSV mismatch; "
            f"missing={sorted(expected_csvs - configured_csvs)}, "
            f"extra={sorted(configured_csvs - expected_csvs)}"
        )

    metric_sensor = metrics.set_index(metrics["csv"].astype(str))["sensor_name"].astype(str)
    display_spec: dict[str, dict[str, float]] = {}
    for row in settings.itertuples(index=False):
        csv_name = str(row.csv)
        if str(row.sensor_name) != metric_sensor.loc[csv_name]:
            raise ValueError(
                f"{csv_name}: sensor_name does not match constraint_metrics.csv"
            )

        saved_off = float(row.saved_off_input_um)
        actual_saved_off = float(
            predictions.loc[predictions["csv"] == csv_name, "inducer"].min()
        )
        if not math.isclose(saved_off, actual_saved_off, rel_tol=1.0e-10, abs_tol=1.0e-15):
            raise ValueError(
                f"{csv_name}: saved_off_input_um={saved_off:g} does not match "
                f"saved predictions minimum {actual_saved_off:g}"
            )

        zero_x = float(row.graphical_zero_x_um)
        positive_min = float(row.positive_log_min_um)
        positive_max = float(row.positive_log_max_um)
        if not (zero_x > 0.0 and positive_min > 0.0 and positive_max > positive_min):
            raise ValueError(f"{csv_name}: invalid zero/positive display limits")
        for field, value in (
            ("positive_log_min_um", positive_min),
            ("positive_log_max_um", positive_max),
        ):
            if not math.isclose(math.log10(value), round(math.log10(value)), abs_tol=1.0e-10):
                raise ValueError(f"{csv_name}: {field} must be an exact power of ten")

        if str(row.visible_zero_label).strip() not in {"0", "0.0"}:
            raise ValueError(f"{csv_name}: visible_zero_label must be 0")
        if not parse_boolean(row.zero_slot_minor_ticks, "zero_slot_minor_ticks", csv_name):
            raise ValueError(f"{csv_name}: zero-slot minor ticks must remain enabled")
        if str(row.tick_direction).strip().lower() != "in":
            raise ValueError(f"{csv_name}: tick_direction must be 'in'")
        if str(row.break_geometry).strip() != EXPECTED_BREAK_GEOMETRY:
            raise ValueError(f"{csv_name}: unexpected break_geometry")
        if not parse_boolean(row.plot_only, "plot_only", csv_name):
            raise ValueError(f"{csv_name}: plot_only must be true")
        if not math.isclose(float(row.model_zero_um), 0.0, abs_tol=1.0e-15):
            raise ValueError(f"{csv_name}: model_zero_um must remain mathematical zero")

        display_spec[csv_name] = {
            "zero_x": zero_x,
            "positive_min": positive_min,
            "positive_max": positive_max,
        }

    return display_spec, settings


def matching_level(frame: pd.DataFrame, level: float) -> pd.DataFrame:
    values = frame["LBD"].to_numpy(dtype=float)
    return frame.loc[np.isclose(values, level, rtol=1.0e-7, atol=1.0e-12)]


def plot_coordinate(actual_x: np.ndarray | float, spec: dict[str, float]) -> np.ndarray:
    """Map positive scientific doses to the plot-only log coordinate."""

    actual = np.asarray(actual_x, dtype=float)
    positive_coordinate_min = spec["zero_x"] * 10.0
    return positive_coordinate_min * actual / spec["positive_min"]


def zero_aware_log_ticks(
    axis: plt.Axes,
    spec: dict[str, float],
) -> None:
    zero_x = spec["zero_x"]
    first_exponent = int(round(math.log10(spec["positive_min"])))
    last_exponent = int(round(math.log10(spec["positive_max"])))
    actual_decades = np.asarray(
        [10.0**exponent for exponent in range(first_exponent, last_exponent + 1)]
    )
    decade_ticks = plot_coordinate(actual_decades, spec).tolist()
    ticks = [zero_x, *decade_ticks]
    labels = ["0"] + [
        rf"$10^{{{exponent}}}$"
        for exponent in range(first_exponent, last_exponent + 1)
    ]
    axis.xaxis.set_major_locator(FixedLocator(ticks))
    axis.xaxis.set_major_formatter(FixedFormatter(labels))

    # The zero slot is a full graphical decade. Give it unlabeled log-style
    # minor ticks too, omitting only ticks that would collide with the measured
    # baseline gap occupied by the two break slashes.
    plot_upper = float(plot_coordinate(spec["positive_max"], spec))
    total_span = math.log10(plot_upper / zero_x)
    zero_slot_minor = []
    for multiplier in range(2, 10):
        candidate = zero_x * multiplier
        axis_fraction = math.log10(candidate / zero_x) / total_span
        if not 0.0414 <= axis_fraction <= 0.0722:
            zero_slot_minor.append(candidate)

    positive_minor_actual = [
        multiplier * 10.0**exponent
        for exponent in range(first_exponent, last_exponent)
        for multiplier in range(2, 10)
    ]
    minor_ticks = [
        *zero_slot_minor,
        *plot_coordinate(np.asarray(positive_minor_actual), spec).tolist(),
    ]
    axis.xaxis.set_minor_locator(FixedLocator(minor_ticks))
    axis.xaxis.set_minor_formatter(NullFormatter())


def draw_graphical_zero_break(axis: plt.Axes) -> None:
    """Reproduce the measured generic Supplementary Figure 13 break geometry."""

    axis.spines["bottom"].set_visible(False)
    style = {
        "transform": axis.transAxes,
        "color": "black",
        "clip_on": False,
        "linewidth": 0.5,
        "solid_capstyle": "butt",
        "zorder": 8,
    }
    # Exact generic reference baseline gap and slash endpoints, expressed as
    # fractions of the square plotting box (Supplementary Figure 13 D-L).
    axis.plot([0.0, 0.0414], [0.0, 0.0], **style)
    axis.plot([0.0722, 1.0], [0.0, 0.0], **style)
    axis.plot([0.0270, 0.0536], [-0.0158, 0.0158], **style)
    axis.plot([0.0456, 0.0722], [-0.0158, 0.0158], **style)


def rebuild_display_curves(
    input_dir: Path,
    result_dir: Path,
    curves: pd.DataFrame,
    display_spec: dict[str, dict[str, float]],
    readme_path: Path | None = None,
) -> pd.DataFrame:
    """Re-evaluate all curves on the plot-only broken-axis grids."""

    readme_path = readme_path or input_dir.parent / "README.md"
    mappings = core.read_sensor_mapping(readme_path)
    fit_data = core.load_fit_data(input_dir, mappings)
    layout = core.ParameterLayout(fit_data.mappings)
    vector = np.load(result_dir / "parameter_vector.npy")
    if vector.shape != (layout.size,):
        raise ValueError(
            f"Saved parameter vector has shape {vector.shape}; expected {(layout.size,)}"
        )

    rebuilt_rows: list[pd.DataFrame] = []
    for csv_name, spec in display_spec.items():
        matches = [
            (csv_index, mapping)
            for csv_index, mapping in enumerate(fit_data.mappings)
            if mapping.csv_name == csv_name
        ]
        if len(matches) != 1:
            raise ValueError(f"Expected exactly one mapping for {csv_name}, found {len(matches)}")
        csv_index, mapping = matches[0]
        original = curves.loc[curves["csv"] == csv_name]
        levels = sorted(original["LBD"].astype(float).unique())
        if len(levels) != 3:
            raise ValueError(f"Expected three LBD input levels for {csv_name}, found {len(levels)}")

        positive_min = spec["positive_min"]
        positive_max = spec["positive_max"]
        positive_grid = np.geomspace(positive_min, positive_max, 600)[1:]
        zero_slot_model = np.linspace(0.0, positive_min, 80)
        zero_slot_plot = np.geomspace(spec["zero_x"], spec["zero_x"] * 10.0, 80)
        plot_grid = np.concatenate(
            (zero_slot_plot, plot_coordinate(positive_grid, spec))
        )
        model_grid = np.concatenate((zero_slot_model, positive_grid))
        for level in levels:
            synthetic = core.synthetic_curve_data(
                mapping, csv_index, level, model_grid, layout
            )
            predicted, _terms = core.predict_rpu_numpy(synthetic, layout, vector)
            rebuilt_rows.append(
                pd.DataFrame(
                    {
                        "csv": csv_name,
                        "sensor_name": mapping.sensor_name,
                        "canonical_dbd": mapping.dbd,
                        "canonical_lbd": mapping.lbd,
                        "LBD": level,
                        "inducer_plot": plot_grid,
                        "model_inducer": model_grid,
                        "RPU_predicted": predicted,
                        "curve_shape_source": "saved_parameters_extended_plot_range",
                        "curve_shape_identifiability": original["curve_shape_identifiability"].iloc[0],
                    }
                )
            )

    return pd.concat(rebuilt_rows, ignore_index=True)


def plot_sensor(
    axis: plt.Axes,
    csv_name: str,
    predictions: pd.DataFrame,
    curves: pd.DataFrame,
    metrics: pd.DataFrame,
    spec: dict[str, float],
    marker_diameter_pt: float,
) -> None:
    observed = predictions.loc[predictions["csv"] == csv_name].copy()
    dense = curves.loc[curves["csv"] == csv_name].copy()
    metric = metrics.loc[metrics["csv"] == csv_name].iloc[0]
    sensor_name = str(metric["sensor_name"])
    r2_log10 = float(metric["R2_log10"])
    r2_raw = float(metric["R2_raw"])
    levels = sorted(dense["LBD"].astype(float).unique())
    source_zero_value = float(observed["inducer"].min())
    is_source_zero = np.isclose(
        observed["inducer"].to_numpy(dtype=float),
        source_zero_value,
        rtol=1.0e-10,
        atol=1.0e-15,
    )
    observed["inducer_plot"] = plot_coordinate(
        observed["inducer"].to_numpy(dtype=float), spec
    )
    observed.loc[is_source_zero, "inducer_plot"] = spec["zero_x"]

    for index, level in enumerate(levels):
        color = COLORS[index % len(COLORS)]
        observed_level = matching_level(observed, level).sort_values("inducer")
        dense_level = matching_level(dense, level).sort_values("inducer_plot")
        axis.plot(
            dense_level["inducer_plot"],
            dense_level["RPU_predicted"],
            color=color,
            linewidth=1.35,
            zorder=2,
        )
        axis.scatter(
            observed_level["inducer_plot"],
            observed_level["RPU"],
            s=marker_diameter_pt**2,
            marker=MARKER,
            facecolor=color,
            edgecolor="none",
            linewidth=0.0,
            alpha=0.88,
            zorder=3,
        )

    x_lower = spec["zero_x"]
    x_upper = float(plot_coordinate(spec["positive_max"], spec))
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlim(x_lower, x_upper)
    axis.set_ylim(Y_MIN, Y_MAX)
    # The caller supplies an explicitly square physical axes rectangle.  Do not
    # invoke Matplotlib's layout-adjusting box-aspect machinery here: it can
    # reposition log axes whose decade spans differ between panels.

    zero_aware_log_ticks(axis, spec)
    draw_graphical_zero_break(axis)

    axis.yaxis.set_major_locator(LogLocator(base=10.0))
    axis.yaxis.set_major_formatter(LogFormatterMathtext(base=10.0))
    axis.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2.0, 10.0)))
    axis.yaxis.set_minor_formatter(NullFormatter())
    axis.grid(which="major", color="#B8B8B8", linewidth=0.45, alpha=0.55)
    axis.grid(which="minor", color="#D8D8D8", linewidth=0.25, alpha=0.30)
    axis.tick_params(
        axis="both", which="major", direction="in", labelsize=7, length=3.0, width=0.6
    )
    axis.tick_params(
        axis="both", which="minor", direction="in", length=1.8, width=0.4
    )
    axis.set_xlabel("Inducer concentration (µM, log)", fontsize=8)
    axis.set_ylabel("RPU (log)", fontsize=8)

    wrapped_sensor = textwrap.fill(sensor_name, width=31)
    axis.set_title(
        (
            f"{csv_name} | {wrapped_sensor}\n"
            f"$R^2_{{raw}}$ = {r2_raw:.3f} | $R^2_{{log10}}$ = {r2_log10:.3f}"
        ),
        fontsize=8.2,
        pad=5.0,
        linespacing=1.15,
    )

    handles = [
        Line2D(
            [0],
            [0],
            color=COLORS[index % len(COLORS)],
            marker=MARKER,
            markersize=marker_diameter_pt,
            linewidth=1.2,
            markeredgecolor="none",
            markeredgewidth=0.0,
            label=f"LBD input = {level:.4g}",
        )
        for index, level in enumerate(levels)
    ]
    axis.legend(
        handles=handles,
        loc="best",
        fontsize=5.8,
        frameon=False,
        handlelength=2.0,
        borderaxespad=0.35,
        labelspacing=0.25,
    )


def load_style_settings(style_settings_path: Path | None) -> dict[str, object]:
    """Load an optional physical-layout preset without changing fit inputs."""

    if style_settings_path is None:
        return {
            "axis_length_mm": REFERENCE_AXIS_LENGTH_MM,
            "reference_axis_length_mm": REFERENCE_AXIS_LENGTH_MM,
            "reference_symbol_diameter_pt": REFERENCE_MARKER_DIAMETER_PT,
            "symbol_scaling": "linear_with_axis_length",
            "symbol_diameter_multiplier": 1.0,
            "page_width_mm": 13.5 * MM_PER_INCH,
            "page_height_mm": 9.4 * MM_PER_INCH,
            "panel_left_positions_mm": [0.07 * 13.5 * MM_PER_INCH, 0.385 * 13.5 * MM_PER_INCH, 0.70 * 13.5 * MM_PER_INCH],
            "panel_bottom_positions_mm": [0.55 * 9.4 * MM_PER_INCH, 0.105 * 9.4 * MM_PER_INCH],
            "single_panel_left_mm": 0.38 * 13.5 * MM_PER_INCH,
            "single_panel_bottom_mm": 0.31 * 9.4 * MM_PER_INCH,
        }

    with style_settings_path.open("r", encoding="utf-8") as stream:
        style = json.load(stream)
    required = {
        "axis_length_mm",
        "reference_axis_length_mm",
        "reference_symbol_diameter_pt",
        "symbol_scaling",
        "symbol_diameter_multiplier",
        "page_width_mm",
        "page_height_mm",
        "panel_left_positions_mm",
        "panel_bottom_positions_mm",
        "single_panel_left_mm",
        "single_panel_bottom_mm",
    }
    missing = sorted(required - set(style))
    if missing:
        raise ValueError(f"Style settings are missing keys: {missing}")
    if str(style["symbol_scaling"]) != "linear_with_axis_length":
        raise ValueError("symbol_scaling must be linear_with_axis_length")
    for key in (
        "axis_length_mm",
        "reference_axis_length_mm",
        "reference_symbol_diameter_pt",
        "symbol_diameter_multiplier",
        "page_width_mm",
        "page_height_mm",
    ):
        if float(style[key]) <= 0:
            raise ValueError(f"{key} must be positive")
    if len(style["panel_left_positions_mm"]) != 3:
        raise ValueError("panel_left_positions_mm must contain three columns")
    if len(style["panel_bottom_positions_mm"]) != 2:
        raise ValueError("panel_bottom_positions_mm must contain two rows")

    axis_length = float(style["axis_length_mm"])
    page_width = float(style["page_width_mm"])
    page_height = float(style["page_height_mm"])
    for left in [*style["panel_left_positions_mm"], style["single_panel_left_mm"]]:
        if float(left) < 0 or float(left) + axis_length > page_width:
            raise ValueError("A configured horizontal plotting box falls outside the page")
    for bottom in [*style["panel_bottom_positions_mm"], style["single_panel_bottom_mm"]]:
        if float(bottom) < 0 or float(bottom) + axis_length > page_height:
            raise ValueError("A configured vertical plotting box falls outside the page")
    return style


def write_pdf(
    input_dir: Path,
    result_dir: Path,
    output_pdf: Path,
    plot_settings_path: Path,
    style_settings_path: Path | None,
    readme_path: Path | None = None,
) -> tuple[Path, Path | None]:
    predictions = pd.read_csv(result_dir / "predictions.csv")
    curves = pd.read_csv(result_dir / "curves_dense.csv")
    metrics = pd.read_csv(result_dir / "constraint_metrics.csv")
    display_spec, _settings = load_display_spec(
        plot_settings_path, metrics, predictions
    )
    style = load_style_settings(style_settings_path)
    axis_length_mm = float(style["axis_length_mm"])
    reference_axis_length_mm = float(style["reference_axis_length_mm"])
    marker_diameter_pt = float(style["reference_symbol_diameter_pt"]) * (
        axis_length_mm / reference_axis_length_mm
    ) * float(style["symbol_diameter_multiplier"])
    page_width_mm = float(style["page_width_mm"])
    page_height_mm = float(style["page_height_mm"])
    curves = rebuild_display_curves(
        input_dir, result_dir, curves, display_spec, readme_path
    )

    csv_names = sorted(metrics["csv"].astype(str).unique(), key=numeric_csv_key)
    if len(csv_names) != 25:
        raise ValueError(f"Expected 25 included sensors, found {len(csv_names)}")
    if predictions["csv"].nunique() != 25 or curves["csv"].nunique() != 25:
        raise ValueError("Predictions and dense curves must both contain all 25 sensors")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    page_count = math.ceil(len(csv_names) / PANELS_PER_PAGE)
    metadata = {
        "Title": "All 25 mammalian sensor fitted response curves",
        "Author": "mamm_check_main_supp_n7 constrained log10-R2 fitting workflow",
        "Subject": "Square-panel double-log plots from the saved fitted parameter vector",
        "Keywords": "mammalian sensor, dose response, log axis, RPU, constrained fit",
    }

    with PdfPages(output_pdf, metadata=metadata) as pdf:
        for page_index, page_start in enumerate(range(0, len(csv_names), PANELS_PER_PAGE)):
            page_csvs = csv_names[page_start : page_start + PANELS_PER_PAGE]
            figure = plt.figure(
                figsize=(page_width_mm / MM_PER_INCH, page_height_mm / MM_PER_INCH)
            )
            if len(page_csvs) == 1:
                panel_positions_mm = [
                    (
                        float(style["single_panel_left_mm"]),
                        float(style["single_panel_bottom_mm"]),
                    )
                ]
            else:
                panel_positions_mm = [
                    (float(x_position), float(y_position))
                    for y_position in style["panel_bottom_positions_mm"]
                    for x_position in style["panel_left_positions_mm"]
                ]
            axes = [
                figure.add_axes(
                    [
                        x_position / page_width_mm,
                        y_position / page_height_mm,
                        axis_length_mm / page_width_mm,
                        axis_length_mm / page_height_mm,
                    ]
                )
                for x_position, y_position in panel_positions_mm[: len(page_csvs)]
            ]
            for axis, csv_name in zip(axes, page_csvs):
                plot_sensor(
                    axis,
                    csv_name,
                    predictions,
                    curves,
                    metrics,
                    display_spec[csv_name],
                    marker_diameter_pt,
                )

            figure.canvas.draw()
            for axis in axes:
                bbox_inches = axis.get_window_extent().transformed(
                    figure.dpi_scale_trans.inverted()
                )
                measured_width_mm = bbox_inches.width * MM_PER_INCH
                measured_height_mm = bbox_inches.height * MM_PER_INCH
                if not np.isclose(measured_width_mm, axis_length_mm, atol=1.0e-9):
                    raise RuntimeError(
                        f"Measured x-axis length {measured_width_mm} mm; expected {axis_length_mm} mm"
                    )
                if not np.isclose(measured_height_mm, axis_length_mm, atol=1.0e-9):
                    raise RuntimeError(
                        f"Measured y-axis length {measured_height_mm} mm; expected {axis_length_mm} mm"
                    )

            figure.suptitle(
                "All 25 mammalian sensor response curves - saved constrained fit",
                fontsize=12,
                y=0.978,
            )
            caption = (
                f"Page {page_index + 1}/{page_count} | Square plotting boxes: x- and y-axis lengths are equal. "
                "Every x axis uses a finite slot labelled 0, inward major/minor ticks, and the measured "
                "Supplementary Figure 13 break geometry; positive dose and RPU axes are log10."
            )
            compact_layout = axis_length_mm < REFERENCE_AXIS_LENGTH_MM - 1.0e-9
            figure.text(
                0.5,
                0.018 if compact_layout else 0.025,
                textwrap.fill(caption, width=105) if compact_layout else caption,
                ha="center",
                va="bottom",
                fontsize=5.5 if compact_layout else 7,
                linespacing=1.05,
            )
            pdf.savefig(figure, bbox_inches=None)
            plt.close(figure)

    if output_pdf.resolve() == DEFAULT_OUTPUT_PDF.resolve():
        used_settings_path = result_dir / USED_PLOT_SETTINGS_NAME
    else:
        used_settings_path = result_dir / f"{output_pdf.stem}_plot_settings_used.csv"
    shutil.copyfile(plot_settings_path, used_settings_path)
    used_style_path: Path | None = None
    if style_settings_path is not None:
        used_style_path = result_dir / f"{output_pdf.stem}_style_used.json"
        shutil.copyfile(style_settings_path, used_style_path)
    return used_settings_path, used_style_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--readme", type=Path, help="README containing the original six-column mapping")
    parser.add_argument("--result-dir", type=Path, default=DEFAULT_RESULT_DIR)
    parser.add_argument("--output-pdf", type=Path)
    parser.add_argument(
        "--plot-settings", type=Path
    )
    parser.add_argument(
        "--style-settings",
        type=Path,
        default=None,
        help=(
            "Physical layout preset. The accepted default is "
            "Input/all_25_sensor_30mm_style.json (30 mm square axes)."
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.output_pdf = args.output_pdf or args.result_dir / DEFAULT_OUTPUT_PDF.name
    args.plot_settings = args.plot_settings or args.input_dir / DEFAULT_PLOT_SETTINGS.name
    args.style_settings = args.style_settings or args.input_dir / DEFAULT_30MM_STYLE_SETTINGS.name
    used_settings_path, used_style_path = write_pdf(
        args.input_dir.resolve(),
        args.result_dir.resolve(),
        args.output_pdf.resolve(),
        args.plot_settings.resolve(),
        args.style_settings.resolve() if args.style_settings is not None else None,
        args.readme.resolve() if args.readme else None,
    )
    print(args.output_pdf.resolve())
    print(used_settings_path.resolve())
    if used_style_path is not None:
        print(used_style_path.resolve())


if __name__ == "__main__":
    main()
