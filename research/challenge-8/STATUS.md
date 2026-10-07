# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: [source-linked pointer select completion](SORT4-SELECT-POINTER-PHASE.md).**
Entry `cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09`; new budget
**2198/5400 summed hosted job seconds**, <=1800/job, <=300/proof. No active run.

Accepted: O4 pointer-value model/SAFE constructor, S4b SAFE `as_mut_ptr`
body/model. Latest S5j/37621751848, source
`2454e860dc75c277686f3031a311501a3cd2b9e3`, profile
`experimental-source-linked-select-pointer-intrinsics-v2`, patch `7bb39a84`:
full constructor/as_mut_ptr regressions and 14 Rust/C/C++ baselines PASS.
All 6 intrinsic positives and 10 intended proof negatives PASS; all 40
source/MIR admission cases ran. 32 classified PASS; 8 correctly rejected before
proof but exact diagnostic expectations differ. Intrinsic NOT ACCEPTED yet.
S5k corrects those profile-specific exact expectations and adds message mutants;
complete same-profile matrix must pass before actual intrinsic-on integration.

Actual helper with intrinsic rule OFF passes both constructor/as_mut_ptr calls;
first error `No such function: std::intrinsics::select_unpredictable` at
`verified/lib.rs(49,21-92)`. Whole helper NOT PROVEN. Full actual MIR graph gate
is implemented but intrinsic-on execution remains gated by component acceptance.
Pointer drop method reaches stock unwind post `Cannot prove false` (stock generic
drop permits unwind). Canonical assume_init source/export/decode/refinement PASS:
5 locals/4 blocks, assert_inhabited -> union field address -> cast -> read.
Normal VF preprocessing failed on a ghost close after a Rust tail expression;
S5k removes that annotation, retaining exact runtime source and all posts/leaks.
Ghost-only probes are diagnostic, not source-linked acceptance or a semantic stop.
Separate assume_init diagnostic profile is drafted; NOT RUN.

[Latest run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848),
[compact evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848/artifacts/11481774726),
[full evidence](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37621751848/artifacts/11482378240).
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
