#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


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
