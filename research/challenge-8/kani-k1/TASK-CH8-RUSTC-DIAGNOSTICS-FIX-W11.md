# Original W11 — localized runner completeness repairs

ISSUED by coordinator on review5db34a924329e05602bf1f8643ad0f4082653b3c,
scopeB CHANGES_REQUIRED. Current model+Fast, reuse original context; no subagents.
Correctness verification, not security work. STOP only real blocker, not volume.
No compiler/cargo/rustc/Kani/CBMC/full runner or CI. Python fixture tests allowed.

Frozen target packageac956bdf4db98a95e2da988ccd2c527582d3d32f,
controlb678fb6cdd5edf69a4e952167422f36a45a3d6cb/treebeb2346615ffbb7027b2f1ea8ea33a149952aa0b,
required parent9e14e033f9ee31522b571c127609dcdff76d230b. Old package/control/review
immutable. Reviewer14 independently ran29tests and reproduced two blockers.
Read REVIEW.md/json, REPRODUCTIONS.json, reproduce.py at exact review commit in
`kani3300/ch8-s2/runner-diagnostics-r2-review/`; no broad audit or unrelated fixes.

- **B-01 / P1:** pack_evidence.py enumerates only directories with existing
  rustc stream receipts, allowing complete setup to hide missing main diagnostics.
  Derive complete coverage from expected execution/group receipt inventory as well
  as actual stream files. Preserve NOT_RUN/interrupted/missing states and explicit
  reasons. Regress exact s2-batch3probes-u34 fallback with complete setup/main
  missing, and removal of both main stream receipts at packing boundary.
- **B-02 / P2:** numbered suggestion lines `N -` / `N +` end the error block as
  complete; 39/165 fixture bytes disappear without accounting. Preserve suggestion
  and following source/note/help context with original byte coordinates, or mark
  unretained context incomplete explicitly. Regress both streams, split/ANSI input
  and packed text/completeness. No cap increase or raw log export.

New isolated control sibling retaining required parent9e14; preserve original
worktree/candidate. Only localized runner/parser/pack/fallback/test changes and
necessary derived bindings. Source9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6 and
stock0aac unchanged; existing hard caps, native exits/shutdown,11roots/20covers/
6negative oracles and proof outcomes unchanged. Any unsupported unrelated issue
returns coordinator. Do not claim production retention or recover missing r1 error.

Run only relevant Python/static/error-path tests and exact negative regressions,
including original long-middle test and changed packing/fallback boundaries.
Write immutable sibling `kani3300/ch8-s2/runner-diagnostics-r2-r1/`: exact full
g0/control/tree/parent/source/tool/request/workflow pins, parent/full/narrow patches,
old-to-new repair map/hash manifest, VALIDATION/test results and HANDOFF for same14.
Name both findings; author repair evidence does not close reviewer findings.

W13 actively composes combined source/package batch-r2 under task43a137ced6;
do not edit its source or g0 output. Deliver exact repaired runner pins for it to
consume after review; no source publication/trigger or request for extra CI.
No CI/rerun/cancel/push/PR/ledger/reservation/budget. Item1 28/28,item2 provisional
10/14,total38/42; r1 accounting/repeat owner-only. Paths from
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/`.
Exact ownpaths commit --only, `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Final `READY <full g0 SHA> <control SHA/tree/parent> <targeted validation>`.
