Retain all14 harnesses and assertions. Proposed packaging is one directory with
three separately compiled source files: main.rs (12 harnesses), recursive-arm.rs
and recursive-zst-arm.rs (one each). Use same-stem .expected files throughout.
This table gives the disposition of all17 currently changed files.

| Current path (relative to tests/expected except compiler row) | Disposition | Reason and oracle |
| --- | --- | --- |
| kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs | Keep logic; shorten new comment | rustc-layout zero-width wrapper payload; logical UnionField type preserved |
| zst-union-arm/main.rs | Keep seven harnesses; append five concrete edge modules | Main reproducer, distinct copy/layout/frame/index controls |
| zst-union-arm/expected | Replace with main.expected | Require complete12-success/0-failure/12-total summary and five named SATISFIED covers |
| zst-union-edge-array-first/main.rs | Move body/types into main module array_first; delete old file | ZST field before data field, ptr typed copy, byte and logical-array assertions |
| zst-union-edge-array-first/expected | Merge named cover block into main.expected; delete old file | Preserve copy_array_first post-copy data and projection SATISFIED |
| zst-union-edge-nested-unit-array/main.rs | Move into main module nested_unit_array; delete old file | Nested nonempty arrays with zero-width element shape |
| zst-union-edge-nested-unit-array/expected | Merge named cover block; delete old file | Preserve copy_nested_unit_array post-copy data and projection SATISFIED |
| zst-union-edge-nested-empty-byte-array/main.rs | Move into main module nested_empty_byte_array; delete old file | Outer nonempty array of empty u8 arrays, inner len0 assertion |
| zst-union-edge-nested-empty-byte-array/expected | Merge named cover block; delete old file | Preserve copy_nested_empty_byte_array post-copy data and projection SATISFIED |
| zst-union-edge-aligned-array/main.rs | Move into main module aligned_array; delete old file | Array of align8 ZSTs plus union alignment, data16 |
| zst-union-edge-aligned-array/expected | Merge named cover block; delete old file | Preserve copy_aligned_array post-copy data and projection SATISFIED |
| zst-union-edge-struct-array/main.rs | Move into main module struct_array; delete old file | Aggregate containing ZST array; distinct struct serialization shape |
| zst-union-edge-struct-array/expected | Merge named cover block; delete old file | Preserve copy_struct_array post-copy data and projection SATISFIED |
| zst-union-recursive-arm/main.rs | Move intact to zst-union-arm/recursive-arm.rs; edit comments/cover label only | Independent invocation retains pointer-first incomplete nonzero Node arm |
| zst-union-recursive-arm/expected | Move to recursive-arm.expected; update label and add complete1-success summary | Named SATISFIED recursive_arm retains null pointer; successful verification |
| zst-union-recursive-zst-arm/main.rs | Move intact to zst-union-arm/recursive-zst-arm.rs; edit comments/label only | Independent invocation retains pointer-first recursive zero-length array arm |
| zst-union-recursive-zst-arm/expected | Move to recursive-zst-arm.expected; update label and add complete1-success summary | Named SATISFIED recursive_zst_arm retains null pointer; successful verification |

Exact harness dispositions and distinct paths:

| Current harness | Action | Distinct semantic/type/layout path and assertions to retain |
| --- | --- | --- |
| array_typed_copy | Retain verbatim | Original CBMC-abort reproducer: ArrayUnion, zero array as second field, initialized full byte8 copy, ZST projection and byte equality |
| padded_typed_copy_c | Retain | repr(C) union with Padded u8/u32 payload; assert byte and word fields, not copied padding |
| padded_typed_copy_rust | Retain | Rust-layout union with same padded repr(C) payload; layout policy varies independently |
| aligned_zst_typed_copy | Retain | Scalar align8 ZST, not an array; union alignment and byte8 copy |
| zst_arm_at_nonzero_offset | Retain | AtOffset.value offset8, copy only inner union, source/destination prefix17/23 preserved |
| all_zst_union | Retain | Union size0/alignment8, padding==0 fast path, all three logical arms and valid zero-length write |
| zst_array_indexing | Retain | kani::any index constrained <2; array copy, index write, reference, and len2 preserve logical array type |
| copy_array_first | Move, no deletion of behavior | First field is [();2], union extent16; declaration order covers physical component ordering |
| copy_nested_unit_array | Move | [[();2];3], outerlen3/innerlen2 and element projection plus full byte16 equality |
| copy_nested_empty_byte_array | Move | [[u8;0];2], outerlen2/innerlen0; empty-array versus unit-element shape |
| copy_aligned_array | Move | [Z;2] align8 despite size0, Edge size16/align8; all-byte data check |
| copy_struct_array | Move | Wrapped{array:[();2]} as zero-width aggregate, field projection through wrapper |
| recursive_arm | Retain isolated invocation | Node->U->Node nonzero recursive field; inferred null pointer and black_box; valid null assertion/cover |
| recursive_zst_arm | Retain isolated invocation | Node2->Link->[Node2;0], zero-width recursive field; same pointer oracle under different incomplete type path |

Helper/type/setup disposition:

| Current declarations/setup | Action | Why |
| --- | --- | --- |
| ArrayUnion | Keep shared by array_typed_copy/offset/indexing | Same nominal union; shared setup already concise |
| Padded, PaddedUnionC, PaddedUnionRust | Keep | One common padded payload plus two layout policies; no generic abstraction |
| Z, AlignedUnion | Keep | Concrete aligned scalar arm; Z can stay distinct from module-local aligned_array::Z |
| AtOffset | Keep | Prefix/frame control requires actual containing struct |
| AllZst | Keep | Explicit no-padding negative control for the changed branch |
| Five Edge declarations | Keep each under its named module | Same old name, five different field types/order; do not merge nominal types |
| aligned_array::Z, struct_array::Wrapped | Keep local to edge modules | Aligned-array and struct-contained-array forms are distinct |
| Node/U, Node2/Link, inferred casts, black_box | Keep bodies and isolated translation units | Preserve pointer-first incomplete-type traversal; no new helper monomorphization |
| Repeated ptr::write_bytes/read/write/assertions | Keep in each concrete harness | Direct concrete typed operations expose regression; helper extraction buys little |
| Imports std::mem/std::ptr | Shared imports are fine in main; modules use super::* or explicit imports | Avoid changing the typed operations; module source must compile independently of old paths |
| Seven existing covers | Keep predicate/status; rename only two recursive prose labels | Required named SATISFIED blocks move with tests |
| New covers for original seven | No recommendation to add | They already have strong assertions and a complete success summary; no count-driven framework |

Only files/directories and repeated prose are removed. Every full-data assertion,
projection, offset/alignment/length check, canary prefix, assumption domain and
cover predicate remains. None of the current tests is an internal-error golden.
Default flags are identical; there are no platform/cfg/ignore directives to carry.
After a later implementation, check discovered12+1+1 harnesses and exact success
summaries using standard CI, plus unchanged original reproducer on base/fixed.
