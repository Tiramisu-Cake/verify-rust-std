# R16 caller conversion investigation

Baseline actual Build f89ce5ff-644e-46ef-90da-044c96931270/source97a9766513d5567bd291d8e49b71240ce246c472. Exact wrapper source440–443 and proof AST441 are in R15-PROOF4-*-READER; fresh R16 baseline Brief and targeted decode.out observations retain archive/index/file/request identities. Decoded call29807 names core::slice::<impl [T]>::as_mut_ptr; target slice/u64/mutability and pointerCoercion unit discriminator occur29738–29742. This is corroborating source evidence, not complete parser-input causal binding.

The original prefix mechanically retains the same wrapper suffix as full_body (first-callback.py:_cut_prefix); both have the same class of blocker. The compiler-generated array-reference→slice-reference cast is not a simple placeholder syntax defect:

- exporter encode_region collapses ReVar/ReErased to erased; encode_rvalue_cast stores only the PointerCoercion discriminator, not its subtype (vf_mir_exporter/src/lib.rs).
- translator Cast lowers generically to CastExpr; erased lifetime becomes InferredTypeExpr. Strict checker rejects that target placeholder (verifast1.ml CastExpr/check_pure_type).
- current sized→unsized generic Upcast evaluates as the same pointer term (verify_expr.ml), although a slice needs length metadata.
- mutable Rvalue::Ref currently follows ignore_ref_creation and becomes AddressOf (vf_mir_translator.ml3893–3926). No TreeBorrows or RustBelt source borrow token is created by this path. Static-array type interp own/full_bor_content are unimplemented (translate_array_ty1807ff).

Existing checked array value/element conversions (Array_to_array/array_to_Array), slice_full_borrow_content and reversible full_borrow_implies can support a future resource-preserving solution, but the latter requires an actual source full_borrow and both implications. A raw array memory chunk is not that token. Existing std::ptr::slice_from_raw_parts_mut supplies fixed-length metadata and preserves the data pointer, so no new metadata axiom is necessary; its reqtrue grants no reference validity/lifetime/borrow ownership. Existing slice reference helpers contain TODO preconditions and cannot be used to invent a stronger guarantee.

A sound original-path contract therefore needs source/target type and coercion identity, a real source lifetime relation, checked array borrow-content/resource conversion, metadata from the exact N, and restoration through the same lifetime/normal-unwind protocol. A broad inferred-cast exemption or raw-pointer→reference cast alone does not meet that contract. No such tool/model change has been implemented or assumed. Qualified original caller remains OPEN; a future checked implementation is in scope, while a new trusted borrow/memory premise would require the owner.

Independent useful work in this session isolates the unchanged actual definition as a separate diagnostic, preserving all original caller/prefix gates. Its verifier completion can narrow actual proof obligations without claiming a caller solution or silently replacing the prerequisite graph. See R16-BODY-ISOLATION-DESIGN-20261021.md.
