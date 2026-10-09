#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

use core::mem::ManuallyDrop;

#[inline(never)]
fn origin_local_may_panic(flag: bool)
/*@ req true; @*/ /*@ ens true; @*/ /*@ on_unwind_ens true; @*/ {
    assert!(!flag);
}

pub unsafe fn origin_local_unwind_cleanup(frame: *const u64, take: bool, panic_flag: bool) -> u64
/*@ req [?f](*frame |-> ?framed); @*/
/*@ ens [f](*frame |-> framed) &*& result == 7; @*/
/*@ on_unwind_ens [f](*frame |-> framed); @*/ {
    let tmp = ManuallyDrop::new(7_u64);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const u64;
    //@ assert (q as usize + std::mem::size_of::<u64>() <= frame as usize || frame as usize + std::mem::size_of::<u64>() <= q as usize);
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<u64>(&tmp, _);
    //@ end_lifetime(k);
    if take {
        origin_local_may_panic(panic_flag); // TARGET: live physical local crosses may-unwind callback
    }
    let result = unsafe { *q };
    result
}
