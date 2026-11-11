Fix code generation for zero-sized fields in padded unions

Typed copies of a union containing a zero-sized array field can make CBMC abort with status 134. This reproduces with the default checks, without `-Z uninit-checks`:

```rust
#[repr(C)]
union U {
    bytes: [u8; 8],
    zst: [(); 2],
}

#[kani::proof]
fn check_union_copy() {
    let mut src = U { zst: [(); 2] };
    let mut dst = U { zst: [(); 2] };
    unsafe {
        std::ptr::write_bytes((&mut src as *mut U).cast::<u8>(), 0x5a, std::mem::size_of::<U>());
        std::ptr::write(&mut dst, std::ptr::read(&src));
        assert_eq!(dst.bytes, [0x5a; 8]);
    }
}
```

Run with `kani repro.rs`.

Union code generation pads each smaller field to the union size. For a zero-sized array field, this produces a nonzero-width wrapper containing a zero-width array member. CBMC cannot reconstruct that array from the wrapper's bitvector when lowering byte operations.

Represent the zero-sized physical payload inside the padded wrapper with an empty struct. Retain the original logical union-field type for projections and indexing. Nonzero-sized payloads, padding widths, and unions requiring no field padding follow the existing code paths.

Seven regression harnesses cover typed copies with a byte-array payload, padded C and Rust payloads, an aligned ZST, a containing struct with the union at a nonzero offset, an all-ZST union, and zero-sized array indexing. The expected result is seven successful harnesses and no failures. The typed-copy assertions read initialized fields rather than padding.

Targeted CI reported four CBMC aborts before the fix and all seven harnesses passing with it, without uninitialized-memory instrumentation. The tests have since moved to the general expected-output suite; full CI for that placement remains pending. A separate compiler panic with `-Z uninit-checks` occurs both before and after this fix and is outside this patch's scope.

*Disclosure: this change and description were prepared with AI assistance.*
