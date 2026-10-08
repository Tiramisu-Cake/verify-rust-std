// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated primitive-spec and checked-source-adapter diagnostics for usize::is_multiple_of.

// Shared prefix: every isolated CASE includes and checks this source adapter.
pub fn repo_usize_is_multiple_of(value: usize, rhs: usize) -> bool
/*@
req true;
@*//*@
ens result == (if rhs == 0 { value == 0 } else { value % rhs == 0 });
@*//*@
on_unwind_ens false;
@*/
{
    match rhs {
        0 => value == 0,
        _ => value % rhs == 0,
    }
}

// CASE_BEGIN usize_multiple_adapter_formula
pub fn usize_multiple_adapter_formula(value: usize, rhs: usize) -> bool
/*@
req true;
@*//*@
ens result == (if rhs == 0 { value == 0 } else { value % rhs == 0 });
@*//*@
on_unwind_ens false;
@*/
{
    repo_usize_is_multiple_of(value, rhs)
}
// CASE_END usize_multiple_adapter_formula

// CASE_BEGIN usize_multiple_builtin_adapter_frame
pub fn usize_multiple_builtin_adapter_frame(
    value: usize,
    rhs: usize,
    frame: *u32,
) -> bool
/*@
req [?f](*frame |-> ?saved);
@*//*@
ens result == (if rhs == 0 { value == 0 } else { value % rhs == 0 }) &*&
    [f](*frame |-> saved);
@*//*@
on_unwind_ens false;
@*/
{
    let adapter_result = repo_usize_is_multiple_of(value, rhs);
    let builtin_result = value.is_multiple_of(rhs);
    //@ assert adapter_result == builtin_result;
    adapter_result
}
// CASE_END usize_multiple_builtin_adapter_frame

// CASE_BEGIN usize_multiple_boundary_examples
pub fn usize_multiple_boundary_examples() -> bool
/*@
req true;
@*//*@
ens result == true;
@*//*@
on_unwind_ens false;
@*/
{
    let zero_is_multiple_of_zero = (0usize).is_multiple_of(0usize);
    let positive_is_not_multiple_of_zero = (6usize).is_multiple_of(0usize);
    let even_is_multiple_of_two = (8usize).is_multiple_of(2usize);
    let odd_is_not_multiple_of_two = (7usize).is_multiple_of(2usize);
    //@ assert zero_is_multiple_of_zero == true;
    //@ assert positive_is_not_multiple_of_zero == false;
    //@ assert even_is_multiple_of_two == true;
    //@ assert odd_is_not_multiple_of_two == false;
    true
}
// CASE_END usize_multiple_boundary_examples

// CASE_BEGIN usize_multiple_zero_divisor_false_negative
pub fn usize_multiple_zero_divisor_false_negative() -> ()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let actual_result = (6usize).is_multiple_of(0usize);
    //@ assert actual_result == true; // TARGET: primitive result is false for positive self and zero rhs
}
// CASE_END usize_multiple_zero_divisor_false_negative

// CASE_BEGIN usize_multiple_odd_divisor_false_negative
pub fn usize_multiple_odd_divisor_false_negative() -> ()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let actual_result = (7usize).is_multiple_of(2usize);
    //@ assert actual_result == true; // TARGET: primitive result is false for odd self and rhs two
}
// CASE_END usize_multiple_odd_divisor_false_negative
