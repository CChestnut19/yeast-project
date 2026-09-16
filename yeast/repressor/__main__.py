"""Run Supplementary Note 10 with explicit, portable input and output paths."""
import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'run', 'validate'))
    parser.add_argument('--data', type=Path, help='Experimental CSV; defaults to the supplied Note 10 data')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'Output/repressor')
    parser.add_argument('--no-plot', action='store_true', help='Write and validate numbers without loading plot dependencies')
    args = parser.parse_args(argv)
    from .pipeline import read_data, calculate_predictions, summarize, run, validate, DEFAULT_DATA
    from yeast.reporting import validation_data_path, write_json
    try:
        data = validation_data_path(args.output_dir, args.data, DEFAULT_DATA) if args.command == 'validate' else args.data or DEFAULT_DATA
        if args.command == 'check':
            rows = calculate_predictions(read_data(data))
            summarize(rows)
            result = {'status': 'PASS', 'observations': len(rows), 'outputs_written': False}
        elif args.command == 'run':
            result = run(data, args.output_dir, plot=not args.no_plot)
        else:
            result = validate(data, args.output_dir)
        print(json.dumps(result))
    except (OSError, ValueError, KeyError, RuntimeError, ImportError) as error:
        if args.command != 'check' and args.output_dir.is_dir():
            write_json(args.output_dir / 'validation.json', {'status': 'FAIL', 'error': str(error)})
        hint = 'Install yeast/requirements-plotting.txt for drawing dependencies.\n' if isinstance(error, ImportError) else ''
        parser.exit(2, f'Repressor {args.command} failed: {error}\n{hint}')


if __name__ == '__main__':
    main()
