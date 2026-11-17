S2 batch3probes — preparation only, task9856043dab21de8346b68196fa91929b96331293.
Owner GO for preparation supersedes the reset wait. No dependency on the parallel
w11 offline merge pilot. Current pane model unchanged; no subagents.

Source `97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a` is isolated from accepted
`99e8456d200fff1299ee5756279cddb23921dc65`. Control
`fc058c97335e4a064c7827b8534b3af2f7460bc3` derives from reviewed reference
`7c41333f9bfcfd7eb4e0ede7bd316443090c9025`. Stock Kani
`0aac16ef62da9e9d5645782d458593e5d78143ba` is unchanged. Full trees,
request/workflow hashes and every bound source file hash are in IDENTITIES.json.

| Probe | Actual body / summary | Expected assurance |
|---|---|---|
| merge32_real | actual bidirectional_merge + merge_up/down; sorted halves; separate uninitialized output32 with guards; no stubs | body attempt, NOT_RUN |
| sort13_assumed | actual sort13 prefix13 in backing15; exact conditional semantic swap contract | DIAGNOSTIC_ASSUMED, no formal credit |
| general32_assumed | actual small_sort_general32 with actual stack scratch48; semantic sort8/insert_tail/merge summaries | DIAGNOSTIC_ASSUMED, no formal credit |

All three assert sortedness and **full-value counts**, not just key order or one
fixed-query count. The two assumed consumers are in a separate expected inventory;
they never enter the future accepted/formal inventory. The actual swap PFC is a
same-head qualification attempt; its eventual success alone would not qualify the
other helpers or the general caller's allocation geometry.

QUALIFICATION-ASSUMPTIONS.json records each actual callee, T/F, offsets, allocation,
initialization, frame, full-value domain and qualification source. Every summary is
opt-in under `kani_smallsort_s2_assumed` plus `kani_smallsort_sorting`/kani. Source
runtime bodies, generic signatures and CFG are unchanged. Existing safety/modifies
clauses are retained. The only reused peer source is the immutable committed exact
swap facade from `24e12a1e98d9dd8de4f272f3d4a6fb489ade5894`; it establishes no proof.
No unfinished offline pilot, invariant or leaf proof is a prerequisite here.

The batch has 11 exact roots: three probes, swap PFC, constructive summary witness
and six negative controls. Witnesses construct sorted permutations for every used
span length8..16/32 and exact pair transfer. Mandatory consumer covers include useful
return, unsorted/duplicate input and nonconstant output. Negative controls exercise
merge order/count corruption, checker order/count corruption, identity swap and
copy-only final merge. Their source-derived expected IDs and exact file/line/class
anchors are explicitly unobserved; any mismatch stays UNKNOWN. Witness/control
results are NOT_RUN. There is no claim of compiler-level nonvacuity from static work.

One future workflow, one serial job, one invocation group, `--jobs=1`. Per-root stock
backend timeout600s, std compile900s; group envelope `900+11*600=7500s`. Workflow phase
step7560s, internal phase cap8100s unchanged, internal cleanup reserve10s; fallback120s,
upload360s. Literal step caps total10620s/177min; job cap10800s/180min, therefore total
maximum180 runner-min for the single future workflow. Stock tool setup/build has the
reviewed1800s overall setup clock and at most900s tool build. No1200s cell profile.
Group RSS ceiling12GiB with2GiB headroom; ≤6GiB/root is an unestablished cost target.
ENVELOPE.json contains the exact limits and output/cleanup calculations.

MEASUREMENTS.json distinguishes stock per-harness reported verification wall, compile
upper bound, group wall and sampled aggregate/driver/backend/compiler/other group RSS.
Body/model/checker/summary phase wall and exact per-root RSS are UNKNOWN where stock
has no bound export. Independent component peaks are not simultaneous; process-comm
categories are observations, not binary-instance proofs. Group metrics cannot meet R8.
Original exit/signal/exception, after-child binary snapshots, native metadata, partial
exports and every remaining requested row are retained. Missing RESULTS, partial,
missing, timeout and explicit NOT_RUN never become PASS. The runner records evidence;
offline expected-oracle matching and formal admission remain separate.

The runner/decoder/capture/snapshot implementation is reused from the reviewed S1
control. Its import directory and some envelope schema names remain `ch8-s1-control`
for compatibility. The new workflow invokes only the new S2 request and exact group;
legacy S1 inventories/collectors are not an S2 admission path. The retained service
controls plus new S2 controls passed43 synthetic tests. No local cargo/rustc/Kani/
CBMC/rustfmt/full runner experiment occurred. See VALIDATION.json for static checks.

READY means ready for independent W14 review of these committed pins. No push, CI,
rerun, cancel, reservation, publication or ledger change. Item2 remains9/14; a later
separately approved S2 dispatch would be charge10/14. W14 APPROVE is required before
coordinator's separate dispatch GO, and neither is supplied by this package.
