#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

fn vf__rust_storage_dead(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    let _ = p;
}

pub unsafe fn origin_reserved_dead_requires_resource(p: *mut u64)
/*@ req true; @*/ /*@ ens true; @*/ {
    vf__rust_storage_dead(p); // TARGET: reserved name ordinary callee precondition
}
