# Yeast activator + repressor: Supplementary Note 11

Adapted from `Supplementary_Note_11_plot(1).zip`. The workflow retains 216 experimental means and sample standard deviations (SDs), 12 panels, the two-page PDF layout, axis coordinates and CMYK palettes.

## Environment and commands

For submission reproduction, use the pinned Python 3.12 environment in [Reproducibility](../../submission/REPRODUCIBILITY.md). The entry points require Python 3.10 or later. To install the workflow's numerical and plotting dependencies separately, run the following from the repository or extracted package root:

```bash
python -m pip install -r yeast/requirements-plotting.txt
python -m yeast.combinatorial --help
python -m yeast.combinatorial check
python -m yeast.combinatorial run --output-dir Output/combinatorial
python -m yeast.combinatorial validate --output-dir Output/combinatorial
```

The examples explicitly write results to `Output/combinatorial`; use `--output-dir` to choose another location. The default `run` command exports both PDF and PNG files. PNG export requires Poppler's `pdftoppm` command on `PATH`.

- `--pdf-only` generates the vector PDF without PNG rendering or Poppler.
- `--no-plot` generates and validates numerical results without loading plotting libraries. Only NumPy from `yeast/requirements.txt` is required for this mode.
- `--data path/to/source/Supplementary_Note_11_plot_data.csv` selects another CSV of experimental means and sample SDs.
- `--resources-dir path/to/source/resources` selects a directory containing the axis, geometry and palette JSON files and the PDF layout.
- `--layout path/to/source/layout.pdf` overrides the layout PDF. It must contain two unrotated A4 pages using the same coordinate system as the resources.
- `--dpi` sets the PNG resolution; the default is 300 and the value must be a positive integer.
- `check` verifies data, metrics and drawing resources without writing output. `check --no-plot` checks numerical inputs only.

For example, to produce numerical results and a vector PDF without Poppler:

```bash
python -m yeast.combinatorial run --pdf-only --output-dir Output/combinatorial
```

## Input rules

The CSV columns are `panel,condition,x_value_uM,series_value_uM,mean_RPU,sample_SD_RPU`.

The table must cover all panels A1-C4, and each panel suffix must agree with `condition`. Doses and SDs must be nonnegative, means must be positive, and each panel/x/series combination must have exactly one mean. Invalid or nonfinite values cause an error.

## Fixed model conventions

- Low/high activator TF inputs are 0.49 / 8.12; low/high repressor TF inputs are 0.21 / 4.56.
- `Tmax=35.85`; both repressors use `T0=0.01`, with two repressor operators.
- The output weight is `p_activator * p_unbound^2`. Note 11 retains its original parameter precision, separately from the full-precision Note 10 parameters.
- In conditions 1/2, the x axis is the activator inducer concentration. In conditions 3/4, it is the repressor inducer concentration.
- Panel log10 R² is calculated from the experimental means. SD is used for error bars, not for weighted fitting.
- The original A2 panel has log10 R² approximately **−1.073005**. This result is retained.

Numerical calculations are in `model.py`, input validation is in `data.py`, and drawing code is in `plotting.py`. The layout and coordinate resources are tied to the original figure design. Alternative data should use the original dose ranges and existing series colors; changing the plotted ranges requires corresponding resource changes.

## Outputs and validation scope

```text
Output/combinatorial/
  predictions.csv
  metrics.json
  provenance.json
  validation.json
  Supplementary_Note_11.pdf
  Supplementary_Note_11_page_1.png
  Supplementary_Note_11_page_2.png
  Supplementary_Note_11.png
```

The PDF preserves the two-page vector layout. Default PNG export produces one image per page and a vertically combined image. `--pdf-only` omits the PNG files; `--no-plot` omits all figure files.

`validate` uses the source CSV recorded in `provenance.json` by default. Pass `--data` to use an identical copy at a new location. Validation recalculates predictions and metrics from the source rather than using saved predictions as their own reference. It does not require plotting libraries, and the presence of figure files is not evidence of numerical correctness.

The supplied archive contains processed experimental means only. Their correspondence to the original workbook has not been independently verified.
