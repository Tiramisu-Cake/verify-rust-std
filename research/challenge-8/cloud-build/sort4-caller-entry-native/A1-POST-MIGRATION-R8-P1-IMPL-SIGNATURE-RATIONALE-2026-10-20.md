# R8 P1 actual-implementation signature specialization

The S3 R-only Build reported `No such type parameter: Self` at
`verified/lib.rs:35`, on the required `small_sort` item. Its bounded source
evidence bound that line to the generic `StableSmallSortTypeImpl` signature.
The required trait prototype preserves its `Self` binder. The pinned R2
translator additionally generates an impl-specialized prototype, removes
`Self` from that prototype's generic binders, but retains `Self` in its
signature types; its `LetTypeAsn` binds `Self` only inside the precondition.
This is the source-supported defect and applicability. The Build result is a
frontend failure, not a proof result.

The authorized correction is limited to the exact
`StableSmallSortTypeImpl::small_sort` compiler item. The translator will keep
the original required signature and contract as the prototype source, find
the unique actual implementation `Ast.Func` by the compiler item `def_id`,
and validate its generic/input/result shape before specializing the required
signature's `Self` references to its declared impl type parameter `T`. It
requires five distinct actual binders in `T, F, lifetime, lifetime, lifetime`
order, matching `F` bound role and three lifetime positions; lifetime names
are alpha-renamed positionally. It requires a const-wrapped first `&mut [T]`
input, exactly three inputs, and an `fn_outcome<unit>` result. `T` is added with its actual
implementation bound; the original required method's `F` and lifetime
binders and their names remain intact. The existing
precondition continues to carry the required clauses and postcondition; its
`Self` type binding and type-id use `RealTypeParam T`. The historical
`<self_ty as trait>::item` prototype name remains, and must equal the matched
compiler item's translated body name. Missing, duplicate, or unexpected AST
shapes fail closed.

This does not parse `self_ty`, synthesize a signature from actual inputs, or
weaken native-interface, contract, compiler-identity, source/MIR, proof, or
negative-case gates. All unrelated trait and item paths retain the existing
behavior. The immutable R2 patch and R7 profile remain unchanged. The new
overlay is SHA-bound after R2 and before the R-only reference build; the
unchanged C overlay is then based on the resulting R source map. Kernel,
schema, exporter, compiler, standard library, toolchain, and R2/C guarantees
are unchanged.

Validation before any target run is a fresh R-only build followed by the
existing native-interface/source gates and focused controls: both certified
implementation bodies must bind the common required prototype; the original
negative controls must still fail for their intended predicates; and the
target source may proceed only if the P1 frontend error is absent. Static
overlay and manifest tests establish only the pinned source transition and
fail-closed metadata handling. No local compiler, proof, or proof acceptance
claim is made here.
