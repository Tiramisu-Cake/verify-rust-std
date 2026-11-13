# CC2 type and mask audit — static only

| Storage | Admission / mask | Boundary |
| --- | --- | --- |
| bool, integers | Existing primitive Scalar::Initialized data bytes; bool true/false identical | Only argument slot; source read obligations retained |
| &T / raw pointer | Existing thin scalar / fat scalar-pair representation and offsets | T is not recursively initialized; MU/raw payload holes remain |
| RefWrapper / tuple / ordinary supported struct | Existing recursive fields at actual layout offsets, padding false | No nonzero closure-to-tuple substitution |
| Direct MU / ordinary union | is_union excludes new seed | Existing paired argument/return and transfer masks unchanged |
| Flat arrays of MU / aggregate containing union | Recursive data_bytes_for_ty rejects UnionAsField | No sized/all-true fallback; no extra aggregate protocol |
| Nonzero closure | Existing UnsupportedType from layout; not seeded | CC3 remains unissued; original captured tests unchanged |
| ZST / zero-size closure | Empty data mask if reached and supported | No pointee or payload byte initialized |
| Unsized/dynamic/other unsupported | Not a supported Sized ordinary mask | Existing reached diagnostic remains; no success claim |

API use is limited to existing parent reexports PointeeInfo/PointeeLayout,
MutableBody::arg_count/locals, Place::from(usize), MemoryInitOp::SetRef,
and current rustc_public type.kind().is_union(). The same APIs already exist
at the reviewed pin; Rust typecheck is nevertheless NOT_RUN locally.

MemoryInitOp::mk_operand takes AddressOf of the slot; build_set uses the existing
typed layout; MEM_INIT_STATE.set only updates the selected byte in that object
and extent, with `value = layout[relative_offset] && value`. This does not retarget
shadow state into a pointee or alter the argument witness buffer. Library code
is unchanged. No claim that source coordinates alone establish emitted-model
binding, dynamic last setter, compiler acceptance or independent proof credit.
