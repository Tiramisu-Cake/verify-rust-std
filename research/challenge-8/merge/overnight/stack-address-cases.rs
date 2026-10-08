#![allow(dead_code)]

// Translator-admission diagnostics for stack-address.patch. These cases are
// intentionally independent; the hosted runner must extract one CASE at a
// time. Their exact outcomes are frontend-admission controls, not proof
// negatives: rejected bodies must remain unentered.

// CASE_BEGIN stack_address_zero
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr requires exactly one unsuffixed decimal literal, no type arguments or indices"}
pub fn stack_address_zero() {
    //@ assert mir_stack_addr(0) == mir_stack_addr(0); // TARGET: zero is outside the positive MIR-local-ID domain
}
// CASE_END stack_address_zero

// CASE_BEGIN stack_address_negative
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr requires exactly one unsuffixed decimal literal, no type arguments or indices"}
pub fn stack_address_negative() {
    //@ assert mir_stack_addr(-1) == mir_stack_addr(-1); // TARGET: negative IDs are outside the decimal-literal grammar
}
// CASE_END stack_address_negative

// CASE_BEGIN stack_address_nonliteral
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr requires exactly one unsuffixed decimal literal, no type arguments or indices"}
pub fn stack_address_nonliteral(id: usize) {
    //@ assert mir_stack_addr(id) == mir_stack_addr(id); // TARGET: a runtime value is not a static MIR local ID
}
// CASE_END stack_address_nonliteral

// CASE_BEGIN stack_address_wrong_arity
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr requires exactly one unsuffixed decimal literal, no type arguments or indices"}
pub fn stack_address_wrong_arity() {
    //@ assert mir_stack_addr(1, 2) == mir_stack_addr(1, 2); // TARGET: the marker accepts exactly one argument
}
// CASE_END stack_address_wrong_arity

// CASE_BEGIN stack_address_high_id
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":16,"column_end":30,"message":"mir_stack_addr(999999): raw MIR local ID is absent"}
pub fn stack_address_high_id() {
    //@ assert mir_stack_addr(999999) == mir_stack_addr(999999); // TARGET: this positive ID is absent from the checked MIR body
}
// CASE_END stack_address_high_id

// CASE_BEGIN stack_address_type_arguments
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":39,"column_end":40,"message":"mir_stack_addr requires exactly one unsuffixed decimal literal, no type arguments or indices"}
pub fn stack_address_type_arguments() {
    //@ assert mir_stack_addr::<usize>(1) == mir_stack_addr::<usize>(1); // TARGET: type arguments are not part of the marker grammar
}
// CASE_END stack_address_type_arguments

// The positive Range/tuple3 probe and scalar/source-named/parameter controls
// require fresh same-SHA MIR local IDs and role certification before insertion.
// Do not infer IDs from an older source or a different annotation set.
