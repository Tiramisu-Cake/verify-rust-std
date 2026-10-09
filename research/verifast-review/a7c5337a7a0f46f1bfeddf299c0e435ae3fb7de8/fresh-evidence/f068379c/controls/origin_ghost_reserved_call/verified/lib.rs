#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

/*@
lem vf__rust_storage_dead(value: u64)
    req true;
    ens true;
{
}
@*/
pub unsafe fn origin_ghost_reserved_call()
/*@ req true; @*/ /*@ ens true; @*/ {
    let local = 7_u64;
    //@ vf__rust_storage_dead(local); // TARGET: ghost reserved name cannot forge storage event
}
