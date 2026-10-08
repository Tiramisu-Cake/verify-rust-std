#![allow(dead_code)]

// Hosted-only normal-MIR ID discovery templates. The preparer replaces every
// 999999 in each isolated case, then re-exports the exact final source.

// CASE_BEGIN stack_address_named_range
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr(999999): local has a source/debug name"}
pub fn stack_address_named_range(n: usize) {
    let named_range = 0..n;
    //@ assert mir_stack_addr(999999) == mir_stack_addr(999999); // TARGET
    core::mem::forget(named_range);
}
// CASE_END stack_address_named_range

// CASE_BEGIN stack_address_named_tuple
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr(999999): local has a source/debug name"}
pub fn stack_address_named_tuple(n: usize) {
    let named_tuple = (n, n, n);
    //@ assert mir_stack_addr(999999) == mir_stack_addr(999999); // TARGET
    core::mem::forget(named_tuple);
}
// CASE_END stack_address_named_tuple

// CASE_BEGIN stack_address_hidden_scalar
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr(999999): local is not a stock materialized struct"}
pub fn stack_address_hidden_scalar(n: usize) {
    core::hint::black_box(n + 1);
    //@ assert mir_stack_addr(999999) == mir_stack_addr(999999); // TARGET
}
// CASE_END stack_address_hidden_scalar
