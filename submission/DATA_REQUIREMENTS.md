# Numerical input requirements

## Included

- `yeast/repressor/data/experiment_data.csv`: 1,141 original supplied replicates for four sensors.
- `yeast/combinatorial/data/Supplementary_Note_11_plot_data.csv`: 216 original supplied means and sample SDs across 12 panels. The historical filename is retained for provenance.
- Numerical reference fixtures under `tests/fixtures/`; activator fixtures are explicitly synthetic.
- Historical notebook parameter variants recorded with their source cells; see [NOTEBOOK_MIGRATION.md](../docs/NOTEBOOK_MIGRATION.md).

Supplied Note 10/11 tables have not been independently checked against primary workbooks. Source-archive hash records describe the original archives, including files that were not retained in this algorithm-only tree.

## Missing activator inputs

- Original `Source data.xlsx`, worksheet `SI-note activator`, original layout through at least `A1:BW296`, cached formula results and source annotations.
- `Supplementary_information_tables.tsv`, with `table_index,row_index,column_index,text` columns and original parameter-table indexing.
- Optional original `source_sheet_dump.json` and prior audit files only for explicitly requested comparisons.

See [activator input details](../yeast/activator/README.md). Worksheet green fills are scientific inclusion annotations, so their parser is retained despite the removal of drawing code.

## Missing mammalian inputs

- Original six-column sensor mapping README: 25 included sensors and excluded `402.csv`.
- Experimental CSVs with numeric `LBD,inducer,RPU` columns.
- Matched `pure_log10_initial_parameter_vector.npy` and `hybrid_initial_parameter_vector.npy`.

See [exact schemas and parameter order](../mammalian/Input/README.md). Fonts, PDF layouts and drawing settings are no longer required.

## Historical algorithms and final release

Personal file paths from notebooks are replaced by function arguments. Original CSVs for those experiments remain missing. Tests on synthetic inputs or literal equations establish code behavior only.

Before release, supply missing inputs or document actual access arrangements, confirm analysis mappings and data distribution terms, then run every claimed manuscript calculation. Predicted values and synthetic fixtures cannot substitute for original observations.
