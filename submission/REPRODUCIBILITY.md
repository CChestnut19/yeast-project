# Reproducing the numerical algorithms

Scope: algorithm-only draft `0.2.1-draft.1`. See [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md) for experimental inputs not included.

## Environment

Use Python 3.12 and a fresh virtual environment. Run from the repository or extracted archive root:

```text
python -m venv .venv
```

Activate `.venv` with `.\.venv\Scripts\Activate.ps1` (PowerShell) or `. .venv/bin/activate` (POSIX). Alternatively invoke `.venv/Scripts/python.exe` or `.venv/bin/python` directly.

```text
python -m pip install -r submission/requirements-lock.txt
python -m pip check
python -m unittest discover -s tests -v
python tools/run_submission_demo.py --output-dir Output/demo
```

The [lock](requirements-lock.txt) contains numerical/data libraries only. Graphics/document libraries and Poppler are unnecessary. No GPU is required. PyTorch is optional for the mammalian backend and historical notebook Adam fitting; see [requirements-torch.txt](../requirements-torch.txt). Tested versions, installation conditions and timings are recorded in [environment.json](environment.json) and [VALIDATION.md](VALIDATION.md). GitHub Actions runs Windows/Linux checks; consult the exact commit's run for its result.

## Demo outputs

Choose a new output directory for each verification. The demo runs the existing repressor/combinatorial numerical CLIs:

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
  note11/
    predictions.csv
    metrics.json
    provenance.json
    validation.json
```

Expected counts: 1,141 Note 10 replicates and 216 Note 11 means across 12 panels. Pooled Note 10 log10 R² is `0.8721193770575127`; Note 11 A2 is `-1.073005331220207`. The runner checks all archived Note 10 log10 metrics and Note 11 panel R² with relative tolerance `1e-10` / absolute tolerance `1e-12`. It returns a nonzero status on failure. Logs report missing experimental workflows as `not_run`.

No plot-related flags are accepted. `PASS` establishes computational agreement on supplied inputs, not full manuscript or experimental validation.

## Other algorithms

[Individual yeast workflows](../yeast/README.md) and [mammalian fitting](../mammalian/README.md) document inputs and commands. The [root-notebook migration inventory](../docs/NOTEBOOK_MIGRATION.md) documents parameter estimation, optimization and other retained numerical APIs. Historical parameter sets are labeled by source cell; do not silently substitute them for the manuscript parameters.

The [current formula and fitting specification](../docs/MODEL_AND_FITTING.md) defines the canonical model and log10 R² objective. Historical raw, mixed raw/log, epsilon and shape-prior fitting configurations are superseded. Refit original observations under the current objective before reporting updated fitted parameters.

## Optional archive

From the intended clean Git commit:

```text
python tools/build_submission.py --output-dir ../submission-archives
```

The builder creates `yeast-project-0.2.1-draft.1-DRAFT-<sha7>.zip`, an internal source/file-hash manifest and a neighboring `.zip.sha256`. It uses the explicit [file inventory](package_files.json), refuses existing outputs and rejects dirty checkouts unless `--allow-dirty` marks a development snapshot. Verify SHA-256 with `Get-FileHash -Algorithm SHA256` or `sha256sum`.

Extracted archives use the same install/test/demo commands as the repository. Repackaging verifies listed file hashes first. Original notebooks, figures and generated results are absent; all retained regression tests are included.
