# Required numerical source inputs

The original experimental inputs and archived initial vectors are not included in this repository. Preserve original files and provenance. Predicted responses or another fit's outputs are not experimental observations. This algorithm-only workflow requires no plotting configuration, PDFs or fonts.

## Fitting and numerical validation

- Original README with 26 mapping entries: 25 `Included` sensors and excluded `402.csv`. Columns, in order: `CSV | Sensor name | Source DBD | Canonical DBD | Canonical LBD | Fit status`.
- The 25 included CSVs, with numeric columns `LBD,inducer,RPU`. Concentrations must be nonnegative and RPU positive. Missing/nonfinite values and invariant data produce errors; entirely empty records may be ignored.
- `pure_log10_initial_parameter_vector.npy`.
- `hybrid_initial_parameter_vector.npy`.

Vector order follows the first appearance of each LBD/DBD in the mapping: `log10(Kd0)`, `log10(Kb)`, `log10(Kd1)`, non-anchor `log10(KA)`, then `T0_variant`. The original 13 LBDs and 11 DBDs give 60 free parameters. Matching vector length alone does not establish matching order: use the mapping and vectors from the same source package.

Numerical validation uses the same original README and observed CSV files alongside the saved parameter vector, predictions, parameter tables, constraint metrics and fit summary. Archived initial vectors are required for input checking and fitting, but not for validating an existing fit.
