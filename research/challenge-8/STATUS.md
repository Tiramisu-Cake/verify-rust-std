# Challenge 8: current checkpoint

Updated2026-10-07. **IN PROGRESS: [source-linked pointer select completion](SORT4-SELECT-POINTER-PHASE.md).**
Owner opened NEW phase atcd44e1bbf115c83c84fd7d4c050b1f74be0e1d09.
New5400jobseconds,<=1800/job,<=300/proof;spend415/5400jobseconds,noactive. Old budget retired.
S3/37610022772/source489416d21b52858b124638d88180378ef2b4b8d0,
newasptrprofilee9b4d025: fullconstructorregression+14baselines/classifiers PASS;
3SAFE/body/frame/state positives+5proofnegative PASS. SixthNone→Some rejection
atpost24 correctlyreached butwrongclassifiermessage; INCONCLUSIVE preserved.
17admissioncontrols andactualintegration NOT RUN, component UNACCEPTED.
Spend415/5400jobseconds,noactive. Compact11477915575 (O4/currentmanifest),
full11477880702; historicalfullO4 preserved. Current S4exactmessagefix+message
mutants thenfullacceptmatrix and dependentactual ifaccepted; nosemanticchange.
[Design](SORT4-SELECT-POINTER-DESIGN.md),[results](SORT4-SELECT-POINTER-RESULTS.md).
Runtime std/signatures and frozen kernel/
memory/alias/provenance/export/refiner unchanged. Narrow spec/translator changes
for listed pointer operations authorized after written component design.
[Design](SORT4-SELECT-POINTER-DESIGN.md),[results](SORT4-SELECT-POINTER-RESULTS.md).
Unsupported names do not stop this phase; forbidden general semantic extension
needs precise reproducer and evidence. Fullsort4 outside scope;RAPx CLOSED/NO-GO,
B/C NOT RUN. Previous phase summary below is historical and superseded as execution
checkpoint; its accepted constructor/profile identities remain valid.

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
