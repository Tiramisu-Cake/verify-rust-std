## Переходный checkpoint — Git sync, повторная приёмка НЕ ВЫПОЛНЕНА

2026-10-08. В этой ветке напрямую влит закреплённый upstream cd371e03.
[UPSTREAM-SYNC](../UPSTREAM-SYNC.md) фиксирует parents/SHA, исходниковые изменения,
бюджеты и два следующих задания. CI budget этой фазы0; исследования отложены.
Старые принятые результаты ниже относятся только к прежним proof SHA/tool profiles.
Новым std/nightly/VF необходима повторная проверка. S7c UNACCEPTED (пять admission
контролей незавершены); G2/A/B и девять Rust projections сохраняют прежние условные
границы в исходных ветках. Бюджеты5306/5400(94) и512/1800(1288) не сброшены.
Git merge не доказывает actual helper/merge/Challenge. Подготовленные задания
НЕ разрешают их выполнение в этой CI0-фазе.

# Merge mathematical proofs and stock Rust component results

## Stock Rust pointer/index stage — applicability audit completed before P1

Owner accepted G2/A/B from documentation HEAD7d27ce106d27208bcd1156fe5675f70f8f9bf1aa;
proof bodies/premises and proof SHAs below preserved. [POINTER-DESIGN](POINTER-DESIGN.md)
records the new component and [SOURCE-MAP](SOURCE-MAP.md) its pinned caller ledger.
Stable and unstable public entry chains exclude T-ZST before SmallSort dispatch;
cached-key sorts nonzero index tuples. Direct general SmallSort ZST remains a
merge route outside those guards. Direct network ZST len2..17 returns; len18..32
repeats its right-region pointer-equality loop without reaching merge on normal
paths. This is source/semantic audit evidence, not stock layout verification.
Standalone generic Challenge scope still includes ZST.

P3 proof SHA **1c318453efa4e3a774b2edd791a5298d76132eb0**,
[run37686627140](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686627140):
all9 selected positive Rust projection units PASS,12 own checked bodies,
102 own execution records,25 return/leak paths. No errors/dead code. Full
readonly export/decode/verifier/refinement0 and source integrity per stage.
Stock26.09/archive/console/exporter/refiner/schema/std admission unchanged.
Refinement is ONLY projection-versus-ghost-free-projection, not the full merge.
Two intended assertion negatives and all128 fail-closed controls PASS.

| Rust projection | Established result | Remaining applicability premise |
| --- | --- | --- |
| g2_steps | Bodies of local G2 step bounds/equations and terminal arithmetic checked anew in Rust | Complete unbounded Rust trace/loop composition OPEN; no C axiom imported |
| init_const, init_mut | Exact add(i), typed address displacement, retained provenance, result within stock limits | Positive size, i<=n, n*size<=isize::MAX, base/end limits; actual allocation/resource proof OPEN |
| forward_left, forward_right | Exact add(is_l as usize)/add(!is_l as usize) realizes i plus the Boolean bit | i<n and same byte/provenance limits; no comparator/copy modeled |
| destination_up, destination_down | Exact add(1)/sub(1) realizes i+1/i-1, provenance/limits retained | i<n, and reverse i>=1; destination write permission OPEN |
| stride_order + pointer_order | Checked multiplication lemma; exact left<left_end iff i<j | Positive size and whole pointer associations to one base; terminal wrapping associations OPEN |
| stride_equal + pointer_guard | Checked multiplication lemma; exact pointer OR guard iff scalar index OR guard | Same associations for all four endpoints, including provenance; no panic/resource theorem |

Component preconditions are explicit sufficient research premises, distinct
from source-audited caller facts in POINTER-DESIGN. Numeric displacement alone
does not supply live provenance, permissions, initialization or safe copies.
No Challenge size restriction, runtime/public contract/A/B/comparator change.

wrong_cursor rejects precisely projected21:23–25 at its step2 assertion after
exact add1. Predicate:
`ptr_add_(ptr_add_(base, i, T_typeid), 1, T_typeid) = ptr_add_(base, (i + 2), T_typeid)`.
address_index rejects precisely15:18–20 at `i = j` when addresses are equal
but indices have no base/offset association. Both enter intended own body,
execute TARGET, retain exporter/decode/refinement0 and source integrity. Ten
strict rejection controls each, including body/line/columns/predicate/source/
earlier-stage/timeout/target-execution, pass; positives have12 controls each.

**First blocker of further pointer/index composition:** exact stock methods
`std::ptr::const_ptr::<impl *const T>::wrapping_sub` and `wrapping_add` are
absent. [P2/run37686101335](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37686101335),
proof source1f2eaaa832a7183180675389979ec15c62a78b5d, rejects wrapping_down15:17–54
and wrapping_end14:20–44 with `No such function`, after export/decode/refinement0.
Those two minimal generic true-post support probes are the reproducers, not
pointer correspondence proofs. No later run repeats them. Existing P2 reentry
case fails safe-prototype precondition; read-from--1 fails a ghost binding shadow,
before the intended read. Both INCONCLUSIVE. Their corrected annotation/prototype
drafts are committed, excluded from P3, NOT RUN / NOT ACCEPTED. No read detector
calibration for intermediate -1 is claimed, and no wrapping is replaced by sub.

Still conditional/OPEN: actual loop invariant and initialization linkage to G2;
signed W(-1) with preserved provenance and modulo address, subsequent exact
wrapping re-entry to source-derived end pointers; lifting conditional order/guard
results to actual merge. Mathematical G2/A/B remain intact, but their transfer
to Rust still needs these links, source-ID/value/key realization, caller resource
proofs, exact copies/ownership, legal FnMut effects and full unwind. ZST has no
injective address-to-index map; its remaining analysis is semantic/audit only.
Full merge safety/functionality and Challenge completion NOT CLAIMED.

| New experiment | Exact checked SHA | Run | Hosted job seconds | Outcome |
| --- | --- | --- | ---: | --- |
| P1 | adb0c7004118fb32b3d20dbd4d085ca145755fd1 | 37685381321 | 111 | 15 annotation parse failures; no proof/support claim |
| P2 | 1f2eaaa832a7183180675389979ec15c62a78b5d | 37686101335 | 36 | Wrapping support blocker; seven raw VF0 positives await classifier; other failures preserved |
| P3 | 1c318453efa4e3a774b2edd791a5298d76132eb0 | 37686627140 | 35 | 9 full positive units +2 intended negatives accepted;128 controls |

Actual budget **512/1800 used,1288 remain**: original330 plus182 new summed
hosted job seconds, setup/evidence included. No reset/transfer/retirement.
P3 artifact11510794272,265475bytes,ZIP SHA256
5a52e5903764deda94f3d0e955ada3fa3e37123f696e5c93c74e9032be730c9f
independently matches GitHub digest. Full stage logs/MIR/resource/metadata/source
hashes inspected,25 own normal return/leak paths retained. Driver4.14s,
peakRSS192276KiB; first failures and detailed hashes preserved in the journal.
No active run. Supported scope complete, wrapping composition STOP. Later
documentation-only HEAD is reported separately from the executable proof SHA;
it is not a new proof run. No networks/exactN13 runs/merges/first-agent-tree edits.

## Preserved mathematical stage

This authorized stage continues from067fb584018760259841210d2cc6c227117798ce
in the isolated challenge-8/merge worktree, with the original1800 hosted-job
second budget. Original G2 report preserved in [GEOMETRY-RESULTS.md](GEOMETRY-RESULTS.md),
original proofSHA b1ed0c22dafec350a64e83675d55350806d77208. Actual Rust OPEN.

## Goal A — ACCEPTED

ProofSHA fc4d03d31f92c6d3f3566b0baa506d0a6dec6805,
[run37677079473](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37677079473).
Stock unchanged VeriFast26.09 checks19 bodies including all8 original G2 bodies,
178statements,55return/leak checks, full posts and source integrity.

For any n>=2 and arbitrary m=n/2 independent pairs of normal Boolean choices,
with arbitrary odd residual h, fa_entry assumes only the final scalar guard.
It proves full G2 access/advance trace; output and chronological write trace of
length n; one write for every destination p in[0,n), zero outside; tracevalue
at every such p equals nth(p,output); for any integer occurrence ID q, its
output count is1 iff0<=q<n and0 otherwise. The distinct original IDs are the
positions0..n-1; equal keys do not collapse occurrences. No key/order/SWO premise.

fa_trace records upward copy before downward copy per iteration, then the next
pair, finally odd copy. fa_output gives natural destination order through
cons(up,append(recursive_middle,[down])), with the same source at each event
before advancement. Signed indicator balances telescope for arbitrary choices,
including crossed source cursor intervals; final scalar equalities cancel the
residual potential. Thus no unproved remaining-set disjointness in Goal A.
Proofs are structural induction over arbitrary decision lists, not bounded tests.

Negative n2 ds=[(true,false)] copies ID0 twice and never ID1. Scalar guardfails,
output=[0,0], exact ID0 count2/ID1 count0 established before the intended false
count1 assertion218cols68-70. Strict classifier accepts intended stage/body/
line/predicate/column/source and all7 rejection controls. Its source is unchanged
between A1 and A2; only diagnostic metadata calibration changed.

## Goal B — ACCEPTED

Proof SHA4e546ec150cf655681516be727aa1a79f525fc56,
[run37681190236](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37681190236).
All65 own bodies checked,505 statements,197 return/leak checks; exit0,
no proof errors/dead code/source changes. Includes unchanged G2/A and all12
constructive SWO bridge bodies plus their3 existing primitive prerequisites.

ms_entry requires n>=2, exactly n/2 decisions, a fixed finite SWO on constructed
original occurrenceIDs0..n-1, both original halves sorted by it, and faithful
normally returning comparator answers at the exact two read pairs of every
iteration. One pure relation represents immutable keys throughout the schedule;
no key mutation/effect assumption is smuggled into unrestricted G2 or A.
Odd h is exactly the logical final left<left_end (endA<endD).

The full exported posts prove scalar guardpasses, all-pairs output ordering
!rel(laterID,earlierID), and equivalent keys imply earlierID<laterID in original
input order. Combined exact arbitrary-ID multiplicities give stable permutation
of separate occurrences; equal keys never collapse. It also exports every A
output/trace/coverage/count/tracevalue post and the full G2 access trace.
ms_sorted_positions exposes sorting/stability at arbitrary i<j. Separate
ms_forward_tie/ms_backward_tie bodies prove exact left/front and right/back
source selection from equivalence without extra sortedness/SWO assumptions.

Rank theorem mb_entry_rank orders lex(key(ID),originalID). Four independent
front/back cross-frontier inequalities imply noncrossed joint residual intervals
[a,m-k+d) and[m+k-a,2m+e-d), even if one becomes empty. Exact paired choices
select strict lex minima/maxima; remaining next-state IDs lie strictly between
them. Structural induction constructs exactly up::(middle++[down]), not an
unchecked reference merge. Terminal cuts give a<=d<=a+e; scalar h=(a<d)
consumes the sole odd occurrence and establishes both final equalities.

The finite SWO wrapper derives predecessor-count ranks constructively, translating
original-half sortedness and every exact source comparison using rechecked
swo_rank_bridge. It then projects rank sorting and equal-rank stability back to
the source relation. No assumed rank embedding, key uniqueness, total strict
order, reference-schedule equivalence or bounded enumeration.

All three isolated functional negatives accepted with exact predicates,
stage/body/location/columns/source integrity and21 classifier rejection controls:

- Without final guard: n2, decisions[(true,false)], output[0,0], ID0 twice/ID1 lost;
  intended count assertion218cols68-70. No ordering assumptions.
- Wrong ties: keys[0,0], decisions[(false,false)], outputIDs[1,0]. Scalar guard and
  permutation pass, keys remain nondecreasing; original equivalent-ID order
  fails at mb_lt(@neg_equal_key,1,0) assertion274cols39-41.
- Wrong comparison answers: keys[1,0], decisions[(true,true)], outputIDs[0,1].
  Each original half sorted (one element), scalar guard/permutation pass;
  key0<=key1 fails at assertion274cols31-33.

B6 verified every post but failed dead-code gate; it remains INCONCLUSIVE.
B7 retains all assertions/posts and reorders steps before contradiction-producing
facts, preserving the stock dead-code check. No disabled checks or erased
obligations were used to obtain acceptance.

## Evidence and source boundary

Full pinned SmallSort SHA25632574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959;
merge_up / merge_down / bidirectional_merge exact signatures and active9/9/30
statements admitted by unchanged original harness. CertificateSHA256
f2ccc11b235e8f2224131ddef4a12c17409c58863c5712726cb13a02a4960bc7.
G2 source geometry.c remains4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8;
A source functional-ids.c20a7d91564bbf49e8f2e8bb0436a7ccc7eec2e7928f6267486a6ab0f291ab814.
Frozen strict classifier994afa65a24c1deb73fd120ac88c96fa5d86eb971f58adba678c850a1153d0c4
unchanged; no proof/run on editing server, no tools/parser/memory/runtime patch.
Original stocktoolpins in GEOMETRY-RESULTS remain valid.

Scalar index guard is not identified with actual pointer equality/order,
especially for ZST. Provenance, usize/byte overflow, initialization, permissions,
copy/ownership, comparator FnMut effects and panic/unwind require separate Rust
integration. Conditional mathematical A is no actual Rust safety theorem and
no public Challenge completion. [Transfer obligations](INTEGRATION.md).

## Hosted ledger

| Run | SHA | Job seconds | Result |
| --- | --- | ---: | --- |
| G1 37671730724 | 90872439be953a960aacbb12c79886d6a87e73db |11| Inconclusive remainder/negative metadata |
| G2 37672184476 | b1ed0c22dafec350a64e83675d55350806d77208 |14| Geometry accepted |
| A1 37676075230 | a4c46af5f860e5117b0d46b154d32f8c8bfbdc1e |14| Trace recursion termination / negative metadata |
| A2 37677079473 | fc4d03d31f92c6d3f3566b0baa506d0a6dec6805 |17| Full A accepted |
| B1 37677923322 | 08d66c14f8a8e1881898dd6f154881829c5121c5 |14| Late nat include parse failure |
| B2 37678436610 | 7b7dd6e6d57cb7271cbe323fe3cc4369fb9826cb |14| Combined ==! token parse failure |
| B3 37679049210 | 8c14883ae898fdce3086c10fdde0f0e2797fdb6e |30| Selected endpoint post unresolved |
| B4 37679577426 | b699b11ddb651d2404f770c4ffdd9a66e7277575 |35| Strict endpoint arithmetic cut unresolved |
| B5 37680109711 | 827726437cfec2add6ad6e4212a5796f43763f01 |52| Domain membership conversion unresolved |
| B6 37680494943 | 00323149706cec799ae1261004e1d3c1802da2b5 |77| All posts checked; dead code rejected |
| B7 37681190236 | 4e546ec150cf655681516be727aa1a79f525fc56 |52| Full B accepted |

At mathematical-stage closeout330/1800 spent,1470remaining including preparation/evidence. No network budget
reset or transfer; networks closed/exactN13OPEN and other direction untouched.

Accepted A artifact11506884092 (18833bytes), ZIP SHA256
cabd3f1f556e4c82dc900e34d636a2f98da419ab7c496c25fba989644c0bd2a9.
Accepted B artifact11508644687 (44096bytes), ZIP SHA256
603414227275569095c213eba7738271f478de51389df9b9b4eb79dd0c86c366.
Downloaded archives match upload digests. Full artifacts inspected: generated
sources/logs/manifest/admission/environment/resources/exit. Every case source
and log digest matched manifest; all accepted pins matched frozen originals.
B assembled source9e7e6b07cc086ca761f64dfdc2e2fd0e2266317eccbf9c3ef910ac2172f9fc52,
log4b2a862bbdd736339462b44eda89f18100807278e8ca257bacd77edc9f87fa2b;
order file58d18c5bbcb301f8ee3d9b05660fbee69ca2c38a40708637ebd634bcdd729154,
SWO applicationd049fd4ba51fe7e022f4d9250c8c51bdf6a7b0d68837bb23e88b642e431fa768.
B proof process39.49s, peakRSS246252KiB; summed job52s includes cold preparation.
The reused runner environment text labels this `merge-order-A` (cosmetic inherited
label); workflow input=merge_order, exact GITHUB_SHA/source, domain/full posts and
actual ms_entry/MS body evidence establish it is B. No label-only extra run.
The frozen classifier also supplies its generic boundary wording; actual full
callee posts are retained in checked source and reported above, never replaced
by ensures true (except isolated intentional negatives).
