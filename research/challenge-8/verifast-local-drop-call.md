# Experimental local Drop call

Current hosted status: run37433028854 passed all 25 regressions, the
exact-source actual Drop body proof, and `cleanup_one` with VF/refinement0.
`cleanup_callback` failed before its body with a frontend declaration-order
error. A separate [local-declarations patch](verifast-local-decls-first.patch)
now moves existing local declarations ahead of generated projection-equality
registrations; no hosted result for that patch exists yet. The following is
not a completed cleanup proof. See [handoff](HANDOFF-2026-10-06.md) for earlier
results.

Apply [verifast-local-drop-call.patch](verifast-local-drop-call.patch) to the
pinned VeriFast 26.09 source **after** the tuple, HRTB, lifetime-cut,
address-taken, and tracked `ManuallyDrop` patches. Its translator input
SHA-256 is `f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432`.
The current patch SHA-256 is
`6f5c2089b16364bc3d33eb98724fef60b5da4022bc70e77eb778b563eadb26ed`, and its
statically applied translator SHA-256 is
`53fdb2ae74f66fd40efc9c60f633cfc159a2b84c2201979000572821d253da37`.
The patch changes only
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml`.

An explicitly annotated, actual `Drop::drop` body in the same exported MIR
unit opts its ADT into this route. Its parsed contract must include a
normal postcondition and literal `on_unwind_ens false`, with no
`assume_correct`. The method body and contract are still checked by the
ordinary whole-unit verifier. A bare-local MIR `Drop` calls that exact
method through its real callee name, concrete type argument, and inferred
late-bound self-reference lifetime, matching ordinary method-call
instantiation. The existing
call-outcome switch sends normal execution to the MIR target and retains the
MIR unwind action, including cleanup and terminate, as a fail-closed AST
branch. Because the selected method's literal false unwind contract is checked
in the same unit, its unwind target is excluded only from *structural*
reachability used to reconstruct blocks and report dead code. A cleanup block
also reached by a genuinely unwinding call remains reachable. The old generic
`std::ptr::drop_in_place` translation remains for unannotated types and
projected places. `DropData` does not export a projected place type, so
this scoped feature makes no specialization claim for those places.

The specialization requires one ADT type argument, exactly one impl type
parameter, the compiler's sole `T: Sized` impl predicate, an exact matching
`Drop` impl item and same-unit method signature, and exactly three
physical struct fields: `src: *T`, `dst: *T`, `len: usize`. The two raw
pointer fields and integer field have trivial field-drop glue. Identical
exporter duplicates of one impl are deduplicated; conflicting matching
records fail closed. Unsupported annotated definitions fail at the Drop
site. A raw local-type table exists only for the translation of one body.
No schema, exporter, parser, kernel, prelude, runtime source, or generic
signature changes.

The method is invoked using its **proven explicit precondition**; the
translator creates no `CopyOnDrop.own`, `T.own`, `foreach`, token, range
permission, or initialized value. The explicit method postcondition
returns the field chunks and padding plus its proved range resources.
Those field chunks are retained as the ordinary physical guard storage;
their known raw-pointer values may be weakened existentially by a later
checked caller proof, but the patch neither discards them nor fabricates an
uninitialized value. A caller must supply every method precondition,
including its single logical `foreach(T.own)`. The default private
`CopyOnDrop.own = false` is not used as evidence for this call.

This first feature does not release a held reference, establish the guard
invariant, prove the insertion loop, or recover full destination ownership
after the destructor. It also does not specialize projected-place Drops or
general nontrivial field glue. The pinned exporter does not serialize MIR
`replace` on `DropData`; in the pinned rustc this flag is diagnostic
metadata and the exporter sees an already elaborated Drop CFG. A different
compiler/exporter version needs a new shape audit.

Hosted acceptance must check the exact source and translator SHA sequence;
retain all 8 HRTB, 12 lifetime-scope, and 5 tracked-reference regressions;
prove the actual annotated destructor body at the same source version; and
exercise both a normal local-Drop edge and a cleanup local-Drop edge in a
caller. The caller gate must establish exact destination values and one
original `T.own` sequence, while missing range permission, missing
ownership, mismatched/unsupported impl, and a broken actual method
postcondition remain failures. This editing server performs only static
patch checks; compilation and verification belong on GitHub-hosted Actions.

## Generated declaration order after a generic callback

Run37433028854 reaches `cleanup_callback<T,F:FnMut()>` only after its direct
Drop body and `cleanup_one` pass. The compiler exports the non-HRTB projection
`<F as FnOnce<()>>::Output = ()`; the pinned translator emits a ghost
`#register_type_projection_equality` expression before every local declaration.
The local guard is subsequently address-taken by its actual Drop terminators.
VeriFast's existing check requires address-taken locals at the start of a
block, so verification stops before the callback or cleanup. The control
`cleanup_one` has no projection registration and passes.

The separate declarations-first patch applies only to `tuple_local_drop`,
after the local-Drop patch. Its exact input is
`53fdb2ae74f66fd40efc9c60f633cfc159a2b84c2201979000572821d253da37`,
patch SHA-256 is
`ff0dd3b57215990835622209c3e728f00bf5b3520140b5cfede6306be3e0d8e4`,
and expected translator output is
`78bfc6825d3dea4dae2590601f5f63a4f68da0799328684259a48a359ec9a6fd`.
It reorders only the translator's generated preamble to local declarations,
projection registrations, then executable MIR. It changes no verifier kernel,
resource predicates, pre/postcondition or actual Rust source. The source-build
gate records both translator states and still requires exactly the same four
modified VeriFast source files. The hosted gate must establish that dependent
associated-type locals still typecheck and that callback normal/unwind paths
actually reach the proved cleanup; the existing 25 regressions and
`cleanup_callback` are the first controls. An independent projection-local
fixture can follow if that risk is not resolved by their evidence.
