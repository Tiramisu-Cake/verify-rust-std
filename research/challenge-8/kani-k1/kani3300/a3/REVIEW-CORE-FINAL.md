# KANI3300 A3 static review

- Baseline: `b207847932da34ac19886c1337f5b69ace0b0843`
- Candidate: `e3c529a0d5a501987a36c1481bb7e8a48c80dc73`
- Candidate tree: `520f75b9df2be108f598b3c62f956666752bdfc5`
- Diff SHA256: `c39b6522f08dc951e130bd36f805ef83be9fe2e3fc692cee8eec7515b0e28028`
- Spec SHA256: `5ca8a699ce50a1f0fda972d79fd717c6aa8d9a25b15dec542cbdae8faa716b4b`

## Static verdict

No confirmed soundness or static compilation blocker found in the committed A3 semantic diff. The argument protocol is internally paired on the inspected normal-call path: caller inserts Begin, snapshots all shadow arguments, and deinitializes each `Operand::Move` source before the original call; the callee loads its shadow arguments in ascending MIR-local order and consumes the protocol before user body execution. A shadow return stores mandatory index 0 on each normal return and the caller loads it after the call. Nested/repeated normal calls can begin once the callee's entry loads have consumed the prior argument protocol. Ordinary union values use the same pairing path. `Ty::to_index()` is documented in source as a compiler-context-local identifier; source inspection shows both call-site and callee instances resolve within the same compiler context, and the ID is not persisted.

`PointeeInfo::for_deinit` builds an all-true mask over the sized operand extent, and `build_set(false)` therefore clears all bytes including padding. Operation insertion preserves Begin → Store(s) → deinit(s) order before the source call. The added `MemoryInitOp` arms appear exhaustive in the inspected matches. `IndexedVal` is used by the new `to_index()` calls; no obvious unused import or `-D warnings` issue was found by source audit.

## Limitations and review notes

- Unwind recovery was not directly tested. Static MIR sequencing shows shadow-argument loads consume the protocol at callee entry before user body code; generated instrumentation calls use terminating unwind actions. I found no concrete ordinary callee-body unwind path that leaves the argument protocol active. This review does not claim behavior for abnormal paths outside the inspected MIR flow.
- A constant union operand would reach `mk_ref`'s `unreachable!()` because only MaybeUninit constants are materialized before StoreArgument. This appears to be an existing union-argument limitation (the baseline also built StoreArgument through `mk_ref`); it is not counted as a regression in this candidate. The actual MIR shape should be checked in the authorized fork if constant union arguments are in the test domain.
- Static inspection covered only union/MaybeUninit types recognized by the existing `transfers_shadow` predicate. It does not review B1 resolver behavior or other A4 stages.

## Validation status

Static source review only. No build, rustc, cargo, Kani, CBMC, Miri, Actions, or proof was run. No compile, runtime, or proof credit is claimed. The test-only fixture delta was not part of this committed candidate packet; verdict is limited to the exact identities above.
