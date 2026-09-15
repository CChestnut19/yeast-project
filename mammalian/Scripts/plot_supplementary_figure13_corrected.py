from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
from pypdf import PdfReader, PdfWriter
from pypdf import PageObject
from pypdf.generic import RectangleObject
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.colors import CMYKColor, black

from model_core import cic_response_numpy


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "Input" / "Supplementary Figure 13_original.pdf"
BACKEND = ROOT / "Output" / "scipy_sensor_logR2_floor_0p5"
PREDICTIONS = BACKEND / "predictions.csv"
PARAMETERS_LBD = BACKEND / "parameters_lbd.csv"
PARAMETERS_DBD = BACKEND / "parameters_dbd.csv"
OUT = BACKEND
TEMP = ROOT / "tmp" / "pdfs"
LAYER = TEMP / "FigS13_DM_sensor_logR2_floor_layer.pdf"
FINAL = OUT / "Supplementary Figure 13_corrected.pdf"
PAGE_W, PAGE_H = 595.276, 841.89

PANEL_CSV = {
    "D": "540.csv",
    "E": "541.csv",
    "F": "542.csv",
    "G": "405.csv",
    "H": "403.csv",
    "I": "415.csv",
    "J": "414.csv",
    "K": "408.csv",
    "L": "406.csv",
    "M": "407.csv",
}

PANELS = {
    "D": dict(axis=(65.4117,248.0774,150.4510,333.1168), letter=(30.1597,235.8036), title_top=238.8918, title=[("lexA",6,0),("ec87",4,-1.4),("-TraR",6,0),("174",4,-1.4),("-VP16",6,0)], xlabel=[("3OC8 (uM)",6,"Helvetica")], exponents=range(0,5), curve="DF", marker="DF"),
    "E": dict(axis=(200.8971,248.0774,285.9365,333.1168), letter=(177.6318,235.8046), title_top=240.7287, title=[("CI434",6,0),("70",4,-1.4),("-TraR",6,0),("174",4,-1.4),("-VP16",6,0)], xlabel=[("3OC8 (uM)",6,"Helvetica")], exponents=range(0,5), curve="DF", marker="DF"),
    "F": dict(axis=(336.4066,248.0774,421.4459,333.1168), letter=(313.1172,235.8046), title_top=240.7287, title=[("CI434",6,0),("70",4,-1.4),("-CinR",6,0),("179",4,-1.4),("-VP16",6,0)], xlabel=[("3OHC14-HSL (uM)",6,"Helvetica")], exponents=range(-2,3), curve="DF", marker="DF"),
    "G": dict(axis=(469.8273,248.0774,554.8666,333.1168), letter=(448.8154,235.8036), title_top=239.8918, title=[("lexA",6,0),("xa101",4,-1.4),("-ER",6,0),("282-595",4,-1.4),("-VP16",6,0)], xlabel=[("β",6,"BetaVector"),("-estradiol (uM)",6,"Helvetica")], exponents=range(-4,1), curve="GM", marker="DF"),
    "H": dict(axis=(65.4073,369.0965,150.4505,454.1359), letter=(30.1597,357.0429), title_top=360.2316, title=[("CI434",6,0),("70",4,-1.4),("-ER",6,0),("282-595",4,-1.4),("-VP16",6,0)], xlabel=[("β",6,"BetaVector"),("-estradiol (uM)",6,"Helvetica")], exponents=range(-6,-1), curve="GM", marker="GM"),
    "I": dict(axis=(201.3639,369.1442,286.4032,454.1836), letter=(177.4980,357.0429), title_top=360.2316, title=[("lexA",6,0),("xa101",4,-1.4),("-MR",6,0),("669-984",4,-1.4),("-VP16",6,0)], xlabel=[("aldo (uM)",6,"Helvetica")], exponents=range(-4,1), curve="GM", marker="DF"),
    "J": dict(axis=(336.7346,369.1442,421.7740,454.1836), letter=(313.9185,357.0429), title_top=360.2316, title=[("lexA",6,0),("ec87",4,-1.4),("-MR",6,0),("669-984",4,-1.4),("-VP16",6,0)], xlabel=[("aldo (uM)",6,"Helvetica")], exponents=range(-4,1), curve="GM", marker="DF"),
    "K": dict(axis=(470.0815,367.0004,555.1208,452.0397), letter=(448.8164,357.0429), title_top=360.8049, title=[("PurR",6,0),("60",4,-1.4),("-DHBR",6,0),("282-595",4,-1.4),("-VP16",6,0)], xlabel=[("DHB (uM)",6,"Helvetica")], exponents=range(-2,3), curve="GM", marker="DF"),
    "L": dict(axis=(64.6445,489.5499,149.6839,574.5893), letter=(30.1597,482.9525), title_top=481.5295, title=[("PurR",6,0),("60",4,-1.4),("-RpaR",6,0),("179",4,-1.4),("-VP16",6,0)], xlabel=[("pC-HSL (uM)",6,"Helvetica")], exponents=range(-1,4), curve="GM", marker="GM"),
    "M": dict(axis=(202.3882,489.5499,287.4277,574.5893), letter=(178.5806,482.9525), title_top=481.5295, title=[("lexA",6,0),("mm115",4,-1.4),("-RpaR",6,0),("179",4,-1.4),("-VP16",6,0)], xlabel=[("pC-HSL (uM)",6,"Helvetica")], exponents=range(-2,4), curve="GM", marker="GM"),
}
PALETTES = {
    "DF": [CMYKColor(0.867,0.469,0.043,0), CMYKColor(0,0.613,1,0), CMYKColor(0.828,0.094,1,0.012)],
    "GM": [CMYKColor(0.992,0.438,0.055,0), CMYKColor(0,0.625,0.965,0), CMYKColor(1,0.020,1,0.004)],
}

# Arial-compatible beta outline, converted to filled vector polygons at unit
# font size.  It avoids adding a non-Helvetica font resource to the D-M layer.
BETA_POLYGONS = [
    [(0.15578125,0.0659375),(0.15578125,-0.19875),(0.0684375,-0.19875),(0.0684375,0.49125),(0.073984375,0.564765625),(0.090625,0.6203125),(0.120820313,0.66296875),(0.16703125,0.6975),(0.224296875,0.720351563),(0.28765625,0.72796875),(0.373867188,0.713867188),(0.43625,0.6715625),(0.47421875,0.612617188),(0.486875,0.54828125),(0.476679688,0.489257813),(0.44609375,0.4428125),(0.402304688,0.410507813),(0.3525,0.39359375),(0.427773438,0.374179688),(0.48359375,0.3325),(0.51828125,0.273710938),(0.52984375,0.20265625),(0.516210938,0.123984375),(0.4753125,0.05390625),(0.40875,0.0046875),(0.3178125,-0.01171875),(0.224570313,0.007695313),(0.15578125,0.0659375)],
    [(0.2334375,0.421875),(0.311054688,0.4296875),(0.36421875,0.453125),(0.395039063,0.491328125),(0.4053125,0.5434375),(0.3965625,0.58734375),(0.3703125,0.6234375),(0.331132813,0.647695313),(0.28328125,0.65578125),(0.240820313,0.649804688),(0.204375,0.631875),(0.177382813,0.606601563),(0.16328125,0.57859375),(0.15765625,0.538359375),(0.15578125,0.47609375),(0.15578125,0.279375),(0.158710938,0.206445313),(0.1675,0.15578125),(0.1859375,0.118203125),(0.2178125,0.08453125),(0.259335938,0.060742188),(0.30671875,0.0528125),(0.36125,0.063242188),(0.40296875,0.09453125),(0.429570313,0.141210938),(0.4384375,0.1978125),(0.431914063,0.2459375),(0.41234375,0.28875),(0.383164063,0.322578125),(0.3478125,0.3434375),(0.303242188,0.354335938),(0.24609375,0.35796875),(0.2334375,0.35796875),(0.2334375,0.421875)],
]


def rows():
    with PARAMETERS_LBD.open(encoding="utf-8-sig") as handle:
        lbd_parameters = {
            row["canonical_lbd"]: row for row in csv.DictReader(handle)
        }
    with PARAMETERS_DBD.open(encoding="utf-8-sig") as handle:
        dbd_parameters = {
            row["canonical_dbd"]: row for row in csv.DictReader(handle)
        }
    csv_to_panel = {csv_name: panel for panel, csv_name in PANEL_CSV.items()}
    with PREDICTIONS.open(encoding="utf-8-sig") as handle:
        source = [
            row for row in csv.DictReader(handle) if row["csv"] in csv_to_panel
        ]

    # Several inherited fitting CSVs used a tiny pseudo-dose at the source
    # zero concentration for log-axis plotting. Supplementary Figure 13 uses
    # a genuine zero slot before the broken log axis, so only the plot x value
    # is restored to zero here; the fitted parameter vector is not changed.
    true_zero_csv = {
        "540.csv",
        "541.csv",
        "405.csv",
        "403.csv",
        "415.csv",
        "414.csv",
        "408.csv",
        "406.csv",
    }
    minimum_by_csv = {
        csv_name: min(float(row["inducer"]) for row in source if row["csv"] == csv_name)
        for csv_name in PANEL_CSV.values()
    }
    output = []
    for row in source:
        panel = csv_to_panel[row["csv"]]
        lbd = lbd_parameters[row["canonical_lbd"]]
        dbd = dbd_parameters[row["canonical_dbd"]]
        inducer = float(row["inducer"])
        if row["csv"] in true_zero_csv and inducer == minimum_by_csv[row["csv"]]:
            inducer = 0.0
        output.append(
            {
                "panel": panel,
                "csv": row["csv"],
                "tf_input_rpu": float(row["LBD"]),
                "inducer_uM": inducer,
                "observed_output_rpu": float(row["RPU"]),
                "kd0": float(lbd["Kd0"]),
                "kb_per_uM": float(lbd["Kb_uM_inverse"]),
                "kd1": float(lbd["Kd1"]),
                "ka": float(dbd["KA"]),
                "t0_variant_rpu": float(dbd["T0_variant"]),
                "tmax_rpu": float(dbd["Tmax"]),
            }
        )
    return output


def model(c_i, ctf, kd0, kb, kd1, ka, t0, tmax):
    return cic_response_numpy(c_i, ctf, kd0, kb, kd1, ka, t0, tmax)[0]


def x_axis(panel, x):
    exps=list(PANELS[panel]["exponents"]); n=len(exps)
    return 0 if x==0 else (1+math.log10(x)-exps[0])/n


def y_axis(y):
    return (math.log10(y)+3)/5


def part_width(text,size,font):
    return 0.56*size if font=="BetaVector" else stringWidth(text,font,size)


def rich_width(parts):
    return sum(part_width(text,size,font) for text,size,font in parts)


def draw_beta_vector(c,x,baseline,size):
    path=c.beginPath()
    for polygon in BETA_POLYGONS:
        path.moveTo(x+polygon[0][0]*size,baseline+polygon[0][1]*size)
        for px,py in polygon[1:]: path.lineTo(x+px*size,baseline+py*size)
        path.close()
    c.setFillColor(black); c.drawPath(path,stroke=0,fill=1,fillMode=0)


def draw_rich(c, center_x, baseline_y, parts):
    x=center_x-rich_width(parts)/2
    for text,size,font in parts:
        if font=="BetaVector": draw_beta_vector(c,x,baseline_y,size)
        else: c.setFont(font,size); c.drawString(x,baseline_y,text)
        x+=part_width(text,size,font)


def draw_title(c, center_x, top, parts):
    converted=[(text,size,"Helvetica") for text,size,shift in parts]
    widths=[stringWidth(text,"Helvetica",size) for text,size,shift in parts]; x=center_x-sum(widths)/2
    base=PAGE_H-top-5.0
    for (text,size,shift),w in zip(parts,widths):
        c.setFont("Helvetica",size); c.drawString(x,base+shift,text); x+=w


def draw_log_label(c, center_or_right, baseline, exponent, align="center"):
    base="10"; exp=str(exponent); w1=stringWidth(base,"Helvetica",6); w2=stringWidth(exp,"Helvetica",4); total=w1+w2
    x=center_or_right-total/2 if align=="center" else center_or_right-total
    c.setFont("Helvetica",6); c.drawString(x,baseline,base)
    c.setFont("Helvetica",4); c.drawString(x+w1,baseline+2.0,exp)


def draw_panel(c,panel,cfg,data):
    x0,top,x1,bottom=cfg["axis"]; y0=PAGE_H-bottom; y1=PAGE_H-top; w=x1-x0; h=bottom-top; exps=list(cfg["exponents"]); n=len(exps)
    # Model curves and individual replicate points, clipped to the axes rectangle.
    c.saveState(); clip=c.beginPath(); clip.rect(x0,y0,w,h); c.clipPath(clip,stroke=0,fill=0)
    levels=sorted({float(r["tf_input_rpu"]) for r in data}); first=data[0]; pars={k:float(first[k]) for k in ("kd0","kb_per_uM","kd1","ka","t0_variant_rpu","tmax_rpu")}
    lo,hi=10**exps[0],10**exps[-1]; ci=np.concatenate([np.linspace(0,lo,80),np.geomspace(lo,hi,1000)[1:]])
    u=np.concatenate([np.linspace(0,1/n,80),np.asarray([(1+math.log10(v)-exps[0])/n for v in np.geomspace(lo,hi,1000)[1:]])])
    for idx,tf in enumerate(levels):
        yy=model(ci,tf,pars["kd0"],pars["kb_per_uM"],pars["kd1"],pars["ka"],pars["t0_variant_rpu"],pars["tmax_rpu"])
        c.setStrokeColor(PALETTES[cfg["curve"]][idx]); c.setLineWidth(0.5); path=c.beginPath(); path.moveTo(x0+u[0]*w,y0+y_axis(yy[0])*h)
        for ux,yv in zip(u[1:],yy[1:]): path.lineTo(x0+ux*w,y0+y_axis(yv)*h)
        c.drawPath(path,stroke=1,fill=0)
        color=PALETTES[cfg["marker"]][idx]; c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.0)
        for r in data:
            if float(r["tf_input_rpu"])!=tf: continue
            px=x0+x_axis(panel,float(r["inducer_uM"]))*w; py=y0+y_axis(float(r["observed_output_rpu"]))*h
            c.circle(px,py,1.417,stroke=1,fill=1)
    c.restoreState()

    # Axes and ticks.
    c.setStrokeColor(black); c.setFillColor(black); c.setLineWidth(0.5)
    c.line(x0,y0,x0,y1); c.line(x0,y1,x1,y1); c.line(x1,y0,x1,y1)
    if panel == "M":
        # Panel M in the supplied reference has a deliberately tighter
        # decorative break than the other panels.  These are direct vector
        # measurements from the reference PDF (page-space top coordinates
        # converted to ReportLab bottom coordinates).
        axis_y = PAGE_H - 574.5893
        c.line(202.3884,axis_y,203.3414,axis_y)
        c.line(205.0804,axis_y,287.4274,axis_y)
        c.line(202.2089,PAGE_H-575.9320,204.4749,PAGE_H-573.2460)
        c.line(203.7953,PAGE_H-575.9320,206.0613,PAGE_H-573.2460)
    else:
        # All other panels share the measured reference break geometry.
        # H's x-axis/break baseline is 0.0481 pt below its vertical-axis end
        # in the source PDF, so preserve that sub-point source geometry.
        axis_y = PAGE_H - 454.1840 if panel == "H" else y0
        c.line(x0,axis_y,x0+0.0414*w,axis_y)
        c.line(x0+0.0722*w,axis_y,x1,axis_y)
        # Exact reference direction: / /
        c.line(x0+0.0270*w,axis_y-0.0158*h,x0+0.0536*w,axis_y+0.0158*h)
        c.line(x0+0.0456*w,axis_y-0.0158*h,x0+0.0722*w,axis_y+0.0158*h)
    for i,e in enumerate(exps,1):
        px=x0+i/n*w; c.line(px,y0,px,y0+2.835); draw_log_label(c,px,y0-8.51,e,"center")
    c.setFont("Helvetica",6); c.drawCentredString(x0,y0-8.51,"0")
    for idx,e in enumerate(exps[:-1],1):
        for m in range(2,10):
            px=x0+(idx+math.log10(m))/n*w; c.setLineWidth(0.6); c.line(px,y0,px,y0+1.62)
    for e in range(-3,3):
        py=y0+(e+3)/5*h; c.setLineWidth(0.5); c.line(x0,py,x0+2.835,py); draw_log_label(c,x0-4.3,py-2.2,e,"right")
        if e<2:
            for m in range(2,10):
                my=y0+(e+3+math.log10(m))/5*h; c.setLineWidth(0.6); c.line(x0,my,x0+1.62,my)
    # Original Helvetica text hierarchy.
    lx,lt=cfg["letter"]; c.setFont("Helvetica-Bold",8); c.drawString(lx,PAGE_H-lt-6.4,panel)
    draw_title(c,(x0+x1)/2,cfg["title_top"],cfg["title"])
    draw_rich(c,(x0+x1)/2,y0-17.0,cfg["xlabel"])
    c.saveState(); c.translate(x0-18.65,(y0+y1)/2); c.rotate(90); c.setFont("Helvetica",6); c.drawCentredString(0,-2.0,"Output (RPU)"); c.restoreState()


def create_layer():
    TEMP.mkdir(parents=True, exist_ok=True)
    data=rows(); grouped=defaultdict(list)
    for r in data: grouped[r["panel"]].append(r)
    c=canvas.Canvas(str(LAYER),pagesize=(PAGE_W,PAGE_H),pageCompression=1)
    c.setTitle("Supplementary Figure 13 corrected D-M - per-sensor log R2 floor")
    for panel,cfg in PANELS.items(): draw_panel(c,panel,cfg,grouped[panel])
    c.showPage(); c.save()


def assemble_clean_pdf():
    OUT.mkdir(parents=True, exist_ok=True)
    if not REFERENCE.is_file():
        raise FileNotFoundError(f"Missing original Figure 13 PDF: {REFERENCE}")
    create_layer()
    ref=PdfReader(str(REFERENCE)); dm=PdfReader(str(LAYER)); source=ref.pages[0]
    # Only A-C are admitted from the reference page.  The crop boundary is
    # above panel D, so no legacy D-M object enters the visible corrected page.
    source.cropbox=RectangleObject([0,PAGE_H-230.0,PAGE_W,PAGE_H])
    page=PageObject.create_blank_page(width=PAGE_W,height=PAGE_H)
    page.merge_page(source)
    page.merge_page(dm.pages[0])
    writer=PdfWriter(); writer.add_page(page); writer.add_metadata({"/Title":"Supplementary Figure 13 corrected - all-sensor log10 R2 floor fit", "/Creator":"Exact reference geometry; Helvetica text; operator number 7"})
    with FINAL.open("wb") as handle: writer.write(handle)
    write_audit_files()
    print(FINAL)


def write_audit_files():
    data = rows()
    grouped = defaultdict(list)
    for row in data:
        grouped[row["panel"]].append(row)
    metric_rows = []
    for panel in sorted(grouped):
        panel_rows = grouped[panel]
        observed = np.asarray(
            [row["observed_output_rpu"] for row in panel_rows], dtype=float
        )
        predicted = np.asarray(
            [
                model(
                    [row["inducer_uM"]],
                    row["tf_input_rpu"],
                    row["kd0"],
                    row["kb_per_uM"],
                    row["kd1"],
                    row["ka"],
                    row["t0_variant_rpu"],
                    row["tmax_rpu"],
                )[0]
                for row in panel_rows
            ],
            dtype=float,
        )
        observed_log = np.log10(observed)
        predicted_log = np.log10(predicted)
        r2 = 1.0 - float(np.sum((observed_log - predicted_log) ** 2)) / float(
            np.sum((observed_log - observed_log.mean()) ** 2)
        )
        metric_rows.append(
            {
                "panel": panel,
                "csv": PANEL_CSV[panel],
                "n": len(panel_rows),
                "R2_log10_with_source_zero_plot_positions": r2,
                "passes_0p5": r2 >= 0.5,
            }
        )
    with (OUT / "corrected_pdf_panel_metrics.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)

    style = {
        "reference": "Supplementary Figure 13_original.pdf",
        "page": {"size": "A4", "width_pt": PAGE_W, "height_pt": PAGE_H},
        "panels_replaced": "D-M",
        "panel_axis_geometry_pt": {
            panel: {
                "x0": cfg["axis"][0],
                "top": cfg["axis"][1],
                "x1": cfg["axis"][2],
                "bottom": cfg["axis"][3],
            }
            for panel, cfg in PANELS.items()
        },
        "font": {
            "family": "Helvetica",
            "panel_letter": {"size_pt": 8, "weight": "bold"},
            "title_axis_tick_base": {"size_pt": 6, "weight": "regular"},
            "tick_exponent": {"size_pt": 4, "weight": "regular"},
        },
        "y_axis": {
            "scale": "log10",
            "limits": [1e-3, 1e2],
            "major_exponents": [-3, -2, -1, 0, 1, 2],
        },
        "x_axis": {
            "scale": "zero slot plus broken log10 axis",
            "major_exponents_by_panel": {
                panel: list(cfg["exponents"]) for panel, cfg in PANELS.items()
            },
            "break_mark_centers_axis_fraction": [0.0403, 0.0589],
            "break_mark_extent_axis_fraction": 0.0267,
            "source_zero_restored_for_plot_only": True,
        },
        "stroke": {
            "axis_and_model_curve_width_pt": 0.5,
            "marker_diameter_pt": 2.834,
            "marker_edge_width_pt": 1.0,
            "major_tick_length_pt": 2.835,
            "minor_tick_length_pt": 1.62,
        },
        "colors": {
            "D-F_DeviceCMYK": [
                [0.867, 0.469, 0.043, 0],
                [0, 0.613, 1, 0],
                [0.828, 0.094, 1, 0.012],
            ],
            "G-M_DeviceCMYK": [
                [0.992, 0.438, 0.055, 0],
                [0, 0.625, 0.965, 0],
                [1, 0.020, 1, 0.004],
            ],
        },
        "model": {
            "operator_number": 7,
            "occupancy": "p7 = 1 - (1 - p1)^7",
            "Tmax": 13.61,
        },
    }
    (OUT / "corrected_pdf_style_spec.json").write_text(
        json.dumps(style, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    global REFERENCE, BACKEND, PREDICTIONS, PARAMETERS_LBD, PARAMETERS_DBD
    global OUT, TEMP, LAYER, FINAL
    parser = argparse.ArgumentParser(description="Rebuild Supplementary Figure 13 D-M")
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    parser.add_argument("--result-dir", type=Path, default=BACKEND)
    parser.add_argument("--output-pdf", type=Path)
    parser.add_argument("--temp-dir", type=Path)
    args = parser.parse_args()
    REFERENCE = args.reference.resolve()
    BACKEND = args.result_dir.resolve()
    PREDICTIONS = BACKEND / "predictions.csv"
    PARAMETERS_LBD = BACKEND / "parameters_lbd.csv"
    PARAMETERS_DBD = BACKEND / "parameters_dbd.csv"
    FINAL = args.output_pdf.resolve() if args.output_pdf else BACKEND / FINAL.name
    OUT = FINAL.parent
    TEMP = args.temp_dir.resolve() if args.temp_dir else OUT / "tmp"
    LAYER = TEMP / LAYER.name
    assemble_clean_pdf()


if __name__ == "__main__":
    main()
