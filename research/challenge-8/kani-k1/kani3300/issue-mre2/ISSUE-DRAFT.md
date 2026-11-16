Title: Slice `modifies` havoc reports an uninitialized read on uninitialized output with `-Z uninit-checks`

When a function whose `modifies` target is a raw slice is replaced by its contract (`stub_verified`), the havoc of that slice fails an initialization check if the destination memory is not yet initialized. The same function body verifies, and the same contract with element-wise (thin pointer) targets also verifies.

```rust
use std::alloc::{alloc, dealloc, Layout};

// Safety: p points to a live, exclusively owned allocation of at least two bytes.
#[kani::modifies(std::ptr::slice_from_raw_parts_mut(p, 2))]
unsafe fn initialize(p: *mut u8) {
    p.add(0).write(1);
    p.add(1).write(2);
}

#[kani::proof_for_contract(initialize)]
fn check_body() {
    let layout = Layout::array::<u8>(2).unwrap();
    unsafe {
        let p = alloc(layout);
        if p.is_null() { return; }
        initialize(p);
        dealloc(p, layout);
    }
}

#[kani::proof]
#[kani::stub_verified(initialize)]
fn check_slice_havoc() {
    let layout = Layout::array::<u8>(2).unwrap();
    unsafe {
        let p = alloc(layout);
        if p.is_null() { return; }
        initialize(p);
        dealloc(p, layout);
    }
}
```

```sh
kani -Z function-contracts -Z uninit-checks -Z stubbing repro.rs --harness check_body --exact
kani -Z function-contracts -Z uninit-checks -Z stubbing repro.rs --harness check_slice_havoc --exact
```

Kani 0.68.0 at `0aac16ef62da9e9d5645782d458593e5d78143ba`, nightly-2026-10-23, CBMC 6.11.0, x86_64 Linux.

Expected: both harnesses succeed. `initialize` only writes to the destination, and the `modifies` clause allows arbitrary new bytes there; nothing reads the old contents.

Actual: `check_body` succeeds. `check_slice_havoc` fails with exactly one failed check:

```text
kani::internal::write_any_slice::<u8>.safety_check.1
Undefined Behavior: Reading from an uninitialized pointer of type `*mut [u8]`
```

Controls, all on the same revision and flags:

| Variant | `check_body` | `check_slice_havoc` |
|---|---|---|
| uninitialized output, slice target (above) | SUCCESS | FAILURE (above) |
| output written with zeros before the call | SUCCESS | SUCCESS |
| uninitialized output, thin targets `#[kani::modifies(p, p.wrapping_add(1))]` | SUCCESS | SUCCESS |

A separate harness that actually reads an uninitialized byte from the same kind of allocation (`read_volatile`) fails as expected with `Reading from an uninitialized pointer of type *const u8`, so the check itself works.

The slice havoc at [kani_core/src/lib.rs:715–716](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/library/kani_core/src/lib.rs#L715-L716) is `(*slice).fill_with(T::any)`. That creates a `&mut [T]` over the existing elements and assigns to them, which reads them as initialized (and for types with destructors would also drop the old values). The thin-pointer havoc at [lines 723–724](https://github.com/model-checking/kani/blob/0aac16ef62da9e9d5645782d458593e5d78143ba/library/kani_core/src/lib.rs#L723-L724) uses `ptr::write`, which is why the thin-target variant passes. Writing each element with `ptr::write` in the slice havoc as well would match the semantics of `modifies` for uninitialized output.

Possibly related but different: #3682 / #4749 (resolution of a doubled slice type before verification).

*Disclosure: this issue was prepared with the help of AI assistants.*
