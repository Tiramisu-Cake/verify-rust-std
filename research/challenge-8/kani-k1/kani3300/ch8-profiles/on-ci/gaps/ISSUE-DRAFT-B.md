# Draft: Slice modifies havoc reads uninitialized output storage

Not submitted. The reduced example below has not been run. Reproduction on
current upstream is pending; this draft records a source-based diagnosis and
an observed diagnostic in a larger verification run.

## Problem

With `-Z function-contracts -Z uninit-checks`, a verified-stub call whose
modifies target is a raw slice over uninitialized output storage can report:

```text
Undefined Behavior: Reading from an uninitialized pointer of type `*mut [u8]`
```

The destination is writable storage for two bytes. The actual function
initializes it without reading any previous contents. Replacing that function
with its contract should not require the old output bytes to be initialized.

## Reduced candidate

```rust
use std::mem::MaybeUninit;

#[kani::modifies(std::ptr::slice_from_raw_parts_mut(out.as_mut_ptr().cast::<u8>(), 2))]
fn initialize(out: &mut [MaybeUninit<u8>; 2]) {
    out[0].write(1);
    out[1].write(2);
}

#[kani::proof_for_contract(initialize)]
fn check_body() {
    let mut out = [MaybeUninit::uninit(); 2];
    initialize(&mut out);
}

#[kani::proof]
#[kani::stub_verified(initialize)]
fn check_slice_havoc() {
    let mut out = [MaybeUninit::uninit(); 2];
    initialize(&mut out);
}
```

Proposed reproduction command, **not yet executed for this reduction**:

```sh
kani -Z function-contracts -Z uninit-checks --harness check_body --exact repro.rs
kani -Z function-contracts -Z uninit-checks --harness check_slice_havoc --exact repro.rs
```

The first harness checks the real body. The second, with `stub_verified`, is
the candidate reproducer for the generated havoc step.

Expected: `check_body` and `check_slice_havoc` should both avoid an uninitialized
read. There is no assertion that relies on a particular value from the stub:
the modifies clause permits arbitrary new byte values.

Actual result for this reduction: **NOT_RUN**. Before submitting, record the
exact tested Kani/toolchain/CBMC versions, command and both harness results.

## Source-based explanation

At upstream commit `0aac16ef62da9e9d5645782d458593e5d78143ba`,
`library/kani_core/src/lib.rs:715–716` defines slice havoc as:

```rust
(*slice).fill_with(T::any)
```

That operation creates a mutable slice reference to existing T elements before
initializing them. `fill_with` assigns to the elements and can also drop their
previous values for types with destructors. Neither operation is appropriate
for uninitialized output. This appears to be a model defect exposed by the
initialization check, rather than evidence that the check itself is incorrect.

Could slice havoc use raw element initialization without reading or dropping
old elements, while preserving full-range bounds/alignment checks and arbitrary
valid new values? The thin-pointer havoc model already uses `ptr::write`.
This draft proposes no suppression of initialization checks.

## Distinction from existing reports

[Issue #3682](https://github.com/model-checking/kani/issues/3682) and
[PR #4749](https://github.com/model-checking/kani/pull/4749) concern resolution
of a doubled slice type before verification. The diagnostic here occurs inside
the slice-havoc initialization check after the element type is resolved.
A targeted issues/PR search on 2026-11-16 found no exact match for this symptom;
that is not an exhaustive absence claim.

## Checks needed before submission

- Run the candidate on the recorded upstream revision and current upstream;
  preserve the distinction between source diagnosis and reproduced behavior.
- Compare initialized storage, replacing both declarations of `out` with
  `[MaybeUninit::new(0u8); 2]`.
- Compare the exact same contract with thin targets:
  `#[kani::modifies(out.as_mut_ptr().cast::<u8>(), out.as_mut_ptr().cast::<u8>().wrapping_add(1))]`.
- Separately check that an actual read from uninitialized `MaybeUninit<u8>`
  still fails, so a proposed fix cannot hide user-code UB.
