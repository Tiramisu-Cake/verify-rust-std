# Named coverage edits

Retain all eight harnesses. All three source files use edition2021 and explicit manual `#[kani::proof]` discovery. No new ignores, generic failure flag, object-bit override, helper framework or file regrouping is recommended.

| Current file / harness | Disposition | Unique purpose and retained oracle |
|---|---|---|
| tests/kani/Intrinsics/Volatile/load_zst.rs — read_volatile_unit_reference | RETAIN | Original5072 public-API reproducer on a reference to unit; retain equality to (). |
| same — read_volatile_dangling_unit | RETAIN | Aligned non-null unit pointer without an allocated readable object; retain unit result equality. |
| same — read_volatile_overaligned_zst | RETAIN | Non-unit, alignment8 ZST via public API; retain typed result equality to Z. Keep Z's repr(align(8)), Debug and PartialEq derives used by assert_eq. |
| same — read_volatile_null_zsts | RETAIN both assertions | Null () and null alignment8 Z ensure the ZST path has no added non-null requirement and zero remains aligned for both layouts. Optional: compute one argument with a counter-increment block and assert the counter is1, preserving the current result assertions. |
| same — intrinsic_volatile_load_zsts | RETAIN both assertions | Direct intrinsic path for dangling aligned Z and null unit, complementing the public API wrapper. Keep both result types; delete only the tautological “Exercise lowering” comment if desired. |
| same — read_volatile_aggregate_zsts | RETAIN | Tuple of [Z;2] and [u8;0], destructured and compared to exact typed arrays. Guards typed construction rather than treating every result as unit. |
| tests/expected/intrinsics/volatile_load/zst_unaligned.rs — misaligned_zst | RETAIN source and separate expected file; STRENGTHEN oracle | without_provenance::<Z>(1) with alignment8 deliberately fails alignment. Keep the specific `src` alignment reason and failed verification; add named harness header and Complete0success/1failure/1total. Retain the local aligned type, independent of the positive suite. |
| tests/expected/intrinsics/volatile_load/zst_uninhabited.rs — uninhabited_zst | RETAIN source and separate expected file; STRENGTHEN oracle | Empty enum cannot have an inhabited result; use its aligned dangling pointer to isolate value validity from misalignment. Keep the specific uninhabited-type safety reason and failed verification; add named harness header and Complete0success/1failure/1total. Confirm actual MIR target presence/absence later before claiming both lowering routes are covered. |

There are no local helper functions to merge. Sharing the two small Z declarations across test modes would add imports and files while joining fixtures with different derives and purposes. The two negative expected files have distinct messages and should remain separate; replacing them with a generic FAILURE-only oracle or a shared broad fallback would lose the cause of failure. The six positives are already in one discoverable source file; shrinking the number of proof attributes provides little useful simplification.

Proposed oracle additions, around each unchanged current expected body:

```text
Checking harness misaligned_zst...
<retain zst_unaligned.expected's four current lines verbatim>
Complete - 0 successfully verified harnesses, 1 failures, 1 total.
```

Use `uninhabited_zst` for the second header and retain its different four-line reason. These are proposed standard-driver output requirements, not newly observed native output. Later authorized validation must confirm the full expected transcript. The static matcher check proves why the completion requirement adds protection against incomplete synthetic failure output; it does not reproduce a compiler failure.
