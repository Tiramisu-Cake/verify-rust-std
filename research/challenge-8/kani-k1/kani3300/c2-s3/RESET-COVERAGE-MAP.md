# S3 reset and coverage map — static, execution NOT_RUN

Only C2-S3/F6. This is correctness verification. Runtime, DFCC, F5, F7, SEL1,
composition roots/checker/allowlist and existing fixtures are unchanged.

## Type and extent

`needs_nested_call_reset` excludes `transfers_shadow(ty)` and matches exactly
`PointeeInfo::from_ty(ty) == Err(UnionAsField(_))`. It does not match all errors,
search generic arguments, follow references/pointers, or add transfer support.
The preliminary `ty.layout().is_ok()` prevents a new layout unwrap on unknown
types. Existing whole-value assignment Unsupported remains unchanged.

`SetRef(false)` addresses the actual MIR place without reading its value.
`check_uninit/mod.rs` selects `for_deinit`, whose all-true selection mask covers
the full sized storage extent, including padding. No payload preserve mask is
used. The helper now rejects unsized layouts with existing
`UnknownUnsizedLayout`, as it already did unknown layouts; no nominal size-zero
or unwrap fallback is introduced. Legitimate sized ZST extents remain zero.

The reset affects the operand object's bytes, including any pointer-field
storage, but never the pointed-to objects or adjacent allocation bytes.

## Ordering and alias review

1. Existing operand traversal, resolver and early Unsupported checks run first.
2. Existing Begin/StoreArgument snapshots for every supported argument run
   before every existing supported Move reset and every new nested Move reset.
3. New source resets run Before Call, even with zero supported union_args.
   They address only actual Operand::Move arguments. Copy arguments and the
   function operand are excluded. Addresses are formed before source storage
   can cease to be live.
4. Nested destination reset uses After only if Call.target is Some. MutableBody
   split_bb_after rewires the normal target, not unwind. None/abort has no reset.
5. The normal reset precedes subsequent continuation statements. Later real
   writes/reinit keep their existing setters. StorageLive/Dead are unchanged.

For projected operands, mk_ref takes the exact Place projection. For overlapping
supported/nested arguments, all witnesses are snapshotted before any reset.
For an aliased source/destination, source reset occurs before the call and
destination reset after normal return; conservative false state may discard
returned initialization, intentionally producing false positives. It does not
erase a later write. These are source-established order/extent arguments,
not actual consumed-MIR or model binding evidence.

## Call coverage

| Route | Disposition |
| --- | --- |
| Direct bodyful Item, paired | Existing supported protocol unchanged; nested Move/destination reset appended after all snapshots, including zero-union-argument calls. |
| MIR-backed Shim | Resolver accepts checked_body; supported shadow transfers retain existing unpaired refusal. Nested values receive reset. |
| Foreign Item | Existing allocator models and supported-shadow unpaired refusal unchanged; nested values receive reset, including opaque accepted foreign calls. |
| Backend hook | Hook is not an InstanceKind. Accepted Item/Shim/foreign routes above receive nested reset even when later codegen replaces the body. Bodyless/indirect routes retain resolver refusal. `any_raw<T>` and `untracked_deref<T>` in library/kani_core/src/lib.rs are generic bodyful hook examples; actual instance/consumed MIR remains NOT_RUN. No claim that every hook already rejects top-level shadow values. |
| Intrinsic black_box | Explicit new nested reset; codegen/intrinsic.rs models it as by-value identity. Top-level shadow refusal remains earlier. It was a real source-level F6 transfer route in the old skip arm. |
| Intrinsic Forget | Existing explicit no-effect exception unchanged; no nested reset. No payload read/return. |
| Other no-effect intrinsics | Existing exclusions unchanged. Scalar/numeric/SIMD operations have no nested union value-transfer type in their legal domains; reference/pointer metadata operations do not consume nested objects by value. is_val_statically_known ignores its Copy input and returns bool; existing no-payload-effect exception is preserved, not generalized to black_box. |
| Modeled pointer effects (volatile load/store, typed_swap, copies, atomics, raw_eq) | Existing pointer/read/copy/write model is retained. Nested typed pointee layouts hit existing UnionAsField Unsupported where relevant; raw_eq uses an explicit full byte-array extent and only reference operands. They do not silently gain nested typed transfers. Arbitrary unsupported intrinsics keep their existing Unsupported branch. |
| Function pointer, Virtual/trait object, LlvmIntrinsic, bodyless nonforeign Item/Shim | Existing shared resolve_call diagnostic, visitor-owned Unsupported, pending operations retained. No new reset or broad refusal. |

Primary source: uninit_visitor.rs, ty_layout.rs, check_uninit/mod.rs,
relevant_instruction.rs, transform/body.rs, points_to/points_to_analysis.rs,
codegen/intrinsic.rs, overrides/hooks.rs and library/kani_core/src/lib.rs.
Nearby Rust reference for ignored-input/no-effect classification is
`/tmp/kani3300-g1r2-rust-source/library/core/src/intrinsics/mod.rs`, pinned in
its SOURCES.json to 7189d39d9ce936881b8132c6addeaf3e295cd455. It is not an
identity claim about the CI toolchain.

## Documentation disposition

contracts.md is unchanged. Neither requested baseline false-success nor
candidate intended-failure pair has run. The current limitation and known tuple
false positive stay intact; no narrowing, general aggregate support, full
soundness claim, #3300 closure or proof credit is asserted.
