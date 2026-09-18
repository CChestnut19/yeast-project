# Algorithm release checklist

Current scope: algorithm-only draft `0.2.1-draft.1`.

## Implemented

- Shared algorithms and distinct model conventions are documented.
- Root notebooks are consolidated into numerical modules with a cell-by-cell migration inventory.
- Drawing code, PDF layouts, palettes, document generation and their dependencies are removed.
- Numerical workflows include tests, reference metrics, input checks and provenance.
- A fixed numerical environment, reproducible demo, GitHub CI and an optional hash-verified archive are provided.

Completed execution evidence is in [VALIDATION.md](VALIDATION.md). Configuration alone is not evidence that a remote run passed.

## Pending author decisions

- [ ] Confirm manuscript/software title, contributors and exact journal.
- [ ] Confirm [analysis mapping](ANALYSIS_MAP.md), including which historical algorithms support manuscript claims.
- [ ] Supply [missing experimental inputs](DATA_REQUIREMENTS.md) or verified access arrangements.
- [ ] Approve the software license and data terms.
- [ ] Complete citation and Code/Data availability statements.
- [ ] Verify every claimed numerical result against final inputs.
- [ ] Freeze an approved commit/version and deposit an immutable archive; record its actual persistent identifier if issued.

No final license, DOI or complete-manuscript validation is asserted. Rendering is outside this repository version's scope.
