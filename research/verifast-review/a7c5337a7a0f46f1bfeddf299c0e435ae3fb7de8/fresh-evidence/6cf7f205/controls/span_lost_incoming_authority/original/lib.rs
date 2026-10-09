#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


// Negative: explicitly discard the incoming physical authority before the
// local's allocation event. This creates only unavailable/dummy authority.
pub unsafe fn span_lost_incoming_authority(p: *mut u64) -> u64
/*@ req *p |-> ?incoming; @*/
/*@ ens result == 9; @*/ {
    //@ leak *p |-> incoming;
    let tmp = ManuallyDrop::new(9_u64);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const u64;
    //@ assert (q as usize + std::mem::size_of::<u64>() <= p as usize || p as usize + std::mem::size_of::<u64>() <= q as usize); // TARGET: leaked incoming authority cannot prove local separation
    let result = unsafe { *q };
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<u64>(&tmp, _);
    //@ end_lifetime(k);
    result
}
