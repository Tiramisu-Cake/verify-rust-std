#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

fn vf__rust_storage_live(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    let _ = p;
}

pub unsafe fn origin_reserved_live_preserves_resource(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    vf__rust_storage_live(p); // TARGET: reserved ordinary callee preserves resource
}
