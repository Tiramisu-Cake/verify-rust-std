# SEL1 quick CI run 43605855700 (46e46583ff + CI-only f707ffd966) — coordinator excerpt

## Summary
test result: ok. 24 passed; 0 failed; 0 ignored; 0 measured; 653 filtered out; finished in 30.46s
test [expected] expected/uninit/select-unpredictable-moves/copy_intrinsic_operands_preserve_both_sources.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-moves/false_selected_arm_still_deinitializes_source_b.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-moves/true_selected_arm_still_deinitializes_source_b.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-moves/false_selected_arm_still_deinitializes_source_a.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-moves/true_selected_arm_still_deinitializes_source_a.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-copy-overwrite/copy_sources_remain_initialized.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-copy-overwrite/overwriting_selected_hole_reinitializes_result.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-copy-overwrite/overwriting_initialized_destination_with_selected_hole_does_not_retain_true.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-pointer-hole-false/main.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-values/main.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-hint-wrapper/hint_wrapper_u8_uses_all_internal_selects.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-hint-wrapper/hint_wrapper_pointer_preserves_selected_alias_and_payload.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-pointer-hole-true/main.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-delayed-padding/write_through_selected_pointer_leaves_false_source_padding_hole.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-delayed-padding/write_through_selected_pointer_leaves_true_source_padding_hole.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-padding/selected_false_maybe_uninit_fields_are_legal.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-padding/selected_true_maybe_uninit_fields_are_legal.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-padding/selected_true_padding_stays_uninitialized.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-padding/selected_false_padding_stays_uninitialized.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/legal_selected_true_arm_with_unselected_hole.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/selected_false_hole_fails.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/copied_unselected_false_hole_remains_false.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/selected_true_hole_fails.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/copied_unselected_true_hole_remains_false.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-nested-unsupported/main.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-maybe-uninit/legal_selected_false_arm_with_unselected_hole.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-pointer-values/selected_initialized_pointer_values.rs ... FAILED
test [expected] expected/uninit/select-unpredictable-pointer-values/selected_null_or_dangling_without_dereference.rs ... FAILED
test result: FAILED. 205 passed; 28 failed; 2 ignored; 0 measured; 510 filtered out; finished in 737.98s
test result: ok. 17 passed; 0 failed; 0 ignored; 0 measured; 155 filtered out; finished in 1.83s
test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 100 filtered out; finished in 3.70s
test [exec] json-handler/uninit-part1-composition ... FAILED
test result: FAILED. 2 passed; 1 failed; 0 ignored; 0 measured; 17 filtered out; finished in 154.54s

## Format diffs (locations)
Diff in /home/runner/work/kani/kani/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:148:
Diff in /home/runner/work/kani/kani/kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:591:
Diff in /home/runner/work/kani/kani/tests/expected/uninit/select-unpredictable-pointer-hole-false/main.rs:22:
Diff in /home/runner/work/kani/kani/tests/expected/uninit/select-unpredictable-pointer-hole-true/main.rs:22:
Diff in /home/runner/work/kani/kani/tests/expected/uninit/select-unpredictable-nested-unsupported/main.rs:15:

## Aggregated failure descriptions
     28  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, std::mem::MaybeUninit<u8>, std::mem::MaybeUninit<u8>) -> std::mem::MaybeUninit<u8> {std::intrinsics::select_unpredictable::<std::mem::MaybeUninit<u8>>}`: no usable standard fallback with signature (bool, T, T) -> T."
     13 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, std::mem::MaybeUninit<u8>, std::mem::MaybeUninit<u8>) -> std::mem::MaybeUninit<u8> {std::intrinsics::select_unpredictable::<std::mem::MaybeUninit<u8>>}`: no usable standard fallback with signature (bool, T, T) -> T.
      8  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, std::mem::MaybeUninit<Padded>, std::mem::MaybeUninit<Padded>) -> std::mem::MaybeUninit<Padded> {std::intrinsics::select_unpredictable::<std::mem::MaybeUninit<Padded>>}`: no usable standard fallback with signature (bool, T, T) -> T."
      8  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *const u8, *const u8) -> *const u8 {std::intrinsics::select_unpredictable::<*const u8>}`: no usable standard fallback with signature (bool, T, T) -> T."
      4 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, std::mem::MaybeUninit<Padded>, std::mem::MaybeUninit<Padded>) -> std::mem::MaybeUninit<Padded> {std::intrinsics::select_unpredictable::<std::mem::MaybeUninit<Padded>>}`: no usable standard fallback with signature (bool, T, T) -> T.
      4 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *const u8, *const u8) -> *const u8 {std::intrinsics::select_unpredictable::<*const u8>}`: no usable standard fallback with signature (bool, T, T) -> T.
      4  - Description: "Kani does not support reasoning about memory initialization of intrinsic `Unimplemented { name: "caller_location", issue_link: "https://github.com/model-checking/kani/issues/374" }`."
      4  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut u64, *mut u64) -> *mut u64 {std::intrinsics::select_unpredictable::<*mut u64>}`: no usable standard fallback with signature (bool, T, T) -> T."
      3  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut u8, *mut u8) -> *mut u8 {std::intrinsics::select_unpredictable::<*mut u8>}`: no usable standard fallback with signature (bool, T, T) -> T."
      3  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut *const u64, *mut *const u64) -> *mut *const u64 {std::intrinsics::select_unpredictable::<*mut *const u64>}`: no usable standard fallback with signature (bool, T, T) -> T."
      2 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut u64, *mut u64) -> *mut u64 {std::intrinsics::select_unpredictable::<*mut u64>}`: no usable standard fallback with signature (bool, T, T) -> T.
      2  - Description: "Kani does not support reasoning about pointer to unallocated memory"
      2  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, u64, u64) -> u64 {std::intrinsics::select_unpredictable::<u64>}`: no usable standard fallback with signature (bool, T, T) -> T."
      2  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, std::mem::MaybeUninit<*const u64>, std::mem::MaybeUninit<*const u64>) -> std::mem::MaybeUninit<*const u64> {std::intrinsics::select_unpredictable::<std::mem::MaybeUninit<*const u64>>}`: no usable standard fallback with signature (bool, T, T) -> T."
      2  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, char, char) -> char {std::intrinsics::select_unpredictable::<char>}`: no usable standard fallback with signature (bool, T, T) -> T."
      2  - Description: "Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, bool, bool) -> bool {std::intrinsics::select_unpredictable::<bool>}`: no usable standard fallback with signature (bool, T, T) -> T."
      1 isolated-immutable_hole_negative: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `u8`
      1 isolated-immutable_hole_negative: Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type `*const u8`
      1 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, u64, u64) -> u64 {std::intrinsics::select_unpredictable::<u64>}`: no usable standard fallback with signature (bool, T, T) -> T.
      1 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut u8, *mut u8) -> *mut u8 {std::intrinsics::select_unpredictable::<*mut u8>}`: no usable standard fallback with signature (bool, T, T) -> T.
      1 Failed Checks: Kani does not support memory initialization of intrinsic `select_unpredictable` for `fn(bool, *mut *const u64, *mut *const u64) -> *mut *const u64 {std::intrinsics::select_unpredictable::<*mut *const u64>}`: no usable standard fallback with signature (bool, T, T) -> T.

## Panic
10186:thread 'rustc' (22229) panicked at kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs:682:44:
10187-called `Result::unwrap()` on an `Err` value: Os { code: 36, kind: InvalidFilename, message: "File name too long" }
10188-stack backtrace:
command: RUSTFLAGS="--edition 2021 -D warnings" "kani" "/home/runner/work/kani/kani/tests/expected/uninit/select-unpredictable-copy-overwrite/overwriting_initialized_destination_with_selected_hole_does_not_retain_true.rs" "-Z" "uninit-checks" "--output-format=regular" "--harness" "overwriting_initia
