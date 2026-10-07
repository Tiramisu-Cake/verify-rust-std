# `select_unpredictable` actual-callee diagnostic

## Current result — S6v2 component accepted, actual initialized-cell obligation

[S6 completion37642650884](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37642650884),
source `4d0e3070ca93e01b7a5ccfad18ea83900bc7536b`, accepts the complete narrow
pointer-drop component at drop-v1/cd660fe9:2positive+11proofnegative+22admission
controls, with same-profile original proof/regression provenance retained.
Constructor, SAFE as_mut_ptr and both typed select intrinsics retain complete
new-profile matrices; fourteen stock/experimental baselines passed.

Actual baseline source/export/decode/refinement/full method +31local/14block
actual certificates and redirects PASS. Actual body reaches the retained runtime
method at `verified/lib.rs(57,14-29)`, then fails its precondition:
`verified/lib.rs(110,55-58): No matching heap chunks: points_to<*Element>(__result2, _)`.
Required resource is the initialized pointer CELL, not Element pointee rights.
The existing wrappers/some states and reborrow tokens have not yet been projected.
All runtime calls/cleanup edges and full target contract remain.

The fresh [S6v2 run37645561507](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37645561507),
source `85ec1711700ff85c899b18b7e021f076aeddb8e6`, patch `8e62e6c3`, accepts
the same complete drop matrix and reruns constructor/asptr/intrinsic matrices and
fourteen baselines successfully. Both added actual ghost-coordinate controls
fail during setup at the second, NORMAL exporter invocation. They are not intended
negatives; canonical projected helper remains NOT RUN.

The v1 projected variant exports/decodes/refines but stops BEFORE proof at
`actual projection ghost source span`. The v2 correction incorrectly used readonly
span geometry for normal MIR: the frozen normal exporter inserts the 32-byte
`crate::VeriFast_ghost_command();` scaffold before each ghost command, while the
explicit parser coordinates retain the original source positions. A separate
hosted diagnostic will retain the full NORMAL typed MIR before any further
admission decision. Projection resources have no proof verdict yet.
[Preimplementation rationale and reassessment](SORT4-SELECT-POINTER-DESIGN.md).
No memory/ownership bridge/guard/forget/assume_init/refiner/kernel extension.

Drop preserves existing initialized cell's full pointer value, thread token and
independent frames, no new Element rights. Compiler raw-pointer glue correspondence
is separately TRUSTED; ghost identity proof does not establish it, recursive free
source is not a runtime-body theorem. Whole helper and sort4 NOT PROVEN.
Budget **3168/5400 used,2232 remain**, no reset; no active run at normal-capture preparation.
Earlier Git/dispatch500 recovered; published identical Git objects force=false.

Correction from original S5j logs: assume_init refinement did NOT pass.
Readonly export/decode0; refiner1 `RawPtr: not yet supported` at bb1command4,
original25/verified33. Normal preprocessing separately fails after-tail ghostclose.
No read-resource proof or ownership/provenance boundary follows from those failures.
[Original S5j run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848).

## Historical O4 result — constructor accepted, as_mut_ptr boundary

[O4/37601511894](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894),
proof source `182ddf29dc73961723bf32be6b65643c524ca927`,
[artifact11473086721](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894/artifacts/11473086721)
`smallsort-research-37601511894-1/maybeuninit-new-pointer`,
profile `experimental-source-linked-maybeuninit-pointer-own-v2`, patch SHA256
`325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d`.
[Constructor/model acceptance](SORT4-POINTER-OWNERSHIP-RESULTS.md) is complete;
**actual select RUN / INCONCLUSIVE**, full select/sort4 NOT PROVEN.

Exact reproduction: same run's `matrix/actual_select_after_constructor/prepared/`
keeps the unchanged N6 pointer adapter, original/verified copies plus certified
constructor module. `fixture.json` pins body
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613`;
original/annotated adapter hashes before helper cd6feb7a/bd332fbb match N6 below.
`matrix/actual_select_after_constructor_run` retains final original/verified units,
MIR binary/text, stage integrity, exporter/decode/refinement logs and full verifier
log. Source hashes at every stage are original
`4c3cd8e16e5f4b38bc85f3bffafaebd85e934488181e1cbc52b3c219c19ab7d7` and verified
`8cec14edfee63213ba0f3d6ac12fdd55d5812c2cbac01a253bc27e81dfadf242`.
All3intrinsics, guards, Drop body, drop_in_place/forget/assume_init and exact
selected-pointer/thread/frame/no-unwind target remain present; no Copy bound.
This is still a thin-pointer/non-const diagnostic adapter, not generic Destruct
or arbitrary MaybeUninit<T> support. Runtime std/signatures are unchanged.

Export/decode/refinement/source-integrity0; complete constructor source/HIR/typed
MIR certificate PASS; exactly two external new calls redirect. SAFE actual-callee
prototype check succeeds and body enters; verifier checks both calls at22/23.
The constructor body, explicit result own and checked introduction lemma were
proved earlier in this same SHA/profile run (`matrix/constructor_positive`);
actual unit fails before visiting that helper's body again. Its checked ownership
lemma does execute. Synthetic DropOnPanic generated structural lemmas are not
verification of its runtime Drop body.

First causal failure: `verified/lib.rs(38,20-41)`:
`No such function: std::mem::MaybeUninit::<T>::as_mut_ptr`, on
`let true_ptr = true_val.as_mut_ptr();`. This is unsupported callee resolution,
not a failed safety post or intended negative. Pinned source
`library/core/src/mem/maybe_uninit.rs:648` takes `&mut self` and returns
`self as *mut _ as *mut T`. Scope inference: validating this storage-address cast and its reference
permissions is a separate capability assessment outside the accepted empty
pointer-value ownership rule. Existing model feasibility for that operation is
NOT RUN; this resolution error alone does not prove a new alias model necessary. No workaround or opaque summary was introduced.

STOP at this scope boundary: intrinsic/copy, runtime Drop/forget/assume_init and
final return/leak/normal/unwind proofs remain NOT REACHED as complete operation
proofs. New storage/alias/borrow capability needs a separate phase decision.
518/5400summedjobseconds across4NEWruns; unused4882s retired; no active run.
RAPx CLOSED/NO-GO; B/C NOT RUN. Full profile pins, matrix targets and trust limits
are in the linked closeout. Final documentation is not a proof run.

## Historical N6 stock diagnostic — before constructor acceptance

**Result: inconclusive at the first call in the real helper body.** Hosted run
[37549040942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549040942),
repository source `aed1d970acb656cd29149241bf6720198895adac`, used stock
VeriFast26.09. Export, decode, refinement and source-integrity stages passed.
The fixture contains one actual-callee body; its exact extracted body SHA256 is
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613`.
Full original adapter SHA256 is
`cd6feb7a22f8ec42c58df341e27e21d5e10215f71c428f11f639b41d76e1de4d`;
annotated adapter SHA256 is
`bd332fbb6a4cbc9fc935b6bc5a0dcc99f691af9182535a1b64ae40ad516bb8fd`.
After stripping ghost annotations the two adapters are byte-equal.
The source identity is
`library/core/src/hint.rs`, blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`,
SHA-256 `d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8`.
The full hosted evidence is under `/tmp/sort4-night-37549040942-artifacts/`;
the per-run log is `/tmp/sort4-night-37549040942.log`.

The fixture targets `T = *const Element`, without `Element: Copy`, and keeps
the runtime body byte-identical. It records a non-const proof adapter for the
pinned compiler, because this is a pointer instantiation diagnostic, not a
proof of the original generic `[const] Destruct` API. Its requested normal post
is full pointer-model equality with the argument selected by `condition`,
preserving provenance through pointer equality, plus the thread token/frame;
the requested unwind post is false for this pointer instantiation. None of
these posts was proved.

The first VeriFast error is at the first body statement:
`No such function: std::mem::MaybeUninit::<T>::new` (`verified/lib.rs:21`). The
prior hypothesis that an intrinsic would be the first unsupported operation
is superseded. The exporter emitted all three intrinsic calls, the local
`DropOnPanic` declaration/body and the later `as_mut_ptr`, `drop_in_place`,
`forget`, and `assume_init` operations; the verifier did not reach their
proof obligations. This is a function-resolution/frontend blocker, not an
intended negative and not evidence about intrinsic semantics, pointer result,
provenance, frame, or normal/unwind correctness.

The target implementation is visible in
`library/core/src/mem/maybe_uninit.rs:345–348,374–398`: `MaybeUninit<T>` is a
transparent union with `uninit: ()` and `value: ManuallyDrop<T>`, and `new`
returns `MaybeUninit { value: ManuallyDrop::new(val) }`. In the pinned
`bin/rust/std/lib.rsspec:429–486`, VeriFast models it as `struct MaybeUninit<T>`
and supplies a ghost fixpoint `MaybeUninit::new(v)` via
`new_maybe_uninit(some(v))`. That algebraic model does not register or prove the
runtime MIR function call emitted for `MaybeUninit::new`; the existing
`MaybeUninit::write` contract at lines 488–493 is a different operation and
cannot stand in for this call while retaining the body.

No checked actual-constructor route was found in the frozen profile. It would
need a checked correspondence from the runtime constructor body to the
`MaybeUninit` ownership model, including initialization of the union's
`ManuallyDrop<T>` field. Adding an opaque constructor summary, aliasing the
runtime call directly to the ghost fixpoint, or introducing a trusted union
ownership bridge would assume the missing step and is outside authorization.
The smallest future capability to assess is a source-linked, checked lowering
or body-verification route for this constructor and its union field ownership;
only after that succeeds can this unchanged helper reach the three intrinsics
and `DropOnPanic` proof obligations.

The diagnostic extracted adapters only in disposable hosted checkouts; repository
std runtime was unchanged. No local executable checks were run. No verifier rerun or patch is proposed in this note.

## Historical S5k pointer-select integration (2026-10-07)

Historical constructor/as_mut_ptr blockers above remain historical evidence.
Current source-linked T=*const Element actual helper: S5k run37624082376,
source `128dd5673c7796c5916017ab4afafaeea8d836b8`, profile
`experimental-source-linked-select-pointer-intrinsics-v2`, patch
`7bb39a84b95fd15ed5be29864c3a22774d37c660baafa694188b14970c344320`.
Pinned source integrity/export/decode/refinement and full31local14BB MIR gate PASS.
Proof trace enters select_unpredictable, verifies ctor calls22/23 and as_mut_ptr38/39,
executes typed intrinsic pointer selections49/50 and guard construction56, then
fails57: `No such function: std::ptr::mut_ptr::<impl *mut T>::drop_in_place`.
Third wrapper intrinsic is certified/translated but its later proof path is not
reached. Final return/leak/normal-unwind posts remain unproved; helper NOT PROVEN.
This is the next unsupported callee, not a proved resource/provenance boundary.
[Run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376),
[compact evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482879763).

Intrinsic component6+10+40 accepted independently at sameprofile S5k; savedS5j
source2454e86 acceptance additionally completed by replay S5r2/source586c9ae,
without build/proof execution or crossprofile transfer. Exactly8 diagnostic reason
corrections; original classifications/source/MIR/logs retained.
[Replay run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885),
[compact replay inclS5j+O4](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885/artifacts/11483952705).
Further semantic work FROZEN per latest user. Assume-init's tail-annotation failure
and subsequent RawPtr refiner/union frontend failure are independent; missing read
ownership hypothesis NOT RUN, refinement semantics unchanged. Drop/guard/forget/
assume_init components unaccepted. Current budget2398/5400,noactive; fullsort4
NOT PROVEN, RAPx CLOSED/NO-GO, B/C NOT RUN. See current phase results and STATUS.
