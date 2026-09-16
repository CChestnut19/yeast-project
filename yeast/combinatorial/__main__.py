"""Run the combined activator/repressor analysis and Supplementary Note 11 plot."""
import argparse
import json
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'run', 'validate'))
    parser.add_argument('--data', type=Path, help='CSV of experimental cell means and sample SDs')
    parser.add_argument('--resources-dir', type=Path, default=Path(__file__).resolve().parent / 'resources')
    parser.add_argument('--layout', type=Path, help='Two-page A4 PDF; defaults to the layout in --resources-dir')
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parents[1] / 'Output/combinatorial')
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--pdf-only', action='store_true', help='Skip Poppler PNG rendering')
    parser.add_argument('--no-plot', action='store_true', help='Generate and validate numerical results only')
    args = parser.parse_args(argv)
    from .data import read_plot_data, DEFAULT_DATA
    from .pipeline import summarize, run, validate
    from yeast.reporting import validation_data_path, write_json
    try:
        if args.dpi <= 0:
            raise ValueError('--dpi must be positive')
        data = validation_data_path(args.output_dir, args.data, DEFAULT_DATA) if args.command == 'validate' else args.data or DEFAULT_DATA
        if args.command == 'check':
            rows = read_plot_data(data)
            summarize(rows)
            if not args.no_plot:
                from .plotting import load_resources, PdfReader, PAGE_WIDTH_PT, PAGE_HEIGHT_PT
                load_resources(args.resources_dir, rows)
                layout = PdfReader(args.layout or args.resources_dir / 'Supplementary_Note_11_layout.pdf')
                if len(layout.pages) != 2 or any(abs(float(p.mediabox.width)-PAGE_WIDTH_PT) > .05 or abs(float(p.mediabox.height)-PAGE_HEIGHT_PT) > .05 or p.rotation != 0 for p in layout.pages):
                    raise ValueError('Layout must contain exactly two unrotated A4 pages')
            result = {'status': 'PASS', 'observations': len(rows), 'panels': 12, 'outputs_written': False}
        elif args.command == 'run':
            result = run(data, args.output_dir, plot=not args.no_plot, resources=args.resources_dir,
                         layout=args.layout, pdf_only=args.pdf_only, dpi=args.dpi)
        else:
            result = validate(data, args.output_dir)
        print(json.dumps(result))
    except (OSError, ValueError, KeyError, RuntimeError, ImportError) as error:
        if args.command != 'check' and args.output_dir.is_dir():
            write_json(args.output_dir / 'validation.json', {'status': 'FAIL', 'error': str(error)})
        hint = 'Install yeast/requirements-plotting.txt for drawing dependencies.\n' if isinstance(error, ImportError) else ''
        parser.exit(2, f'Combinatorial {args.command} failed: {error}\n{hint}')


if __name__ == '__main__':
    main()
