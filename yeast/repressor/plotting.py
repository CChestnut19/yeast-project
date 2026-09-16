"""Original 35 mm Note 10 scatter layout; annotation explicitly uses raw R2."""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from .model import SENSORS
from .pipeline import summarize

COLORS = {"CI94": "#80BED8", "CI43470": "#F0B5A7", "LexAgs91": "#B6D3A5", "LexAbs94": "#E5A3BB"}
PANEL_INCH = 35.0 / 25.4
AXIS_MIN, AXIS_MAX = 1e-3, 1e2


def pooled_r2(rows):
    return summarize(rows)["raw"]["pooled"]["R2"]


def make_plot(rows: list[dict], output_dir) -> None:
    output_dir = Path(output_dir)
    PDF_FILE = output_dir / "pdf/experiment_vs_prediction_35mm.pdf"
    SVG_FILE = output_dir / "svg/experiment_vs_prediction_35mm.svg"
    PNG_FILE = output_dir / "png/experiment_vs_prediction_35mm_600dpi.png"
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans", "Helvetica"],
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.linewidth": 0.55,
    })

    fig = plt.figure(figsize=(PANEL_INCH, PANEL_INCH), facecolor="white")
    ax = fig.add_axes([0.205, 0.176, 0.755, 0.755])
    ax.set_xscale("log", base=10)
    ax.set_yscale("log", base=10)
    ax.set_xlim(AXIS_MIN, AXIS_MAX)
    ax.set_ylim(AXIS_MIN, AXIS_MAX)
    ax.set_aspect("equal", adjustable="box")

    for sensor in SENSORS:
        selected = [row for row in rows if row["sensor"] == sensor]
        ax.scatter(
            [row["experiment_rpu"] for row in selected],
            [row["prediction_rpu"] for row in selected],
            s=6.2,
            marker="o",
            facecolor=COLORS[sensor],
            edgecolor="black",
            linewidth=0.28,
            alpha=1.0,
            label=sensor,
            zorder=3,
        )

    ax.plot(
        [AXIS_MIN, AXIS_MAX],
        [AXIS_MIN, AXIS_MAX],
        color="black",
        linewidth=0.62,
        linestyle=(0, (3.5, 2.2)),
        zorder=1,
    )
    ax.text(
        0.045,
        0.965,
        f"R\u00b2 (raw) = {pooled_r2(rows):.2f}",
        transform=ax.transAxes,
        fontsize=4.7,
        ha="left",
        va="top",
    )

    major_ticks = [10.0**exponent for exponent in range(-3, 3)]
    minor_ticks = [
        multiplier * 10.0**exponent
        for exponent in range(-3, 2)
        for multiplier in range(2, 10)
    ]
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(mpl.ticker.FixedLocator(major_ticks))
        axis.set_minor_locator(mpl.ticker.FixedLocator(minor_ticks))
        axis.set_major_formatter(mpl.ticker.LogFormatterMathtext(base=10))
        axis.set_minor_formatter(mpl.ticker.NullFormatter())

    ax.tick_params(
        which="major", direction="in", length=3.0, width=0.5,
        labelsize=4.15, pad=1.0, top=False, right=False,
    )
    ax.tick_params(
        which="minor", direction="in", length=1.5, width=0.45,
        top=False, right=False,
    )
    ax.set_xlabel("experiment (RPU)", fontsize=5.7, fontweight="bold", labelpad=1.0)
    ax.set_ylabel("prediction (RPU)", fontsize=5.7, fontweight="bold", labelpad=1.2)
    ax.legend(
        loc="lower right",
        bbox_to_anchor=(0.975, 0.025),
        ncol=2,
        frameon=False,
        fontsize=3.25,
        handletextpad=0.22,
        columnspacing=0.45,
        labelspacing=0.15,
        borderpad=0.0,
        markerscale=0.78,
    )

    for path in (PDF_FILE, SVG_FILE, PNG_FILE):
        path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PDF_FILE, format="pdf", bbox_inches=None, pad_inches=0)
    fig.savefig(SVG_FILE, format="svg", bbox_inches=None, pad_inches=0)
    fig.savefig(PNG_FILE, format="png", dpi=600, bbox_inches=None, pad_inches=0)
    plt.close(fig)

    svg = SVG_FILE.read_text(encoding="utf-8")
    svg = svg.replace(
        'width="99.212598pt" height="99.212598pt"',
        'width="35mm" height="35mm"',
        1,
    )
    SVG_FILE.write_text(svg, encoding="utf-8")
