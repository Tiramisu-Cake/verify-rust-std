# Functional mathematical bidirectional merge

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

## Goal B — IN PROGRESS

Exact rank-key schedule and constructive fixed finite SWO composition drafted
in functional-order.c / functional-swo.c. Final acceptance pending. No claimed
sortedness, stability or guard theorem until all bodies and controls pass.

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

84/1800 spent,1716remaining including preparation/evidence. No network budget
reset or transfer; networks closed/exactN13OPEN and other direction untouched.
