# Analysis-to-code mapping

Labels originate from the supplied material and need author confirmation against the final manuscript. Only numerical algorithms and outputs are retained.

| Analysis | Location / entry point | Numerical result | Input status |
| --- | --- | --- | --- |
| Note 9 activator | `yeast/activator/`, `python -m yeast.activator run` with workbook and parameter paths | Conditional means, model predictions, R² and QA tables | Original workbook/TSV missing |
| Note 10 repressor | `python -m yeast.repressor run --output-dir Output/repressor` | 1,141 predictions and per-sensor/pooled raw/log10 statistics | Supplied CSV included |
| Note 11 combined model | `python -m yeast.combinatorial run --output-dir Output/combinatorial` | 216 predictions and 12 log10 metric sets | Supplied means/SD CSV included |
| Historical notebook algorithms | [Migration inventory](../docs/NOTEBOOK_MIGRATION.md) | Shared response/fold-change/Pareto calculations and distinct fitting/analysis algorithms | Parameter variants retained; original experimental CSVs missing |
| Mammalian CIC | `mammalian/Scripts/run_pipeline.py` | Fit parameters, observation predictions, numerical validation and optional shape-analysis API | Original CSV/mapping/vector package missing |

Note 10 individual-replicate statistics and Note 11 mean-based statistics remain distinct. Activator primary R² uses within-batch conditional means. Historical `Imax` is amplitude, whereas manuscript `Tmax` is a total ceiling. Mammalian uses its own ceiling `13.61` and parameter mapping.

Drawing is outside this version's scope. Figure-generation code/resources are available in Git history at `bfd2de5` if needed separately; they are not required inputs or outputs for these algorithms.

All CIC fitting entry points maximize equal-dataset log10 R². Current equations, parameter-name conversions and corrections to historical notebook formulas are specified in [MODEL_AND_FITTING.md](../docs/MODEL_AND_FITTING.md). Fixed-parameter reconstruction metrics are diagnostics, not fit objectives.
