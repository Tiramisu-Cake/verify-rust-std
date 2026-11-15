# SEL1-C2 control map

Candidate `14bc57fdb99960240c4944845a3d985c8af4dcf7`. All new outcomes **NOT_RUN**. Exactly 29 selectors: 12 intended SUCCESS and 17 intended FAILURE/Unsupported. All 65 fixture files, including corrected goldens, are byte-identical to 39a6521bf1. Full exact descriptions, required own SUCCESS assertions, paths and hashes: `CONTROL-MAP.json`.

| Group | Exact selector | Intended failures / result | Operation or exact refusal boundary |
| --- | --- | --- | --- |
| copy-overwrite | `copy_sources_remain_initialized` | 0 / SUCCESS | Copy sources and selected payload remain readable. |
| copy-overwrite | `overwriting_selected_hole_reinitializes_result` | 0 / SUCCESS | A write replaces the selected hole and makes its payload readable. |
| copy-overwrite | `overwrite_hole` | 1 / Uninit | Read overwritten destination after selecting a hole; previous true state must be replaced. |
| delayed-padding | `write_through_selected_pointer_leaves_true_source_padding_hole` | 1 / Uninit | Read x as u64 after typed Padded write through selected pointer; true branch leaves source padding false. |
| delayed-padding | `write_through_selected_pointer_leaves_false_source_padding_hole` | 1 / Uninit | Read y as u64 after typed Padded write through selected pointer; false branch leaves source padding false. |
| hint-wrapper | `hint_wrapper_u8_uses_all_internal_selects` | 0 / SUCCESS | Real public wrapper including its pointer and MaybeUninit selects/assume_init, u8. |
| hint-wrapper | `hint_wrapper_pointer_preserves_selected_alias_and_payload` | 0 / SUCCESS | Real public wrapper, chosen pointer alias and payload preserved. |
| maybe-uninit | `legal_selected_true_arm_with_unselected_hole` | 0 / SUCCESS | Read initialized true arm; unselected false arm is a hole. |
| maybe-uninit | `legal_selected_false_arm_with_unselected_hole` | 0 / SUCCESS | Read initialized false arm; unselected true arm is a hole. |
| maybe-uninit | `copied_unselected_false_hole_remains_false` | 1 / Uninit | Read original unselected false-arm Copy hole after selected result succeeds. |
| maybe-uninit | `copied_unselected_true_hole_remains_false` | 1 / Uninit | Read original unselected true-arm Copy hole after selected result succeeds. |
| maybe-uninit | `selected_true_hole_fails` | 1 / Uninit | Read selected true-arm MaybeUninit payload; original unselected Copy value remains valid. |
| maybe-uninit | `selected_false_hole_fails` | 1 / Uninit | Read selected false-arm MaybeUninit payload; original unselected Copy value remains valid. |
| moves | `copy_intrinsic_operands_preserve_both_sources` | 0 / SUCCESS | Custom MIR Copy operands: selected result and both original sources readable, both conditions covered. |
| moves | `true_selected_arm_still_deinitializes_source_a` | 1 / Uninit | Actual Move of both arms; read moved-from source A after consuming true-chosen initialized result. |
| moves | `false_selected_arm_still_deinitializes_source_a` | 1 / Uninit | Actual Move of both arms; read moved-from source A after consuming false-chosen initialized result. |
| moves | `true_selected_arm_still_deinitializes_source_b` | 1 / Uninit | Actual Move of both arms; read moved-from source B after consuming true-chosen initialized result. |
| moves | `false_selected_arm_still_deinitializes_source_b` | 1 / Uninit | Actual Move of both arms; read moved-from source B after consuming false-chosen initialized result. |
| nested-unsupported | `nested_shadow_layout_remains_unsupported` | 1 / Unsupported | First Nested aggregate construction hits general UnionAsField before select; NOT select-specific guard coverage. |
| padding | `selected_true_maybe_uninit_fields_are_legal` | 0 / SUCCESS | Chosen true-arm typed fields readable; no requirement that padding be initialized. |
| padding | `selected_false_maybe_uninit_fields_are_legal` | 0 / SUCCESS | Chosen false-arm typed fields readable; no requirement that padding be initialized. |
| padding | `selected_true_padding_stays_uninitialized` | 1 / Uninit | Read true-arm result padding byte after legal field reads; padding remains false. |
| padding | `selected_false_padding_stays_uninitialized` | 1 / Uninit | Read false-arm result padding byte after legal field reads; padding remains false. |
| pointer-hole-false | `selected_hole_in_false_arm_fails` | 1 / Uninit | Dereference selected pointer to false-arm uninitialized byte; alias assertion must succeed. |
| pointer-hole-true | `selected_hole_in_true_arm_fails` | 1 / Uninit | Dereference selected pointer to true-arm uninitialized byte; alias assertion must succeed. |
| pointer-values | `selected_initialized_pointer_values` | 0 / SUCCESS | Choose pointer to initialized value with correct alias/readback. |
| pointer-values | `selected_null_or_dangling_without_dereference` | 0 / SUCCESS | Select null/dangling pointer values without dereference or pointee initialization. |
| unmodeled-intrinsic | `unmodeled_shadow_intrinsic_stays_unsupported` | 1 / Unsupported | BlackBox<MaybeUninit<u8>> retains explicit unsupported shadow argument/return refusal. |
| values | `selected_scalar_values` | 0 / SUCCESS | Actual core/std intrinsic path preserves chosen scalar value. |

`nested-unsupported` rejects the Nested aggregate through UnionAsField before reaching select. It supplies no runtime credit for the select-specific layout guard. Absent/overridden fallback and unsized T remain static-only: no source fixture executes those compiler-state/signature cases. BlackBox is the other explicit Unsupported control.

The original C2 mode/Replace/Recursive/hook/mixed-root, S5 mutation and F7 isolation suites remain unchanged. No new ignore, golden relaxation or test filter was introduced. Historical 29/0 on 39a6521bf1 is compiletest evidence; new Quick/Gate A/replay and independent proof credit remain NOT_RUN/NONE.
