"""Check inputs or run the mammalian fit, numerical validation and publication scripts."""

import argparse
from pathlib import Path
import subprocess
import sys

import model_core as core

SCRIPTS = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("check", "fit", "numerical", "figures", "all"), default="check")
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
        needed = []
        if args.stage in {"check", "fit", "all"}:
            from fit_sensor_logr2_floor import load_start_vectors
            layout = core.ParameterLayout([m for m in mappings if m.included])
            load_start_vectors(args.input_dir, layout)
        if args.stage in {"check", "figures", "all"}:
            needed += [args.input_dir / name for name in (
                "all_25_sensor_plot_settings.csv", "all_25_sensor_30mm_style.json",
                "mammalian_experiment_vs_prediction_plot_settings.json", "Supplementary Figure 13_original.pdf")]
        missing = [str(path) for path in needed if not path.is_file()]
        if missing:
            raise FileNotFoundError("Missing publication inputs: " + ", ".join(missing))
    except (ValueError, FileNotFoundError) as error:
        parser.exit(2, f"Input check failed: {error}\nSee mammalian/Input/README.md for the required source package.\n")
    if args.stage == "check":
        print("Input data, mapping and archived vector shapes checked. Publication files exist; fonts and layouts require the figure stage.")
        return

    result_dir = args.output_dir.resolve() / "scipy_sensor_logR2_floor_0p5"
    input_args = ["--input-dir", str(args.input_dir.resolve()), "--readme", str(args.readme.resolve())]

    def run(script, *arguments):
        subprocess.run([sys.executable, str(SCRIPTS / script), *map(str, arguments)], check=True)

    if args.stage in {"fit", "all"}:
        run("fit_sensor_logr2_floor.py", *input_args, "--output-dir", args.output_dir.resolve(), "--max-nfev", args.max_nfev)
    if args.stage in {"fit", "numerical"}:
        run("validate_results.py", *input_args, "--result-dir", result_dir, "--numerical-only")
    if args.stage in {"figures", "all"}:
        run("validate_results.py", *input_args, "--result-dir", result_dir, "--numerical-only")
        run("plot_all_25_sensor_curves.py", *input_args, "--result-dir", result_dir)
        run("plot_supplementary_figure13_corrected.py", "--result-dir", result_dir,
            "--reference", args.input_dir.resolve() / "Supplementary Figure 13_original.pdf")
        run("plot_mammalian_experiment_vs_prediction.py", "--predictions", result_dir / "predictions.csv",
            "--settings", args.input_dir.resolve() / "mammalian_experiment_vs_prediction_plot_settings.json",
            "--output-dir", result_dir)
        run("build_mammalian_parameter_tables_docx.py", "--result-dir", result_dir, "--readme", args.readme.resolve())
        run("validate_results.py", *input_args, "--result-dir", result_dir)


if __name__ == "__main__":
    main()
