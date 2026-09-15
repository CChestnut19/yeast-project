"""Command-line entry point for portable activator source reconstruction."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zipfile


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "dump", "recalculate", "validate", "run"))
    parser.add_argument("--source-xlsx", type=Path, help="Original Source data.xlsx, with cached formula values")
    parser.add_argument("--parameter-table", type=Path, help="Supplementary_information_tables.tsv")
    parser.add_argument("--source-dump", type=Path, help="Optional frozen JSON snapshot to cross-check against the workbook")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "Output" / "activator")
    parser.add_argument("--previous-root", type=Path, help="Optional previous audit package, used only by validation")
    args = parser.parse_args(argv)
    if args.command != "validate" and args.source_xlsx is None:
        parser.error("--source-xlsx is required for this command")
    if args.command in {"check", "recalculate", "run"} and args.parameter_table is None:
        parser.error("--parameter-table is required for this command")
    try:
        if args.command == "dump":
            from .source import read_sheet, write_json
            workbook, _ = read_sheet(args.source_xlsx)
            path = args.output_dir / "02_numeric_reconstruction" / "source_sheet_dump.json"
            qa = args.output_dir / "04_qa" / "02_log10_R2_QA_summary.json"
            if qa.exists():
                write_json(qa, {"status": "NOT_VALIDATED", "reason": "Source snapshot updated; rerun reconstruction and validation"})
            write_json(path, workbook)
            print(path)
        elif args.command == "check":
            from .source import load_source_package
            from .parameters import read_manuscript_parameters, dbd_parameters_for_panel
            from .measurements import extract_measurements
            from .panels import PANELS
            workbook, green = load_source_package(args.source_xlsx, args.source_dump)
            dbds, lbds = read_manuscript_parameters(args.parameter_table)
            for panel in PANELS:
                if dbd_parameters_for_panel(panel, dbds)["T0_variant"] is None or panel.lbd not in lbds:
                    raise ValueError(f"Missing parameters for {panel.panel_id}")
            rows = extract_measurements(workbook["values"], green)
            present = {r["panel_id"] for r in rows if r["plot_type"] == "dose_response"}
            if present != {p.panel_id for p in PANELS}:
                raise ValueError("Not all 27 panels have source measurements")
            print(json.dumps({"status": "PASS", "panels": len(present), "raw_measurements": len(rows),
                              "outputs_written": False}))
        else:
            if args.command in {"recalculate", "run"}:
                from .recalculate import run_recalculation
                print(json.dumps(run_recalculation(args.source_xlsx, args.parameter_table, args.output_dir, args.source_dump), ensure_ascii=False))
            if args.command in {"validate", "run"}:
                from .validate import validate
                print(json.dumps(validate(args.output_dir, args.previous_root), ensure_ascii=False))
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        if args.command in {"validate", "run"} and args.output_dir.is_dir():
            from .source import write_json
            write_json(args.output_dir / "04_qa" / "02_log10_R2_QA_summary.json", {"status": "FAIL", "error": str(error)})
        parser.exit(2, f"Activator {args.command} failed: {error}\nSee yeast/activator/README.md for input requirements.\n")


if __name__ == "__main__":
    main()
