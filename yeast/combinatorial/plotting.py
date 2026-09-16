"""Draw Note 11 using archived geometry, palettes and the two-page layout."""
from __future__ import annotations
import json
import math
import shutil
import subprocess
from io import BytesIO
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from yeast.metrics import regression_metrics
from .model import PANELS, predicted_rpu

PAGE_WIDTH_PT, PAGE_HEIGHT_PT = 595.276, 841.89


def log10_r2(panel, rows):
    selected = [r for r in rows if r["panel"] == panel]
    return regression_metrics([r["mean_RPU"] for r in selected],
        [predicted_rpu(panel, r["condition"], r["x_value_uM"], r["series_value_uM"]) for r in selected])["R2"]


def load_resources(directory, rows):
    directory = Path(directory)
    def load(name):
        return json.loads((directory / name).read_text(encoding="utf-8-sig"))
    geometry, axes, palettes = (load(name) for name in ("panel_geometry.json", "axis_template.json", "panel_palettes.json"))
    if any(set(resource) != set(PANELS) for resource in (geometry, axes, palettes)):
        raise ValueError("Geometry, axes and palettes must define all 12 panels")
    for panel in PANELS:
        box = geometry[panel]
        if box["page"] not in (1, 2) or not (0 <= box["x0"] < box["x1"] <= PAGE_WIDTH_PT and 0 <= box["top"] < box["bottom"] <= PAGE_HEIGHT_PT):
            raise ValueError(f"Invalid page geometry for {panel}")
        for key in ("x_major_tick_positions_pt", "y_major_tick_top_positions_pt"):
            ticks = np.asarray(axes[panel][key], dtype=float)
            direction = 1 if key.startswith("x_") else -1
            if ticks.shape != (6,) or not np.isfinite(ticks).all() or not np.all(direction * np.diff(ticks) > 0):
                raise ValueError(f"Invalid axis ticks for {panel}: {key}")
        lines = axes[panel].get("black_axis_lines")
        labels = axes[panel].get("r2", {})
        line_fields = ("linewidth", "x1", "x2", "top1", "top2")
        label_fields = ("right_edge_pt", "main_top_pt", "superscript_size_pt", "superscript_top_pt")
        if (not isinstance(lines, list) or not lines
                or any(any(key not in line or not math.isfinite(float(line[key])) for key in line_fields) for line in lines)
                or any(key not in labels or not math.isfinite(float(labels[key])) for key in label_fields)):
            raise ValueError(f"Missing or invalid drawing fields for {panel}")
        colors = panel_colors(panel, palettes)
        used = {r["series_value_uM"] for r in rows if r["panel"] == panel}
        if len(colors) != len(palettes[panel]) or not used.issubset(colors):
            raise ValueError(f"Missing or duplicate palette series for {panel}")
        if any(len(color) != 4 or not all(math.isfinite(v) and 0 <= v <= 1 for v in color) for color in colors.values()):
            raise ValueError(f"Invalid CMYK color for {panel}")
    return geometry, axes, palettes


def first_positive_x(panel: str) -> float:
    return 0.1 if panel in {"A1", "A2"} else 0.001


def x_to_page(x_uM: float, panel: str, axis_templates: dict) -> float:
    major = axis_templates[panel]["x_major_tick_positions_pt"]
    first = first_positive_x(panel)
    if x_uM <= 0:
        return float(major[0])
    position = 1.0 + math.log10(x_uM / first)
    if position <= 1.0:
        return float(major[0]) + max(0.0, x_uM / first) * (float(major[1]) - float(major[0]))
    position = min(5.0, position)
    lower = min(4, int(math.floor(position)))
    fraction = position - lower
    return float(major[lower]) + fraction * (float(major[lower + 1]) - float(major[lower]))


def page_to_x(page_x: float, panel: str, axis_templates: dict) -> float:
    major = axis_templates[panel]["x_major_tick_positions_pt"]
    first = first_positive_x(panel)
    if page_x <= float(major[1]):
        return max(0.0, (page_x - float(major[0])) / (float(major[1]) - float(major[0]))) * first
    for lower in range(1, 5):
        if page_x <= float(major[lower + 1]):
            fraction = (page_x - float(major[lower])) / (float(major[lower + 1]) - float(major[lower]))
            return first * 10 ** (lower + fraction - 1)
    return first * 1e4


def y_to_page(value_rpu: float, panel: str, axis_templates: dict) -> float:
    major = axis_templates[panel]["y_major_tick_top_positions_pt"]
    position = min(5.0, max(0.0, math.log10(value_rpu) + 3.0))
    lower = min(4, int(math.floor(position)))
    fraction = position - lower
    return float(major[lower]) + fraction * (float(major[lower + 1]) - float(major[lower]))


def pdf_y(top_position: float) -> float:
    return PAGE_HEIGHT_PT - top_position


def panel_colors(panel: str, palettes: dict) -> dict[float, tuple[float, float, float, float]]:
    return {
        float(entry["series_value_uM"]): tuple(float(value) for value in entry["pdf_color"])
        for entry in palettes[panel]
    }


def draw_axes(c: canvas.Canvas, panel: str, axis_templates: dict) -> None:
    c.setStrokeColorCMYK(0, 0, 0, 1)
    for line in axis_templates[panel]["black_axis_lines"]:
        c.setLineWidth(float(line["linewidth"]))
        c.line(
            float(line["x1"]),
            pdf_y(float(line["top1"])),
            float(line["x2"]),
            pdf_y(float(line["top2"])),
        )


def draw_r2_label(c: canvas.Canvas, panel: str, value: float, axis_templates: dict) -> None:
    label_spec = axis_templates[panel]["r2"]
    right_edge = float(label_spec["right_edge_pt"])
    baseline = pdf_y(float(label_spec["main_top_pt"])) - 4.758
    suffix = f" = {value:.2f}"
    superscript_size = float(label_spec["superscript_size_pt"])
    width = (
        stringWidth("R", "Helvetica", 6)
        + stringWidth("2", "Helvetica", superscript_size)
        + stringWidth(suffix, "Helvetica", 6)
    )
    x = right_edge - width
    c.setFillColorCMYK(0, 0, 0, 1)
    c.setFont("Helvetica", 6)
    c.drawString(x, baseline, "R")
    x += stringWidth("R", "Helvetica", 6)
    c.setFont("Helvetica", superscript_size)
    superscript_offset = PAGE_HEIGHT_PT - baseline - float(label_spec["superscript_top_pt"]) - 2.7755
    c.drawString(x, baseline + superscript_offset, "2")
    x += stringWidth("2", "Helvetica", superscript_size)
    c.setFont("Helvetica", 6)
    c.drawString(x, baseline, suffix)


def draw_panel(
    c: canvas.Canvas,
    panel: str,
    rows: list[dict[str, float | str | int]],
    geometry: dict,
    axis_templates: dict,
    palettes: dict,
) -> None:
    axis = geometry[panel]
    x0, x1 = float(axis["x0"]), float(axis["x1"])
    top, bottom = float(axis["top"]), float(axis["bottom"])
    condition = int(panel[1])
    panel_rows = [row for row in rows if row["panel"] == panel]
    colors = panel_colors(panel, palettes)

    c.saveState()
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0 - 1.2, pdf_y(bottom + 1.2), x1 - x0 + 2.4, bottom - top + 2.4, stroke=0, fill=1)
    clip = c.beginPath()
    clip.rect(x0, pdf_y(bottom), x1 - x0, bottom - top)
    c.clipPath(clip, stroke=0, fill=0)

    page_grid = np.linspace(
        float(axis_templates[panel]["x_major_tick_positions_pt"][0]),
        float(axis_templates[panel]["x_major_tick_positions_pt"][-1]),
        1000,
    )
    for series_uM in sorted({float(row["series_value_uM"]) for row in panel_rows}):
        color = colors[series_uM]
        c.setStrokeColorCMYK(*color)
        c.setLineWidth(0.5)
        curve = c.beginPath()
        for index, page_x in enumerate(page_grid):
            x_uM = page_to_x(float(page_x), panel, axis_templates)
            page_y = y_to_page(predicted_rpu(panel, condition, x_uM, series_uM), panel, axis_templates)
            if index == 0:
                curve.moveTo(float(page_x), pdf_y(page_y))
            else:
                curve.lineTo(float(page_x), pdf_y(page_y))
        c.drawPath(curve, stroke=1, fill=0)

        c.setStrokeColorCMYK(*color)
        c.setFillColorCMYK(*color)
        series_rows = sorted(
            [row for row in panel_rows if math.isclose(float(row["series_value_uM"]), series_uM)],
            key=lambda row: float(row["x_value_uM"]),
        )
        for row in series_rows:
            page_x = x_to_page(float(row["x_value_uM"]), panel, axis_templates)
            mean_rpu = float(row["mean_RPU"])
            sd_rpu = float(row["sample_SD_RPU"])
            upper = min(1e2, mean_rpu + sd_rpu)
            lower = max(1e-3, mean_rpu - sd_rpu)
            upper_y = y_to_page(upper, panel, axis_templates)
            lower_y = y_to_page(lower, panel, axis_templates)
            mean_y = y_to_page(mean_rpu, panel, axis_templates)
            c.setLineWidth(0.716)
            c.line(page_x, pdf_y(upper_y), page_x, pdf_y(lower_y))
            c.line(page_x - 1.505, pdf_y(upper_y), page_x + 1.505, pdf_y(upper_y))
            c.line(page_x - 1.505, pdf_y(lower_y), page_x + 1.505, pdf_y(lower_y))
            c.setLineWidth(0.119)
            c.circle(page_x, pdf_y(mean_y), 1.505, stroke=1, fill=1)

    c.restoreState()
    draw_axes(c, panel, axis_templates)
    draw_r2_label(c, panel, log10_r2(panel, rows), axis_templates)


def build_pdf(
    rows: list[dict[str, float | str | int]],
    layout_path: Path,
    output_path: Path,
    geometry: dict,
    axis_templates: dict,
    palettes: dict,
) -> None:
    overlay_buffer = BytesIO()
    overlay_canvas = canvas.Canvas(
        overlay_buffer,
        pagesize=(PAGE_WIDTH_PT, PAGE_HEIGHT_PT),
        pageCompression=1,
    )
    for page_number in (1, 2):
        panels = sorted(
            [panel for panel, axis in geometry.items() if int(axis["page"]) == page_number],
            key=lambda panel: (float(geometry[panel]["top"]), float(geometry[panel]["x0"])),
        )
        for panel in panels:
            draw_panel(overlay_canvas, panel, rows, geometry, axis_templates, palettes)
        overlay_canvas.showPage()
    overlay_canvas.save()
    overlay_buffer.seek(0)

    layout_pdf = PdfReader(str(layout_path))
    overlay_pdf = PdfReader(overlay_buffer)
    if len(layout_pdf.pages) != 2 or len(overlay_pdf.pages) != 2:
        raise ValueError("The layout and generated content must each contain exactly two pages.")
    for page in layout_pdf.pages:
        if abs(float(page.mediabox.width) - PAGE_WIDTH_PT) > .05 or abs(float(page.mediabox.height) - PAGE_HEIGHT_PT) > .05 or page.rotation != 0:
            raise ValueError("Layout must contain two unrotated A4 pages matching the coordinate resources")
    writer = PdfWriter()
    for layout_page, overlay_page in zip(layout_pdf.pages, overlay_pdf.pages):
        layout_page.merge_page(overlay_page)
        writer.add_page(layout_page)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        writer.write(handle)


def render_pngs(pdf_path: Path, output_dir: Path, dpi: int) -> list[Path]:
    if isinstance(dpi, bool) or not isinstance(dpi, int) or dpi <= 0:
        raise ValueError("PNG DPI must be a positive integer")
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("PNG output requires pdftoppm (Poppler) on PATH. Use --pdf-only to skip PNG rendering.")
    prefix = output_dir / "Supplementary_Note_11_page"
    result = subprocess.run(
        [pdftoppm, "-png", "-r", str(dpi), str(pdf_path), str(prefix)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "pdftoppm could not render the PDF.")
    raw_page_paths = [output_dir / "Supplementary_Note_11_page-1.png", output_dir / "Supplementary_Note_11_page-2.png"]
    if not all(path.exists() for path in raw_page_paths):
        raise RuntimeError("Expected two rendered PNG pages.")
    page_paths = [output_dir / "Supplementary_Note_11_page_1.png", output_dir / "Supplementary_Note_11_page_2.png"]
    for raw_path, page_path in zip(raw_page_paths, page_paths):
        raw_path.replace(page_path)
    images = []
    for path in page_paths:
        with Image.open(path) as image:
            images.append(image.convert("RGB"))
    combined = Image.new("RGB", (max(image.width for image in images), sum(image.height for image in images)), "white")
    y_offset = 0
    for image in images:
        combined.paste(image, (0, y_offset))
        y_offset += image.height
    combined_path = output_dir / "Supplementary_Note_11.png"
    combined.save(combined_path, dpi=(dpi, dpi))
    combined.close()
    for image in images:
        image.close()
    return [*page_paths, combined_path]
