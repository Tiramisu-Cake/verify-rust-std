# Finite native controls — all NOT_RUN

Each exact selector is run alone for the acceptance oracle. Source/expected files are proposals, never execution evidence. Summary failure counts have no expected total-check inventories. No initializedness or alias assumptions/global skips. Native wrappers call the real intrinsic; hint controls call the complete public wrapper.

| File group | Exact selector | Expected failed properties | Result |
| --- | --- | ---: | --- |
| select-unpredictable-copy-overwrite | `copy_sources_remain_initialized` | 0 | SUCCESS |
| select-unpredictable-copy-overwrite | `overwriting_selected_hole_reinitializes_result` | 0 | SUCCESS |
| select-unpredictable-copy-overwrite | `overwrite_hole` | 1 | FAILURE |
| select-unpredictable-delayed-padding | `write_through_selected_pointer_leaves_true_source_padding_hole` | 1 | FAILURE |
| select-unpredictable-delayed-padding | `write_through_selected_pointer_leaves_false_source_padding_hole` | 1 | FAILURE |
| select-unpredictable-hint-wrapper | `hint_wrapper_u8_uses_all_internal_selects` | 0 | SUCCESS |
| select-unpredictable-hint-wrapper | `hint_wrapper_pointer_preserves_selected_alias_and_payload` | 0 | SUCCESS |
| select-unpredictable-maybe-uninit | `legal_selected_true_arm_with_unselected_hole` | 0 | SUCCESS |
| select-unpredictable-maybe-uninit | `legal_selected_false_arm_with_unselected_hole` | 0 | SUCCESS |
| select-unpredictable-maybe-uninit | `copied_unselected_false_hole_remains_false` | 1 | FAILURE |
| select-unpredictable-maybe-uninit | `copied_unselected_true_hole_remains_false` | 1 | FAILURE |
| select-unpredictable-maybe-uninit | `selected_true_hole_fails` | 1 | FAILURE |
| select-unpredictable-maybe-uninit | `selected_false_hole_fails` | 1 | FAILURE |
| select-unpredictable-moves | `copy_intrinsic_operands_preserve_both_sources` | 0 | SUCCESS |
| select-unpredictable-moves | `true_selected_arm_still_deinitializes_source_a` | 1 | FAILURE |
| select-unpredictable-moves | `false_selected_arm_still_deinitializes_source_a` | 1 | FAILURE |
| select-unpredictable-moves | `true_selected_arm_still_deinitializes_source_b` | 1 | FAILURE |
| select-unpredictable-moves | `false_selected_arm_still_deinitializes_source_b` | 1 | FAILURE |
| select-unpredictable-nested-unsupported | `nested_shadow_layout_remains_unsupported` | 1 | FAILURE |
| select-unpredictable-padding | `selected_true_maybe_uninit_fields_are_legal` | 0 | SUCCESS |
| select-unpredictable-padding | `selected_false_maybe_uninit_fields_are_legal` | 0 | SUCCESS |
| select-unpredictable-padding | `selected_true_padding_stays_uninitialized` | 1 | FAILURE |
| select-unpredictable-padding | `selected_false_padding_stays_uninitialized` | 1 | FAILURE |
| select-unpredictable-pointer-hole-false | `selected_hole_in_false_arm_fails` | 1 | FAILURE |
| select-unpredictable-pointer-hole-true | `selected_hole_in_true_arm_fails` | 1 | FAILURE |
| select-unpredictable-pointer-values | `selected_initialized_pointer_values` | 0 | SUCCESS |
| select-unpredictable-pointer-values | `selected_null_or_dangling_without_dereference` | 0 | SUCCESS |
| select-unpredictable-unmodeled-intrinsic | `unmodeled_shadow_intrinsic_stays_unsupported` | 1 | FAILURE |
| select-unpredictable-values | `selected_scalar_values` | 0 | SUCCESS |

Required own SUCCESS descriptions, intended failure descriptions/source operations and original regression scopes are in CONTROL-MANIFEST.json. Move tests split A/B observations and both selections; ordinary tuples avoid nested-storage admission. Copy is expressed by bare places in custom MIR (snapshot mir.rs Operands), Move by Move(place). Typed field legality and padding failure are distinct controls.

compiletest lines are substring matches; status+description pairs use one trailing backslash to require adjacent lines. Each selector now has one execution and one expected file (multi-root sources share controls.inc through isolated exact root wrappers); statuses/counts cannot match a sibling harness output. Summary pins failed properties only, never full totals.

No source fixture can select compiler-state absent/overridden fallback or legal unsized T for this intrinsic; these are explicit static guard controls, not claimed executed tests. BlackBox<MU<u8>> and nested MU payload supply executable refusal controls. Original B1/bodyless/conflict suites remain required and unchanged.

Total: 29 native selectors in12 new groups, plus6 named std rows. All compile/Kani/verdict/coverage outcomes NOT_RUN.

Final fixture paths and per-selector expected files are in CONTROL-MANIFEST.json. Shared controls.inc retains the reviewed Rust items; root wrapper crate flags/features are preserved.

Followup43605855700: current sourceb6f1b08eb512ff9006aff7b4924c2e8f13930d70; overwrite_hole is the shortened existing selector, not a removed control; still29 roots, all new outcomes NOT_RUN.
