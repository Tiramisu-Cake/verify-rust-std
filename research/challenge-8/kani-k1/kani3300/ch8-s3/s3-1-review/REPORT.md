# Independent14: REQUEST_CHANGES — exact S3-1 candidate

Owner23:54 explicit `/new14`; task `7afd3d52d959a246df4e968e9cc8a66f029fbedf`.
Independent source/static/service review of g0
`e8a8e5328a941af8a07b778122604b0c9bf4579b`. Two reproducible controller/evidence
blockers remain. **No APPROVE and no root GO-request.** Findings go to original13;
repair must be a new immutable candidate followed by this same14 delta review.
The reviewed source/control/tool and the original package were not edited.

| Input | Exact identity |
|---|---|
| Source | `513341f41ce53833a279571401c924bdddddb6c8` |
| Source tree / parent | `a818efb2157d57af0c9c604f6d0ca85873b8712c` / `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` |
| Control | `1dfc267b66abd83d536eb41a17052a4f3d767d2b` |
| Control tree / parent | `07d2500da97ca0a2bd6e62aede3bc5e79d15cfcd` / `9e14e033f9ee31522b571c127609dcdff76d230b` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba`, tree `9d8bc9312bf955ef126d32b819b3cd0ed105ed2b` |
| Request SHA256 | `b26b8dd8afdacc9dd09b94b2a043e6da96047826efa949ae8a34b74cb5efabc3` |
| Workflow SHA256 | `8d5fd03476d3d7666692cc7267d3fe598a0007c54ec6576de3538cef434ac709` |

## Blocking findings for original13

### R14-02 — P1: a FAILED worker bypasses recorded protected-snapshot failures

`ch8-s1-control/s3_campaign.py:186` checks request/source-before/source-after,
`binary_identity` and `snapshot_errors` only when the worker group state is
`COMPLETE`. The real worker changes the group state to `FAILED` when protected
capture fails (`runner.py:1183`, `1190`, `1204`, `1238`). Thus the state that
needs the error check bypasses it. A later successful controller Ei.post validates
against E0 but does not invalidate the earlier recorded failure. `root_outcome`
seals the row as UNKNOWN and permits the next root.

The independent regression injects either a real-writer-shaped
`source_after_error` with `std HEAD drift`, or AFTER `snapshot_errors` with an
unreadable cbmc and `binary_identity=UNKNOWN`, into a FAILED worker. Controller
E0/pre/post remain complete and equal. Both cases launch all nine roots, including
the six roots after the failed third invocation; terminal state is
`SELECTED_PARTIAL`, `stop_reason=null`, with nine seals. This is a continuation
bug, not a false proof-success claim. It violates the explicit global-stop rule
for recorded input drift/unreadable protected snapshots.

Repair: inspect all available worker protected evidence regardless of group
state. Any recorded mismatch, snapshot error, or source-after error must remain a
global stop and retain the original error/exit. Keep the permitted distinction:
an interrupted worker that never captured its inner AFTER may have an additional
controller AFTER after verified shutdown; absence due to interruption is not an
affirmative drift/unreadability observation. Do not erase evidence, rebaseline,
or restore the blanket R5 missing-AFTER rejection. Add distinguishing FAILED vs
COMPLETE drift/read-error tests and retain the interrupted-worker continuation
test. If a stopped package is replayed, its global failure must remain visible.

### R14-01 — P2: compilation and source-under-test receipts retain bd62 identities

`ch8-s1-control/runner.py:511` sets compile receipt `std_sha` from legacy
`STD_SHA=bd62e54df1b4749154790aa3db3cc7978f547f75`.
`runner.py:1091` likewise sets `source_under_test.base_std_sha` to that old
candidate, while the group/source-before correctly identify `513341…`. This
second field describes the pre-overlay source under test; it is not the separate
request `base_std_sha=99e845…` patch ancestry. Binding metadata copies the stale
source-under-test record. The S3 collector at `s3_campaign.py:386` checks compile
state/limit/selector/request but not its source/tool identities; the generic
collector only compares the two identical source-under-test copies.

The independent test calls the actual singleton writer with synthetic execution:
group state COMPLETE, group/source-before `513341…`, compile/source-under-test
`bd62…`. A full synthetic campaign then passes local and upload-only collector
replay, accepting all eighteen observed compile receipts across the two replays
with that stale SHA. Other identity guards still bind the real requested source;
this finding does not establish execution against bd62 or false formal credit.
It does establish contradictory evidence in a package requiring exact provenance.

Repair: supply explicit request-derived source/tool identities to the S3 compile
monitor and source-under-test writer. Validate them against the request in local
finalization and portable replay, including negative tests for missing, null,
wrong-type and stale identities. Preserve legacy defaults/fixtures/policy. If
historical patch-base identity is needed, give it its own unambiguous field.

`tests/review14.stdout.txt` records both reproductions; `tests/test_review14.py`
contains three checks that intentionally assert the current defective behavior.
Their PASS means **bugs reproduced**, not candidate acceptance.

## Source, domain and gate review

The frozen da891 plan, ebd77 committed intake and issued implementation/review
tasks were read. Native/raw artifacts were not acquired. All 55 package files
match their committed e8a8 bytes; all 54 manifest records match. Source/control/
stock-tool HEAD, tree, full parent and clean status match. Eight patches replay
to exact target trees using temporary Git indexes. Audited checkout chains retain
the 5/7/2 ancestry and base objects. Request/workflow bytes match the control tree.
No #4591 `969f…` tool was substituted.

The bd62→513341 production smallsort delta adds only the guarded sort4 semantic
post. The complete legacy batch differs only by the exact 22 literal assertion
normalizations: six negatives and sixteen supporting semantic/activation/frame
sites. Expressions, assumptions, covers, faulty seams and source copies remain
intact. The faithful sort13 copy uses an ordinary no-op stub of uncontracted
`s2_swap_seam`; it is a negative diagnostic, not an actual positive provider.
Request/root/role maps bind all nine selectors and all 71 selected literal sites
(44 covers and 27 assertion sites). Producer IDs and compiled counts remain
UNKNOWN until native inventory; source sites are not compiled property counts.

| Serial root | Domain/body reviewed | Unwind |
|---|---|---:|
| checker_order_corrupt | `[1,2]→[2,1]`: same counts, wrong order; intended sole literal failure | 34 |
| checker_count_corrupt | `[1;32]` with output last byte 2: sorted, wrong full count | 34 |
| s3_swap_u8_geometry | Actual swap; backing34, base0..20, a/b0..12 including equal and reversed; exact transfer and whole outside frame | 36 |
| s3_sort4_u8_separate | Actual five-comparison sort4; source/dst6, active1..5, uninitialized dst and two canaries | 8 |
| s3_sort4_u8_same_alloc | Actual sort4; backing48, independent disjoint four-ranges0..44, uninitialized dst, initialized outside and source/canary frame | 50 |
| s3_insert_tail_u8_rel16 | Actual sift/CopyOnDrop; backing34, begin1..16, tail1..16, initialized sorted prefix, length2..17, whole outside frame | 36 |
| s3_merge8_u8_separate | Actual up/down merge; source/dst10, sorted full-byte halves4/4, active1..9, uninitialized dst, source/canary frame | 12 |
| s3_merge8_u8_same_alloc | Actual merge; backing48, disjoint eight-ranges0..40, source-only shared borrow, dst retains raw provenance, outside initialized; explicit32→0 and40→16 covers | 50 |
| sort13_weak | Descending12..0, unchanged uncontracted fault seam; intended sole literal failure | 34 |

Inputs are independent full u8 values with actual pure stateless KeyLess `<`.
The specialization activation assertions remain required. The snapshot owns all
input bytes; sortedness plus per-input-value multiplicity and equal lengths
excludes novel output values. No reduced alphabet or assumed summary is used by
the six selected positives. Actual initialized-source, writable-destination,
same-allocation/range-disjointness, offset and modifies premises remain present.
The same-allocation harnesses create no encompassing typed slice over
uninitialized destination storage; merge borrows only the initialized source.
Typed output reads occur after the actual writes. Frame assertions cover every
initialized outside byte and preserve source bytes. The sort4 semantic post is
guarded to active u8/KeyLess; no generic T/F theorem is inferred.

All loop maxima in DOMAIN-UNWIND were checked against harness/helper/spec code:
48 initialization/frame, 34 swap/insert backing, 32 checker snapshot/count loops,
17 insert snapshot/count and at most16 sift steps, 10 separate-merge backing,
8 merge output/count and four actual merge iterations, four sort4 count loops.
Nested multiplicity loops need per-loop bounds, not their product. Selected
bounds conservatively exceed these maxima. Compiler-generated loop behavior and
actual unwind/proof outcomes remain NOT_RUN; this is a source derivation.

Ordinary-target, cfg/PFC, lexical and contract-stack gates execute in the exact
new S3 cfg before build. The active provider walk includes compiled unselected
consumers and sort8 registration. Registration is correctly separated from
qualification. Source tests distinguish missing providers/roles, wrong cfg/name,
alias-chain resolution and ordinary replacement of a contracted target. The
independent check-source CLI on the real source and stock-tool checkouts passed;
it performs static checks only, with no compiler/expansion run.

Normal-return bounded correctness is the declared scope. Backing48 with outside
initialized does not cover arbitrary uninitialized scratch, larger/different
allocations or locality lifting. The two sort8 geometry covers do not prove
sort8 composition, its scratch state, all thresholds, arbitrary callbacks,
Cell/non-Copy, stability, termination, unwind/abort or full S3/S4. These gaps stay
OPEN. Frozen S4 `9e013a2683afbf64de762e570a052c11917e52f7` is not used for proof credit.

## Controller, policy and finalization review

E0/pre/post capture retains source, control HEAD/tree/parent/clean state, request,
binary path/hash set and invocation/rank/epoch context. The controller captures
post only after verified shutdown, and comparisons do not redefine E0. Tests
reject changed/unavailable controller snapshots, wrong parent/epoch/path and
unknown containment. **This does not cure R14-02's skipped worker errors.**

Exact ESRCH/ENOENT handling is confined to named enumeration/sampling/pidfd
operations. Owned-process operations require previously observed exclusive
PID/start-time identity; re-observation rejects recycled or unexplained live
processes. Enumeration disappearance supplies no ownership. Exceptions retain
operation/errno/bounded traceback; diagnostic retention has an omission count.
Subreaper cleanup, ownership groups, original exits/signals and unknown output
accounting remain checked. Real small Python child tests cover success, timeout
and a detached descendant; no native tool is launched by these tests.

Fresh singleton selection/order, unique target namespaces, shared output/export/
artifact caps, no retry/resume, explicit deferred outcomes, sealed completed
prefix and structured upload-only replay were reviewed and exercised. Resource
scope is honestly sampled non-atomic PGID/observed-owned VmRSS, not a strict
cgroup/tree memory proof. Child600 includes compile180; nine slot720 plus
controller180 and cleanup240 equals6900, inside outer7500/step7560/phase8100.
Setup remains aggregate1800/job180min; host validation margin is not native fit.
R14-01 still prevents truthful complete per-stage source provenance.

The late-publication delta against6684 was separately reviewed. It marks only
the row UNKNOWN with `durable_publication_cutoff`; it leaves already published
supervision identical in lifecycle, supervision file, row and seal. The dedicated
regression passes. This correct localized delta is not the cause of the findings.

The explicit U proposal is disabled. Current S3 and legacy policies reject ALL U,
including roles and unknown/extra statuses. Four historical source-local arguments
and exact source coordinates match current files, but do not establish fresh
MIR/caller-instance binding or causal origin. No waiver or assumed promotion,
filtered inventory, historical verdict rewrite or admission change is approved.

## Validation and disposition

The recorded final Validate is exactly1dfc: 136 legacy +36 S3 = **172 PASS**,
**601.497913089s**, execution_count1, margin1080/elapsed = **1.7955174515130843**.
Its transcript/script/request/workflow hashes and monotonic elapsed arithmetic
match. The root-level171/619.748906721s result belongs to6684 and is retained only
as precursor. Prior precommit failures remain in PRECURSORS; none is relabelled.
These are original preparation receipts, not an independently witnessed CI run.

Independent14 ran the 36 S3 tests once: PASS/47.184s; the real source check-source
CLI: PASS; input/patch/ancestry/roles/transcript audit: PASS; and the three
distinguishing reproduction checks: PASS/5.833s. The full final Validate was not
rerun. Test commands and scope are in VALIDATION.json and tests/.

**REQUEST_CHANGES** applies to the complete exact candidate. Original13 should
repair both findings in a new immutable source/control/package set as needed,
retain old artifacts and this report, refresh affected pins/maps/patches/gates
and exact validation provenance, and return the bounded delta to same14.
No new compiler audit or native proof is requested by this review. Only an exact
subsequent APPROVE can precede a root GO-request; only the user coordinator may
authorize/launch/account the future item2 12/17 attempt.

Native compile/Kani/CBMC/full native runner/fit/CI remain **NOT_RUN**. Qualified
leaves0; proof obligations closed0; independent B1/B2 credit NONE. No dispatch,
push/PR/issues, ledger/reservation/budget action, subagent or model/settings
change occurred. Current high/Fast OFF instructions were preserved.
