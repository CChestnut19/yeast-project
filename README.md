# Yeast regulatory models and mammalian CIC analysis

**DRAFT — version `0.1.0-draft.1`.** This repository is being prepared for a Nature Portfolio submission. The manuscript title, authors, target journal, final figure assignments, DOI and software license remain to be confirmed. This descriptive software title is not a proposed manuscript title.

The repository provides yeast activator, repressor and combinatorial models and a separate mammalian CIC fitting workflow. The included demo recomputes the supplied Note 10 and Note 11 datasets with fixed parameters. It does not refit these models or reproduce the complete manuscript.

## Reproduction scope

| Workflow | Included material | Current scope |
| --- | --- | --- |
| Yeast repressor, source Supplementary Note 10 | 1,141 measurements from four sensors, parameters and plotting code | Numerical recomputation, validation and 35 mm scatter plot |
| Yeast combinatorial, source Supplementary Note 11 | 216 experimental means with sample SDs, 12 panels, two-page PDF layout, axes and palettes | Numerical recomputation, validation and PDF; optional PNG export |
| Yeast activator, source Supplementary Note 9 | Analysis code and synthetic fixtures | Workbook and parameter TSV missing; real-data reproduction not run |
| Mammalian CIC | Fitting/validation/plotting code and synthetic tests | Experimental CSVs, mapping, vectors and publication resources missing; real-data reproduction not run |

The supplied Note 10/11 CSVs have not been independently checked against primary workbooks or experimental records. Numerical validation establishes computational consistency, not experimental validity or model quality.

## Quick start

Use Python 3.12. From the repository root:

```text
python -m venv .venv
```

Activate using your shell:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
. .venv/bin/activate
```

Install, test and run:

```text
python -m pip install -r submission/requirements-lock.txt
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir ./Output/demo
```

The default demo generates Note 10 PDF/SVG/PNG and Note 11 PDF, numerical results, workflow logs and `demo_report.json`. It does not require Poppler. Missing-data workflows are reported as `not_run`.

```text
python tools/run_submission_demo.py --output-dir ./Output/demo-numerical --no-plot
python tools/run_submission_demo.py --output-dir ./Output/demo-png --png
```

`--png` additionally exports Note 11 PNGs and requires Poppler's `pdftoppm` on `PATH`. No GPU is required. PyTorch is optional for separate backends; inspect the test summary for skipped tests.

See [reproducibility instructions](submission/REPRODUCIBILITY.md) and [validation evidence](submission/VALIDATION.md) for tested versions, measured installation/runtime, outcomes and limits. Cross-platform commands are not evidence that every platform was tested.

Use an explicit output directory. The example `Output/` directory is ignored by Git; an external directory is also supported.

## Reference results

| Check | Reference |
| --- | --- |
| Note 10 observations / sensors | 1,141 / 4 |
| Note 10 pooled raw R² | `0.8769196761349058` |
| Note 10 pooled log10 R² | `0.8721193770575127` |
| Note 11 means / panels | 216 / 12 |
| Note 11 A2 log10 R² | `-1.073005331220207` |

Negative R² is retained. R² means `1-SSE/SST`, not squared correlation. Note 10 uses `1-(1-p_unbound)^2`; Note 11 uses `p_activator*p_unbound^2`. Their parameter precision and statistical units remain distinct.

## Repository guide

- [Repressor workflow](yeast/repressor/README.md): Note 10 code and included data.
- [Combinatorial workflow](yeast/combinatorial/README.md): Note 11 code, data and resources.
- [Activator workflow](yeast/activator/README.md): analysis requiring missing experimental inputs.
- [Mammalian workflow](mammalian/README.md): separate CIC model.
- `yeast/binding.py`, `yeast/metrics.py`, `yeast/reporting.py`: shared calculations, statistics and provenance.
- `tests/`: regression, CLI and input-validation checks, including identified synthetic fixtures.
- `tools/run_submission_demo.py`: reproducible demo and timing report.

Ten historical root notebooks remain in the development repository. Some cells contain personal input paths and alternative parameter sets. They are not the submission demo; filenames do not establish manuscript figure assignments. The optional archive excludes them and development-only documentation. Its exact contents are recorded in [package_files.json](submission/package_files.json).

## Submission documentation

- [Reproducibility](submission/REPRODUCIBILITY.md)
- [Figure mapping, pending confirmation](submission/FIGURE_MAP.md)
- [Data requirements](submission/DATA_REQUIREMENTS.md)
- [Release checklist](submission/RELEASE_CHECKLIST.md)
- [Draft Code availability](submission/CODE_AVAILABILITY.md)
- [Citation guidance](submission/CITATION_GUIDANCE.md)
- [License status: pending](submission/LICENSE_STATUS.md)
- [Validation](submission/VALIDATION.md), [environment](submission/environment.json), [metadata](submission/metadata.json)

## Optional archive

The GitHub repository is the primary entry point. If an uploadable snapshot is needed, run from the intended clean checkout:

```text
python tools/build_submission.py --output-dir ../submission-archives
```

The builder produces a DRAFT ZIP, internal `PACKAGE_MANIFEST.json` containing source revision and per-file SHA-256, and a neighboring `.zip.sha256`. It rejects dirty checkouts by default. `--allow-dirty` is for explicitly identified prevalidation snapshots.

No license has been granted and no DOI is asserted. Preparation references: [Nature Portfolio code-publication guidelines](https://www.nature.com/documents/GuidelinesCodePublication.pdf) and [Nature Communications reporting standards](https://www.nature.com/ncomms/editorial-policies/reporting-standards). The target journal is unspecified; this draft does not claim full compliance or editorial acceptance.
