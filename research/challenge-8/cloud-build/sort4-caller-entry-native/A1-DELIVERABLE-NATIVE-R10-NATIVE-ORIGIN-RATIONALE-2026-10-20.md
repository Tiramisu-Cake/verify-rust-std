# R10 rationale — bind the native small_sort body to its impl source origin

## Observed defect and applicability

The accepted R10 S1 run reported two body-bearing `Ast.Func` declarations with
the same exact name, `<T as StableSmallSortTypeImpl>::small_sort`, at
`verified/lib.rs:50:5` and `verified/lib.rs:68:5`. Both had `body=Some`; the
existing name-and-body filter therefore correctly failed closed, but could not
identify which implementation body belonged to the current serialized
`TraitImplItem`. This is an actual source-selection blocker, not evidence that
either candidate is the intended implementation.

At pinned VeriFast commit `f76012fb518703b1d98e243ac4f487f16877cfcb`,
`TrName.translate_def_path` is identity. The compiler's serialized display path
does not distinguish these two generic implementation bodies, so comparing the
`TraitImplItem.defId` text with `Body.defPath` is necessary but insufficient.
The existing `vf_mir.capnp` payload already retains `TraitImpl.span`,
`Body.span`, `Body.impSpan`, `Body.fnSigSpan`, and `Body.isFromExpansion`.
`translate_body` uses the translated `Body.span` as both the generated
`Ast.Func.loc` and `VF0.debug_info_rust_fe.id`; `translate_program` preserves
Body/result order through `ListAux.split3`. Pairing the serialized Body and
debug record before declaration sorting therefore carries compiler-origin
metadata to the exact generated declaration without adding a schema field or
matching on coordinates alone. The origin list is passed as a lexical partial
application to the existing prototype helper; it is not stored in mutable
process-global selector state, and the C-patch call-site context remains
byte-compatible.

## Bounded selection and preserved controls

For `StableSmallSortTypeImpl::small_sort` only, retain an origin sidecar for
each serialized Body: exact `defPath`, translated full body location, full
`impSpan`, full `fnSigSpan`, and expansion flag. Within the current compiler
`TraitImpl.loc`, require exactly one non-expansion Body whose exact path matches
the item's `defId`, whose regular same-file body/implementation/signature
spans are all contained in that impl span, and whose translated body location
equals its paired debug ID. Then require exactly one body-bearing
`Ast.Func` with the existing exact name and the full matching location.
Missing or multiple origin records, malformed/dummy/quoted locations,
empty-file or non-1-based locations, expansion bodies, cross-file or
out-of-impl spans, and missing or multiple AST declarations remain hard
errors. Once both unique joins succeed, a bounded escaped diagnostic reports
the selected compiler path, Body/implementation/impl locations, candidate
counts, and body kind. This records selection identity only; it makes no proof
or conformance claim. The selected declaration still passes the
existing compiler item/impl-name, generic and lifetime role/count, Sized-bound,
native result and input-shape checks. Trait-required declarations,
preconditions, normal and unwind posts, equality/refinement criterion,
conformance, C patch, and source transitions are unchanged.

## Static controls

The patch applies only to the exact R2 translator output pinned by the active
manifest. Validate the new R-only source digest, then apply the unchanged C
patch and confirm the final digest. Historical R9 evidence and profile bytes
remain immutable; the active manifest identifies R10. No local compilation,
extraction, preparation, decoder run, proof, verifier, or Cloud operation is
part of these source-only checks. The new selector remains experimental until
its exact compiled source is exercised in the authorized Cloud target and the
existing native-interface and conformance controls pass.
