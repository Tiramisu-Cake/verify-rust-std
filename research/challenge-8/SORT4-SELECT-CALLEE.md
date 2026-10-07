# `select_unpredictable` actual-callee diagnostic

## Current result — S7 acceptance blocked; actual still at forget guard-own

Current S7: **STOP at independent positive dead-code acceptance; forget NOT ACCEPTED.**
[Exact report](SORT4-SELECT-FORGET-RESULTS.md), [design/trust](SORT4-SELECT-FORGET-DESIGN.md).
Latest [37669436220](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37669436220),
source `a5ce1b5f71d2f0a2ecd1f74e44063ba079683b4d`: all9 NORMAL/readonly exports and
refinement PASS. Exact nominal guard/body captured; both positive bodies return/
leak-check but exit1 on frozen global dead-code gate. Seven intended raw proof
errors observed; automatic all9 INCONCLUSIVE retained (negative duplicate note
headers), no classifier change/replay. Full admission/mutation/borrow controls and
new-profile regressions NOT RUN. No new semantic profile/guard-own/actual redirect.
S6v4 components unchanged/accepted. Actual latest remains S6 forget63 missing
nominal guard-own, not assume_init; full helper/sort4 NOT PROVEN.
Budget **4411/5400 summed hosted jobseconds used;989 remain**, samebudget/noreset,
noactive. STOP for independent-acceptance design; no dead-code suppression or
preprocessor/focus/model extension. Historical S6 checkpoint follows.

Historical S6 closeout: **COMPONENT_ACCEPTED (v4); actual integration STOPPED at forget guard-own.**
[Fresh run37656621026](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37656621026), proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, profile
`experimental-source-linked-select-pointer-drop-v4`, patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Constructor/as_mut_ptr/typed intrinsics/narrow pointer drop matrices and14baselines
PASS freshly; S6 has2positive+11proofnegative+22source/MIR/pin negatives, all on
intended obligations. All19 independent NORMAL controls reject exactly beforeproof,
including oldreceiver26→23. Full source/typed method+actual MIR/runtime/normal-unwind
CFG correspondence preserved; diagnostic37649244205 is not a proof. Five extra
stock ghost locals/blocks and every annotation coordinate are in the design table.

Actual baseline still lacks initialized payloadcell. Stock-projected actual enters
proof after full36/19 admission and checkedmethod redirect. Both stock opens, proof
condition split, retained runtime drop at verified/lib.rs60 and both closes61/62
pass in the recorded prefix. Next blocker: verified/lib.rs63 `mem::forget(guard)`,
frozen std/lib.rsspec420:41–42 requires nominal
`<DropOnPanic<*const Element>>.own(t, guard)`, absent. No guard/forget extension;
STOP at this exact obligation. Current classifier stays INCONCLUSIVE with heuristic
kind intrinsic_select; rawlog establishes the forget guard-own failure separately.
Finalreturn/leak/fullnormal-unwind posts not reached; wholehelper/sort4 NOT PROVEN.

Checked method and ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence and frozen stock frontend ghost substitution.
Existing initializedcell/fullpointervalue/thread/independentframes required, no
Element rights. Recursive free stub is not a runtime-body theorem. Runtime std,
signatures/targetcontract unchanged; broader04d67f4b/Drop/guard/forget/assume_init/
union/refiner/kernel/memory/alias/provenance stay frozen. Further semantic work
requires a separate owner decision; no additional dispatch authorized at this stop.
Budget **3954/5400 summed hosted jobseconds used;1446remain**, same budget/noreset,
noactive. Last two proof orchestration jobs:37654585346=184s,37656621026=202s.

### Actual stock projection: accepted drop prefix and next stop

Let Ptrue/Pfalse be the complete modeled pointers returned by the two checked
as_mut_ptr calls (38/39), equal to their existing wrapper receiver addresses.
Constructors22/23 supplied each wrappercell with inner=some(true_val/false_val).
Stock open_MaybeUninit(40/41) consumes `*self |-> wrapper` and produces
`*(self as *T) |-?-> wrapper.inner()`. Here inner=some(value); frozen
`points_to<T>(p,value) = points_to_<T>(p,some(value))` supplies the initialized
payloadcell, without Element ownership or an assumed storage bridge.
The checked second pointer intrinsic establishes
`drop = condition ? Pfalse : Ptrue`, preserving the full modeled pointer.
The proof condition split59 makes the selected existing cell available at that
exact receiver; the other payloadcell and existing thread/reborrow resources frame
it. Drop req115 is `thread_token(t) &*& t == currentThread &*& *slot |-> value`;
post118 returns the same fullvalue/cell/thread, unwind121 is false.

Rawlog lines331–365 records both opens returning, split59, actual drop60 call
checking, auto-close points_to at prelude_core213 and consumption retry at
verified/lib.rs115:55–58, then continuation and both ordinary stock closes61/62.
These closes consume initialized cells and restore wrappercell=MaybeUninit::new(value).
This is the verified call-prefix result. The log does not print per-branch heap or
condition valuation; no claim of complete path/unwind/return/leak coverage follows.
Actual method body later in this file was not entered before failure; acceptance
rests on its fresh same-profile component proof plus exact certified redirect.

Next call63 `crate::mem::forget(guard)` reaches stock generic req420
`thread_token(?t) &*& <T>.own(t,value)` and fails its nominal guard own:
`own(select_unpredictable::DropOnPanic_type_info(pointer_typeid(Element_typeid)))(t,
mk_select_unpredictable::DropOnPanic(get_select_unpredictable::DropOnPanic_inner(
mk_select_unpredictable::DropOnPanic(__result1))))`.
A pointer own predicate for inner does not supply this aggregate own predicate.
This is the exact next blocker, not a failure of drop, and not a generic memory
impossibility theorem. STOP; guard/forget semantics remain frozen. Existing JSON
classification INCONCLUSIVE / kind intrinsic_select retained verbatim; the exact
rawlog obligation is reported separately. Final intrinsic/assume_init/return and
whole normal/unwind/leak contract remain unproved.

S5j historical correction from [original logs37621751848](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848):
readonly export/decode0, refinement1 `RawPtr: not yet supported`, bb1command4
original25/verified33; normalpreprocessing separately after-tailghostclose failure.
Earlier successful-refinement claim withdrawn; no readresource/ownership conclusion.

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
