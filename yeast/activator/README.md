# Yeast activator: Supplementary Note 9

Adapted from the supplied `05_scripts(1).zip` archive. This workflow recalculates 27 panels using parameters from the supplementary tables; it does not refit parameters. The default analysis and model conventions follow the original scripts.

## Environment and installation

For submission reproduction, use the pinned Python 3.12 environment in [Reproducibility](../../submission/REPRODUCIBILITY.md). The entry points require Python 3.10 or later. To install only the dependencies for this numerical workflow, run the following from the repository or extracted package root:

```bash
python -m pip install -r yeast/requirements.txt
python -m yeast.activator --help
```

## Required inputs

1. The original `Source data.xlsx`, containing the `SI-note activator` worksheet. Its original layout must cover at least `A1:BW296`; row and column positions map to the 27 panels in `panels.py`.
2. `Supplementary_information_tables.tsv`, extracted from the supplementary tables, with tab-separated columns `table_index,row_index,column_index,text`. Indices follow the original scripts: Table 1 contains DBD/operator/KA/T0 values, and Table 2 contains LBD/Kd0/Kb/Kd1 values.
3. Optionally, the original `source_sheet_dump.json`, passed with `--source-dump`. When supplied, the reader cross-checks the worksheet name, A1 origin, cell values and available workbook hashes.

The supplied archive contained scripts and Python caches, but none of these experimental inputs. `tests/activator_fixture.py` generates synthetic test data only; those fixtures cannot substitute for experimental observations.

The reader uses cached OOXML cell values, preserves textual asterisks and RGB `A9D18E` green fills, and does not calculate Excel formulas. Formulas without cached values and Excel error cells cause an error; calculate and save the original workbook before running this workflow. Recorded formula information retains the original OOXML content. The reader neither expands nor recalculates shared formulas.

## Commands

Run these commands from the repository or extracted package root. Replace `path/to/source` with the directory containing the original inputs. The examples explicitly write results to `Output/activator`; use `--output-dir` to choose another location.

```bash
# Check inputs without creating output files.
python -m yeast.activator check --source-xlsx "path/to/source/Source data.xlsx" --parameter-table path/to/source/Supplementary_information_tables.tsv

# Extract cached values; replaces the original 00_dump_source_sheet.mjs.
python -m yeast.activator dump --source-xlsx "path/to/source/Source data.xlsx" --output-dir Output/activator

# Recalculate and independently validate the results.
python -m yeast.activator run --source-xlsx "path/to/source/Source data.xlsx" --parameter-table path/to/source/Supplementary_information_tables.tsv --output-dir Output/activator

# Validate results that have already been generated.
python -m yeast.activator validate --output-dir Output/activator
```

`--source-xlsx` is required for `check`, `dump`, `recalculate` and `run`. `--parameter-table` is also required for `check`, `recalculate` and `run`. Add `--source-dump path/to/source/source_sheet_dump.json` to cross-check the workbook during `check`, `recalculate` or `run`.

`recalculate` performs reconstruction and writes the validation manifest, leaving the status as `NOT_VALIDATED` until independent validation succeeds. `run` executes reconstruction followed by validation. A validation failure returns exit code 2 and updates the QA status to `FAIL`.

For comparison with a previous audit, add `--previous-root path/to/source/previous_audit` to `run` or `validate`. When requested, all of the following historical files are required; missing files cause an explicit error. Without this option, validation checks the current results independently.

```text
previous_audit/
  04_quantitative_audit/03_R2_three_metrics_batch_specific.csv
  02_numeric_reconstruction/01_raw_measurements_long.csv
  02_numeric_reconstruction/source_sheet_dump.json
```

## Preserved analysis rules

- The main model combines the S32-S47 mass-balance equations with S11. `Tmax=35.85` is the total output ceiling, and `T0_variant` comes from the supplementary table.
- The `KA=0.74` override for LexAec87 comes from the original archive. Its `T0_variant` remains the table value.
- Measurements with a trailing `*` are excluded first. Values marked only by green fill remain in the main analysis; a separate sensitivity analysis excludes them.
- Each R² observation is the arithmetic mean of unstarred replicates sharing the same panel, batch/Run/Day, actual TF input and inducer concentration. Different batches are not pooled when calculating R².
- Plot summaries separately group batches with similar actual TF inputs. Each nonzero member must be within 30% of the group mean. This grouping does not change the observation unit used for R².
- The original primary metric is **raw-scale R²**. `batch_conditional_log10` separately reports **log10 R²**. Both use `1-SSE/SST`; Pearson r² is a diagnostic only.
- The original sensitivity analyses are retained: `Tmax=35`, a uniform `T0=0.035`, exclusion of green values, individual-replicate analysis and literal S83. Log10 metrics record the number of omitted nonpositive or nonfinite values.

## Outputs and validation scope

```text
Output/activator/
  02_numeric_reconstruction/  # Seven numerical tables, source snapshot, execution metadata and hash manifest
  03_results/                 # Independent log10 R² recheck for 27 panels
  04_qa/                     # QA status and optional historical source-change tables
```

Numerical CSV filenames follow the original scripts. The manifest uses portable JSON. Historical comparison fields in the QA tables remain blank when no previous package is supplied.

`validate` first verifies output-file hashes, then recalculates conditional means, predictions and R² from the saved source snapshot, raw measurements and parameter tables. This establishes computational consistency; it does not establish good model fit or the correctness of the original experimental data.

| Module | Purpose |
| --- | --- |
| `source.py` | Worksheet cached values, asterisks, green fills, CSV/JSON and hashes |
| `panels.py` / `parameters.py` / `settings.py` | Layout of 27 panels, supplementary-table parsing and original analysis defaults |
| `measurements.py` | Parsing numeric headers, ordinal positions and Run/Day batch layouts |
| `model.py` | Model equations, unit conversion, R² and Pearson diagnostics |
| `aggregation.py` | Batch-specific conditional means and separate plot summaries |
| `recalculate.py` / `validate.py` | Reconstruction, numerical exports and independent validation |
| `__main__.py` | Command-line entry point |

See [validation evidence](../../submission/VALIDATION.md) for the current test scope. All outputs are numerical tables; the original source-schema names are retained for traceability.
