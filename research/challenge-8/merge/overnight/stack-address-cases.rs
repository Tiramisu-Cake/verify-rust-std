#![allow(dead_code)]

// Translator-admission diagnostics for stack-address.patch.  These cases are
// intentionally independent; the hosted runner must extract one CASE at a
// time.  Parser acceptance and exact failure locations remain to be checked
// on the pinned hosted tool.  They are not proof negatives.

// CASE_BEGIN stack_address_zero
pub fn stack_address_zero() {
    //@ assert mir_stack_addr(0) == mir_stack_addr(0);
}
// CASE_END stack_address_zero

// CASE_BEGIN stack_address_negative
pub fn stack_address_negative() {
    //@ assert mir_stack_addr(-1) == mir_stack_addr(-1);
}
// CASE_END stack_address_negative

// CASE_BEGIN stack_address_nonliteral
pub fn stack_address_nonliteral(id: usize) {
    //@ assert mir_stack_addr(id) == mir_stack_addr(id);
}
// CASE_END stack_address_nonliteral

// CASE_BEGIN stack_address_wrong_arity
pub fn stack_address_wrong_arity() {
    //@ assert mir_stack_addr(1, 2) == mir_stack_addr(1, 2);
}
// CASE_END stack_address_wrong_arity

// CASE_BEGIN stack_address_high_id
pub fn stack_address_high_id() {
    //@ assert mir_stack_addr(999999) == mir_stack_addr(999999);
}
// CASE_END stack_address_high_id

// CASE_BEGIN stack_address_type_arguments
pub fn stack_address_type_arguments() {
    //@ assert mir_stack_addr::<usize>(1) == mir_stack_addr::<usize>(1);
}
// CASE_END stack_address_type_arguments

// The positive Range/tuple3 probe and scalar/source-named/parameter controls
// require fresh same-SHA MIR local IDs and role certification before insertion.
// Do not infer IDs from an older source or a different annotation set.
