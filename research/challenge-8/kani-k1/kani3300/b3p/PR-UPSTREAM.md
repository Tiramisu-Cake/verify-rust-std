Title: Avoid CBMC aborts when copying padded unions with zero-sized fields

A typed copy of a union whose smaller arm is a zero-sized array makes CBMC abort (exit status 134). This happens with the default checks, no unstable flags needed:

```rust
#[repr(C)]
union ArrayUnion {
    bytes: [u8; 8],
    zst_array: [(); 2],
}

#[kani::proof]
fn array_typed_copy() {
    let mut src = ArrayUnion { zst_array: [(); 2] };
    let mut dst = ArrayUnion { zst_array: [(); 2] };
    unsafe {
        std::ptr::write_bytes((&mut src as *mut ArrayUnion).cast::<u8>(), 0x5a, 8);
        std::ptr::write(&mut dst, std::ptr::read(&src));
        assert_eq!(dst.bytes, [0x5a; 8]);
    }
}
```

On current `main` (bf9c58e662) CBMC 6.11.0 stops in `bits2expr` (`simplify_utils.cpp:345`) on the invariant `el_size_opt.has_value() && *el_size_opt > 0`.

### Cause

`codegen_union` wraps each arm narrower than the union in a struct with explicit padding. For a zero-sized arm the wrapper is `{ [(); 2], padding }`. When CBMC lowers byte operations on the union, it rebuilds that struct from a bitvector and cannot rebuild an array whose element width is zero.

### Change

Inside the padded wrapper, represent a zero-width payload with the existing empty unit struct. The union field keeps its original logical type, so projections and indexing still see `[(); 2]`. Union and arm widths still come from the rustc layout. Nonzero payloads and unions without padding, including all-ZST unions, are unchanged.

### Testing

`tests/expected/zst-union-arm` adds seven harnesses:
- typed copies with a byte-array arm;
- a padded `repr(C)` payload in both `repr(C)` and Rust-layout unions;
- a union at a nonzero offset inside a struct;
- an aligned ZST arm;
- an all-ZST union;
- nondeterministic in-bounds indexing of the ZST array.

On the base commit four of them abort with status 134 (the three copy cases and the offset case). With this change all seven pass.

CI on this commit in my fork: [Kani CI](https://github.com/Tiramisu-Cake/kani/actions/runs/43184599218) passes the regression jobs on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM and macOS 15 Intel, plus perf, documentation, LLBC and benchcomp. The macOS 15 Intel job needed one rerun after a CBMC timeout in the unrelated `cargo_autoharness_multichareq_searcher` test. The macOS 14 runner is not available on the fork.

### Related

- Related to #5085, which reports the same CBMC invariant for nested zero-width arrays in statics and constants. It is reached through a different lowering path, so this PR does not claim to fix it.
- With `-Z uninit-checks`, the same unions hit a separate compiler panic in `relevant_instruction.rs` (similar to #4854). It occurs both with and without this change and is not addressed here.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with AI assistance.*
