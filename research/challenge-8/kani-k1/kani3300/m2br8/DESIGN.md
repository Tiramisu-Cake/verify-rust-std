# R8 design, written before source edits

Base 8e01eb2aff5183c53403e1d1e73e573ce28d3095, tree
8554b019e0eb8d2daf09e5ab70bc0c0d09917de1. R7-C already included.
Only mem_init.rs and codegen/contract.rs may change. Source-ready is not compiled/proved.

## Relation and protocol

Replace ArgumentBuffer.relative_offset:usize with saved_base:*const u8 and
saved_byte:*const u8; all eleven other fields keep their types and meanings.
Main tracked_object_id/offset/value, registry/finalizer/reset seeds are unchanged.
Related states have identical protocol, has_witness and captured value; if selected
and has_witness, old.relative_offset equals decode(new saved pair). Inactive or
no-witness pointer payload is unobserved. Null initializes both pointer cells; null
is never used to infer a flag or value. A captured false witness remains a witness.

Keep mandatory return0, demonic argument competition including none, active,
signature/count/written/remaining/index/order/layout and all existing assertions.
Store computes the unchanged live-source match and captures value into locals
before new codec calls, before caller Move/deinit. Selected witness: relative is
tracked_offset.wrapping_sub(from_offset); form byte pointer using u8 wrapping_add.
Assert same object, unchanged base offset, byte offset >= base, exact round-trip,
and relative<N. These are proof obligations, never assumptions or fallback guards.
Selected no-witness: both payloads null, captured bool still saved; no byte add or
decode. Existing live-source metadata queries remain, including for zero extent:
keeping them retains the exact source-match calculation; N=0 cannot select a witness.

Load retains the same selected && has_witness && any() branch. Extract only stored
pointer metadata; assert same object and nondecreasing offsets, decode with target
usize wrapping_sub, assert relative<N. Retarget ONLY the live destination using the
captured value && layout[relative]. Never reread source bytes/shadow, even after death.
No new helper, reference, assumes, allocation/liveness query or pointer subtraction.

## Metadata lemma and representability

See CARRIER-LEMMA.md for pinned CBMC 6.11 source identities and arithmetic.
Let W=target usize/pointer width, O=W-object_bits. BV metadata zero-extends O offset
bits. For a backend-representable valid live source extent, base offset b and each
byte b+r satisfy 0<=b<=b+r<2^O, with 0<=r<N. Addition modulo 2^O then loses no bit;
zero-extended offsets subtract modulo 2^W to exactly r. This includes interior
source bases; no N<=32 or u32/index truncation. Pointer copies into globals preserve
these bits across Move/DEAD/pop_frame; only metadata is consumed after death.
The checks make encoding loss observable. A guard failure on any previously admitted
representable valid case is a blocker, never accepted scope narrowing. Extents whose
bytes cannot all be represented by this backend are not silently excluded: failure
must be reported as a model/backend boundary; no extra assume admits them.
Actual backend/version/flags/binary binding and reached nonzero witness paths await CI.
No claim for another backend. No measured cost attribution to a particular operator.

## Frame and validation

Keep unique main and distinct buffer markers and exact emitted-global lookup.
Main target unchanged. Replace one numeric member target with two u8-pointer member
lvalues: thirteen buffer cells, never pointees, object_whole, casts or blanket skip.
Expected IR is Type::unsigned_int(8).to_pointer(), derived from codegen_ty_ref/uint.
Public routing, caller instrumentation, bootstrap skip and partial reset unchanged.
No runtime whole-buffer write. Inactive payload may remain, but is not read.

One bounded independent Luna HIGH review of committed source and dependencies.
Local validation: source/type audit, hashes, diff checks and pinned rustfmt only.
Coordinator alone: build/fmt/clippy, unchanged P1 resource gate, P2/R8-C/all mapped
controls; G2 full Uninit matrix includes legal-pair/postcondition-hole. M3 HELD,
proof credit 0, Cloud $0. Heavy P1 or carrier guard/frame/path failure stops the gate.
