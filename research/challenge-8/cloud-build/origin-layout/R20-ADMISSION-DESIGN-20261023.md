# R20 admission and source closure

R20 registers `MERGE-UNWIND-ACCEPTANCE-R20-2026-10-23` against the fresh
3600-second account in `CURRENT-RECOVERY-R20-BUDGET-20261023.json`. The prepared
ledger remains `PREPARED_NOT_REGISTERED`; registration requires the assigned
client's exact phase gate and independent review. Its immutable session bounds
are T0 `2026-10-22T20:08:00Z`, main deadline `22:08:00Z`, and absolute deadline
`22:38:00Z`. Builds require a 510–1200 second timeout, one identical full
published infra/proof SHA, merge lane, and a 60-second queue allowance. The
existing execute-budget validator reserves 420 seconds for publication, limits
execution to 780 seconds, and preserves the 140-second nested compile reserve.
There is no R19 carry: R19's closed 3600 seconds remain retired.

Preparation note: the reuse-profile `smallsort-session prepare` attempt refused
the pinned profile because its `independent_credit: 0` value is numeric rather
than boolean `false`. A generated DRAFT profile bundle was then used only to
mechanically prepare the ledger. R20 keeps the original pinned R19
`GLUE-PROFILE.json` bytes and does not adopt the draft profile or its recipe;
the recipe below is the committed R20 source delta with the R19 ledger
preserved.

The selected profile remains the published R19 `GLUE-PROFILE.json`, SHA-256
`1404842fc70c2fbc4d422d63ff3035edeacd22ac64cdf02382b2300e94fd57bb`. Admission
pins the existing cumulative patch SHA-256
`8b2cfaa4cf28e12bd4997cf0de131bb5e5cb424d393a2b4c315c829818b4c3a4`, exact
published provider module SHA-256
`2bed7d32a35ac10121820ffdf8a6dbcb645f5eefb838c9bb0d89915086a34ef3`, its
`prove.py` pin, and starting tool commit
`39f6b0cacd00575c8ca2d39e9f15632723bf1227`. It requires the selected worktree
entries and final encoded source payload to match the committed source and
existing transport limit.

R20 compares historical closure from baseline
`e278869253e5a1e553d0ac0c1bc7adb5221b681e` to the selected R20 source. That
baseline already contains the R19 closed ledger, so the closure check preserves
that exact closed record instead of comparing against R19's older open account.
The exact recipe delta from this closed baseline adds the R20 ledger, metadata
admission test, and checked-content helper. It omits five dormant synthetic
test inputs: `r9-guard-return-controls-service-test.py` (31,882 bytes),
`r5-emitter-service-test.py` (8,201), `r9-phase-service-test.py` (7,345),
`r10-invariant-service-test.py` (3,552), `r10-phase-service-test.py`
(7,035), and `r9-marker-service-test.py` (6,354). This changes recipe
inclusion only; all files remain in the repository
and historical input records. The active `merge.sh` preflight retains its R8
wiring, R8 freshness, and tool-evidence service tests. No runtime controls or
source-preflight fixtures are deleted. The source preflight recomputes the
selected commit's encoded payload against the unchanged 571,567-byte cap
before reservation.

The client checks account identity/status, owner/lane, exact ledger path,
budget arithmetic and terminal accounting, exact start/main/absolute windows,
profile/tool/source pins, historical closure, recipe delta, publication gate,
provider pins, worktree closure, timeout and queue reserve, final deadline,
and upload-guard routing. It does not register or reserve a phase while the
ledger remains prepared, and no Cloud action is performed by these checks.
