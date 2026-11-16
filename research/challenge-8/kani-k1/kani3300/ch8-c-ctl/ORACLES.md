# C source oracles — all NOT_RUN

Prefix for all roots: `slice::sort::shared::smallsort::verify::c_controls::`.
Exact source-qualified form additionally begins with `core::`. No generated property
IDs have been invented. The control request contains exact selectors, target names,
unwinds, expected diagnostics and cover descriptions. Source assertions below have
literal descriptions; stock JSON exports aggregate successful checks without their
names, so this table is a correlation requirement for later review, not observed credit.

| Root | Expected | Named source assertion descriptions | Reachability descriptions |
| --- | --- | --- | --- |
| `c_merge_source_write_restore` | FAIL assigns/frame; other failures separate | `C_MERGE_ARGUMENT_IS_SOURCE_SLOT`, `C_MERGE_LIVE_REFERENCE_RESTORED`, `C_MERGE_SOURCE_FINAL`, `C_MERGE_OUTPUT` must not be the negative oracle | `C_merge_callback`, `C_N1_transient_write`, `C_merge_live_read_after_restore`, `C_merge_return` |
| `c_merge_source_read_only` | PASS | `C_MERGE_ARGUMENT_IS_SOURCE_SLOT`, `C_MERGE_LIVE_REFERENCE_RESTORED`, `C_MERGE_SOURCE_FINAL`, `C_MERGE_OUTPUT` | `C_merge_callback`, `C_merge_live_read_after_restore`, `C_merge_return` |
| `c_callback_live_shared_in_outer_frame` | Stock PASS diagnostic ALIAS_GAP | `C_N2_ARGUMENT_IS_TAIL`, `C_OUTER_LIVE_REFERENCE_RESTORED`, `C_OUTER_OUTPUT`; these final assertions do not establish legal transient access | `C_outer_callback`, `C_N2_transient_write`, `C_outer_live_read_after_restore`, `C_outer_return` |
| `c_callback_read_only_in_outer_frame` | PASS | `C_N2_ARGUMENT_IS_TAIL`, `C_OUTER_LIVE_REFERENCE_RESTORED`, `C_OUTER_OUTPUT` | `C_outer_callback`, `C_outer_live_read_after_restore`, `C_outer_return` |
| `c_external_mut_state` | PASS | `C_L3_MUT_OUTPUT` (sorted pair and counter exactly 1) | `C_L3_mut_changed`, `C_L3_mut_return` |
| `c_external_cell_state` | PASS | `C_L3_CELL_OUTPUT` (sorted pair and counter exactly 1) | `C_L3_cell_changed`, `C_L3_cell_return` |
| `c_insert_tail_local_lifetime` | PASS | `C_L4_N3_COPY_BACK`, `C_L4_OUTPUT_PERMUTATION_SUFFIX` | `C_L4_tmp_comparison_after_gap_shift`, `C_L4_gap_shift_and_copy_back`, `C_L4_next_insertion_return` |
| `c_local_storage_reuse` | PASS | `C_L4_FIRST_LIVE_READ`, `C_L4_FRESH_LIVE_READ` | `C_L4_scoped_read`, `C_L4_reinitialized_read_return` |

N1's generated negative property must have exported class exactly `assigns`, named
description matching `^Check that .+ is assignable$`, and source file/line binding to
the volatile writes at `verify/c_controls.rs:23` or `:25` on the pinned std commit.
One or more matching checks are allowed; every failed property must match.
Unmatched pointer/alias/unwind/assertion/setup failures remain INCONCLUSIVE/UNKNOWN.
If lowering reports a different location, retain the original result and diagnose
binding; do not broaden this matcher to turn an unknown into detection. The future
receipt must establish real helper/generated modifies wrapper/callback binding,
retention of both writes, and source-label-to-cover-ID correspondence.

N2 is a deliberately invalid shared-reference write scenario. Its PASS means only
the stock run did not detect that violation; qualify ALIAS_GAP using actual body,
write and reachability evidence before extending a diagnostic claim. No C PASS,
generic borrow inventory, alias enforcement or unwind claim follows from any row.
