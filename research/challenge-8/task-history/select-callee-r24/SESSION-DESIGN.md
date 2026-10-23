# R24 exact admission

Defect: the branch client admits only the closed R23 account for the separate
`o26-select-callee-r20` lane. R24 has a fresh owner-authorized window and must
not inherit R23's dates, budget, account, or session phase.

Applicability: exact owner `select-sort4`, phase
`SORT4-ACTUAL-SELECT-2026-10-24-R24`, and lane
`o26-select-callee-r20`; T0 `2026-10-23T10:48:18Z`, main deadline
`2026-10-26T10:48:18Z`, absolute deadline `2026-10-26T11:48:18Z`, budget
21600s, per-Build timeout 1200s, report reserve at least 240s, and queue
allowance 60s.

Invariant: preserve historical phase gates and ledger behavior, the existing
R21 route marker consumed by the pinned translator and runner, coordinator v4
(read-only), recipe, proof/tool/profile pins, and review state. Export the R21
route marker separately from the R24 session phase; use a fresh R24 ledger with
no carry or inherited credit. Do not alter proof behavior, runtime source, or
controls.

Controls: isolated synthetic tests cover exact owner/phase/lane/window/budget,
both deadline boundaries, timeout and reserve constraints, stale or malformed
accounts, runner marker and session-phase exports, and refusal before any
Cloud/coordinator call. Static route checks confirm the existing pinned
consumer still receives the R21 marker. Historical R21/R23 constants and
admission remain unchanged.

Preparation uses the R24 session spec against baseline `f565e3ee`; the bundle
is review-only. It does not register the phase, submit work, or grant proof
credit.
