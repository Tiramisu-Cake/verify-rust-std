# Unpublished follow-up for model-checking/kani#3762

Existing issue: https://github.com/model-checking/kani/issues/3762 (open, checked
2026-11-16). This is a correctness/unsupported-feature report. No publication.

At pinned Kani `0aac16ef62da9e9d5645782d458593e5d78143ba`, a curated
SmallSort census on std P′ `c5ff36ff433692140605891f646043f991db05de`
reports 224/235 roots with copy validity Unsupported. There are 237 failed
copy properties; 13 roots have two. No other failed-property family was observed.
Source inspection finds the unconditional TODO at
`kani-compiler/src/kani_middle/transform/check_values.rs:491–497`.

Minimal proposed standalone reproducer (NOT_RUN; no local compiler invocation):

```rust
#[kani::proof]
fn copy_integer() {
    let src = kani::any::<u8>();
    let mut dst = 0u8;
    unsafe { core::ptr::copy_nonoverlapping(&src, &mut dst, 1) };
    assert_eq!(dst, src);
}
```

Future command, not executed here: `kani -Z valid-value-checks mre.rs --harness copy_integer --exact`.
Expected Rust behavior: valid disjoint initialized copy, assertion holds.
Source-predicted current Kani behavior: copy validity Unsupported despite integer
having no restrictive bit-pattern validity requirements. This minimal MRE has
not itself been executed; runtime evidence is the bound SmallSort census.

A proposed integer fast path must not turn raw copy into an eager typed read.
These distinguishing controls are proposals, all NOT_RUN:

```rust
// Legal raw copy may transport invalid bool bytes if overwritten before typed read.
#[kani::proof]
fn raw_bool_overwrite() {
    let byte = 2u8;
    let mut dst = core::mem::MaybeUninit::<bool>::uninit();
    unsafe {
        core::ptr::copy_nonoverlapping(
            (&byte as *const u8).cast::<bool>(), dst.as_mut_ptr(), 1);
    }
    dst.write(true);
    assert!(unsafe { dst.assume_init() });
}

// Paired invalid-value control: same transport, then a real typed read.
#[kani::proof]
fn raw_bool_read() {
    let byte = 2u8;
    let mut dst = core::mem::MaybeUninit::<bool>::uninit();
    unsafe {
        core::ptr::copy_nonoverlapping(
            (&byte as *const u8).cast::<bool>(), dst.as_mut_ptr(), 1);
        let value = core::ptr::read_volatile(dst.as_ptr());
        assert!(value);
    }
}
```

Required after any restrictive-validity support: legal overwrite companion PASS;
typed-read companion fails specifically an invalid-value check. On current
0aac both are predicted to stop at Unsupported, not to qualify either oracle.
For an integer-only patch these bool-copy sites must remain fail-closed; do not
claim that such a patch implements these producer/consumer controls. Also test
integer-byte copy into bool backing followed by overwrite/read: integer pointee
alone cannot certify future aliased typed uses. Add legal bool/char/NonZero
positive cases, invalid read cases, raw uninitialized/padding transport, count0,
ZST, overlapping copy/memmove and both mutable-cast directions before extending
support. Retain existing memory/default checks. Unknown is never NoConstraints.
