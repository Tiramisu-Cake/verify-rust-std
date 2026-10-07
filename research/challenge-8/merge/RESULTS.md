# Functional mathematical bidirectional merge

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

Prepared symbolic Rust fixtures isolate add/sub/Boolean steps, checked local G2
formulas, pointer order/equality, wrapping support/re-entry and three negative
obligations. All results pending P1; no full Rust merge safety/completion claim.
Entry budget330/1800 used1470remain, separate from all other directions.

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

330/1800 spent,1470remaining including preparation/evidence. No network budget
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
