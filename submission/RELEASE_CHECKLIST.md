# Manuscript code release checklist

This repository is a **DRAFT** prepared for code review. The checklist follows [Nature Portfolio code-publication guidance](https://www.nature.com/documents/GuidelinesCodePublication.pdf); the exact target journal's requirements still need confirmation.

## Implemented in this preparation

- [x] Separate yeast activator, repressor and combinatorial workflows, with an independent mammalian module.
- [x] Shared numerical functions, documented model distinctions and regression references.
- [x] English installation, input, output and figure-mapping documentation.
- [x] Exact dependency lock and machine-readable tested environment.
- [x] Runnable supplied-data demo with metric checks, timings and missing-data disclosure.
- [x] GitHub Actions configuration for Windows/Linux tests and PDF reproduction.
- [x] Optional draft archive with explicit inventory, source revision and SHA-256 checksums.

Completed run results, including skipped tests and platform limits, are recorded in [VALIDATION.md](VALIDATION.md). A configured workflow is not itself evidence of a passing remote run.

## Author inputs still required

- [ ] Confirm target journal, manuscript title, software title and contributors.
- [ ] Confirm every manuscript figure/panel and analysis in [FIGURE_MAP.md](FIGURE_MAP.md).
- [ ] Provide missing experimental inputs or verified access arrangements in [DATA_REQUIREMENTS.md](DATA_REQUIREMENTS.md).
- [ ] Confirm the license and applicable terms for data and figure resources; see [LICENSE_STATUS.md](LICENSE_STATUS.md).
- [ ] Complete software citation metadata and the manuscript Code/Data availability statements.
- [ ] Run and inspect every claimed manuscript result with the final inputs; report discrepancies without changing reference values to hide failures.

## Freeze the approved version

- [ ] Review the GitHub branch and merge the approved code into the intended publication branch.
- [ ] Verify the exact clean commit with tests, the demo and the final figure/input mapping.
- [ ] Choose a final version and tag; this draft-only builder does not promote a draft to a final release.
- [ ] Deposit that immutable version in the chosen archive and record its actual persistent identifier/DOI when issued.
- [ ] Cite the version-specific artifact and full source commit in the manuscript.
- [ ] Verify archive contents/checksums and include accurate installation/runtime instructions.

No final release, DOI, license or manuscript acceptance is implied by this preparation.
