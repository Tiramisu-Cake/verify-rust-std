#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

extern "Rust" {
    fn vf__rust_storage_dead(p: *mut u64);
}
/*@
fn vf__rust_storage_dead(p: *mut u64);
req *p |-> ?v;
ens *p |-> v;
on_unwind_ens *p |-> v;
@*/

pub unsafe fn origin_reserved_dead_extern_requires_resource(p: *mut u64)
/*@ req true; @*/ /*@ ens true; @*/ {
    unsafe { vf__rust_storage_dead(p) }; // TARGET: reserved extern callee precondition
}
