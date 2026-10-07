# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: S6 pointer drop only**, explicitly resumed by
owner from bea6248. Prior freeze lifted ONLY for checked pointer method + trusted
compiler glue rule at payload *const Element, receiver *mut *const Element.
Design/trust review: SORT4-SELECT-POINTER-DESIGN.md S6 authorization section.
Budget continues **2736/5400 used; 2664 summed hosted job seconds remain**;
<=1800/job, <=300/proof, one relevant hosted Actions run at a time. S6 run37637630477/source de7ed9de861eea7346301f6807e242862a68c0ab completed;
194jobseconds14:33:07–14:36:21UTC. Budget2592/5400 used;2808remain,noactive.
S6 implementation profile experimental-source-linked-select-pointer-drop-v1,
patch cd660fe9f470293cc16712a4a71714c8f5f6e802608cedb5b486c3d8a1d27413,
full2+11proof/22admission matrix collected independently. Proof positives VF0;
all13 classifier INCONCLUSIVE due unsafe/SAFE gate and exact diagnostic/location
mismatches;22admissions:16classified PASS,3reason-only mismatches,3setupfailures.
Ctor/asptr/intrinsic/full14baselines PASS. Actual NOT RUN (component gate).
Next: sameprofile saved replay, NEW3fixed admission controls, then actual only
after composite fullmatrix acceptance. No semantic change planned.
Completion37640750987/source dbb70d0 completed144s14:55:22–14:57:46UTC:
build/classifier checks PASS, replay module SyntaxError144 before replay/actual.
Harness-only syntax repair + hosted preflight ready; no active run. Budget2736,
remaining2664; next NEW source run uses unchanged cd660fe9/drop-v1.
Full S6 independent matrix and accepted-component regressions precede actual
integration, then STOP at initialized-cell precondition or next actual blocker.
04d67f4b/assume/guard/forget/general Drop/memory/refiner/kernel remain frozen.

Previous checkpoint (historical freeze superseded ONLY for S6):


Updated 2026-10-07. **IN PROGRESS: [source-linked pointer select completion](SORT4-SELECT-POINTER-PHASE.md).**
Entry `cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09`; new budget
**2398/5400 summed hosted job seconds**, <=1800/job, <=300/proof. No active run.

Accepted: O4 pointer-value model/SAFE constructor, S4b SAFE `as_mut_ptr`, and
S5k typed intrinsic rule at frozen `experimental-source-linked-select-pointer-intrinsics-v2`
/patch `7bb39a84`. S5k/37624082376, source
`128dd5673c7796c5916017ab4afafaeea8d836b8`: all6 positive+10 intended proof negatives
+40 exact admission controls PASS; classifier60 gate+10 wrong-result+28 admission
message mutants PASS; full ctor/asptr/14Rust/C/C++ regressions PASS. S5k was dispatched
before the user's replay-only correction. New semantic extensions now FROZEN;
04d67f4b assume diagnostic patch and unfinished controls are NOT RUN drafts.

Actual intrinsic-on helper source/export/decode/refinement/full31local14BB MIR
certificate PASS; all3 intrinsic calls translated, both ctor/asptr redirects reached.
First proof blocker: `verified/lib.rs(57,9-29): error: No such function:
std::ptr::mut_ptr::<impl *mut T>::drop_in_place`. Whole helper NOT PROVEN; translation
of third intrinsic is not proof execution of its later branch. Drop/forget/assume
remain unaccepted. No ownership/provenance semantic stop has been established.

Independent diagnostics: pointerdrop method fails its stock unwind post; assume-init
S5j invalid ghostclose after Rust tail expression (body NOT entered); corrected
S5k readonly export/decode pass but normal refinement fails `RawPtr: not yet supported`
at bb1 command4, original25/verified33. VF separately rejects local union declaration
`Todo: AdtDef::Union`. These setup/applicability failures do not test read permissions
and do not gate intrinsic acceptance. Refiner and kernel unchanged.

S5r2 replay/37626031885, classifier source
`586c9ae4155a3ad0d3c50ebed2d22d9716a80b4f`, PASS: saved S5j source2454e86,
frozen7bb/v2 only; all3839 manifest entries verified and all6+10+40 reclassified.
Exactly8 reason-only admission corrections; original INCONCLUSIVE classifications
and byte-identical source artifact retained separately. Corrected classifier
60+10+28 plus16 stage/certificate checks and36 replay mutants PASS. No build,
exporter, refiner or proof execution. No evidence transfer across semantic profiles.
[Replay run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885),
[compact replay3.7MiB incloriginal S5j+O4](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37626031885/artifacts/11483952705).

Current checkpoint: requested intrinsic acceptance/replay and actual integration
complete; whole helper remains unproved at drop_in_place57. Further semantic
extension temporarily FROZEN per owner; drafts saved, no new assume/drop rule applied.
Budget **2398/5400** used, **3002 seconds remain in this phase**, no active/queued run.
No automatic continuation of Drop/assume semantic work while this freeze applies.
Runtime/std signatures, kernel and refinement semantics unchanged.

[Latest run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376),
[compact evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482879763),
[full evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37624082376/artifacts/11482659442).
Each compact includes O4/37601511894 with byte/hash mapping; original/full O4
preserved. [Design](SORT4-SELECT-POINTER-DESIGN.md),
[results](SORT4-SELECT-POINTER-RESULTS.md). Runtime std/signatures and frozen
kernel/general memory/provenance/aliasing/export/refiner remain unchanged.
RAPx CLOSED / NO-GO; B/C NOT RUN; full sort4 out of scope.

The previous closed phase below is historical, not the current authorization.

Updated 2026-10-07. **CLOSED: [pointer ownership phase](SORT4-POINTER-OWNERSHIP-PHASE.md)**
at the dependent actual callee's storage/borrow boundary.
[Final report](SORT4-POINTER-OWNERSHIP-RESULTS.md).
Entry `e0920ecb07cd05ef08acd6fb5a2fb228af9a1f98`; proof source
`182ddf29dc73961723bf32be6b65643c524ca927`.
[O4/37601511894](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894),
[artifact11473086721](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894/artifacts/11473086721),
profile `experimental-source-linked-maybeuninit-pointer-own-v2`, patch SHA256
`325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d`.

**Experimental pointer-value model and SAFE MaybeUninit::new ACCEPTED:**
explicit defined own, checked introduction lemma/body, generated safety prototype,
exact inner/token, no unwind, frame/return/leak; no pointee premises or Copy bound.
Full source/HIR/typed MIR graph certification and all5proof/8source/9MIR controls
PASS. Nonpointer opaque ownership retained;5classifier groups and14 separate
stock/experimental Rust/C/C++ baseline controls PASS. Optional feasibility mode
cannot accept; O4 uses complete acceptance. Runtime std/signatures unchanged.

**Actual select RUN / INCONCLUSIVE:** unchanged N6 source-linked pointer body,
all source/export/decode/refinement gates PASS; SAFE prototype and both constructor
calls at22/23 reached. First remaining blocker:
`No such function: std::mem::MaybeUninit::<T>::as_mut_ptr`, adapter38,20–41.
[Exact reproduction and limitations](SORT4-SELECT-CALLEE.md).
Storage/reference/provenance permissions require a new capability decision;
no alias/borrow/general union/copy/FnMut/Drop/unwind expansion implemented.
Final selected-pointer/frame/no-unwind posts and full sort4 NOT PROVEN.

New budget **518/5400 summed hosted job seconds (8m38s),4 NEW runs**,
<=1800/job,<=300/proof;4882s retired at boundary. Previous budgets not transferred.
No active/queued relevant Actions run; no pending implementation draft.
Final closeout is documentation-only, separately committed/pushed from proof SHA.
Next permitted action: read-only review/documentation. New implementation or
workflow dispatch for as_mut_ptr needs a separately approved named phase.
RAPx remains CLOSED / NO-GO; B/C NOT RUN. No upstream PR/messages/submission.

Earlier accepted components remain separate: stock H_align, index permutation,
rank stability, finite-SWO bridge, scalar ranges ([night report](SORT4-NIGHT-RESULTS.md));
pure SWO composition and exact fieldless layout d4a12525 full matrix
([previous closeout](SORT4-COMPOSITION-CONSTRUCTOR-RESULTS.md)). None supplies
callback/resource/unwind composition or a full Rust sort4 theorem. Their original
source/run/profile identities and failed controls remain in those reports and
EXPERIMENT-LOG. Historical "next" statements do not authorize further work.

Current S5g/37619961051/source53f4d94/ec841d1c: canonical patch audit PASS,
build fails on unannotated decoded guard_type record (`kind` field). No new proof.
S5h adds only D.ty annotation and canonical regeneration; complete matrices
and actual/source-linked read diagnostic remain required. No active run.

S5h/37620410162/source634de56: build fails decoded UInt128 conversion on
cleanup bool switch. S5i uses existing schema-reader conversion, patch7bb39a84.
All numeric APIs reviewed; no new semantic rule. Four independent ghost-only
storage probes added (cast initialized, union initialized, cast none/unknown);
source-linked assume_init export remains separately NOT PROVEN. No active run.

S5i/37621093604/source3d822b0/7bb39a84: build/ctor/asptr regressions PASS.
Pointer-drop body reaches stock unwind post `Cannot prove false` at10.
Assume export requires missing transparent_unions crate feature; admission and
ghost matrix NOT RUN. S5j fixes feature only and collects independent diagnostic
stages without preventing component matrix; any diagnostic setup failure retains
nonzero overall exit. No semantic change; no active run.
