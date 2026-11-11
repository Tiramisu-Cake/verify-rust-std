# KANI3300 G1R2 — independent static review

Verdict: **No static blocker found; reviewed test delta and sweep are consistent with the stated controls.** This is not a GO, compilation result, or proof credit.

## Identities

- Baseline: `3d085249c9c6c49a9c2e5747e2167d629748fb70`
- Candidate: `02b734151ada1dd0d216b0db329776eb522d2d67`; tree `cc8e8747e3ed3fc35d267ee9a5f0bbfd2cac83c5`
- Review packet SHA256: `e6f849181b5bc4ce031c5c2f499b0873ea7384435dab8aea758e74d6b9081b81`; `review check` state `PACKET_VALID_NOT_REVIEWED`
- Spec SHA256: `fc3608ee50112925eb19badbd6bbbdec6d2e0b7a86fdb8206a250dbd6e49fbf1`
- Packet diff SHA256: `66311c5d89a36e4a6401797f423eed61483da1087c48776b82a07a49f5f36a58`
- TEST-SWEEP.md SHA256: `963fd018b4d34612639bc4000e872223358dcdda75b9fcb4b008534155d4a234`
- TEST-MANIFEST.json SHA256: `6b2eeb71d1618999cc296805510c1c66a54ad399568eb071120315fe0ff39050`
- RUST-SOURCES.json SHA256: `ab98668843515b26fc0e7a5d86e1d6733bb188363576ac37e658380092fdb27d`; pinned source hashes match the local Rust source snapshot.

## Findings

- The committed delta contains five test paths only; no production path differs from the baseline. The G1 manifest retains all 63 positive and 70 negative harness names and outcomes. Changed source bodies are limited to explicit raw-union field reads and explicit `ManuallyDrop` borrows; the negative and positive goldens remain unchanged.
- The 15 positive and 8 negative `ManuallyDrop` borrow edits preserve the same field, tuple, array-element, and padding projections. They do not suppress the nightly `dangerous_implicit_autorefs` lint. The `reject_manuallydrop_union` edit makes the wrapper borrow explicit while retaining `ManuallyDrop<U>` as the accessed pointee, so the original `UnionAsField` guard remains in the path.
- `reject_union_transmute` now declares a local `repr(C, align(8))` union with an 8-byte layout and transmutes that union to `[u64; 1]`. The original union-transmute handling still reaches the existing incompatible-layout safety check; no helper or diagnostic expectation changed.
- The init-predicate golden change is supported by the source path: `can_dereference` calls `assert_is_initialized`, which calls the marked `is_initialized` intrinsic; the intrinsic inserts the Unsupported check for `PointeeLayout::Union`. The new `kani::mem::is_initialized::<U>.unsupported_construct.1` property therefore names the intended guard at the expanded API site (`library/kani/src/lib.rs:63`), with failure reason, harness, and summary retained.
- Static sweep review covered the 23 fixture mains and shared include: edition 2021, include resolution, imports/types, unsafe union/raw operations, guard routing, harness count, and deny/forbid attributes. No statically identifiable compile or naming blocker found. The manifest's package B fixtures and expected records are unchanged by the candidate delta.

## Limits

No rustc, Cargo, Kani, CBMC, build, or Cloud execution was performed. Compiler/lint behavior and native verification remain **NOT_RUN**; proof credit is **NONE**.
