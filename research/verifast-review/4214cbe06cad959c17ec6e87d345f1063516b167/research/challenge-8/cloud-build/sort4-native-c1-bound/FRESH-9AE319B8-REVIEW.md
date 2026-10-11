# Entry-bound cause confirmed on fresh frozen controls

Build9ae319b8-7f82-4045-818c-ef654567f57f, proof=infra
b81f1c3ccce23e0b5e2a029350c0a6443b929747; diagnostic collector SUCCESS,
verification_accepted:false. Create2026-10-11T01:11:11.187097637Z→
finish01:17:04.716959Z,354sec. Archivef23156ad5744bace48a0dd1c36b4eae7a2e05c672787331539644298fdc70466;
archive/manifest/every artifact and text-log index/chunks integrity verified.
Config13ca3f51b8a97b97105bfd86aa9854aeec2e8740723ece8b8b81c8d3cd33ddc5;
source-inputc511986a7fead8b7b75adff476d8acd053ed0c74e73c411ee5871a112dd242ba.
No general semantic change; frozen C4 console8d686fef29ae6fe5b6adb91a946ff9942aef682baf934b273cc61d71a625527b.

## Target and negative controls unchanged

Nativepositive stillVF1 dead228,2. Diagnostic reader again identifies only
physical203, postlist138/ordinal256 Goto63 afterLabel3, originalroot131,
noEXEC203;202/204 at same printed position execute. All six source/original/
fullnormal/fullreadonly/pre/postAST bytes equal009 and3521. All8 source pairs
immutable and paired exports/decodes/refinement pass before verifier.
False-normal226 and mapped false-unwind210 fail Cannot prove false after the
same native cleanup. Default-off strict entry172 and four admission refusals
remain exact. No guard/path/check is deleted; full reached normal, directC1
unwind and len<8 native posts/unit/free/leak remain as in009. Zero path remains
excluded, so nativeC1 INCOMPLETE and connectedC4 NOT_RUN.

## First constraint: entry array_inv, before calls and body

The two callback-free controls add first-body ghost assertion
`assert std::mem::size_of::<T>() > 0;` before `let len=v.len();`. This is a
proof query, never an assume and never a change to the actual native target.
Both retain runtime sizezero return and len>=8 branch. Original runtime source
hashes match009 exactly; verified sources gain only the ghost obligation.
Normal/readonly full-MIR decode/export and refinement pass in both cases.

Without scratch, verifierexit1 at(5,41–42): Cannot prove0<sizeof(T_typeid).
No len/size_of runtime call is executed before this refusal. With unused
nativeMU scratch, the first query passes, runtime len and size_of then execute,
and the retained zero-route return remains dead(13,2), verifierexit1.

Exact with-MU verification.log ordered events (lines refer to saved raw log):

| Log line | Event |
| --- | --- |
| 2356 | Starts verifying generic callback-free target |
| 2404 | Produces scratch native precondition, Applying autolemma |
| 2413 | array_inv post at prelude_core.rsspec257,104–106, preparing MU size term |
| 2414 | Redux: Axiom std::mem::size_of_MaybeUninit triggered |
| 2415 | Redux: Axiom std::mem::MaybeUninit_size_limits triggered |
| 2416 | Assumes ptr_len(scratch)*sizeof(MaybeUninit_type_info(T_typeid)) <= isize::MAX |
| 2558–2562 | First body ghost assertion: query0<sizeof(T_typeid), succeeds |
| 2563 / 2568 | First runtime len preparation/call, later than bound |
| 2595 / 2600 | Runtime size_of preparation/call, later than bound |
| 2819 | Retained zero path dead-code refusal(13,2) |

This directly observes both named triggers during **native entry production**,
not a conjectured effect of len/size_of or callback/type binding/CFG. The frozen
axiom body in verifast1.ml6519 is quantified over struct type arguments and
requires positive MU size; stock size_of_MaybeUninit523–525 equates MU and T
sizes. Together they entail Tsize>0 before body execution. In the actual native
C1 log verbosity4 does not name these triggers, but the identical native scratch
array_inv introduces the same MU size term before calls (see009review); the
unchanged generic model and callback-free pair isolate the causal chain.

## Diagnostic pins and interpretation

No logging patch is used by the model controls: they use the frozen C4 tool.
The native target adds only physical-node logging, with original dead-map logic
and exit preserved. All kernel/translator/RSSpec/refiner/proof std pins retained.
This is a localized limitation of this **existing frozen MU/struct layout model**.
It does not establish generic ZST support or a blanket defect in VeriFast.
Generic T/native source array alone does not imply positive size; the additional
MU native resource does. Source-specific binding/CFG repair cannot undo this
axiom chain while preserving native opaque scratch and all required branches/
checks. A general model/layout/semantics repair needs separate maintainer scope,
rationale, trust/admissibility review and regression gate. No such implementation
is authorized here. See ZST-MODEL-BLOCKER.md. No C4 extension attempted.
