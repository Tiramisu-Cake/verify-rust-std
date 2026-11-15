# Slice 03 LAYOUT-RAW — worker15 independent review

2026-11-15. **PASS_STATIC_ONLY; no blocking findings.** Candidate
`d0345ddf4f70d10caf5ee34ddca402867264379e`, tree
`8ac48a5660a94de062919ebcf80fdcdef2cc2f03`, sole parent
`932fb8395a58f8c86c0d702ba2cae835823b2962` (accepted run43701587141).
Input g0 `fc82cfd8b40d653b71ff2b2ba383682bc185165e`. Source was read-only.

## Scope and findings

Reviewed only parent→candidate: five production files, raw_eq documentation row,
and nineteen complete source/golden pairs. Read-only line-part recomposition matches
the candidate, with all22 effective owner3 part hashes checked. The neutral UintTy
minus/plus import pair is needed by this first RawEq consumer; SOURCE-MAP-CORRECTION
keeps that ownership adjustment explicit for extraction4. No storage4, closure5,
E1 or F7 production parts are added. All existing test bytes and flags are unchanged.

- `ty_layout.rs`: Pat propagates current_offset; enum variant field masks are
  compared in enum-local coordinates, then translated by the enclosing offset once.
  Tag offset remains enclosing-relative. Different masks still return the existing
  error. Storage helper and closure arms retain ancestor behavior.
- `ptr_uninit/uninit_visitor.rs`: RawEq checks both reference operands before the
  call, using `[u8; full pointee layout size]`, including padding/union storage.
  This avoids substituting a typed data mask for raw extent. Layout/array construction
  failure emits explicit Unsupported; RawEq is removed from the skip list.
- `initial_target_visitor.rs`: both RawEq operands seed relevance through existing
  place/anonymous/static handling, preserving both operand orders and immutable2.
- `relevant_instruction.rs` and `check_uninit/mod.rs`: CheckAs pointer type/layout,
  reference-place raw reborrow and diagnostic agree. Copy/Move reference places use
  AddressOf on a dereferenced place, without reading the pointee; constants retain
  the direct cast path. Existing raw-pointer CheckAs callers retain their behavior.

## Independent compile-seam check

Manually inspected changed imports, complete impl headers and affected API consumers,
including unchanged call sites. A separate Luna High reviewer independently checked
the same seam boundary and found no obvious compile seam. The bounded token checker
also reports errors[] for24 changed Rust files; it is supplementary evidence.

| Symbol / seam | Result |
|---|---|
| InitialTargetVisitor<'tcx>, constructor, MirVisitor impl | Explicit lifetime retained, including `impl MirVisitor for InitialTargetVisitor<'_>`; push_operand/try_resolve_instance callers unchanged |
| CheckUninitVisitor impls, RawEq, can_skip_intrinsic | Impl parameters retained; UintTy imported; Ty::try_new_array receives2 args; push_target existing ABI |
| MemoryInitOp::mk_operand / mk_cast / mk_ref | Existing variants and signatures retained; arities3/5/4 including unchanged users; ProjectionElem imported |
| UninitInstrumenter::build_get_and_check | Existing4-argument method and callers retained; reference CheckAs diagnostic uses explicit checked type |
| data_bytes_for_ty / generate_byte_mask | Existing3/2 argument contracts and recursion retained; required layout/type imports available |

No local compiler, formatter, build, Kani or verifier ran. Static analysis does not
establish Rust name/type/borrow checking or native fixture lowering. The earlier
slice2 E0726 failure is a reason for this check, not compile evidence for slice3.

## Oracles and qualification limits

All19 pairs equal exact F: four u8 mixed stack/promoted raw/eq orders plus15 immutable2
consumers. Goldens prescribe10 SUCCESSFUL and9 FAILED outcomes, with literal verdicts
and diagnostics; these are **not exact-N property oracles**. In particular direct/helper
left/right holes require native output review to establish the intended byte check
failure, the other operand's success and absence of unrelated Unsupported/earlier UB.
Aggregate compiletest exit0 alone does not establish those distinctions.

`immutable-subrange-legal` deliberately retains F's known conservative false positive:
FAILED with `[u8; 3]` diagnostic. It is not a useful positive SUCCESS. No golden was
strengthened, weakened or repaired by this review.

All nine deferred owner3 fixtures remain absent: four raw-MU mixed, two nested Pat,
two nested enum, and whole multi-root raw-eq-uninit. Their integration qualification
remains PENDING on4. Owner1 obligations remain pending4/5, with later owner2 consumers
unchanged. u8/promoted RawEq results cannot close nested offset obligations.

## Validation and handoff

`../ci/slice-03/SOURCE-VALIDATION.json`:44 changed paths,22 part hashes,19 exact-F
pairs,649 manifest file identities, all inherited selectors unchanged, only19 additions
from Quick head3, deferred9 absent, git diff --check clean.
`../ci/slice-03/SEAM-VALIDATION.json`: PASS_BOUNDED_STATIC_SEAM_AUDIT, errors[].
`../ci/slice-03/STATIC-VALIDATION.json`: CI-only overlay/source guard, accepted runner
byte identity and19 Python synthetic checks PASS. Source production/tests/docs unchanged.

Ready for coordinator's exact-head Quick after overlay preparation. Native qualification
NOT_RUN; push/dispatch NOT_RUN. This is neither Gate A nor independent formal proof credit.
