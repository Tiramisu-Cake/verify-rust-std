# Phase2 results and precise unfinished composition

2026-10-07 checkpoint. **Generic finite SWO -> integer ranks ACCEPTED. Whole
N9 SWO network composition remains OPEN; N13 was not dispatched.** Final
R9f proof source is committed locally but has not run: GitHub rejects writes
with HTTP500. This is not a completed phase/public Challenge or Rust safety proof.

## Proven mathematical statements

Unchanged official stock VeriFast26.09 accepted all15 named bodies of the generic
unit in R9d and again R9e, VF0,81statements,39return and39leak checks. R9d source
`955fd2a3334e8fe14c55bdb00f98c4f9813da775`, generic generated-source SHA256
`33b0ec72b9e8585046d3d8ef5b41b6ac63d809596e5e8639cb25d8959cd604cd`.
[Accepted generic R9d run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37653851684)
and [repeat R9e evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37654875244).
Both overall workflows failed on the separate composition timeout; generic
acceptance is supported by its complete case log/exit/body/return/leak gate.

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

## Exact networks and pending post

Phase1 accepted N9/N13 rank and identity theorems, exact25/45 actual calls,
remain preserved in RESULTS.md/PHASE1-STATUS.md and their original journal.
New composition regenerates the accepted rank-theorem bodies verbatim via
unchanged prove.py and checks them in the same unit before using their summaries.
Actual SmallSort full-source SHA256
32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959;
new R9e artifact certifies each of the25 N9 calls at source441..465.

R9e proves all25 CE transitions against symbolic original domain d, per-step
ID/rank DAG equality, domain membership, exact rel(right,left), constructed
rank correspondence and arbitrary-q total multiplicity. It completes the
accepted full integer-rank theorem application. These reached assertions are
partial progress, not an accepted whole composed lemma/post.

Precise unaccepted theorem `network9_finite_swo_composition(rel,d,q)`:
requires finite_swo(rel,d) and mem(0,d),...,mem(8,d); ensures every final ID
is in d, !rel(out[i+1],out[i]) for all i=0..7 and
sum(ce_occ(out[i],q))==sum(ce_occ(i,q)) for arbitrary q.
R9e generated source84ca65e3bae37e4c1456c6413192ddba1ba63ae68ec733aa3c327207c538db13
times out180s while checking its second final swo_rank_bridge call at5059,
after the first call starts90.653s and finishes149.321s. No assertion error;
543completed return/leak checks belong to earlier checked bodies. The composed
return/leak/post and thin `network9_finite_swo_order` exact0..8 wrapper are
not accepted. Final post is adjacent sortedness; all-pairs order is a separate
mathematical corollary of the constructed rank bridge and integer transitivity.

R9f source `65f2ddb06a8de05b718209f8df746fe1fb03163e` adds a body for
`swo_ordered_pair`: finite_swo/membership/rank(left)<=rank(right) ->
!rel(right,left), derived internally from the full accepted bridge. The network
uses only that projected summary for final pairs; all original full generic and
network posts remain. **This additional body and revised composition are not
hosted-checked yet.** N13 SWO composition remains unattempted behind full N9 gate.

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

**447/1800 summed hosted job seconds spent,1353remaining.** Includes cold
setup/checkout/evidence/post steps via actual job start/end; skipped jobs cost0.
R9f has no run/job cost. Phase1 stays1499/1800spent,301unused not transferred.
Other direction's budget is untouched. All executable checks were hosted.
Full source/log/artifact hashes and first failures are preserved in
RANK-EXPERIMENT-LOG.md; no generated source/downloaded logs are committed.

Push/dispatch failed HTTP500 starting16:53:28Z; ordinary push, HTTP/1.1 and
complete no-thin pack failed, as did Git Data API blob creation (HTTP500 with
empty JSON body,16:58:47Z; no ref update). Remote branch remained a38cc109...;
no new/duplicate/old-source run was created. Check STATUS for final publication
state. Next permitted action is publish exact pending local commits, verify
remote SHA, dispatch one ranks9 R9f and inspect full evidence. Only full N9
acceptance allows R13; remaining budget and stock trust boundary stay in force.
