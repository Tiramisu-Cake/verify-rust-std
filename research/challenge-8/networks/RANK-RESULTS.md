# Phase2 results and precise unfinished composition

2026-10-07 current result: **Generic finite SWO -> integer ranks and full N9
SWO network composition ACCEPTED. N13 composition is being checked in R13.**
Saved commits65f2ddb... and04ea220... were published without changes after
GitHub writes recovered. R9f exact checked SHA04ea22075f87634221cc43ccba59486fb10ad817.
No Rust safety or public Challenge completion is established.

## Proven mathematical statements

Unchanged official stock VeriFast26.09 accepted all15 named bodies of the generic
unit in R9d and again R9e, VF0,81statements,39return and39leak checks. R9d source
`955fd2a3334e8fe14c55bdb00f98c4f9813da775`, generic generated-source SHA256
`33b0ec72b9e8585046d3d8ef5b41b6ac63d809596e5e8639cb25d8959cd604cd`.
[Accepted generic R9d run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653851684)
and [repeat R9e evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37654875244).
Both overall workflows failed on the separate composition timeout; generic
acceptance is supported by its complete case log/exit/body/return/leak gate.

R9f includes the additional ordered-pair projection body and completes ALL16
named generic bodies, VF0,83statements,40return/leak checks. Generic generated
sourceacc2d0bd1d43eba573c57c206438398ab1dc7a887945ea1bdf96a1885312f2ca.
[Accepted full R9f](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37661652169).

For arbitrary fixed pure relation rel on a finite list d, assume only finite
irreflexivity, strict transitivity and transitive incomparability. For members
x,y, construct rank(x)=count of ORIGINAL occurrences z with rel(z,x). Checked
induction, not an embedding assumption, establishes:

- rel(x,y) iff rank(x)<rank(y); both preservation and reflection.
- x and y incomparable in both directions iff rank(x)==rank(y).
- 0<=rank(x),rank(y)<length(d). Tied/equal keys are included.
- Exact CE decision rel(right,left) selects either (right,left) or (left,right),
  realizes min/max constructed ranks, remains in d and preserves the count of
  arbitrary occurrence q. Ties keep that local pair unchanged.

The ranks are weighted predecessor counts and may have gaps; occurrence IDs are
distinct from ranks. These lemmas do not require Copy/Freeze or stable sorting.
Own proof bodies derive every correspondence post; stock list/count/forall
semantics and verifier are unchanged. No own bodyless lemma/axiom/imported solution.

## Exact networks and full N9 composition

Phase1 accepted N9/N13 rank and identity theorems, exact25/45 actual calls,
remain preserved in RESULTS.md/PHASE1-STATUS.md and their original journal.
New composition regenerates the accepted rank-theorem bodies verbatim via
unchanged prove.py and checks them in the same unit before using their summaries.
Actual SmallSort full-source SHA256
32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959;
R9f artifact certifies each of25 N9 calls at source441..465.

Accepted R9f verifies all25 exact CE transitions against symbolic original
domain d: per-step ID/rank DAG equality, membership, comparison rel(right,left),
constructed rank correspondence and arbitrary-q total multiplicity. It completes
the accepted full integer-rank theorem application and derives ALL8 adjacent
key-order posts using checked swo_ordered_pair. Both the composed theorem and
its exact0..8 specialization return with full posts, VF0,4214statements,
546return/leak checks. Generated composition source SHA256
984b6479c71dd2788583319df7d21b248778e99c53888920f6f1bc484079afa9.

`network9_finite_swo_composition(rel,d,q)` requires finite_swo(rel,d) and
mem(0,d),...,mem(8,d); ensures every final ID is in d, !rel(out[i+1],out[i])
for every i=0..7 and sum(ce_occ(out[i],q))==sum(ce_occ(i,q)) for arbitrary q.
`network9_finite_swo_order(rel,q)` instantiates exact domain0..8, discharges
every initial membership and exports the same order/domain/multiplicity posts.
Unique initial IDs and universal q yield every occurrence exactly once, including
when keys tie. Adjacent sortedness is the literal machine post; global all-pairs
order is its mathematical corollary using rank correspondence/integer transitivity.

Earlier R9e all25 CEs and first SEVEN final adjacent pairs reached; last full
swo_rank_bridge at5059 timed out180s. Earlier second-pair reading was incorrect,
corrected by independent owner review and journal continuation. Its immutable
source84ca65e3bae37e4c1456c6413192ddba1ba63ae68ec733aa3c327207c538db13
and raw failure evidence remain preserved; it was not accepted as whole N9.
R9f adds a checked projection body with exactly finite_swo/pair membership/
rank(left)<=rank(right) -> !rel(right,left), keeping large equality/bound facts
inside a small lemma context. No timeout increase, premise/post weakening,
correspondence assumption or semantic/tool change.

R13 checks the SAME code for13 original IDs, exact45 CEs, all12adjacent order
posts,13memberships and full arbitrary-q multiplicity. It began only after
complete R9f acceptance and full artifact inspection, at published/checked
sourcef00f446e72758ec8c6da1f34d74c7c92719aecf2. Its outcome is pending; see STATUS.

## Meaningful negative and functional applicability

The accepted negative is strict-transitive and irreflexive with only0<2;
0~1 and1~2 but0 !~2 violate incomparability transitivity. It checks ranks1=0
and2=1 and reaches the intended false comparison-correspondence assertion:
less(1,2)=false despite rank1<rank2. Exact proof-stage assertion at65,26–28;
all7 wrong-location/predicate/body/target/column/timeout/source controls reject.
No unrelated preparation or failed SWO-precondition is counted as a negative.

Arbitrary immutable keys are represented by their strict-weak-order pullback
on occurrence IDs. Applying the result to actual code requires preserved keys
and one fixed order throughout, normal comparator return with exactly that
relation on the current operands, and actual helper realization of ID swaps.
Non-key effects need not vanish; no stability or unrestricted comparator order
is inferred. Actual Rust FnMut/borrow effects, select_unpredictable *mut T,
ManuallyDrop, pointer/memory ownership, normal/unwind and safety remain OPEN
for integration. No Rust integration/verifier patch or merge was performed.

## New-phase budget and publication

| Experiment | Run | Source commit | Hosted job seconds | Result |
| --- | --- | --- | ---: | --- |
| R9 | [37653028959](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653028959) | ccf813e797a1cea88c9629aaf33d501a57db0e15 | 14 | Include placement preparation failure |
| R9b | [37653292102](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653292102) | b8359b838e96312693f0340cc6daf5db7c78fd1d | 12 | Boolean-post elaboration; negative accepted |
| R9c | [37653560718](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653560718) | 09d41dd233d4b15366a38532b6b2cc5e5820b701 | 37 | Bare relation assertion elaboration |
| R9d | [37653851684](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653851684) | 955fd2a3334e8fe14c55bdb00f98c4f9813da775 | 192 | Generic bridge accepted; N9 timeout after6 CEs |
| R9e | [37654875244](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37654875244) | a38cc109329613645de8d995a5faba2feed7627f | 192 | All25 CEs reached; final conversion timeout |

**519/1800 summed hosted job seconds spent,1281remaining before active R13.** Includes cold
setup/checkout/evidence/post steps via actual job start/end; skipped jobs cost0.
R9f cost72s, job17:46:29Z–17:47:41Z. R13 active; its cost pending completion. Phase1 stays1499/1800spent,301unused not transferred.
Other direction's budget is untouched. All executable checks were hosted.
Full source/log/artifact hashes and first failures are preserved in
RANK-EXPERIMENT-LOG.md; no generated source/downloaded logs are committed.

Historical publication failed HTTP500 starting16:53:28Z; ordinary push,
HTTP/1.1/no-thin pack and Git Data blob creation failed, no ref update or
old-source run. After owner continuation, ordinary push successfully published
both saved commits65f2ddb... and04ea220...; remote exactly04ea220... verified.
R9f was then dispatched on04ea220..., not old a38cc109... . R13 card was committed
and published atf00f446e72758ec8c6da1f34d74c7c92719aecf2 and this remote SHA
verified before its sole dispatch. See STATUS for final local/published/checked
SHA distinction and current exact pending action. No merge or permission bypass.
