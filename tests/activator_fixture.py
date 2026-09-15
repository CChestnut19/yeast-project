"""Synthetic OOXML fixture for the archived 27-panel layout; never experimental data."""
from pathlib import Path
import csv
import math
import zipfile
from xml.sax.saxutils import escape
from yeast.activator.panels import PANELS
from yeast.activator.source import excel_col


def make_source_package(directory, starred=True):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    cells = {}
    green = set()
    targets = [.1, .2, .5, 1, 2, 5]
    doses = [0, .001, .01, .1, 1, 10, 100, 1000]

    def response(panel, tf, dose):
        ka = .74 if panel.dbd.casefold() == "lexaec87" else 2
        unit = .001 if panel.dose_unit == "nM" else 1
        a, b = .001 + .5*(.1*dose*unit)**2, 1+.1*dose*unit
        z = ka * a * (2*tf/(b+math.sqrt(b*b+8*a*tf)))**2
        return .016 + (35.85-.016)*z/(1+z)

    def left(panel, first, replicas, on_start, on_dose):
        for j, tf in enumerate(targets):
            row = first+j
            cells[row, 0] = tf
            for k in range(replicas):
                cells[row, 1+k] = response(panel, tf, 0)*(1+.01*(k-1))
                cells[row, on_start+k] = response(panel, tf, on_dose)*(1+.01*(k-1))

    def dose_matrix(panel, rows, dose_column, groups):
        for i, row in enumerate(rows):
            dose = doses[i]
            cells[row, dose_column] = dose
            for tf, start, width in groups:
                for k in range(width):
                    cells[row, start+k] = response(panel, tf, dose)*(1+.01*(k-1))
        first = rows[0], groups[0][1]
        green.add(first)
        if starred and panel.panel_id == "SN9-P1-A":
            cells[first] = f"{cells[first]}*"

    for panel in PANELS:
        start = panel.block_row-1
        groups = []
        if panel.source_kind == "DBD":
            if panel.dbd.startswith("CI94-"):
                left(panel, start+2, 6, 7, 100)
                for j, tf in enumerate(targets):
                    column = 20+6*j
                    cells[start+1, column] = tf
                    groups.append((tf, column, 6))
                dose_matrix(panel, list(range(start+2, start+10)), 19, groups)
            elif panel.dbd == "LexAbs94":
                left(panel, start+2, 6, 13, 1000)
                for j, tf in enumerate(targets):
                    column = 20+6*j
                    cells[start+2, column] = tf
                    groups.append((tf, column, 6))
                dose_matrix(panel, list(range(start+3, start+11)), 19, groups)
            else:
                left(panel, start+2, 6, 13, 1000)
                for j, tf in enumerate(targets):
                    column = 22+8*j
                    for k in range(2):
                        cells[start+2, column+k] = f"2nd ({tf})"
                        cells[start+2, column+2+k] = f"3rd ({tf*1.1})"
                    groups += [(tf, column, 2), (tf*1.1, column+2, 2)]
                dose_matrix(panel, list(range(start+3, start+11)), 19, groups)
        elif panel.source_kind == "LBD":
            left(panel, start+2, 6, 7, doses[-1])
            for j, tf in enumerate(targets):
                if panel.panel_id == "SN9-P5-D":
                    column = [14,22,28,34,40,46][j]
                    cells[start, column] = tf
                    cells[start, column+2] = tf*1.1
                    groups += [(tf, column, 2), (tf*1.1, column+2, 2)]
                else:
                    column = 14+6*j
                    cells[start, column] = tf
                    groups.append((tf, column, 6))
            dose_matrix(panel, list(range(start+1, start+9)), 13, groups)
        else:
            mutant = panel.source_kind == "BJAMUT_SPECIAL"
            left(panel, 275 if mutant else 287, 9, 10, 1000 if mutant else 10)
            columns = [21,30,39,48,57,66] if mutant else [21,30,42,48,57,66]
            widths = [9]*6 if mutant else [9,12,6,9,9,9]
            for tf, column, width in zip(targets, columns, widths):
                cells[272 if mutant else 286, column] = tf
                cells[273 if mutant else 287, column] = "Day1" if mutant else "Run1"
                groups.append((tf, column, width))
            dose_matrix(panel, list(range(274,282) if mutant else range(288,296)), 20, groups)

    source_xlsx = directory / "Source data.xlsx"
    write_workbook(source_xlsx, cells, green)
    table = directory / "Supplementary_information_tables.tsv"
    rows = []
    for i, operator in enumerate(dict.fromkeys(p.operator for p in PANELS), 1):
        for column, value in {0:"synthetic DBD",1:operator,3:"2",4:"0.016"}.items():
            rows.append(dict(table_index=1,row_index=i,column_index=column,text=value))
    for i, lbd in enumerate(dict.fromkeys(p.lbd for p in PANELS), 1):
        for column,value in {0:lbd,1:"synthetic inducer",2:"0.001",3:"0.1",4:"0.5"}.items():
            rows.append(dict(table_index=2,row_index=i,column_index=column,text=value))
    with table.open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=["table_index","row_index","column_index","text"],delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return source_xlsx, table


def write_workbook(path, cells, green=(), formula=None):
    ns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rows=[]
    for r in sorted({r for r,c in cells}):
        row=[]
        for (rr,c),value in sorted(cells.items()):
            if rr != r:
                continue
            reference=f"{excel_col(c)}{r+1}"
            style=' s="1"' if (r,c) in green else ''
            if formula and (r,c) == formula[0]:
                cache=f"<v>{value}</v>" if formula[2] else ""
                row.append(f'<c r="{reference}"{style}><f>{escape(formula[1])}</f>{cache}</c>')
            elif isinstance(value,str):
                row.append(f'<c r="{reference}" t="inlineStr"{style}><is><t>{escape(value)}</t></is></c>')
            else:
                row.append(f'<c r="{reference}"{style}><v>{value}</v></c>')
        rows.append(f'<row r="{r+1}">{"".join(row)}</row>')
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("xl/workbook.xml",f'<workbook xmlns="{ns}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="SI-note activator" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr("xl/_rels/workbook.xml.rels",'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>')
        archive.writestr("xl/styles.xml",f'<styleSheet xmlns="{ns}"><fills><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FFA9D18E"/></patternFill></fill></fills><cellXfs><xf fillId="0"/><xf fillId="1"/></cellXfs></styleSheet>')
        archive.writestr("xl/worksheets/sheet1.xml",f'<worksheet xmlns="{ns}"><sheetData>{"".join(rows)}</sheetData></worksheet>')
