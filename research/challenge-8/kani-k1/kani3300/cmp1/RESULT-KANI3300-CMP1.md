# RESULT-KANI3300-CMP1 — native partial / acceptance OPEN
Build `77e4765a-d82a-48c8-bf2e-cb6ae2fcdc07`, head `66881e0c52d010af94403a9bcf6dd7775b1d7cfb`; full `6ef9fd72066443f7f113440ba32f77f310520a93` tree `97159e7c2d7ce369fb7cf7fee60c58002a7a2610`; build tree `4c0c56b2808adb542f6e58a59f4672fdc89b439c`; patch `e216f41ca8887c85e19ba84ee56fc6581ee5b95f68ad982e111c5f1b0ca19183`; request `49fb4a6df2268219dd96b29febb4c598b1490e5bc726773760e819949851b53e`; tooling3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c PASS.
Cloud FAILURE / TOOL_ERROR, gate=false; tool-build PASS; native15PASS/3ERROR (offset0IntoIter,1positives,6padding). Spent$0.1755/reserved$0/cap$0.60. R/S/P invariant/review unchanged; diff4files+606/-15. Full checks/covers UNKNOWN; two single-root FC matches below,33root causes UNKNOWN. Core U8/U9(+U1/U2,U6) NOT_RUN/noGO; PFC-OOM OPEN. Details POST-BUILD-OBSERVATIONS.json / POST-BUILD-KANI3300-CMP1.md.
|offset: negative harness|own Failed Checks result|
|---|---|
|2: empty_source_slot_read|FAILURE via golden; own FC UNKNOWN|
|2: empty_copy_destination_slot_read|FAILURE via golden; own FC UNKNOWN|
|3: overwrite_full_destination_with_empty_source_copy|FAILURE via golden; own FC UNKNOWN|
|3: overwrite_full_destination_with_empty_source_move|FAILURE via golden; own FC UNKNOWN|
|3: shifted_empty_source_slot_does_not_reuse_destination_witness|FAILURE via golden; own FC UNKNOWN|
|4: empty_slot_read_in_caller_after_return|FAILURE via golden; own FC UNKNOWN|
|4: first_argument_empty_at_distinct_slot_after_return|FAILURE via golden; own FC UNKNOWN|
|4: second_argument_empty_at_distinct_slot_after_return|FAILURE via golden; own FC UNKNOWN|
|4: initialized_return_does_not_bless_later_empty_return|FAILURE via golden; own FC UNKNOWN|
|4: callee_read_of_nonreturned_second_argument_empty_slot_fails|FAILURE via golden; own FC UNKNOWN|
|4: callee_read_of_nonreturned_first_argument_empty_slot_fails|FAILURE via golden; own FC UNKNOWN|
|4: caller_reads_original_nonreturned_second_argument_copy|FAILURE via golden; own FC UNKNOWN|
|4: caller_reads_original_nonreturned_first_argument_copy|FAILURE via golden; own FC UNKNOWN|
|5: true_unsize_reborrow_empty_index_is_uninitialized|FAILURE via golden; own FC UNKNOWN|
|5: drop_impl_read_of_empty_slot_fails|FAILURE via golden; own FC UNKNOWN|
|5: dropping_ordinary_field_keeps_empty_manually_dropped_neighbor_empty|FAILURE via golden; own FC UNKNOWN|
|5: reset_filled_slot_through_reference_preserves_empty_state|FAILURE via golden; own FC UNKNOWN|
|6: partial_ordinary_field_cannot_be_read_as_whole_product_after_copy|UNKNOWN|
|6: partial_ordinary_field_read_remains_checked_after_call_copy|UNKNOWN|
|6: padding_byte_stays_uninitialized_after_typed_copy|UNKNOWN|
|6: padding_stays_uninitialized_after_call_return|UNKNOWN|
|6: ordinary_operand_aggregate_preserves_typed_source_checks|UNKNOWN|
|7: arbitrary_union_product_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|7: storage_enum_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|7: nested_maybe_uninit_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|7: nested_union_product_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|7: indirect_whole_product_write_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|8: bodyless_shadow_carrying_argument_is_unsupported_before_call|one own FC: shadow-carrying bodyless-call Unsupported; other checks UNKNOWN|
|10: typed_padding_is_not_initialized|FAILURE via golden; own FC UNKNOWN|
|11: typed_source_read_still_checked|FAILURE via golden; own FC UNKNOWN|
|13: overwrite_copy|FAILURE via golden; own FC UNKNOWN|
|14: frame_negative|one own FC: *var_7 not assignable; full list UNKNOWN|
|15: no_mir_shadow_argument_is_unsupported|FAILURE via golden; own FC UNKNOWN|
|16: nested_two_argument_return_reads_uninit|FAILURE via golden; own FC UNKNOWN|
|17: clause_pfc_negative|FAILURE via golden; own FC UNKNOWN|
