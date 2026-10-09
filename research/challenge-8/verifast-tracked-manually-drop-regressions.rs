#![no_std]
#![allow(dead_code)]

// The runner compiles and verifies one physical case at a time.

// CASE_BEGIN positive_scalar_after_merge
pub unsafe fn positive_scalar_after_merge() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let x = 7_i32;
    //@ let k = begin_lifetime();
    //@ merge_fractions lifetime_token(k);
    let p = &x as *const i32;
    let result = *p;
    //@ end_lifetime(k);
    result
}
// CASE_END positive_scalar_after_merge

// CASE_BEGIN positive_manually_drop_after_merge
pub unsafe fn positive_manually_drop_after_merge() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let tmp = core::mem::ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let p = &*tmp as *const i32;
    let result = *p;
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<i32>(&tmp, _);
    //@ end_lifetime(k);
    result
}
// CASE_END positive_manually_drop_after_merge

// CASE_BEGIN negative_missing_precreated_reference
pub unsafe fn negative_missing_precreated_reference() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let tmp = core::mem::ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    // Deliberately no precreation before the address-scan merge cutoff.
    //@ merge_fractions lifetime_token(k);
    let p = &*tmp as *const i32;
    let result = *p;
    //@ end_lifetime(k);
    result
}
// CASE_END negative_missing_precreated_reference

// CASE_BEGIN negative_missing_reference_initialization
pub unsafe fn negative_missing_reference_initialization() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let tmp = core::mem::ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    let p = &*tmp as *const i32;
    let result = *p;
    //@ end_lifetime(k);
    result
}
// CASE_END negative_missing_reference_initialization

// CASE_BEGIN negative_read_without_permission
pub unsafe fn negative_read_without_permission() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let tmp = core::mem::ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let p = &*tmp as *const i32;
    // Intentionally discard the exact read fraction in this negative case.
    //@ leak [1/2]points_to::<i32>(p, _);
    let result = *p;
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<i32>(&tmp, _);
    //@ end_lifetime(k);
    result
}
// CASE_END negative_read_without_permission
