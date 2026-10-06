#![no_std]
#![allow(dead_code)]

// Each case is physically isolated before compilation and verification.

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
    //@ merge_fractions lifetime_token(k);
    let p = &*tmp as *const i32;
    let result = *p;
    //@ end_lifetime(k);
    result
}
// CASE_END positive_manually_drop_after_merge

// CASE_BEGIN negative_read_without_permission
pub unsafe fn negative_read_without_permission() -> i32
/*@ req true; @*/ /*@ ens result == 7; @*/ {
    let tmp = core::mem::ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ merge_fractions lifetime_token(k);
    let p = &*tmp as *const i32;
    // Deliberately discard the read permission in this negative fixture.
    //@ leak points_to::<i32>(p, _);
    let result = *p;
    //@ end_lifetime(k);
    result
}
// CASE_END negative_read_without_permission
