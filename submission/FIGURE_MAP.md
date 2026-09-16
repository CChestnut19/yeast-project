# Analysis and figure mapping

**Provisional:** labels below come from the supplied source archives. Authors must confirm their correspondence to the final manuscript and supplementary information. Notebook filenames are not a verified figure map.

| Source analysis | Entry point from repository root | Input | Generated result | Validation status |
| --- | --- | --- | --- | --- |
| Supplementary Note 9 activator, 27 panels | `python -m yeast.activator run --source-xlsx "path/to/Source data.xlsx" --parameter-table path/to/Supplementary_information_tables.tsv --output-dir Output/activator` | Original workbook and parameter TSV, missing | Reconstruction tables, batch-specific metrics and QA report; no standalone panel drawing command in this module | Synthetic fixtures only |
| Supplementary Note 10 repressor | `python -m yeast.repressor run --output-dir Output/repressor` | Included `yeast/repressor/data/experiment_data.csv`, 1,141 replicates | Predictions, raw/log10 metrics, 35 mm experiment-versus-prediction PDF/SVG/PNG | Supplied-table reproduction |
| Supplementary Note 11 combinatorial, A1-C4 | `python -m yeast.combinatorial run --pdf-only --output-dir Output/combinatorial` | Included means/SD CSV and layout/axis/palette resources | Predictions, panel log10 R², two-page `Supplementary_Note_11.pdf` | Supplied-table reproduction |
| Mammalian CIC, 25 sensors and corrected Figure 13 | `python mammalian/Scripts/run_pipeline.py --stage all --readme path/to/source/README.md --input-dir path/to/source/Input --output-dir Output/mammalian` | Original source package, missing | Constrained fit, 25 curves, Figure 13 D-M redrawing, experiment-versus-prediction plots and Word parameter tables | Synthetic numerical/CLI tests only |
| Ten historical notebooks | Notebook-specific cells and input paths | Missing source data and multiple model variants | Exploratory and historical analyses | Syntax/output cleanup and limited synthetic execution; final figure mapping unconfirmed |

## Statistical and model distinctions

- Note 10 uses individual replicates and reports both raw and log10 R². Its logarithmic scatter plot is labeled with **raw R²**. The repressor weight is `1-(1-p_unbound)^2`, with sensor-specific total output ceilings.
- Note 11 uses experimental means, log10 R² and SD error bars. Its weight is `p_activator*p_unbound^2`, with total ceiling `35.85`. The A2 value `-1.073005331220207` is retained.
- Activator uses batch-specific conditional means. Its original primary metric is raw-scale R², with log10 metrics reported separately. The total ceiling is `35.85`.
- Historical notebook `Imax` is an amplitude, giving total ceiling `I0+Imax`. It must not be substituted for the activator total ceiling.
- Mammalian uses total ceiling `13.61` and its own parameter mapping and constrained fitting objective.

Confirm the exact panel assignment, parameter source, data source and expected output for every manuscript claim before freezing a publication release. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md) and [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md).
