# Cloud-only strict CUT declaration relocation TEST

The completed TRACE diagnostic names `$_32: &? T` as the first failing outer
entry and preserves the strict error at `verified/lib.rs(84,9-38)`. This card
authorizes only the independent, isolated diagnostic in `run-cut-relocate.sh`:
production source copied under `/workspace`, frozen CUT patch `d557082b…`,
then declaration relocation TEST patch `e7189430…`. The TRACE patch is absent.
The production source, console, specifications, exporter, refiner, and schema
remain byte-identical before and after the diagnostic.

The only fixture is `callback_positive` from `positive_f_bound`: verified
source SHA-256 `66bf5a6e…`, original `9b41aef5…`, full NORMAL target MIR
`10356bf1…`, and full readonly target MIR `9fdee764…`. Both MIR hashes are
mandatory graph gates, including the direct `Continue` unwind. The runner
compares no-relocation and relocation proof on the same source and MIR, with
unchanged normal and unwind posts recovering thread/type resources, both T
cells/owners, and the comparator F cell/owner. It records the six AST
declarations removed from outer scope and inserted once inside the strict
block. `StorageDead` at line 103 is a normal-path fact; it is **not** assumed
on the unwind path. The existing CUT kernel checks remain byte-identical.

An unchanged baseline first error followed by either full fixture VF0 or one
new first proof blocker is a **diagnostic only**. Any source/MIR mismatch,
missing AST trace, changed baseline boundary, or other stage failure is
inconclusive. Neither outcome accepts CUT, relocation, or actual sort4.

Before any acceptance, the following gates remain **OPEN**: independent
normal and unwind all-path liveness; no post-cut use, renewed StorageLive,
address escape, Drop/cleanup, or retained heap/bound/outer-variable type;
source/MIR mutation negatives for each of those hazards and changed unwind
successor; full normal/unwind resource and leak review; fresh combined S6 and
ordinary no-cut callback regressions; and separate exact source/MIR admission
for actual `sort4_stable`. The full-MIR hash gate establishes this one input
graph, not a general relocation rule or a proof of those open properties.
