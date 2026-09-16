# Reproducibility guide

This guide covers the current draft repository. The included demo reconstructs the supplied Note 10/11 tables using fixed parameters. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md) for workflows awaiting original inputs.

## Environment and installation

The tested environment is CPU-only CPython 3.12.14 on 64-bit Windows 11. Use Python 3.12 and the exact versions in [requirements-lock.txt](requirements-lock.txt). No GPU is required. Environment details and measured timings are in [environment.json](environment.json) and [VALIDATION.md](VALIDATION.md). GitHub Actions additionally checks Windows and Linux; inspect the run for the chosen commit before claiming either platform passed. macOS is not locally tested.

Clone the repository and select the commit associated with the intended manuscript version, or extract a verified draft archive. Run commands from its root:

```text
python -m venv .venv
```

Activate `.venv` using `.\.venv\Scripts\Activate.ps1` in Windows PowerShell, or `. .venv/bin/activate` in a POSIX shell. Then run:

```text
python -m pip install -r submission/requirements-lock.txt
python -m pip check
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir Output/demo
```

If shell activation is unavailable, use `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on POSIX directly. Install into a new virtual environment without system packages. Installation time depends on connection speed and package caches; the measured cache condition is recorded with the timing.

## Included demo

The demo runs `yeast.repressor` and `yeast.combinatorial`, independently validates their outputs, compares the numerical metrics with archived references, and returns a nonzero exit code on a failed check. Choose a fresh output directory for each validation run.

```text
Output/demo/
  demo_report.json
  note10.log
  note11.log
  note10/
    predictions.csv
    metrics.json
    provenance.json
    validation.json
    pdf/experiment_vs_prediction_35mm.pdf
    svg/experiment_vs_prediction_35mm.svg
    png/experiment_vs_prediction_35mm_600dpi.png
  note11/
    predictions.csv
    metrics.json
    provenance.json
    validation.json
    Supplementary_Note_11.pdf
```

Expected counts are 1,141 Note 10 replicate observations and 216 Note 11 means across 12 panels. Note 10 pooled log10 R² is `0.8721193770575127`; Note 11 A2 is `-1.073005331220207`. The runner checks all recorded Note 10 log10 metrics and all Note 11 panel R² values, using relative tolerance `1e-10` and absolute tolerance `1e-12`. Module tests also check raw-scale statistics and independent equations. Negative R² values are preserved.

`demo_report.json` records status, commands, durations, metrics and missing-data workflows marked `not_run`. `PASS` applies to the supplied data and computations, not to the complete manuscript or experimental validity.

Options:

```text
python tools/run_submission_demo.py --no-plot --output-dir Output/demo-numerical
python tools/run_submission_demo.py --png --output-dir Output/demo-with-png
```

The default demo needs no Poppler. `--png` additionally creates Note 11 page and combined PNGs using `pdftoppm`, which must be installed separately and available on `PATH`. `--no-plot` omits figures. These options cannot be combined.

## Individual workflows and new inputs

- [Note 10](../yeast/repressor/README.md): `python -m yeast.repressor run --output-dir Output/repressor`.
- [Note 11](../yeast/combinatorial/README.md): `python -m yeast.combinatorial run --pdf-only --output-dir Output/combinatorial`.
- [Activator](../yeast/activator/README.md): supply the original workbook and parameter TSV before running.
- [Mammalian](../mammalian/README.md): supply the original mapping, experimental CSVs, initial vectors and plotting assets.

Module `--data` options accept the documented schemas. Their `validate` commands recompute predictions from the recorded input data. The combined submission demo deliberately targets the supplied reference datasets; it is not a general goodness-of-fit test for alternative data.

PyTorch is optional for a separate mammalian backend and is not included in this lock. Install `requirements-torch.txt` separately if needed and record that environment. The lock's tests report the optional backend as skipped when absent.

## Optional draft archive

The GitHub repository is the primary source. For a review upload, build from a clean committed checkout:

```text
python tools/build_submission.py --output-dir ../submission-archives
```

The filename is `yeast-project-0.1.0-draft.1-DRAFT-<sha7>.zip`. It includes an explicit inventory, per-file SHA-256 values and the full source revision in `PACKAGE_MANIFEST.json`. A neighboring `.zip.sha256` records the archive checksum. Verify it with `Get-FileHash -Algorithm SHA256` (PowerShell) or `sha256sum` (Linux). Existing output archives are never overwritten.

`--allow-dirty` creates an explicitly marked `-working` draft for development checks. It does not identify those working changes solely by the base commit. A verified extracted archive can also be repackaged; changes to listed files are rejected. Identical file bytes produce identical archives with the same Python/compression runtime.

Historical notebooks and their two development-only tests are excluded from this archive. The remaining tests run from the extracted root using the same command above. Generated results are intentionally excluded and can be regenerated.
