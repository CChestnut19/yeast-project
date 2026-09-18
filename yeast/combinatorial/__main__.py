"""Run numerical analysis for the combined activator/repressor model."""
import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'run', 'validate'))
    parser.add_argument('--data', type=Path, help='CSV of experimental cell means and sample SDs')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'Output/combinatorial')
    args = parser.parse_args(argv)
    from .data import read_data, DEFAULT_DATA
    from .pipeline import summarize, run, validate
    from yeast.reporting import validation_data_path, write_json
    try:
        data = validation_data_path(args.output_dir, args.data, DEFAULT_DATA) if args.command == 'validate' else args.data or DEFAULT_DATA
        if args.command == 'check':
            rows = read_data(data)
            summarize(rows)
            result = {'status': 'PASS', 'observations': len(rows), 'panels': 12, 'outputs_written': False}
        elif args.command == 'run':
            result = run(data, args.output_dir)
        else:
            result = validate(data, args.output_dir)
        print(json.dumps(result))
    except (OSError, ValueError, KeyError, RuntimeError, ImportError) as error:
        if args.command != 'check' and args.output_dir.is_dir():
            write_json(args.output_dir / 'validation.json', {'status': 'FAIL', 'error': str(error)})
        parser.exit(2, f'Combinatorial {args.command} failed: {error}\n')


if __name__ == '__main__':
    main()
