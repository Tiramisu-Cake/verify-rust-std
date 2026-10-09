#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


// Negative: a new local allocation is compared with an arbitrary incoming raw
// address that carries no storage/points-to fact.
pub unsafe fn span_raw_arbitrary(p: *const u64) -> u64
/*@ req p as usize != 0 &*& p as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(p, std::mem::size_of::<u64>()) == true &*&
    p as usize <= usize::MAX - std::mem::size_of::<u64>();
@*/ /*@ ens result == 7; @*/ {
    let tmp = ManuallyDrop::new(7_u64);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const u64;
    //@ assert (q as usize + std::mem::size_of::<u64>() <= p as usize || p as usize + std::mem::size_of::<u64>() <= q as usize); // TARGET: arbitrary incoming raw address
    let result = unsafe { *q };
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<u64>(&tmp, _);
    //@ end_lifetime(k);
    result
}
