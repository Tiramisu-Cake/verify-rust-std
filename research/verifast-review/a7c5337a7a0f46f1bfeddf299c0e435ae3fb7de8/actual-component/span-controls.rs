#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;

/*@
lem initialized_storage_alignment<T>(p: *T)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& p as usize % std::mem::align_of::<T>() == 0;
{
    open [f]points_to::<T>(p, v);
    to_u8s_::<T>(p);
    from_u8s_::<T>(p);
    close [f]points_to::<T>(p, v);
}
@*/

// CASE_BEGIN span_positive
// Minimal live local versus an incoming readonly physical fraction. The old
// generic read/copy control is retained in immutable e6d30d02 evidence; its
// untranslated unwind return produced dead-code, so it gave no full PASS.
pub unsafe fn span_positive(frame: *const i32) -> i32
/*@ req [?f](*frame |-> ?framed); @*/
/*@ ens [f](*frame |-> framed) &*& result == 7; @*/ {
    let tmp = ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const i32;
    //@ assert (q as usize + std::mem::size_of::<i32>() <= frame as usize || frame as usize + std::mem::size_of::<i32>() <= q as usize); // TARGET: positive local versus incoming fractional frame
    let result = unsafe { *q };
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<i32>(&tmp, _);
    //@ end_lifetime(k);
    result
}
// CASE_END span_positive

// CASE_BEGIN span_overlap
// Negative: two readonly aliases identify the same positive-sized allocation.
pub unsafe fn span_overlap(p: *const i32)
/*@ req 0 < std::mem::size_of::<i32>() &*& p as usize != 0 &*&
    p as usize % std::mem::align_of::<i32>() == 0 &*&
    object_pointer_within_limits(p, std::mem::size_of::<i32>()) == true &*&
    p as usize <= usize::MAX - std::mem::size_of::<i32>() &*&
    [?f](*p |-> ?v);
@*/ /*@ ens [f](*p |-> v); @*/ {
    let q = p;
    let first = unsafe { *p };
    let second = unsafe { *q };
    let _observed = first == second;
    //@ assert (p as usize + std::mem::size_of::<i32>() <= q as usize || q as usize + std::mem::size_of::<i32>() <= p as usize); // TARGET: overlapping aliases
}
// CASE_END span_overlap

// CASE_BEGIN span_raw_arbitrary
// Negative: a new local allocation is compared with an arbitrary incoming raw
// address that carries no storage/points-to fact.
pub unsafe fn span_raw_arbitrary(p: *const i32) -> i32
/*@ req p as usize != 0 &*& p as usize % std::mem::align_of::<i32>() == 0 &*&
    object_pointer_within_limits(p, std::mem::size_of::<i32>()) == true &*&
    p as usize <= usize::MAX - std::mem::size_of::<i32>();
@*/ /*@ ens result == 7; @*/ {
    let tmp = ManuallyDrop::new(7_i32);
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const i32;
    //@ assert (q as usize + std::mem::size_of::<i32>() <= p as usize || p as usize + std::mem::size_of::<i32>() <= q as usize); // TARGET: arbitrary incoming raw address
    let result = unsafe { *q };
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<i32>(&tmp, _);
    //@ end_lifetime(k);
    result
}
// CASE_END span_raw_arbitrary


// CASE_BEGIN span_zero_extent
// Negative: a tracked local read from a real typed input has zero extent, so
// a distinct numeric address is not guaranteed by positive-sized disjointness.
pub unsafe fn span_zero_extent<T>(p: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    std::mem::size_of::<T>() == 0 &*& p as usize != 0 &*&
    p as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(p, std::mem::size_of::<T>()) == true &*&
    *p |-> ?v &*& <T>.own(t, v);
@*/ /*@ ens thread_token(t) &*& type_interp::<T>() &*& *p |-> v &*& <T>.own(t, v); @*/ {
    let tmp = ManuallyDrop::new(unsafe { ptr::read(p) });
    //@ let k = begin_lifetime();
    //@ let held_ref = precreate_ref(&tmp);
    //@ merge_fractions lifetime_token(k);
    //@ init_ref_readonly(held_ref, 1/2);
    let q = &*tmp as *const T;
    //@ assert q as usize != p as usize; // TARGET: zero-sized read has no positive extent
    unsafe { ptr::copy_nonoverlapping(q, p, 1); }
    //@ end_ref_readonly(held_ref);
    //@ merge_fractions points_to::<T>(&tmp, _);
    //@ end_lifetime(k);
}
// CASE_END span_zero_extent

// CASE_BEGIN span_retired_local_reuse
// Negative: preserve a raw address after its local lifetime ends, then compare
// it with a new tracked local which may reuse the retired stack slot.
pub unsafe fn span_retired_local_reuse() -> i32
/*@ req true; @*/ /*@ ens result == 9; @*/ {
    let saved = {
        let tmp0 = ManuallyDrop::new(7_i32);
        // Keep this retired epoch free of explicit fraction merges so a later
        // address-taken local remains representable to precreate_ref.
        //@ let k0 = begin_lifetime();
        //@ let ref0 = precreate_ref(&tmp0);
        //@ init_ref_readonly(ref0, 1/2);
        let q0 = &*tmp0 as *const i32;
        //@ end_ref_readonly(ref0);
        //@ end_lifetime(k0);
        q0
    };
    let tmp1 = ManuallyDrop::new(9_i32);
    //@ let k1 = begin_lifetime();
    //@ let ref1 = precreate_ref(&tmp1);
    //@ merge_fractions lifetime_token(k1);
    //@ init_ref_readonly(ref1, 1/2);
    let newq = &*tmp1 as *const i32;
    //@ assert newq as usize != saved as usize; // TARGET: retired local address is not globally fresh
    let result = unsafe { *newq };
    //@ end_ref_readonly(ref1);
    //@ merge_fractions points_to::<i32>(&tmp1, _);
    //@ end_lifetime(k1);
    result
}
// CASE_END span_retired_local_reuse
