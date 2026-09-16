# Required source inputs

These inputs were absent from the seven supplied Python scripts and the repository. Preserve original files and provenance. Predicted curves or another fit's outputs are not experimental observations.

## Fitting and numerical validation

- Original README with 26 mapping entries: 25 `Included` sensors and excluded `402.csv`. Columns, in order: `CSV | Sensor name | Source DBD | Canonical DBD | Canonical LBD | Fit status`.
- The 25 included CSVs, with numeric columns `LBD,inducer,RPU`. Concentrations must be nonnegative and RPU positive. Missing/nonfinite values and invariant data produce errors; entirely empty records may be ignored.
- `pure_log10_initial_parameter_vector.npy`.
- `hybrid_initial_parameter_vector.npy`.

Vector order follows the first appearance of each LBD/DBD in the mapping: `log10(Kd0)`, `log10(Kb)`, `log10(Kd1)`, non-anchor `log10(KA)`, then `T0_variant`. The original 13 LBDs and 11 DBDs give 60 free parameters. Matching vector length alone does not establish matching order: use the mapping and vectors from the same source package.

## Publication figures

- `all_25_sensor_plot_settings.csv`
- `all_25_sensor_30mm_style.json`
- `mammalian_experiment_vs_prediction_plot_settings.json`
- `Supplementary Figure 13_original.pdf`

The Figure 13 workflow preserves panels A–C and redraws D–M. The original PDF, zero-dose display conventions, style files and Helvetica fonts are required reproduction resources. See the [data checklist](../../submission/DATA_REQUIREMENTS.md).
