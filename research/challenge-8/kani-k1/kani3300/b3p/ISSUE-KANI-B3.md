Title: CBMC invariant failure (`bits2expr`) when copying a padded union with a zero-sized array field

With default checks, a typed copy of a union whose smaller field is a zero-sized array makes CBMC abort:

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

```
Invariant check failed
File: ../src/util/simplify_utils.cpp:345 function: bits2expr
Condition: el_size_opt.has_value() && *el_size_opt > 0
Reason: Check return value
```

Kani 0.68.0 (`main` at 0aac16ef62), CBMC 6.11.0, x86_64 Linux. CBMC exits with status 134 and Kani reports `VERIFICATION:- FAILED` for a correct program.

`codegen_union` wraps a field that is narrower than the union in a struct with explicit padding, here `{ [(); 2], padding }`. When CBMC lowers byte operations on the union, it rebuilds that struct from a bitvector and cannot rebuild an array whose element width is zero.

The root cause is in CBMC, and I have opened a fix there: diffblue/cbmc#9487. With a CBMC built from that branch and unmodified Kani `main`, this example verifies successfully, and so do the reproducer from #5085 (same invariant, reached through a `static`/`const`) and a typed copy of `struct Tail { b: u8, z: [(); 2] }`; all of them hit the invariant with CBMC 6.11.0 ([replay](https://github.com/Tiramisu-Cake/kani/actions/runs/43724925747)).

Until Kani picks up a CBMC release with the fix, Kani can avoid generating this shape for union fields; I will open a small PR that does that.

*Disclosure: this issue was prepared with the help of AI assistants.*
