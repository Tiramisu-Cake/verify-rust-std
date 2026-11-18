# Coordinator handoff — scope B CHANGES_REQUIRED

Review target: package `ac956bdf4db98a95e2da988ccd2c527582d3d32f`,
control `b678fb6cdd5edf69a4e952167422f36a45a3d6cb` /
tree `beb2346615ffbb7027b2f1ea8ea33a149952aa0b` /
parent `9e14e033f9ee31522b571c127609dcdff76d230b`.
26 package files and exact three-patch replays MATCH; independently 29/29
targeted tests PASS. Additional probes reproduce two blocking findings.

Return to original **owner11**:

1. **B-01 / P1:** successful setup plus missing main diagnostics produces false
   artifact `diagnostic_retention.complete=true`. Aggregate expected group
   coverage and missing/interrupted receipts, with explicit reasons. Regress the
   exact-group fallback and both-diagnostic-receipts removal boundaries.
2. **B-02 / P2:** `N -` / `N +` suggestion lines terminate the block as complete;
   39/165 fixture bytes disappear with zero dropped bytes in both streams and
   packing. Preserve context/coordinates or report explicit incompleteness;
   regress split/ANSI input and compact evidence.

Repairs are **NOT_APPLIED**. Publish a new immutable candidate/package, preserve
this target, old packages and this review, and return the exact delta with pins,
hashes and targeted regressions to the **same reviewer14**. Keep all proof,
selection, exit, shutdown, source/tool and numeric cap invariants. Do not change
an old verdict or historical evidence/ledger. REVIEW.md/json and
REPRODUCTIONS.json contain the reproduction details; `reproduce.py` runs only
bounded local fixtures and expects these failures on the frozen candidate.

Source13's combined task `43a137ced6c25a9fe2b34f3df6048474d0415516` does not
delay this handoff. Scope A `fc8eeb66342d588a513e22c1e2bf8552007fb690` remains
outside this review and was not rerun. The current runner is not approved;
later combined review must bind runner bytes to a repaired, approved immutable
runner before inheriting that approval. This handoff grants no runtime or CI
authorization.

Production retention **NOT_RUN**; historical compilation cause **UNKNOWN**;
proof credit **NONE**. No compiler/full runner/CI/push/PR/cancel/ledger/
reservation/budget or author implementation edits. Local review files only.
