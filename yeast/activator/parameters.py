"""Read manuscript table parameters and retain the supplied LexAec87 override."""
from __future__ import annotations
import csv
import math
from pathlib import Path
import re
from .panels import Panel
from .settings import LEXAEC87_KA_OVERRIDE

def parse_scientific(text: str) -> float:
    text = text.strip().replace("−", "-").replace("–", "-")
    text = text.replace(" ", "")
    if "×10" in text:
        mantissa, exponent = text.split("×10", 1)
        return float(mantissa) * (10.0 ** int(exponent))
    return float(text)


def normalized_operator(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def read_manuscript_parameters(table_tsv: Path) -> tuple[dict[str, dict], dict[str, dict]]:
    cells: dict[tuple[int, int, int], str] = {}
    with table_tsv.open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = (int(row["table_index"]), int(row["row_index"]), int(row["column_index"]))
            if key in cells:
                raise ValueError(f"Duplicate manuscript table cell: {key}")
            cells[key] = row["text"]

    dbd_by_operator: dict[str, dict] = {}
    current_dbd = ""
    for r in range(1, 18):
        dbd = cells.get((1, r, 0), "").strip()
        if dbd:
            current_dbd = dbd
        operator = cells.get((1, r, 1), "").strip()
        ka_text = cells.get((1, r, 3), "").strip()
        t0_text = cells.get((1, r, 4), "").strip()
        if operator and ka_text:
            if normalized_operator(operator) in dbd_by_operator:
                raise ValueError(f"Duplicate manuscript operator: {operator}")
            dbd_by_operator[normalized_operator(operator)] = {
                "dbd_table_name": current_dbd,
                "operator": operator,
                "KA": parse_scientific(ka_text),
                "T0_variant": parse_scientific(t0_text) if t0_text else None,
                "source_locator": f"Supplementary information.docx; Supplementary Table 1; row {r + 1}",
            }

    lbd_by_name: dict[str, dict] = {}
    for r in range(1, 20):
        lbd = cells.get((2, r, 0), "").strip()
        if not lbd:
            continue
        if lbd in lbd_by_name:
            raise ValueError(f"Duplicate manuscript LBD: {lbd}")
        lbd_by_name[lbd] = {
            "LBD": lbd,
            "inducer_table": cells.get((2, r, 1), "").strip(),
            "Kd0": parse_scientific(cells[(2, r, 2)]),
            "Kb": parse_scientific(cells[(2, r, 3)]),
            "Kd1": parse_scientific(cells[(2, r, 4)]),
            "source_locator": f"Supplementary information.docx; Supplementary Table 2; row {r + 1}",
        }
    for row in dbd_by_operator.values():
        if not math.isfinite(row["KA"]) or row["KA"] <= 0:
            raise ValueError("Manuscript KA must be finite and positive")
        if row["T0_variant"] is not None and (not math.isfinite(row["T0_variant"]) or not 0 <= row["T0_variant"] < 35.0):
            raise ValueError("Manuscript T0 must be finite and below both analysis ceilings")
    for row in lbd_by_name.values():
        if any(not math.isfinite(row[key]) or row[key] <= 0 for key in ("Kd0", "Kb", "Kd1")):
            raise ValueError("Manuscript LBD parameters must be finite and positive")
    return dbd_by_operator, lbd_by_name


def dbd_parameters_for_panel(panel: Panel, dbd_params: dict[str, dict]) -> dict:
    """Return the panel's DBD parameters with declared panel-level overrides.

    LexAec87 retains the lexOrec.sym T0,variant from Supplementary Table 1,
    while KA is fixed to 0.74 for every Supplementary Note 9 LexAec87 sensor
    as recorded in the supplied archive; retained as a reproducibility default.
    """
    selected = dict(dbd_params[normalized_operator(panel.operator)])
    selected["KA_source_locator"] = selected["source_locator"]
    if panel.dbd.casefold() == "lexaec87":
        selected["KA"] = LEXAEC87_KA_OVERRIDE
        selected["KA_source_locator"] = (
            "Supplied 05_scripts archive parameter default: all Supplementary Note 9 "
            "LexAec87 sensors use KA=0.74"
        )
    return selected
