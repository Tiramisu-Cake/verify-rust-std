# R23 source-level borrow route — static navigation, no proof result

Read-only exploration on tool worktree0f4e336b. Current root profile still
selects fc0208d4; typed capture-site additions at26d0ee13/0f4e336b are not
adopted. No compiler/exporter/decoder/refiner/verifier or actual preparation
was run locally.

`first-callback.py::_raw_local_caller_suffixes` derives the experimental raw
wrapper from the original local array caller (`values=[10,20,5]`,
`values.as_mut_ptr()`, `insert_tail(begin,begin.add(2),is_less)`). The raw
wrapper substitutes `&raw mut values as *mut u64`, installs the checked R18
array invariant/ownership protocol and R19 cleanup. It does not close the
original `as_mut_ptr` route.

Relevant tool anchors (line numbers are navigation only):

- exporter `encode_ty_ref`2835, `encode_region`2875, body scope1317/2129;
  `Rvalue::Ref`3121 retains place/type/kind/region; Cast3175 retains exact
  operand/source type/target type and pointerCoercion kind/source2358.
- capnp RefData/CastData710–742 and coercion611–642. Scoped inference region
  metadata and capture-stage point identity are not an emitted-stage mapping.
- translator `translate_array_ty`1800 currently lacks array own/FBC/share;
  `slice_ref_ty_info`1259 gives mutable slice full_borrow ownership;
  `decode_ref_ty`1684 currently uses the legacy region string.
- translator slice `as_ptr`2892 has a data-pointer cast path, while slice
  `as_mut_ptr` has no corresponding special case. Ref creation3940 has the
  ignored-reference route and create_ref/create_slice_ref helpers. The
  TODO true-premise slice helpers cannot establish this resource protocol.
- prelude_core337–342: checked Array_to_array/array_to_Array. Slice FBC463–469
  contains element array plus foreach element ownership. Fixed array type
  interpretation and slice metadata must agree on actual T/N/place.
- lifetime_logic71–80: begin_lifetime/end_lifetime;117–125: borrow/borrow_end
  consumes/restores the same predicate with a real end token and dead token.
  str_mut_ref62–70 shows resource encapsulation, not arbitrary loan authority.

Prospective route: bind exact original Ref -> array/slice Unsize -> slice
as_mut_ptr shape, Mut mutability, source/target types, actual array length,
place/body/lifetime identity. Build slice contents through checked array
conversions and existing element ownership, encapsulate through borrow/end,
expose only the data component, and restore the same resources on the actual
normal and unwind paths. Static source inspection does not establish the
actual MIR shape, region identity, or a legal lifetime end point. These need
actual evidence and checked source/frontend obligations; do not infer them
from equal addresses, matching spans, unavailable liveness, or loan_killed_at.

Candidate controls: missing/wrong/ambiguous body/place/type/coercion/lifetime/
length identity; noncanonical element ownership; unavailable derived liveness;
original caller and insert_tail both observed; normal/panic/Drop/Resume with
exact stage/source target receipts. Keep RawPtr state/index controls separate.
F5 remains OPEN: current R19 block copied on normal/unwind with identical
callee posts cannot be distinguished by a bad count alone. A changed callee
unwind post must itself be proved before caller resource-negative credit.

This is a navigation/implementation plan, not an established adapter or a new
trusted premise. B2/generic/arbitrary-n/sorting credit remains zero.
