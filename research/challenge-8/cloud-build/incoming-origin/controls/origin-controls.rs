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

// CASE_BEGIN origin_unit_runtime_layout
pub unsafe fn origin_unit_runtime_layout()
/*@ req true; @*/ /*@ ens true; @*/ {
    let runtime_size = core::mem::size_of::<()>();
    //@ assert runtime_size == 0; // TARGET: runtime concrete unit size zero
}
// CASE_END origin_unit_runtime_layout

// CASE_BEGIN origin_ghost_reserved_call
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
// CASE_END origin_ghost_reserved_call

// CASE_BEGIN origin_local_death_lost_cell
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
// CASE_END origin_local_death_lost_cell

// CASE_BEGIN origin_branch_unwind_resource
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
// CASE_END origin_branch_unwind_resource

// CASE_BEGIN origin_local_unwind_cleanup
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
// CASE_END origin_local_unwind_cleanup
