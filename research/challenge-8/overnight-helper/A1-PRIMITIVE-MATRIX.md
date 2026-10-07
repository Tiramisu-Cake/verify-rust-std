# A1 pointer transmute primitive matrix — BEFORE

2026-10-08, after O4 full typed MIR review. This is an experimental gate for
the exact updated `core::mem::transmute_neo` body specialized to
`MaybeUninit<*const Element> -> *const Element`, not a generic proof or a
call-linkage certificate. The updated source SHA, union/direct-field layout,
compiler intrinsic signature and nounwind attribute are pinned by
`prepare-assume-init-2610.py`.

Obligation: `const { assert!(Src::SIZE == Dst::SIZE) }; unsafe {
intrinsics::transmute_unchecked(src) }`. The trusted primitive correspondence
is restricted to a plain MIR local Move whose decoded local declaration is
exactly `MaybeUninit<*const Element>`, into a typechecked argument of the
same type, with `inner(src)=some(p)` and its
pointer-only own predicate. It returns the same complete p, including
provenance, raw-pointer own, current thread and no unwind. It grants no
`Element` cell. The const size check is part of the exact source/MIR path;
the physical union/transparent layout equivalence remains a source-pinned
compiler-to-model assumption.
The spec function returns VeriFast's normal `fn_outcome<*Element>`; lowering
uses `result_of_outcome`, justified by its false unwind post, to produce the
MIR cast's pointer-typed value.

Positives: exact local body under symbolic initialized pointer, and the same
body with an independent mutable frame; both require full return, leak,
dead-code, NORMAL/readonly MIR and refinement. No call to the still-unproved
external `std::mem::transmute_neo` is used. Negative proof obligations are:
`none`/unknown inner at primitive pre; false or wrong complete-pointer post;
lost/duplicated frame or thread at leak/post; attempted `Element` points-to
at post without a precondition right. A negative only counts if the expected
function, source line and predicate fail after successful export/refinement.

Admission/typing controls must reject source/body/layout mutations, changed
full MIR graph, cast kind, changed result/pointee type, non-MaybeUninit source,
mutable-pointer source, Box source, Copy and any projection. The minimal frontend leaves exporter
unchanged: destination, cast kind and plain Move are checked structurally;
the per-body local-declaration lookup enforces source ADT, const mutability
and matching Element, while the generated primitive's typed input is an
independent check through VeriFast's normal typechecker. A typecheck failure is a
successful control, not a proof negative of the actual std body. Any setup
or unrelated failure remains INCONCLUSIVE. Until all relevant controls and
the cumulative S6 regression pass, this component is experimental.

The candidate also explicitly rejects remaining generic const-pointer
transmutes after the stock BoxAsNonNull special case. Such rejection is an
admission control, not a proof failure. The hosted classifier remains
provisional until the exact emitted error location and predicate are reviewed.

Outcome mapping: a missing trusted primitive or patch/build failure first
requires repairing that exact application; it proves nothing about the cast.
A positive full-verifier failure at the primitive precondition requires
checking the S6 ownership predicate and exact typed argument. A positive
dead-code failure requires inspecting a synthetic unwind or unused function,
with no global check suppression. A proof negative at an unrelated
obligation is inconclusive. If a changed-source, wrong-type or Box control
passes verification, reject the primitive design rather than accept the
positive. Only after the full direct matrix and cumulative regression can
the pointer-specific compiler correspondence be accepted separately;
`assume_init` and actual helper linkage stay open.
