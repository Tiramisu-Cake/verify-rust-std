# O17 recovered evidence and exact tested profile

Proof `11d888ba8ff2231a80c759148194aa9ae6b9d30e`, [run37717092130](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37717092130).
Hosted job113115950593,02:16:55–02:20:49UTC,234seconds. Ledger3094/21600,
no active run. Prior CI window expired06:30UTC; new CI needs explicit extension.

No full actual select_unpredictable or sort4_stable theorem. The unchanged actual
pointer helper has a checked source/MIR prefix through constructor/as_mut_ptr/
typed intrinsics/drop, then stock forget needs nested nominal ownership. New
owner projection is a distinct unqualified ghost inventory and does not reuse
that prefix certificate. Original generic/ZST/fat-pointer coverage is not closed
by the pointer-specialized local diagnostic.

## Proven local bodies versus acceptance

| Obligation | O17 evidence | Remaining boundary |
| --- | --- | --- |
| Local nominal DropOnPanic<T> | Constructor/u32 witness, generic pointer callee, SAFE Drop normal AND unwind return/leak, ordinary Drop fullVF0 | Full source/ADT/typed-MIR/template-post mutation matrix, actual nested DefPath linkage |
| Checked completion lemma | FullVF0; false/pointee-right/thread-dup/wrong-pointer posts reject at11 | No actualbody composition; raw_ptr_own is definitionally empty |
| Marked generic callback | Actual unwind recovery/full current T/F/thread post/leak;3intended unwind negatives and4admission rejects | Normal call96 FnOnce::Output/bool; fullHRTB/resource/alias/CFG controls |
| S6 primitive families+CFG | Fresh complete8stage regression allaccepted; independently accepted earlier | New combined frontend semantic stack remains experimental |
| Actual sort4 first FnMut | Checked4cell split/stock sharedref/Args preparation+realcall | Unwind cannot restore source array; complete normal dst, all5calls, generic/ZST, functionality |

H2b method/drop owner requires initialized target cell plus exactly one current
T.own. Generic destruction consumes owner/value, returns optional storage only on
both outcomes. No arbitrary guard.own=true, no Element permission, Copy/Freeze/purity
or nonpanic restriction. Callback posts preserve current cells/owners, allow legal
interior mutation, and never assume values unchanged.

## Exact applied patch order

Paths relative to research/challenge-8. Inactive G1call-CFG, H2c admission, HRTBoutput,
strictlifetimecut, and source-only safetyproof/linked-owner drafts are **outside** this
profile. Committing a draft is not activating or verifying it.

| Patch | SHA-256 |
| --- | --- |
| overnight-s6/verifast-s6-26.10-candidate.patch | `20f7d07ac9bdaca7c46f737b89925dfac3f4cef66c3f5d48aa9634ac949dbc1c` |
| verifast-manuallydrop-new-cfg-2610.patch | `593d09405379974ffbc475c2e0b65d648d8a6913f55b765dd0c3bebdc0922781` |
| overnight-helper/verifast-a1-assert-inhabited-26.10.patch | `b3fdae6588c5d88a5151f9b103b2f5ab6d2d58db880955a1b975a7f88ca2feb9` |
| overnight-helper/verifast-a1-pointer-transmute-26.10.patch | `44b460e64eede02bb7776ef36c6be12eb2bed2e5a4fd37ad9b733c7b5633c8ab` |
| overnight-callback/verifast-tuple2-own-26.10.patch | `84b58b71bfb65ac2bfac1a63d181239001cf0a7ffba3f8bfb5d5b0f1d3a640da` |
| overnight-helper/verifast-a1-transmute-linkage-26.10.patch | `40fb77888c9b907f150d32f9d85769512cad9c57bb0b14f9c9dbd593fc44c0e7` |
| overnight-guard/verifast-h2a-generic-guard-link-26.10.patch | `4a36239b68dade6aa486e4bccedf77e92f4104278456d1c568c58d28efa18a7a` |
| overnight-callback/verifast-callback-unwind-26.10.patch | `61d7525cc8ff3e6e9c736ea00178c002f071b521c78845bf68d0e4890e2be07a` |
| overnight-guard/verifast-h2b-nominal-drop-template-26.10.patch | `c9afb4bfd696efc38f2bc71e10463a34170d9d769e851a07388c01278e99b2ff` |

Console0495b7e5f49048707e3256ad2c7d6b0a532178ec8cc4380898a034281fc3d514;
translator2472f5ecfb65ba01ffb934f6cf9ef94f77380ca396b444413ad5c92181319535;
parser7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2;
stdspecd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf.
Base VFf76012fb, compiler nightly2026-09-25f7575a9d, stdcd371e03.
Stock exporterb00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796,
refinerb049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28,
schemaf48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469.
Full binary/dependency/source identifiers in run artifacts/environment and experiment log.

## Trust and open checks

Compiler/source correspondence for ManuallyDrop identity/destructor suppression,
pointer layout and typed glue remains trusted; full actual compiler glue is not
verified from runtime body. Existing stock primitive/prelude/borrow models remain
trusted dependencies. S6/A1 typed source gates and H2 selected SAFE template are
new frontend assumptions checked by admitted body proofs, not a kernel soundness
proof. Exporter/refiner unwind TODOs are explicitly retained; refinement PASS is
not independent unwind semantics validation. O17 has no new verifast.ml change.

H2b local positive and source/resource negatives do not close all MIR applicability
or layout representations. `retains_initialized` original class INCONCLUSIVE is
preserved: optional-vs-initialized points_to auto-close fails prelude_core213 from
callerpost25; future classifier replay must match that actual obligation.
HRTBoutput and strictlifetimecut introduce distinct new trust if activated later.
No checked lemma or trusted primitive asserts the actual helper/sort4 theorem.

Continuation: finish H2b boundary controls, capture complete linked owner unit
before new actual-source admission, qualify same-unit callees before redirects,
then prove helper full normal/unwind/return/leak and separately sort4 safety/SWO.
