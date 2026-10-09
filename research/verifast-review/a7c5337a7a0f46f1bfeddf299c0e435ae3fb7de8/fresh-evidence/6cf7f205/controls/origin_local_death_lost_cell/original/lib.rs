#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

use core::mem::ManuallyDrop;

pub unsafe fn origin_local_death_lost_cell() -> u64
/*@ req true; @*/ /*@ ens result == 9; @*/ {
    let result = {
        let tmp = ManuallyDrop::new(7_u64);
        //@ leak points_to::<u64>(&tmp, _);
        9_u64
    }; // TARGET: local death after physical cell leak
    result
}
