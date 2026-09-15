#!/usr/bin/env python3
"""Plot pooled mammalian experiment RPU against saved model predictions.

This is a plot-only script. It reads the already fitted ``predictions.csv``
table, calculates the pooled log10-scale R2 across all individual observations,
and writes the accepted publication-ready PDF plus auditable source data and
metrics. It never refits or changes any fitted parameter.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullFormatter
import numpy as np
import pandas as pd
from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont


MM_PER_INCH = 25.4
POINTS_PER_INCH = 72.0

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULT_DIR = PACKAGE_ROOT / "Output" / "scipy_sensor_logR2_floor_0p5"
DEFAULT_PREDICTIONS = DEFAULT_RESULT_DIR / "predictions.csv"
DEFAULT_SETTINGS = (
    PACKAGE_ROOT / "Input" / "mammalian_experiment_vs_prediction_plot_settings.json"
)

OUTPUT_STEM = "mammalian_experiment_vs_prediction"
REQUIRED_COLUMNS = {
    "csv",
    "sensor_name",
    "source_row",
    "LBD",
    "inducer",
    "RPU",
    "RPU_predicted",
}
REQUIRED_SETTINGS = {
    "font_family",
    "figure_width_mm",
    "figure_height_mm",
    "axes_left_mm",
    "axes_bottom_mm",
    "axes_length_mm",
    "symbol_diameter_mm",
    "symbol_fill_color",
    "symbol_edge_color",
    "symbol_edge_width_pt",
    "axis_min_rpu",
    "axis_max_rpu",
    "identity_line_color",
    "identity_line_width_pt",
    "identity_line_dash_on_pt",
    "identity_line_dash_off_pt",
    "axis_line_width_pt",
    "major_tick_length_pt",
    "minor_tick_length_pt",
    "tick_width_pt",
    "tick_label_size_pt",
    "axis_label_size_pt",
    "r2_label_size_pt",
    "r2_decimal_places",
    "png_dpi",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_settings(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as stream:
        settings = json.load(stream)
    missing = sorted(REQUIRED_SETTINGS - set(settings))
    if missing:
        raise ValueError(f"Plot settings are missing keys: {missing}")

    positive_keys = (
        "figure_width_mm",
        "figure_height_mm",
        "axes_length_mm",
        "symbol_diameter_mm",
        "axis_min_rpu",
        "axis_max_rpu",
        "png_dpi",
    )
    for key in positive_keys:
        if not np.isfinite(float(settings[key])) or float(settings[key]) <= 0:
            raise ValueError(f"{key} must be finite and positive")

    left = float(settings["axes_left_mm"])
    bottom = float(settings["axes_bottom_mm"])
    length = float(settings["axes_length_mm"])
    width = float(settings["figure_width_mm"])
    height = float(settings["figure_height_mm"])
    if not np.isfinite([left, bottom]).all() or left < 0 or bottom < 0 or left + length > width or bottom + length > height:
        raise ValueError("The requested square axes do not fit inside the figure canvas")
    if float(settings["axis_min_rpu"]) >= float(settings["axis_max_rpu"]):
        raise ValueError("axis_min_rpu must be smaller than axis_max_rpu")
    if not str(settings["symbol_fill_color"]).upper() == "#5CC4E3":
        raise ValueError("symbol_fill_color must remain #5CC4E3 for this figure")
    if not np.isclose(float(settings["axes_length_mm"]), 35.0, atol=1e-12):
        raise ValueError("axes_length_mm must remain exactly 35 mm")
    if not np.isclose(float(settings["symbol_diameter_mm"]), 1.36, atol=1e-12):
        raise ValueError("symbol_diameter_mm must remain exactly 1.36 mm")
    return settings


def load_predictions(path: Path) -> pd.DataFrame:
    predictions = pd.read_csv(path)
    missing = sorted(REQUIRED_COLUMNS - set(predictions.columns))
    if missing:
        raise ValueError(f"predictions.csv is missing columns: {missing}")
    if predictions["csv"].nunique() != 25:
        raise ValueError("Expected saved predictions for exactly 25 mammalian sensors")

    numeric = predictions[["RPU", "RPU_predicted"]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("Experiment and prediction RPU values must all be finite")
    if (numeric <= 0).any():
        raise ValueError("Experiment and prediction RPU values must all be positive")
    return predictions


def font_can_be_pdf_subset(path: Path) -> bool:
    """Reject installed font files that FontTools cannot safely subset."""

    try:
        logging.getLogger("fontTools.subset").setLevel(logging.ERROR)
        font = TTFont(path)
        subsetter = Subsetter()
        subsetter.populate(
            text="0123456789experimentpredictionRPUlog-scale=.-²⁰¹²³⁴⁵⁶⁷⁸⁹⁻"
        )
        subsetter.subset(font)
        font.close()
        return True
    except Exception:
        return False


def font_weight(value: str | float) -> float:
    """FontManager entries may store named weights such as 'normal' or 'bold'."""
    if isinstance(value, str) and value.lower() in font_manager.weight_dict:
        return float(font_manager.weight_dict[value.lower()])
    return float(value)


def resolve_helvetica(family: str) -> tuple[Path, Path]:
    if family.strip().lower() != "helvetica":
        raise ValueError("This figure requires Helvetica")
    candidates = [
        entry
        for entry in font_manager.fontManager.ttflist
        if entry.name == "Helvetica" and entry.style == "normal"
    ]

    def choose(weight: str) -> Path:
        if weight == "normal":
            selected = [entry for entry in candidates if font_weight(entry.weight) < 600]
            preferred_filename = "helvetica_0.ttf"
        else:
            selected = [entry for entry in candidates if font_weight(entry.weight) >= 600]
            preferred_filename = "helvetica-bold.ttf"
        selected.sort(
            key=lambda entry: (
                Path(entry.fname).name.lower() != preferred_filename,
                str(entry.fname).lower(),
            )
        )
        for entry in selected:
            path = Path(entry.fname)
            if "helvetica" in path.name.lower() and font_can_be_pdf_subset(path):
                return path
        raise RuntimeError(f"No PDF-embeddable Helvetica {weight} font is installed")

    return choose("normal"), choose("bold")


def pooled_log10_r2(observed: np.ndarray, predicted: np.ndarray) -> tuple[float, float, float]:
    observed_log10 = np.log10(observed)
    predicted_log10 = np.log10(predicted)
    sse = float(np.sum((observed_log10 - predicted_log10) ** 2))
    tss = float(np.sum((observed_log10 - observed_log10.mean()) ** 2))
    if tss <= 0:
        raise ValueError("Cannot calculate pooled log10 R2 because TSS is not positive")
    return 1.0 - sse / tss, sse, tss


def write_source_data(
    predictions: pd.DataFrame,
    observed: np.ndarray,
    predicted: np.ndarray,
    output_path: Path,
) -> None:
    columns = ["csv", "sensor_name", "source_row", "LBD", "inducer"]
    source_data = predictions.loc[:, columns].copy()
    source_data["experiment_RPU"] = observed
    source_data["prediction_RPU"] = predicted
    source_data["log10_experiment_RPU"] = np.log10(observed)
    source_data["log10_prediction_RPU"] = np.log10(predicted)
    source_data.to_csv(output_path, index=False)


def configure_fonts(
    regular_path: Path,
    bold_path: Path,
) -> tuple[font_manager.FontProperties, font_manager.FontProperties]:
    regular = font_manager.FontProperties(fname=str(regular_path), weight="normal")
    bold = font_manager.FontProperties(fname=str(bold_path), weight="bold")
    matplotlib.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.unicode_minus": False,
        }
    )
    return regular, bold


SUPERSCRIPT_TRANSLATION = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def format_log_decade(value: float, _: object) -> str:
    if value <= 0 or not np.isfinite(value):
        return ""
    exponent = int(round(np.log10(value)))
    if not np.isclose(value, 10.0**exponent, rtol=1e-10, atol=0.0):
        return ""
    return "10" + str(exponent).translate(SUPERSCRIPT_TRANSLATION)


def make_figure(
    observed: np.ndarray,
    predicted: np.ndarray,
    r2_log10: float,
    settings: dict[str, object],
    regular_font: font_manager.FontProperties,
    bold_font: font_manager.FontProperties,
) -> tuple[plt.Figure, plt.Axes, float]:
    figure_width_mm = float(settings["figure_width_mm"])
    figure_height_mm = float(settings["figure_height_mm"])
    axes_left_mm = float(settings["axes_left_mm"])
    axes_bottom_mm = float(settings["axes_bottom_mm"])
    axes_length_mm = float(settings["axes_length_mm"])

    figure = plt.figure(
        figsize=(figure_width_mm / MM_PER_INCH, figure_height_mm / MM_PER_INCH),
        facecolor="white",
    )
    axis = figure.add_axes(
        [
            axes_left_mm / figure_width_mm,
            axes_bottom_mm / figure_height_mm,
            axes_length_mm / figure_width_mm,
            axes_length_mm / figure_height_mm,
        ]
    )

    axis_min = float(settings["axis_min_rpu"])
    axis_max = float(settings["axis_max_rpu"])
    if observed.min() < axis_min or predicted.min() < axis_min:
        raise ValueError("An experiment or prediction value falls below axis_min_rpu")
    if observed.max() > axis_max or predicted.max() > axis_max:
        raise ValueError("An experiment or prediction value exceeds axis_max_rpu")

    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlim(axis_min, axis_max)
    axis.set_ylim(axis_min, axis_max)

    axis.plot(
        [axis_min, axis_max],
        [axis_min, axis_max],
        color=str(settings["identity_line_color"]),
        linewidth=float(settings["identity_line_width_pt"]),
        linestyle=(
            0,
            (
                float(settings["identity_line_dash_on_pt"]),
                float(settings["identity_line_dash_off_pt"]),
            ),
        ),
        zorder=1,
    )

    symbol_diameter_pt = float(settings["symbol_diameter_mm"]) * POINTS_PER_INCH / MM_PER_INCH
    axis.scatter(
        observed,
        predicted,
        s=symbol_diameter_pt**2,
        marker="o",
        facecolor=str(settings["symbol_fill_color"]),
        edgecolor=str(settings["symbol_edge_color"]),
        linewidth=float(settings["symbol_edge_width_pt"]),
        alpha=1.0,
        clip_on=True,
        zorder=2,
    )

    decade_min = int(round(np.log10(axis_min)))
    decade_max = int(round(np.log10(axis_max)))
    major_ticks = 10.0 ** np.arange(decade_min, decade_max + 1)
    # LogLocator expects decade multipliers 2-9, not fractional values 0.2-0.9.
    # Using the correct multipliers makes all x-axis minor ticks visible.
    # Force enough candidate ticks for the physically short 35 mm axis.
    # LogLocator's default numticks='auto' can otherwise suppress every minor
    # tick after estimating the small amount of available label space.
    minor_locator = LogLocator(
        base=10.0,
        subs=np.arange(2.0, 10.0),
        numticks=100,
    )
    formatter = FuncFormatter(format_log_decade)
    axis.xaxis.set_major_locator(FixedLocator(major_ticks))
    axis.yaxis.set_major_locator(FixedLocator(major_ticks))
    axis.xaxis.set_minor_locator(minor_locator)
    axis.yaxis.set_minor_locator(
        LogLocator(
            base=10.0,
            subs=np.arange(2.0, 10.0),
            numticks=100,
        )
    )
    axis.xaxis.set_major_formatter(formatter)
    axis.yaxis.set_major_formatter(FuncFormatter(format_log_decade))
    axis.xaxis.set_minor_formatter(NullFormatter())
    axis.yaxis.set_minor_formatter(NullFormatter())

    axis.tick_params(
        axis="both",
        which="major",
        direction="in",
        top=False,
        right=False,
        length=float(settings["major_tick_length_pt"]),
        width=float(settings["tick_width_pt"]),
        labelsize=float(settings["tick_label_size_pt"]),
        pad=2.0,
    )
    axis.tick_params(
        axis="both",
        which="minor",
        direction="in",
        top=False,
        right=False,
        length=float(settings["minor_tick_length_pt"]),
        width=float(settings["tick_width_pt"]),
    )
    for spine in axis.spines.values():
        spine.set_color("#000000")
        spine.set_linewidth(float(settings["axis_line_width_pt"]))

    axis.set_xlabel(
        "experiment (RPU)",
        fontsize=float(settings["axis_label_size_pt"]),
        fontproperties=bold_font,
        labelpad=4.5,
    )
    axis.set_ylabel(
        "prediction (RPU)",
        fontsize=float(settings["axis_label_size_pt"]),
        fontproperties=bold_font,
        labelpad=5.0,
    )
    decimals = int(settings["r2_decimal_places"])
    axis.text(
        0.03,
        0.97,
        f"log10-scale R² = {r2_log10:.{decimals}f}",
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=float(settings["r2_label_size_pt"]),
        fontproperties=regular_font,
        zorder=4,
    )
    for label in [*axis.get_xticklabels(), *axis.get_yticklabels()]:
        label.set_fontproperties(regular_font)
        label.set_fontsize(float(settings["tick_label_size_pt"]))

    figure.canvas.draw()
    bbox_inches = axis.get_window_extent().transformed(figure.dpi_scale_trans.inverted())
    actual_width_mm = bbox_inches.width * MM_PER_INCH
    actual_height_mm = bbox_inches.height * MM_PER_INCH
    if not np.isclose(actual_width_mm, axes_length_mm, atol=1e-9):
        raise RuntimeError(f"x-axis physical length is {actual_width_mm}, expected {axes_length_mm} mm")
    if not np.isclose(actual_height_mm, axes_length_mm, atol=1e-9):
        raise RuntimeError(f"y-axis physical length is {actual_height_mm}, expected {axes_length_mm} mm")
    return figure, axis, symbol_diameter_pt


def main(
    predictions_path: Path,
    settings_path: Path,
    output_dir: Path,
) -> list[Path]:
    settings = load_settings(settings_path)
    predictions = load_predictions(predictions_path)
    regular_path, bold_path = resolve_helvetica(str(settings["font_family"]))
    regular_font, bold_font = configure_fonts(regular_path, bold_path)

    observed = predictions["RPU"].to_numpy(dtype=float)
    predicted = predictions["RPU_predicted"].to_numpy(dtype=float)
    r2_log10, sse_log10, tss_log10 = pooled_log10_r2(observed, predicted)

    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{OUTPUT_STEM}.pdf"
    source_data_path = output_dir / f"{OUTPUT_STEM}_source_data.csv"
    metrics_path = output_dir / f"{OUTPUT_STEM}_metrics.csv"
    settings_used_path = output_dir / f"{OUTPUT_STEM}_plot_settings_used.json"

    write_source_data(predictions, observed, predicted, source_data_path)
    figure, _, symbol_diameter_pt = make_figure(
        observed,
        predicted,
        r2_log10,
        settings,
        regular_font,
        bold_font,
    )
    figure.savefig(
        pdf_path,
        format="pdf",
        facecolor="white",
        metadata={
            "Title": "Mammalian experiment versus prediction",
            "Subject": "Pooled log10-scale R2 from the saved 25-sensor fit",
            "Creator": "plot_mammalian_experiment_vs_prediction.py",
        },
    )
    plt.close(figure)

    metrics = pd.DataFrame(
        [
            {
                "n_points": len(predictions),
                "n_sensors": predictions["csv"].nunique(),
                "pooled_R2_log10": r2_log10,
                "SSE_log10": sse_log10,
                "TSS_log10": tss_log10,
                "experiment_RPU_min": observed.min(),
                "experiment_RPU_max": observed.max(),
                "prediction_RPU_min": predicted.min(),
                "prediction_RPU_max": predicted.max(),
                "x_axis_length_mm": float(settings["axes_length_mm"]),
                "y_axis_length_mm": float(settings["axes_length_mm"]),
                "symbol_diameter_mm": float(settings["symbol_diameter_mm"]),
                "symbol_diameter_pt": symbol_diameter_pt,
                "symbol_fill_color": str(settings["symbol_fill_color"]),
                "font_family": str(settings["font_family"]),
                "font_regular_file": str(regular_path),
                "font_bold_file": str(bold_path),
                "predictions_sha256": sha256(predictions_path),
            }
        ]
    )
    metrics.to_csv(metrics_path, index=False)
    shutil.copyfile(settings_path, settings_used_path)

    outputs = [
        pdf_path,
        source_data_path,
        metrics_path,
        settings_used_path,
    ]
    for output in outputs:
        print(output)
    print(f"pooled log10-scale R2 = {r2_log10:.12f}; n = {len(predictions)}")
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULT_DIR)
    arguments = parser.parse_args()
    main(arguments.predictions, arguments.settings, arguments.output_dir)
