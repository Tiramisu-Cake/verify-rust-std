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

On current `main` (0aac16ef62), CBMC 6.11.0 stops in `bits2expr` (`simplify_utils.cpp:345`) on the invariant `el_size_opt.has_value() && *el_size_opt > 0`.

### Cause

`codegen_union` wraps each arm narrower than the union in a struct with explicit padding. For a zero-sized arm the wrapper is `{ [(); 2], padding }`. When CBMC lowers byte operations on the union, it rebuilds that struct from a bitvector and cannot rebuild an array whose element width is zero.

### Change

Inside the padded wrapper, represent a zero-width payload with the existing empty unit struct. This is the same physical shape that the `uninit: ()` arm of every `MaybeUninit<T>` already has. The union field keeps its original logical type, so projections and indexing still see `[(); 2]`. Whether an arm is zero-sized is decided from the rustc layout (its padding equals the union size), not from the GOTO type, so arms of recursive types that are still being built are handled. Nonzero payloads and unions without padding, including all-ZST unions, are unchanged.

The root cause is the zero-width element check in CBMC's `bits2expr`, which diffblue/cbmc#9487 fixes. Until Kani picks up a CBMC release with that fix, this change avoids generating that shape for union arms, which Kani controls.

### Testing

`tests/expected/zst-union-arm` adds seven harnesses:
- typed copies with a byte-array arm;
- a padded `repr(C)` payload in both `repr(C)` and Rust-layout unions;
- a union at a nonzero offset inside a struct;
- an aligned ZST arm;
- an all-ZST union;
- nondeterministic in-bounds indexing of the ZST array.

Seven more single-harness tests cover the ZST arm declared first, nested `[[(); 2]; 3]` and `[[u8; 0]; 2]` arms, an aligned ZST array, a ZST struct wrapping an array, and two recursive types (`zst-union-recursive-*`) where a union is reached through a pointer while the enclosing struct is still incomplete. Each new harness includes a `kani::cover!` so that a vacuous pass would be visible.

On `main`, four of the seven `zst-union-arm` harnesses and all five new arm-shape tests fail with the CBMC invariant; the two recursive tests pass. With this change all of them pass.

CI on this commit in my fork: [Kani CI](https://github.com/Tiramisu-Cake/kani/actions/runs/43605511755) passes the regression jobs on Ubuntu 22.04, Ubuntu 24.04, Ubuntu 24.04 ARM, macOS 15 and macOS 15 Intel (the Intel job needed one rerun after a CBMC timeout in the unrelated `cargo_autoharness_multichareq_searcher` test), plus documentation, LLBC and benchcomp; Cargo Deny and Format Check also pass. The perf job lost its runner twice. In a separate run with memory sampling, the heaviest perf case (`s2n-quic-core`) reaches the same CBMC peaks with and without this change (about 7.5 GB for its largest harness, plus the external SAT solver), and runs out of memory on the 16 GB runner on `main` as well ([main](https://github.com/Tiramisu-Cake/kani/actions/runs/43624201005), [this change](https://github.com/Tiramisu-Cake/kani/actions/runs/43624196686)). The macOS 14 runner is not available on the fork.

### Limitations

A nonzero-width arm that contains a zero-sized array, such as `struct Tail { b: u8, z: [(); 2] }` or `(u64, [(); 2])`, still hits the same CBMC invariant after this change. It goes through the struct-field representation rather than the union wrapper, and is closer to #5085. With a CBMC build that includes diffblue/cbmc#9487, the `Tail` typed copy passes ([replay in #5085](https://github.com/model-checking/kani/issues/5085#issuecomment-6863856826)).

### Related

- #5085 reports the same CBMC invariant for nested zero-width arrays in statics and constants. It is reached through a different lowering path, so this PR does not claim to fix it.
- diffblue/cbmc#9487 fixes the invariant in CBMC itself. Once Kani's CBMC includes it, the special case here can be removed.
- With `-Z uninit-checks`, the same unions hit a separate compiler panic in `relevant_instruction.rs` (similar to #4854; seen on bf9c58e662, not rechecked on current `main`). It occurs both with and without this change and is not addressed here.

By submitting this pull request, I confirm that my contribution is made under the terms of the Apache 2.0 and MIT licenses.

*Disclosure: this change and description were prepared with the help of AI assistants.*
