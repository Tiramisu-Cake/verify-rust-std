#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


// Minimal live local versus an incoming readonly physical fraction. The old
// generic read/copy control is retained in immutable e6d30d02 evidence; its
// untranslated unwind return produced dead-code, so it gave no full PASS.
pub unsafe fn span_positive(frame: *const u64) -> u64
/*@ req [?f](*frame |-> ?framed); @*/
/*@ ens [f](*frame |-> framed) &*& result == 7; @*/ {
    let tmp = ManuallyDrop::new(7_u64);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const u64;
    //@ assert (q as usize + std::mem::size_of::<u64>() <= frame as usize || frame as usize + std::mem::size_of::<u64>() <= q as usize); // TARGET: positive local versus incoming fractional frame
    let result = unsafe { *q };
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<u64>(&tmp, _);
    //@ end_lifetime(k);
    result
}
