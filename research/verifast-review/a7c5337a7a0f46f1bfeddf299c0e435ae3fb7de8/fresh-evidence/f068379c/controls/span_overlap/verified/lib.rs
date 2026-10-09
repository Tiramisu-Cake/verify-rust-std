#![no_std]
#![allow(dead_code)]

use core::mem::ManuallyDrop;
use core::ptr;


// Negative: two readonly aliases identify the same positive-sized allocation.
pub unsafe fn span_overlap(p: *const u64)
/*@ req 0 < std::mem::size_of::<u64>() &*& p as usize != 0 &*&
    p as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(p, std::mem::size_of::<u64>()) == true &*&
    p as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    [?f](*p |-> ?v);
@*/ /*@ ens [f](*p |-> v); @*/ {
    let q = p;
    let first = unsafe { *p };
    let second = unsafe { *q };
    let _observed = first == second;
    //@ assert (p as usize + std::mem::size_of::<u64>() <= q as usize || q as usize + std::mem::size_of::<u64>() <= p as usize); // TARGET: overlapping aliases
}
