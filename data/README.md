# Source workbook

[Source data.xlsx](Source%20data.xlsx) is the author-supplied `Source data(5).xlsx`, updated on 2026-10-16. The repository copy is byte-for-byte identical to the supplied file. It contains 21 worksheets covering main figures, supplementary figures and supplementary-note observations.

SHA-256: `fcbeb334cd553d674ce425dfc69f6dd3778864385117a1f9bee71ea561335e7c`.

[source_data_manifest.json](source_data_manifest.json) records the original filename, file size, worksheet dimensions and cached Excel error cells. The workbook is preserved with its original values, formulas, cached results, annotations and formatting. Formula errors are recorded rather than replaced or recalculated.

## Version details

Comparing cached cell values and formulas with the preceding repository `Source data(4).xlsx`, only `Figure 5` differs. Fig. 5E (`A2:D1143`) now uses normalized sensor names, six-decimal experimental values and predictions matching the current Note 10 calculation. All 1,141 observation/prediction pairs match the archived CSV plus the current model, allowing for worksheet row order. The previous 66 negative predictions are absent. The other 20 worksheets retain their cached values and formulas.

The following changes from the earlier `Source data(3).xlsx` are retained:

- `Supplementary figure 2!J121:O121` now differs from `J122:O122`; the labels remain `spb13` and `spb17`.
- `SI-note-hybrid!N36` and `V36` now contain `1000` nM. This records the supplied version and is not an independent confirmation of the experimental concentration.
- The Fig. 6 table uses `.csv` source labels, and the worksheet ends at row 1019. This does not by itself verify the provenance of every removed or replaced observation.

## Use with the numerical workflows

Run from the repository or extracted submission archive root:

```text
python -m yeast.activator dump --source-xlsx "data/Source data.xlsx" --output-dir Output/activator_source
```

The dump reads cached values from `SI-note activator`; it does not fit parameters or validate sample identity. Activator reconstruction additionally requires the original `Supplementary_information_tables.tsv`. The mammalian fitter additionally requires its sensor mapping, numerical CSVs and matched initial parameter vectors. See [input requirements](../submission/DATA_REQUIREMENTS.md).

Existing Note 10/11 CSVs remain the inputs to their numerical CLIs. Adding this workbook does not replace those tables or regenerate predictions. Full experimental reproduction remains subject to the documented remaining inputs and source checks.
