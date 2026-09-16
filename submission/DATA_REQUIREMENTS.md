# Data and resource requirements

## Included and runnable

| Workflow | Repository input | Scope |
| --- | --- | --- |
| Note 10 | `yeast/repressor/data/experiment_data.csv` | 1,141 replicate measurements from four sensors |
| Note 11 | `yeast/combinatorial/data/Supplementary_Note_11_plot_data.csv` | 216 experimental means and sample SDs, 12 panels |
| Note 11 figure | `yeast/combinatorial/resources/` | Two-page layout PDF, axis geometry and palettes |

These are tables/resources from the supplied archives. Their correspondence to primary experimental workbooks has not been independently verified. Original-file hashes are recorded in `yeast/REPRESSOR_SOURCE_ARCHIVES.json` and `yeast/activator/SOURCE_ARCHIVE.json`.

## Missing activator inputs

- Original `Source data.xlsx`, worksheet `SI-note activator`, with the original layout covering at least `A1:BW296`, cached formula results, textual asterisks and green cell fills.
- `Supplementary_information_tables.tsv`, columns `table_index,row_index,column_index,text`, preserving the original table indexing and parameter values.
- Optional original `source_sheet_dump.json` for source consistency checks.
- Optional earlier audit files only when `--previous-root` is requested.

Full schemas and the analysis rules are in [the activator guide](../yeast/activator/README.md). `tests/activator_fixture.py` creates synthetic test data and cannot replace these experimental inputs.

## Missing mammalian inputs

- The original six-column README mapping for 25 included sensors and excluded `402.csv`.
- Experimental CSVs with `LBD,inducer,RPU` columns.
- `pure_log10_initial_parameter_vector.npy` and `hybrid_initial_parameter_vector.npy`, matched to the mapping's order.
- Plot settings/style files and `Supplementary Figure 13_original.pdf`.
- External Helvetica regular and bold fonts for the publication plotting workflow.

See [the exact input list and vector order](../mammalian/Input/README.md). The fixed full-validation count of 953 observations is a source-workflow expectation, not a count verified from included data.

## Historical notebooks

Ten notebooks remain in the development repository. Some retain personal input paths, distinct experiments and alternative parameter sets. Their source data and final manuscript mapping are not supplied. They are excluded from the optional draft archive; cleaned outputs and passing syntax checks do not establish reproduction of their original figures.

## Before manuscript release

Supply missing inputs or document their actual access arrangements, confirm source-to-figure mapping, record dataset versions/checksums and confirm the applicable distribution terms. Re-run all claimed analyses with those inputs. Do not substitute synthetic fixtures, predictions or reconstructed fit outputs for missing experimental measurements.
