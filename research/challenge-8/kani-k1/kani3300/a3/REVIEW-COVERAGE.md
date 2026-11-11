# KANI3300 A3 final coverage review

## Reviewed identities

- Semantic candidate: `e3c529a0d5a501987a36c1481bb7e8a48c80dc73`; tree `520f75b9df2be108f598b3c62f956666752bdfc5`; diff SHA256 `c39b6522f08dc951e130bd36f805ef83be9fe2e3fc692cee8eec7515b0e28028`; semantic spec SHA256 `5ca8a699ce50a1f0fda972d79fd717c6aa8d9a25b15dec542cbdae8faa716b4b`.
- Final fixture candidate: `0b1d68ac691cac7e03dbe73f4aec139bb5389059`; tree `7b249e34038812fb2ad22027ae1201345653c125`; diff SHA256 `36cb214ff6035cee2b41130167f32d21f017e5a36c892ea1902cd3e3f3788ffb`; review packet SHA256 `1773299988da07a139bd9271790d3c30f26baa9b44f4acf6b4df647d1b4640b7`; spec SHA256 `b9c4a7f0309a3e409b9309b359740d3ad3e65bc377a6ef9df63e473b82d9e5ee`.
- Baseline for this fixture-only delta: `14c0a3c95b6ece62b01f96f663b455f8c5e155dc`. Only `maybe-uninit-call-move/main.rs` and its `expected` file changed; semantic implementation is unchanged.

## Static assessment

The delta adds the two missing control families identified by the earlier fixture review:

- Ordinary union return: `union_roundtrip` returns a `Byte` union. One harness checks an initialized `byte` field; another constructs the zero-sized `empty` field and reads the uninitialized `byte` field.
- Full-extent padded MaybeUninit Move/Copy: `Padded` has `repr(C)`, size 8, and `value` at offset 4. Within each custom MIR function, a helper writes all eight source bytes before the target call. The Move case passes `Move(source)`; the Copy case passes `source`. Both then read byte offset 1 through a raw pointer. The callee reads only `tag`, so the post-call source observation distinguishes whether the caller's padding stayed initialized.

The source uses `addr_of_mut!(source)` although the custom MIR function parameter is not declared `mut`. This is inside the `mir!` custom-MIR DSL and produces a raw mutable pointer; it does not create a Rust mutable reference. Given the stated custom MIR borrow-checking behavior and the absence of a borrow in the emitted protocol, I found no concrete compile blocker from the binding's source-level mutability. The custom MIR syntax and compiler lowering remain unverified because compilation is prohibited.

The expected output contains 13 harness entries, matching the 13 `#[kani::proof]` functions by name. It records 7 successes and 6 failures. These are expected files only; the names/counts are internally consistent, but they are not observed outcomes.

## Static verdict and limits

No concrete fixture or source-level blocker found in this coverage-only delta. The padded source is fully initialized inside custom MIR before the target Move/Copy, avoiding typed `MaybeUninit` initialization that would discard padding state. The union-return pair exercises initialized and uninitialized payload flow through the normal return slot.

Compilation, MIR lowering, test execution, and all expected outcomes remain `NOT_RUN`. No runtime or proof credit is claimed. The review remains limited to the existing union/MaybeUninit `transfers_shadow` domain; it does not expand B1 or A4 scope.
