# Pointer-carried witness lemma — source argument, CI binding pending

This is a representation argument, not a solver result or a claim that R8 is cheaper.
Let N=LAYOUT_SIZE, W=target usize/pointer width, O=W-object_bits. No fixed W/O is
hardcoded. Runtime guards are assertions and every one must be SUCCESS in CI.

## Formation and exactness

The original match is object equality, tracked_offset>=from_offset and
tracked_offset-from_offset<N. Therefore r=tracked_offset.wrapping_sub(from_offset)
is the ordinary nonnegative difference and r<N. Capture has_witness and value into
locals before calling any new codec operation. Source lifetime has not ended.
From the thin source pointer form base:*const u8, then byte=base.wrapping_add(r).
No source value/reference is constructed; u8 scaling is exactly one byte.

For any existing backend-representable valid source extent [b,b+N), its byte offsets
are in [0,2^O). Thus b+r<2^O and r<2^O. BV pointer addition preserves object bits and
adds modulo 2^O to offset bits. Extracted offsets zero-extend to W bits, so
byte_offset-base_offset (mod 2^W) equals exactly r. Interior bases b>0 are included.
Store checks r<N, same object of base/byte, extracted base==original from_offset,
byte_offset>=base_offset, and exact decoded r. None can silently drop the witness.

The guards also expose limits rather than imposing N<=32/u32/another hidden bound.
For example, with O=8, b=250,r=10,N=20, byte offset becomes4; object equality alone
passes, but store offset-wrap and round-trip fail. This is not a representable
valid 20-byte source extent at b=250. r=256,b=0 likewise fails round-trip. Such an
input cannot earn relief by a fallback/no-witness branch. CBMC add_addr does not
itself reject every oversized static object; this document does not claim otherwise.
If CI discovers a previously admitted representable valid case that fails a guard,
STOP with exact source/config/input; no scope change. A fallback proposal for a
real representation gap is restoring the exact numeric relative carrier with its
known resource limit, or a separately designed checked multi-limb encoding; neither
is included in R8. No legacy pointer-copy or pointer-validity assumptions are added.

## Lifetime stability and consumption

The stored pair is two initialized pointer values in marked global cells. Rust
Move/deinit may change source shadow state; it does not overwrite these cells.
CBMC DEAD removes dead local SSA names/value-set entries; frame pop drops local
names and restores renaming. Neither operation rewrites stored global pointer bits.
Metadata hooks construct pointer expressions, without dereference or live check.
Thus decode after return/DEAD has the same offsets and exact r, while source bytes
and source shadow must never be read. No object-size/allocation query is needed.

On the existing selected && has_witness && demonic-source-follow branch, Load
checks pair object equality and byte>=base, decodes with usize::wrapping_sub and
checks r<N. Only live to_ptr supplies the new tracked object and base offset.
Captured value && layout[r] retains false for a false witness. Unselected/no-witness
paths and optimistic destination writes are the original protocol. N=0 cannot set
has_witness, so it never forms a byte pointer or decodes a payload. Captured false
is NOT the no-witness path and must run the codec. Null is only initialized payload.

Inductive relation: identical protocol/flags/value; selected witness implies old.r
=decode(pair). Store establishes it; unselected stores preserve it; consumption
uses identical demonic choice/destination/mask; clear/reset makes payload unobserved.
No private buffer writer outside Store changes the active payload. Partial reset
and M1 seed epoch stay unchanged. All admitted representable valid extents satisfy
the algebra; no new backend-wide extent admission or general lifetime proof is claimed.

## Audited primary sources and binding limits

CBMC tag cbmc-6.11.0:
- [bv_pointers.cpp](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/solvers/flattening/bv_pointers.cpp):
  77–113 widths/slices, 675–713 zero-extension metadata, 853–876 modular offset
  arithmetic/object preservation; 879–894 add_addr checks object count, not all extents.
- [symex_dead.cpp](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_dead.cpp):
  21–78 local-name/value-set/propagation cleanup.
- [symex_function_call.cpp](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-symex/symex_function_call.cpp):
  387–453 pop_frame/normal return.
Hashes/URLs are in SOURCE-MANIFEST. These are primary implementation reads, not CI evidence.
Kani hooks.rs PointerObject/PointerOffset cast to hook return usize and construct
Expr metadata. Expr::pointer_offset has ssize_t IR type but the pinned BV extraction
zero-extends O bits, then the hook casts to usize. No signed-isize decode is used.
Kani intrinsic.rs::codegen_arith_offset emits pointer plus offset. Rust API snapshot
wrapping_add casts usize to isize then arith_offset; low O bits are unchanged and the
representable valid extent case has no lost high bits. TYPE-AUDIT records snapshots.

No established mechanism that metadata extraction enumerates all objects. Possible
compound-formula/operator cost is open. CI must bind actual backend/version/flags,
binary, target widths, source copies, reached Store/Move/return/Load/ensures paths
and pointer-cell assigns. VCC presence alone is insufficient. Other backends/versions
are unproved; guards and a source argument do not grant independent proof credit.
