# Challenge 8: current checkpoint

Updated 2026-10-07. **IN PROGRESS: [source-linked pointer select completion](SORT4-SELECT-POINTER-PHASE.md).**
Entry `cd44e1bbf115c83c84fd7d4c050b1f74be0e1d09`; new budget
**1352/5400 summed hosted job seconds**, <=1800/job, <=300/proof. No active run.

Accepted: O4 pointer-value model/SAFE constructor, and S4b SAFE `as_mut_ptr`
body/model at e9b4d025 (3 positives, 6 proof negatives, 8 source, 9 MIR controls).
S5b/37615266238, source `2fb924f02061a00a6e0204ed90145ef8c8f1e912`,
profile `experimental-source-linked-select-pointer-intrinsics-v1`, patch `2cd1a04a`:
constructor/as_mut_ptr full regressions and Rust/C/C++ baselines PASS. All six
intrinsic SAFE/body/value/state/frame positives PASS. Wrong pointer result and
wrong wrapper inner reach intended normal posts; unrecognized exact diagnostics
keep classification INCONCLUSIVE. Eight remaining proof negatives and 40
source/MIR admissions NOT RUN: intrinsic component NOT ACCEPTED.

Actual helper RUN with intrinsic rule disabled: both constructor and as_mut_ptr
calls pass; first remaining error is `No such function:
std::intrinsics::select_unpredictable` at `verified/lib.rs(49,21-92)`.
Whole helper NOT PROVEN. This unsupported name is a next authorized operation,
not a semantic stop. Full 31-local/14-block actual intrinsic certificate is being
implemented separately; it cannot be enabled before complete component acceptance.
S5c/37616835826/source6a9ddc9: all6positive+10proofnegative PASS; firstsource
identity admission PASS, inputtype reaches HIR generic count/kind instead of
predicted source-marker diagnostic. Remaining38 admissions NOT RUN. S5d pins
that exact reason with4 diagnostic mutants and collects all40 independent
admissions after proof acceptance. Same semantic patch, no relaxed gates.
It also exports the source-linked pointer-drop method with the existing stock
free-drop contract, to expose its first cell/no-unwind obligation; no new drop
rule active or component acceptance in that diagnostic.

[Compact S5b](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238/artifacts/11478479176),
[full S5b](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238/artifacts/11478894018),
[run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37615266238).
Each compact includes O4/37601511894 with byte/hash mapping; historical/full O4
preserved. [Design](SORT4-SELECT-POINTER-DESIGN.md),
[results](SORT4-SELECT-POINTER-RESULTS.md). Runtime std/signatures and frozen
kernel/general memory/provenance/aliasing/export/refiner remain unchanged.
Narrow source-linked pointer-operation spec/translator changes are authorized
only after written design. RAPx CLOSED / NO-GO; B/C NOT RUN; full sort4 out of scope.

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
