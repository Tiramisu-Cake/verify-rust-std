# ENSURES G2 — authorized exact scaling packet

Historical preparation packet; G2 completed successfully. See observed outcome below.

Coordinator GO after G1 `c0fbf091c42025e6eb5144bf2ca839f43fbe63e2` authorizes preparing,
committing, publishing and self-dispatching exactly seven fixed-tail insert_tail ensures PFCs
on backing8 (tails1..7), plus a real insertion_sort_shift_left u64 N8 consumer with
stub_verified(insert_tail). Maximum8 rows, ten minutes per row. Owner k1-network was explicitly
declared free; k1-merge remains outside this packet. Own task cap is now $4.00, project cap
remains $118.96. No further PRE-BUILD GO is required for this exact packet.

Worktree `/root/verify-rust-std-kani-ensures`, branch `experiment/kani-k1-ensures-20261105`.
Library commit `65c2e72b90eac24e335f1a1f3a21d1db722e177b`; no runtime/model/contract changes.
Tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`, Kani pin
`cd355b0bccd32300713bc2ce4f765dafa1510607`, same as G1.
Request `ensures-g2-20261105`, owner `k1-network`, SHA-256
`a78d65680499ede6d7e510b29e2854c9cba316e6676c6da494bcadd104133a2f`.
Diagnostic / standard4 / controls=true / jobs1 / ten-minute harness timeout; flags, including
--no-assert-contracts and disabled uninit/value-validity checks, remain unchanged.

## Eight rows and matched domains

Every root is under `slice::sort::shared::smallsort::verify::realcontracts::`, unwind16.

| Row | Expectation | Concrete domain |
| --- | --- | --- |
| insert_tail_ensures_u64_tail1_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=1 |
| insert_tail_ensures_u64_tail2_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=2 |
| insert_tail_ensures_u64_tail3_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=3 |
| insert_tail_ensures_u64_tail4_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=4 |
| insert_tail_ensures_u64_tail5_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=5 |
| insert_tail_ensures_u64_tail6_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=6 |
| insert_tail_ensures_u64_tail7_backing8 | SUCCESS | u64 / InsertTailU64Less / backing8 / tail=7 |
| insertion_ensures_u64_n8_stubbed | SUCCESS | same T/F and backing8, actual helper calls at tails1..7 |

The seven PFC roots each call exercise_insert_tail_ensures_backing8 with exactly one compile-time
tail constant. Each starts with arbitrary full [u64;8] and arbitrary full u64 probe, copies the
original backing, then invokes the real insert_tail body once. There is no sorted-prefix
assumption and no verified stub in any of these seven PFCs. The unchanged conditional order
ensures and unconditional canonical full-value count ensures are checked, with independent
harness-side order/count assertions and scalar suffix-frame checks. The specialization-selected
model is asserted explicitly. Covers request sorted premise, movement/early return, present
probe and return (five); tails2..7 also request unsorted premise (six). The singleton prefix at
tail1 cannot be unsorted, so that root does not request an impossible cover.

Let D_i contain arbitrary initialized u64 backing8, F=InsertTailU64Less with an arbitrary immutable
full-value probe, begin=base and tail=base+i. The PFC union is D_1 union ... union D_7.
The real consumer starts insertion_sort_shift_left at offset1 and makes exactly these seven
helper calls on its backing8 with the same F/probe. Thus the union covers every consumer
call domain, including all full-value intermediate states; PFCs do not require a sorted prefix.
Each helper modifies only begin..=tail, so suffix and probe frames compose. The consumer's
initial singleton prefix is sorted; conditional order ensures then extend it to all eight
values. Full-value probe counts telescope through all seven calls and the suffix frame.

The N8 consumer runs the unchanged actual insertion loop with stub_verified(insert_tail),
then asserts sortedness and count preservation over all eight values using the independent
harness checkers. Only the helper is replaced by its verified contract; its body is not unfolded
in this consumer under Kani semantics. No whole-entry stub, manual sort wrapper, new assumption,
negative control, extra row or N16 root is in G2. Consumer covers return, present probe,
nonconstant result and reaching the assertions (four).

## Validation and budget

Existing validator accepts exactly8 rows and the required flags. Static source checks match
each of the seven PFC roots to its literal tail1..7 and find every requested root once.
G1 realcontracts source remains an exact prefix of the extended file. No existing G1 root,
model, ensures or runtime source was edited. Protected lane paths match the full tooling base;
git diff --check passes. No local cargo/rustc/Kani/CBMC, raw logs, credentials or competing code
were accessed. Library and research changes are separate [skip ci] commits, pushed without force.

G2 worst-case reserve `(8*10+30)*$0.0135=$1.4850`; G1 actual spend $0.2565 gives own maximum
$1.7415 <= $4.00. The existing dispatcher refreshes the project ledger before submission and
rejects a reserve exceeding $118.96. Any repair must remain within the task repair/build limits
and both caps; there is no authority to add a third primary build or an unchanged-input retry.

After publication dispatch exactly this request under the coordinator's GO, immediately register
k1g.sh watch BUILD and end the turn. On notification use only bounded summary/rows, check-tooling
and budget evidence. Update RESULT-ENSURES.md in <=35 lines, preserve the G1 history here/in its
PREBUILD, and explicitly state PFC-domain union >= consumer domain, full N8 sortedness/count
via ensures, times vs N5 and a qualified N16 forecast. Publish [skip ci] reporting,
REVIEW REQUEST / ENSURES ЗАВЕРШЁН, then stop.


## Observed G2 outcome / final review handoff

Published source `9286a7713f4a8331184004ccc435055968e1ff16` was checked against the exact
eight-row GO packet and dispatched without another approval request under the coordinator's
explicit authorization. Owner k1-network was declared free by that GO. Build
`e8526f1c-c5f7-48c8-a314-fb50bed6b517` was registered with k1g watch; the turn ended.
The queued completion reported SUCCESS. Bounded summary COMPLETE, gate/expectations true,
Kani exit0. The eight-row page binds exact request hash, build and source with offset0/count8,
total8/next_offset=done. Check-tooling passes expected standard4 pool, source/run identity,
all protected lane paths and six bound hashes against the full tooling base.

| Root realcontracts:: | Status | Time s | Failed/total | Covers | Unreachable checks |
| --- | --- | --- | --- | --- | --- |
| insert_tail_ensures_u64_tail1_backing8 | SUCCESS | 69.21353 | 0/531 | 5/6 | 4 |
| insert_tail_ensures_u64_tail2_backing8 | SUCCESS | 80.58219 | 0/531 | 6/6 | 4 |
| insert_tail_ensures_u64_tail3_backing8 | SUCCESS | 92.28954 | 0/531 | 6/6 | 4 |
| insert_tail_ensures_u64_tail4_backing8 | SUCCESS | 92.91752 | 0/531 | 6/6 | 4 |
| insert_tail_ensures_u64_tail5_backing8 | SUCCESS | 113.276955 | 0/531 | 6/6 | 4 |
| insert_tail_ensures_u64_tail6_backing8 | SUCCESS | 130.98123 | 0/531 | 6/6 | 4 |
| insert_tail_ensures_u64_tail7_backing8 | SUCCESS | 117.54943 | 0/531 | 6/6 | 6 |
| insertion_ensures_u64_n8_stubbed | SUCCESS | 548.07477 | 0/492 | 4/4 | 4 |

All eight expected SUCCESS rows pass. Covers for tails2..7 are6/6, consumer4/4.
Tail1 is5/6 with one unreachable cover, rather than the five registered covers anticipated
in preparation. Bounded log-lines2794/count20 confirms this exact tail1 block, SUCCESS and
one unreachable cover; terse output does not identify an individual cover property. The source
has a sixth cover guarded by TAIL>1 for an unsorted prefix; at TAIL=1 that guard is false
and the singleton prefix is always sorted. Attribution to that guarded cover is a source-based
inference, not a separately printed property-ID binding. No code/build repair is needed to
meet the request. Unreachable checks do not add independent proof credit.

The union of the seven actual real-body PFC domains covers every N8 consumer helper call:
u64, InsertTailU64Less, arbitrary full [u64;8], arbitrary immutable full-u64 probe, begin at
allocation base and tail1..7. The consumer executes the original insertion loop with precisely
those seven calls. stub_verified(insert_tail) supplies only the helper contract under Kani
semantics, without unfolding its body in this consumer; sortedness and full-value count are
checked over all eight output elements. No sorted-prefix assumption narrows the PFC domains.
The singleton initial prefix plus conditional order ensures, count ensures and suffix/probe
frame establish the bounded composition. This uses source/attribute binding and Kani semantics,
not an independent lowered-IR/callgraph audit or a universal havoc multiset axiom.

N5 consumer247.8377s -> N8 consumer548.07477s, ratio2.211426, leaving51.92523s below the
600s harness limit. Fixed-tail PFCs total696.810395s, individually69.21..130.98s, versus the
G1 symbolic-tail/backing5 PFC229.96153s. Those PFC timings change both partition and domain;
the aggregate ratio3.030117 is not an isolated causal measurement of increasing N.

N16 forecast is deliberately conditional: a linear-in-N extrapolation from N8 gives1096.15s
(18.27min); a power fit through the two consumer points gives exponent1.688578 and1766.66s
(29.44min). These are model examples, not a guaranteed interval or proof that either scaling
law applies. CBMC peak increases3.58->8.94GiB (2.4972x); the N8 monolithic consumer already
uses most of its ten-minute allowance. A direct N16 consumer with current summaries may exceed
both time and16GB constraints. Larger PFC backing16/tails1..15 and checked unwind bounds are
required before composition credit; fifteen PFCs plus one consumer exceed one eight-row packet.
No N16/32 verification, extra build or further authorization is inferred.

G2 wall including compilation24:23.93, max RSS9374368KiB, sampled sum RSS8.93GiB,
per-CBMC peak8.94GiB attributed by bounded summary to the N8 consumer. OOM scan none_seen is
not a headroom proof. Budget for both actual builds: `2 0.6750 0.0000`; G2=$0.4185,
G1=$0.2565, total$0.6750 under own cap$4.00. Dispatch maximum was$101.3955 under$118.96.
Both primary builds are consumed; there were no compile-error repairs or additional dispatches.
The final RESULT preserves all twelve G1/G2 rows, exact ensures, domains, comparisons and
qualified forecast in at most35 lines. After G2 only reporting files change. Publish [skip ci],
REVIEW REQUEST / ENSURES ЗАВЕРШЁН, then stop.
