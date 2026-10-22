# R21 admission on the reviewed tool578/profile9496 HANDOFF

R21 registers `MERGE-CALLER-ACCEPTANCE-R21-2026-10-23` against the fresh
3600-second account `CURRENT-RECOVERY-R21-BUDGET-20261023.json`. The ledger is
prepared as `PREPARED_NOT_REGISTERED`; activation is a status-only change after
independent review. Session bounds: T0 `2026-10-22T22:25:31Z` (actual start,
including preparation), main deadline `2026-10-23T00:25:31Z`, absolute deadline
`2026-10-23T00:55:31Z`. No R20 carry: R20's 763 seconds stay retired.

Builds keep the R20 envelope: one identical full published infra/proof SHA,
merge lane, `pinned-objects`, timeout 510–1200 plus 60-second queue allowance
inside the absolute deadline, and the unchanged R17 execute-budget validator
(reserve 420, execute ≤780, soft ≤765, nested compile reserve 140 in
`merge.sh`). Submit/request are refused at or after the main deadline.

Baseline (probe) is the R20 closeout `e819a3155c76499be35879697e4fe607528de3e3`,
whose proof inputs equal the reviewed HANDOFF candidate
`41d449f3243a021efdf8ab1581f8bc8bd2fb2e6a` except for the closed R20 ledger.
The selected profile must be byte-identical to the baseline
`GLUE-PROFILE.json` (SHA-256 `9496331…0301`, `effective_tool_commit`
`578120769161e217e53bd569bafdccbd4b2e020e`), with cumulative patch
`R20_METADATA_PATCH_SHA256` and the exact R20 metadata provider module and
`prove.py` pin. There is no profile extension in R21.

Historical closure: all ledgers listed in the baseline recipe (including the
closed R20 ledger), the R13 mode card, R14 publication gate and the profile
must be byte-identical between baseline and selected source. The existing S8–S16
checks (R14 gate bytes, publisher AST, regular-file closure, provider pin
sources, worktree identity, unchanged 571,567-byte transport cap) are reused
verbatim from R20.

Recipe delta: adds the R21 ledger; removes
`origin-layout/r20-metadata-admission-service-test.py` from the Cloud recipe
only. That file is a local synthetic test; no Cloud runtime file
(`merge.sh`, `run.sh`, `run-merge.sh`, provider overlay pins, static preflight
list) references it. It stays in the repository and still passes locally
against the R20 recipe at the baseline commit. Measured transport without the
pruning: 572,023 bytes (over cap); with it: 570,657 bytes (margin 910) on the
prepared tree. No runtime control, preflight fixture, matrix entry, timeout or
cap changes.

Client hooks: upload-guard routing (and its R14 C13 self-check string),
spent-seconds alias in reconcile, phase authorization dispatch, execute-budget
validation and reservation routing each gain R21 exactly as R20 did. Historical
R19/R20 service tests were adjusted only for the extended guard tuple and to
read the R20 recipe from the baseline commit instead of the live worktree.

Local checks (no Cloud): r21-phase 11 tests, r20-phase 11, r19-phase 13,
r20-metadata-admission 7, r17-rawptr, r19-unwind, r17/r18-phase OK; real
`r21_validate_sources` PASS on a probe commit of this tree; `bash -n merge.sh`.
