# READY — first S3-1, independent14 review next

Source `513341f41ce53833a279571401c924bdddddb6c8`, tree `a818efb2157d57af0c9c604f6d0ca85873b8712c`,
parent `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a`.
Control `1dfc267b66abd83d536eb41a17052a4f3d767d2b`, tree `07d2500da97ca0a2bd6e62aede3bc5e79d15cfcd`,
parent `9e14e033f9ee31522b571c127609dcdff76d230b`.
Tool stock `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b`, unchanged.
Request SHA256 `b26b8dd8afdacc9dd09b94b2a043e6da96047826efa949ae8a34b74cb5efabc3`.
Workflow SHA256 `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709`.
Exact package g0 is the commit containing MANIFEST.sha256; full SHA is reported
in the completion response. `PINS.json` records all worktrees, roots and cfg.

Implemented all22 literal old assertion sites (six negatives plus16 supporting
positive/semantic sites), six actual full-byte u8/KeyLess PFC candidates and the
three selected literal controls. Exact serial order: checker_order_corrupt,
checker_count_corrupt, s3_swap_u8_geometry, s3_sort4_u8_separate,
s3_sort4_u8_same_alloc, s3_insert_tail_u8_rel16, s3_merge8_u8_separate,
s3_merge8_u8_same_alloc, sort13_weak. There are44 source cover sites and71 total
selected literal role/cover sites; compiled property counts and producer IDs
remain UNKNOWN. The complete source-bound maps retain all loop instances.

Sort4 has a guarded semantic post, and all selected positives execute actual
bodies with no assumed helper/PFC summary or panic stub. Same-allocation sort4
and merge8 use backing48 with uninitialized dst and initialized outside frame;
merge8 explicitly covers sort8 geometry32→0 and40→16. Insert covers relative
tail1..16, lengths2..17 and symbolic begin1..16 in backing34. Bounds are
34/34/36/8/50/36/12/50/34, derived in DOMAIN-UNWIND.json. Larger/different
allocations and arbitrary scratch init/locality, generic T/F and full consumers
remain OPEN. No unchanged heavy or reduced-alphabet root is selected.

Controller E0/pre/post snapshots are fail-closed and never rebaseline. Durable
AFTER is captured by the surviving controller only after verified shutdown,
while original worker errors/exits and absent inner AFTER remain intact. Exact
owned disappearing-process cases validate PID/start-time/ownership/errno and
retain bounded operation/traceback/epoch diagnostics. Unknown containment, input
drift, missing/unreadable post-state or uncertain output accounting globally stop.
Fresh singleton namespaces, shared caps, native selection/order, immutable
completed prefix and structured upload-only replay are checked. Late publication
marks the row UNKNOWN without mutating recorded supervision.

Actual final Validate on1dfc: **172 PASS** (136 legacy +36 S3), execution count1,
**601.497913089s**, margin **1.795517452x** at1080s, >=1.5x.
Final source preflight STATIC_PASS /40.676456463s on the real
source/tool checkouts. Eight patch replays match exact trees; depths5/7/2 retain
base objects. Tests cover success/error/timeout/partial/missing/null/wrong type/
NOT_RUN, source-stage-target mismatch, missing provider/role, aliases/cfg,
vanished PID sampling/signal/cleanup, drift, epoch/parent/path mismatch,
interruption, sealed prefix and upload-only replay. Full provenance is in
VALIDATION.json and validation-final/. No extra final rerun was made on1dfc.

Precursor6684's original root-level FINAL-VALIDATE.json remains immutable:
171 PASS /619.748906721s. A concrete late-publication serialization
inconsistency required a new sibling control1dfc and a distinguishing regression;
CONTROL-FINALIZATION-DELTA.patch binds that change. Earlier precommit failures,
including56 minimal-fixture errors and2 source/target rejection findings, remain
in PRECURSORS.json with scope limits. No earlier run is attributed to final bytes.

U-SITE-PROPOSAL.json is explicit and disabled. Current S3 and legacy zero-U
admission reject all UNREACHABLE statuses, including roles; unknown U rejects.
Four historical source-local arguments/identities are recorded without claiming
future MIR/caller-instance binding. No waiver, filtering or legacy verdict rewrite.

Native compile, Kani/CBMC proof outcome, native runner/fit and CI: **NOT_RUN**.
Qualified leaves0; proof obligations closed0; independent B1/B2 credit NONE.
Budget/ledger unchanged by W13: item2 11/17,total41/48; no reservation or reserve.
No compiler, tool install/build, CI, push, PR/issues, external message or ledger
operation was performed. Source/control commits and this package are local only.

**READY → independent14 review → separately issued GO only.**
Use REVIEW14-REQUEST.md. No native dispatch or GO request before accepted review.
