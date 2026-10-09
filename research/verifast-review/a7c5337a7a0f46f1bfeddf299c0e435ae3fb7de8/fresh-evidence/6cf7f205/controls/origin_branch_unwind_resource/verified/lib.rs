#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

extern "Rust" {
    fn origin_may_unwind(p: *mut u64);
    //@ req *p |-> ?v;
    //@ ens *p |-> v;
    //@ on_unwind_ens *p |-> v;
}

pub unsafe fn origin_branch_unwind_resource(p: *mut u64, take: bool)
/*@ req *p |-> ?v; @*/
/*@ ens *p |-> v; @*/
/*@ on_unwind_ens *p |-> v; @*/ {
    if take {
        unsafe { origin_may_unwind(p) }; // TARGET: branch callback normal and unwind resource
    }
}
