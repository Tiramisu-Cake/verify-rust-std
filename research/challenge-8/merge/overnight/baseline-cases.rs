#![allow(dead_code)]
// Separate VF26.10 normal/unwind/dead-code baseline controls.

// CASE_BEGIN ordinary_call_normal_unwind
#[inline(never)]
fn may_panic(flag: bool) -> i32
/*@ req true; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens true; @*/
{
    assert!(!flag);
    7
}

pub unsafe fn ordinary_call_normal_unwind(flag: bool) -> i32
/*@ req true; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens true; @*/
{
    may_panic(flag)
}
// CASE_END ordinary_call_normal_unwind

// CASE_BEGIN false_unwind_post
#[inline(never)]
fn may_panic_for_false_post(flag: bool) -> i32
/*@ req true; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens true; @*/
{
    assert!(!flag);
    7
}

pub unsafe fn false_unwind_post(flag: bool) -> i32
/*@ req true; @*/
/*@ ens result == 7; @*/
/*@ on_unwind_ens false; @*/
{
    may_panic_for_false_post(flag) // TARGET: callee permits unwind, caller post forbids it
}
// CASE_END false_unwind_post

// CASE_BEGIN unreachable_body_after_panic
pub unsafe fn unreachable_body_after_panic() -> i32
/*@ req true; @*/
/*@ ens false; @*/
/*@ on_unwind_ens true; @*/
{
    assert!(false, "unreachable-body baseline");
    0 // TARGET: normal continuation after the unconditional panic is unreachable
}
// CASE_END unreachable_body_after_panic
