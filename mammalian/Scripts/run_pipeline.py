"""Check numerical inputs or run the mammalian fit and numerical validation."""

import argparse
from pathlib import Path
import subprocess
import sys

import model_core as core

SCRIPTS = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("check", "fit", "all"), default="check")
    parser.add_argument("--readme", type=Path, default=core.DEFAULT_README)
    parser.add_argument("--input-dir", type=Path, default=core.DEFAULT_INPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=core.DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-nfev", type=int, default=50_000)
    args = parser.parse_args()
    if args.max_nfev < 1:
        parser.error("--max-nfev must be positive")
    try:
        mappings = core.read_sensor_mapping(args.readme)
        core.load_fit_data(args.input_dir, mappings)
        from fit_sensor_logr2_floor import load_start_vectors
        layout = core.ParameterLayout([m for m in mappings if m.included])
        load_start_vectors(args.input_dir, layout)
    except (ValueError, FileNotFoundError) as error:
        parser.exit(2, f"Input check failed: {error}\nSee mammalian/Input/README.md for the required source package.\n")
    if args.stage == "check":
        print("Numerical input data, sensor mapping and archived initial vectors checked.")
        return

    result_dir = args.output_dir.resolve() / "scipy_sensor_logR2_floor_0p5"
    input_args = ["--input-dir", str(args.input_dir.resolve()), "--readme", str(args.readme.resolve())]

    def run(script, *arguments):
        subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, arguments)], check=True)

    run("fit_sensor_logr2_floor.py", *input_args, "--output-dir", args.output_dir.resolve(), "--max-nfev", args.max_nfev)
    run("validate_results.py", *input_args, "--result-dir", result_dir)


if __name__ == "__main__":
    main()
