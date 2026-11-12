# M2-A minimization ledger — no original obligation discharged

Original matrix: ../m2/QUALIFICATION-MAP.json, exact hash in INPUTS.json (41 existing harness obligations plus six M2 roots). RETAINED means retained as source/request, not proved; QUALIFIED_ELSEWHERE requires an exact property/run binding, and no row qualifies for that status here. Every original combined obligation remains STILL_UNRESOLVED pending coordinator acceptance.

| Feature / original obligation | Draft or reduction | Status and consequence |
| --- | --- | --- |
| Legal ordinary full original body, scalar selected true, array3 writes, equality sites, out assignment | ordinary-singleton removes only the other PFC root | RETAINED; original multi-root/codegen/cache composition STILL_UNRESOLVED; singleton is a separate input |
| Legal PFC useful ensures, modifies(out), frame and private state | C02 retains original root in original file through compiler filtering | RETAINED as non-solving inventory only; actual legal PFC acceptance STILL_UNRESOLVED |
| Ensures scalar7 and array equality, wrapper/capture lowering | C04 disables Assert; C05/C06 remove attrs | STILL_UNRESOLVED for these removed checks; SUCCESS cannot qualify original ensures/frame or fix model |
| Body and root array equality, same assert_eq lowering | C03–C06 keep [u8;3] and assert_eq syntax | RETAINED; actual both-operand raw_eq/CheckAs and promotion bindings UNKNOWN |
| Function-contracts flag without decorated body | C05 vs C06 | RETAINED body; mode/flag axis only, no contract proof credit |
| Both scalar select arms, shadow args1,2/count2, return0/count0 | All drafts retain select; legal picks true, hole picks false | RETAINED; actual source-following false/true transfer pairing STILL_UNRESOLVED |
| Valid returned MU, first hole payload read in ensures | scalar-pfc-hole copies original byte-for-byte | RETAINED, DEFERRED; OOM gives no intended-negative qualification |
| Genuine PFC useful ensures | scalar-pfc-legal uses true-selected initialized17 | RETAINED, DEFERRED; scalar PASS cannot close original array3/PFC/modifies(out) composition |
| Array3 equality sites and modifies(out) frame | Scalar PFC companions omit these legal-pair features | STILL_UNRESOLVED in scalar calibration; not replacement inputs or resource fix |
| Out-pointer full offsets0,2,1; partial legal endpoints0/2 and false middle1 | Original source/golden unchanged; no replacement | RETAINED; all failures incl *const u8 and endpoints UNKNOWN, substring match not qualification |
| Normal false return7 versus true abort no normal continuation | Original source/golden unchanged | RETAINED; matched panic golden lacks actual CFG/trace; true unwind NOT_COVERED |
| Full Quick and original heavy solver combined roots | Not requested in first six configurations | STILL_UNRESOLVED; defer until accepted resource decision |
| Initializedness assumptions/checks/required negative reads/bounds | No alterations; all comparisons retained in faithful drafts | RETAINED; no weakened original or golden expectations |
| C1-T2-A mixed legal controls on other composition | Only coordinator-reported source facts, no import | STILL_UNRESOLVED for M2; no exact M2 property/run establishes equivalence |

No assert_eq→assert substitution, array-size change, model/ABI/setter/registry change, nested MU-of-flat expansion, B3/G1/B4/T1b or M3 activation. Changed attributes/modes and singleton composition are independent inputs, not fixes. No concrete source gap has been established, so no repair is proposed. If a later actual source gap is bound: minimal reproducer + narrow repair proposal + falsifying negative, then STOP for a separate task.

## Original M2 roots: runtime qualification still open

| Root | Source retained / current assurance |
| --- | --- |
| legal-pair::legal_ordinary_transfer | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |
| legal-pair::legal_pfc_transfer | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |
| postcondition-hole::postcondition_reads_returned_hole | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |
| out-pointer::out_pointer_fully_written | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |
| out-pointer::out_pointer_preserves_middle_hole | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |
| normal-abort::normal_return_or_abort | RETAINED unchanged source/golden; STILL_UNRESOLVED, coordinator-reported observations only |

## All inherited obligations (no silent omission)

Paths, source/golden hashes, binding-profile requirements and exact obligation wording remain authoritative in the unchanged M2 matrix referenced by INPUTS.json. No new run/property qualifies any inherited row.

| Original obligation ID | Source/request status | Qualification status |
| --- | --- | --- |
| maybe-uninit-initialized::partial_copy_preserves_written_byte | RETAINED unchanged, profiles normal-destination, immutable-reset, raw-typed | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-initialized::array_value_as_used_by_merge_output | RETAINED unchanged, profiles normal-destination, immutable-reset, raw-typed | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::selected_first_argument_reads_uninit | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::selected_middle_argument_reads_uninit | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::selected_last_argument_reads_uninit | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::nested_same_size_calls_preserve_selected_uninit | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::initialized_argument_return_control | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-pairing::repeated_call_unread_uninit_then_initialized_return | RETAINED unchanged, profiles item-protocol, normal-destination | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-argument-return::argument_return | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-argument-buffer::nested_two_argument_return_reads_uninit | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| item-return-initialized-plain::item_return_preserves_initialized_value | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| item-return-initialized-seeded::item_return_preserves_initialized_value | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| item-return-uninit-plain::item_return_preserves_uninitialized_read | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| item-return-uninit-seeded::item_return_preserves_uninitialized_read | RETAINED unchanged, profiles item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-contract-frame::frame_negative | RETAINED unchanged, profiles item-protocol, contract-private | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-contract-clause::clause_pfc_negative | RETAINED unchanged, profiles item-protocol, contract-private | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::raw_nonoverlapping_copy_preserves_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::raw_copy_preserves_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::typed_assignment_preserves_data | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::typed_argument_return_preserves_data | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::typed_array_preserves_data | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-transfer-data::raw_array_copy_preserves_second_slot_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-assignment-padding::typed_assignment_discards_written_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-argument-padding::typed_argument_discards_written_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-return-padding::typed_return_discards_written_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-array-padding::typed_array_discards_second_slot_padding | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-partial-data::typed_assignment_preserves_unwritten_data | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-typed-array-partial-data::typed_array_preserves_second_slot_unwritten_data | RETAINED unchanged, profiles raw-typed, item-protocol | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_move_reads_initialized_callee_then_uninit_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_move_still_checks_uninitialized_callee_payload | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_move_delivers_initialized_payload_to_callee | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_move_write_still_deinitializes_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_copy_preserves_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::in_place_copy_write_changes_parameter_only | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::ordinary_by_value_temporary_preserves_original_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::union_in_place_move_deinitializes_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::union_in_place_copy_preserves_source | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::union_normal_return_preserves_initialized_byte | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::union_normal_return_preserves_uninitialized_byte | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::padded_custom_move_deinitializes_source_padding | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
| maybe-uninit-call-move::padded_custom_copy_preserves_source_padding | RETAINED unchanged, profiles item-protocol, raw-typed, normal-abnormal | STILL_UNRESOLVED; no new actual property/run |
