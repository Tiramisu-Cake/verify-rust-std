#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

// CASE_BEGIN origin_reserved_dead_diverge
extern "Rust" {
    fn vf__rust_storage_dead(value: u64) -> !;
    //@ req true;
    //@ ens false;
}

pub unsafe fn origin_reserved_dead_diverge() -> u64
/*@ req true; @*/ /*@ ens false; @*/ {
    let local = 7_u64;
    unsafe { vf__rust_storage_dead(local) } // TARGET: reserved dead diverging extern call
}
// CASE_END origin_reserved_dead_diverge

// CASE_BEGIN origin_reserved_live_diverge
extern "Rust" {
    fn vf__rust_storage_live(value: u64) -> !;
    //@ req true;
    //@ ens false;
}

pub unsafe fn origin_reserved_live_diverge() -> u64
/*@ req true; @*/ /*@ ens false; @*/ {
    let local = 7_u64;
    unsafe { vf__rust_storage_live(local) } // TARGET: reserved live diverging extern call
}
// CASE_END origin_reserved_live_diverge

// CASE_BEGIN origin_plain_diverge
extern "Rust" {
    fn origin_plain_never(value: u64) -> !;
    //@ req true;
    //@ ens false;
}

pub unsafe fn origin_plain_diverge() -> u64
/*@ req true; @*/ /*@ ens false; @*/ {
    let local = 7_u64;
    unsafe { origin_plain_never(local) } // TARGET: plain diverging extern call
}
// CASE_END origin_plain_diverge

// CASE_BEGIN origin_reserved_dead_requires_resource
fn vf__rust_storage_dead(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    let _ = p;
}

pub unsafe fn origin_reserved_dead_requires_resource(p: *mut u64)
/*@ req true; @*/ /*@ ens true; @*/ {
    vf__rust_storage_dead(p); // TARGET: reserved name ordinary callee precondition
}
// CASE_END origin_reserved_dead_requires_resource

// CASE_BEGIN origin_reserved_dead_extern_requires_resource
extern "Rust" {
    fn vf__rust_storage_dead(p: *mut u64);
    //@ req *p |-> ?v;
    //@ ens *p |-> v;
}

pub unsafe fn origin_reserved_dead_extern_requires_resource(p: *mut u64)
/*@ req true; @*/ /*@ ens true; @*/ {
    unsafe { vf__rust_storage_dead(p) }; // TARGET: reserved extern callee precondition
}
// CASE_END origin_reserved_dead_extern_requires_resource

// CASE_BEGIN origin_reserved_live_preserves_resource
fn vf__rust_storage_live(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    let _ = p;
}

pub unsafe fn origin_reserved_live_preserves_resource(p: *mut u64)
/*@ req *p |-> ?v; @*/ /*@ ens *p |-> v; @*/ {
    vf__rust_storage_live(p); // TARGET: reserved ordinary callee preserves resource
}
// CASE_END origin_reserved_live_preserves_resource

// CASE_BEGIN origin_unit_layout
pub unsafe fn origin_unit_layout()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ assert std::mem::size_of::<()>() == 0; // TARGET: concrete unit size zero
}
// CASE_END origin_unit_layout
