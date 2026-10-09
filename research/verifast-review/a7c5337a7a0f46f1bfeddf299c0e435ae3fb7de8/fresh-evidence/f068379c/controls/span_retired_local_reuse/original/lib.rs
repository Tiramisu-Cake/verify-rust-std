#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


// Negative: preserve a raw address after its local lifetime ends, then compare
// it with a new tracked local which may reuse the retired stack slot.
pub unsafe fn span_retired_local_reuse() -> u64
/*@ req true; @*/ /*@ ens result == 9; @*/ {
    let saved = {
        let tmp0 = ManuallyDrop::new(7_u64);
        // Keep this retired epoch free of explicit fraction merges so a later
        // address-taken local remains representable to precreate_ref.
        //@ let k0 = begin_lifetime();
        //@ let ref0 = precreate_ref(&tmp0);
        //@ init_ref_readonly(ref0, 1/2);
        let q0 = &*tmp0 as *const u64;
        //@ end_ref_readonly(ref0);
        //@ end_lifetime(k0);
        q0
    };
    let tmp1 = ManuallyDrop::new(9_u64);
    //@ let k1 = begin_lifetime();
    //@ let ref1 = precreate_ref(&tmp1);
    //@ merge_fractions lifetime_token(k1);
    //@ init_ref_readonly(ref1, 1/2);
    let newq = &*tmp1 as *const u64;
    //@ assert newq as usize != saved as usize; // TARGET: retired local address is not globally fresh
    let result = unsafe { *newq };
    //@ end_ref_readonly(ref1);
    //@ merge_fractions points_to::<u64>(&tmp1, _);
    //@ end_lifetime(k1);
    result
}
