"""Source JSON/CSV and OOXML cached-value access, without a private Node runtime."""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from .settings import SOURCE_SHEET

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fieldnames=None):
    rows = list(rows)
    if fieldnames is None:
        if not rows:
            raise ValueError("An empty CSV requires explicit fieldnames")
        fieldnames = list(rows[0])
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _json_values(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(k): _json_values(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_values(v) for v in value]
    return value


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_json_values(value), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def excel_col(index0):
    if index0 < 0:
        raise ValueError("Excel column index must be non-negative")
    value, chars = index0 + 1, []
    while value:
        value, remainder = divmod(value - 1, 26)
        chars.append(chr(65 + remainder))
    return "".join(reversed(chars))


def cell_coordinates(reference):
    match = re.fullmatch(r"\$?([A-Z]+)\$?([1-9]\d*)", reference.upper())
    if match is None:
        raise ValueError(f"Invalid cell reference: {reference}")
    column = 0
    for char in match.group(1):
        column = column * 26 + ord(char) - 64
    return int(match.group(2)) - 1, column - 1


def parse_cell(value):
    if value is None or value == "" or isinstance(value, bool):
        return None, False
    text = str(value).strip()
    starred = text.endswith("*")
    if starred:
        text = text[:-1].strip()
    if text.lower().startswith("rpu="):
        text = text[4:]
    try:
        number = float(text)
        return (number if math.isfinite(number) else None), starred
    except ValueError:
        return None, starred


def clean_number(value):
    number, _ = parse_cell(value)
    if number is None:
        raise ValueError(f"Expected numeric source cell, received {value!r}")
    return number


def _sheet_part(archive, sheet_name):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    sheets = workbook.find(f"{{{NS}}}sheets")
    sheet = next((item for item in sheets if item.get("name") == sheet_name), None) if sheets is not None else None
    if sheet is None:
        raise ValueError(f"Workbook has no worksheet {sheet_name!r}")
    relations = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relation = next((item for item in relations if item.get("Id") == sheet.get(f"{{{REL}}}id")), None)
    if relation is None or relation.get("TargetMode") == "External":
        raise ValueError("Worksheet must reference an internal OOXML part")
    target = relation.get("Target", "")
    part = posixpath.normpath(target.lstrip("/") if target.startswith("/") else posixpath.join("xl", target))
    if not part.startswith("xl/"):
        raise ValueError(f"Worksheet part is outside xl/: {target}")
    return part


def _green_styles(archive):
    if "xl/styles.xml" not in archive.namelist():
        return set()
    styles = ET.fromstring(archive.read("xl/styles.xml"))
    fills = styles.find(f"{{{NS}}}fills")
    green = set()
    for index, fill in enumerate([] if fills is None else list(fills)):
        pattern = fill.find(f"{{{NS}}}patternFill")
        if pattern is None or pattern.get("patternType") != "solid":
            continue
        foreground = pattern.find(f"{{{NS}}}fgColor")
        if foreground is not None and foreground.get("rgb", "").upper().endswith("A9D18E"):
            green.add(index)
    xfs = styles.find(f"{{{NS}}}cellXfs")
    return {index for index, xf in enumerate([] if xfs is None else list(xfs)) if int(xf.get("fillId", "0")) in green}


def _rich_text(element):
    return "".join(node.text or "" for node in element.iter(f"{{{NS}}}t"))


def read_sheet(source_xlsx, sheet_name=SOURCE_SHEET):
    """Read cached values, formulas and green fills. Never recalculate formulas."""
    with zipfile.ZipFile(source_xlsx) as archive:
        sheet = ET.fromstring(archive.read(_sheet_part(archive, sheet_name)))
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            strings = [_rich_text(item) for item in ET.fromstring(archive.read("xl/sharedStrings.xml"))]
        green_styles = _green_styles(archive)
        cells, formulas, green = {}, {}, set()
        for cell in sheet.iter(f"{{{NS}}}c"):
            reference = cell.get("r")
            if reference is None:
                raise ValueError("OOXML cell has no reference")
            position = cell_coordinates(reference)
            formula = cell.find(f"{{{NS}}}f")
            cached = cell.find(f"{{{NS}}}v")
            kind = cell.get("t", "n")
            if formula is not None:
                if cached is None or cached.text is None:
                    raise ValueError(f"Formula cell {reference} has no cached value; recalculate and save the workbook first")
                formulas[position] = "=" + (formula.text or "")
            if kind == "inlineStr":
                inline = cell.find(f"{{{NS}}}is")
                value = _rich_text(inline) if inline is not None else None
            elif cached is None or cached.text is None:
                value = None
            elif kind == "s":
                value = strings[int(cached.text)]
            elif kind == "b":
                value = cached.text == "1"
            elif kind in {"str", "e"}:
                if kind == "e":
                    raise ValueError(f"Excel error at {reference}: {cached.text}")
                value = cached.text
            else:
                value = float(cached.text)
                if not math.isfinite(value):
                    raise ValueError(f"Non-finite cached value at {reference}")
            if value is not None or formula is not None:
                cells[position] = value
            if int(cell.get("s", "0")) in green_styles:
                green.add(position)
        if not cells:
            raise ValueError(f"Worksheet {sheet_name!r} contains no cached values")
        max_row = max(row for row, _ in cells)
        max_column = max(column for _, column in cells)
        values = [[cells.get((r, c)) for c in range(max_column + 1)] for r in range(max_row + 1)]
        formula_grid = [[formulas.get((r, c)) for c in range(max_column + 1)] for r in range(max_row + 1)]
    return {"sheetName": sheet_name, "address": f"A1:{excel_col(max_column)}{max_row + 1}",
            "values": values, "formulas": formula_grid, "source_workbook_sha256": sha256(source_xlsx),
            "value_source": "OOXML cached values; formulas not evaluated"}, green


def _comparable_values(payload):
    address = str(payload.get("address", "")).split("!")[-1].replace("$", "")
    if not address.startswith("A1:") and address != "A1":
        raise ValueError("Source snapshot must be anchored at A1 so cell locators remain absolute")
    return {(r, c): value for r, row in enumerate(payload["values"]) for c, value in enumerate(row)
            if value is not None and value != ""}


def load_source_package(source_xlsx, source_dump=None):
    workbook, green = read_sheet(source_xlsx)
    if source_dump is not None:
        snapshot = json.loads(Path(source_dump).read_text(encoding="utf-8-sig"))
        if snapshot.get("sheetName") != SOURCE_SHEET or _comparable_values(snapshot) != _comparable_values(workbook):
            raise ValueError("Source JSON snapshot does not match the workbook cached values")
        if snapshot.get("source_workbook_sha256", workbook["source_workbook_sha256"]) != workbook["source_workbook_sha256"]:
            raise ValueError("Source snapshot workbook hash does not match")
    if len(workbook["values"]) < 296 or len(workbook["values"][0]) < 75:
        raise ValueError("Activator source layout requires at least A1:BW296")
    return workbook, green
