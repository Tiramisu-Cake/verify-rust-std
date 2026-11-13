# E2 patch rationale

Only existing backend immutable admission and static producer plus four fixtures change. Named static initialization already uses codegen_alloc_in_memory; it keeps declared CBMC type and identity. Therefore adding anonymous origins alone would not bind named storage, and the anonymous canonical byte-struct gate cannot apply to its declared type.

The narrow producer hook captures the exact initializer Allocation after emission. It requires Freeze and the existing supported type domain, no relocations, immutability and exact sized length, then captures the matching declared backend type and storage flags. Finalization checks the same allocation/type and byte extent before using the existing reset-only mask seeding. No static reference setter or blanket initializedness is added. Some(0) and None stay distinct; mutable targets never become seed origins. The anonymous strict storage gate remains unchanged in meaning.

Type review: StaticDef/CrateDef::ty and Instance::from(def).mangled_name already used by static_var; rustc_internal::internal(Ty)/is_freeze use the same pattern as anonymous_allocations. Backend Type values are owned clones, not Rust pointee values. named mask indexes remain guarded by offset < n, with n checked against target usize. Pointee MU arrays are valid references even with uninitialized slots. Subrange byte offset 1 plus extent 3 exactly fits parent 4; alignment is 1. MU<&u8> has pointer-sized/aligned slots, and only initialized slots construct &u8.

No runtime, points-to/relevance graph, DFCC, driver, schema, export checker, existing golden, or trust/domain policy is modified. Actual Rust type checking, MIR, reset code generation and property sets are NOT_RUN.

Independent read-only Luna HIGH review of committed 478aad601..19588e0af found no source-level blocker. It checked admission gates, initializer masks, reset timing, exact-allocation alias/coalescing, anonymous layout gates and fixture geometry. The reviewer also inspected targeted baseline failure summaries after correcting its initial path typo. It did not run or claim actual type/MIR/Kani validation. No semantic changes followed review.
