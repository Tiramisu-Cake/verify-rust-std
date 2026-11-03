//! LOOPINV diagnostic pilot: the loop contract on the outer pointer loop of
//! `insertion_sort_shift_left`; selected explicitly, never an ordinary suite entry.
//! The two copies of that loop are tool controls, not proofs of the real helper.
//! Every root is bounded: no unbounded safety claim follows from any outcome.

use crate::mem::size_of;
use crate::{intrinsics, kani, ptr};

/// Read-only comparator: reads both references and returns an arbitrary result. Under the
/// loop contract it runs only in the abstracted step, so its cover marks that step reachable.
fn reading_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: initialized readable references; volatile reads retain both accesses.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
    kani::cover(true, "loopinv: abstracted step reaches the comparator");
    kani::any()
}

#[kani::proof]
#[kani::unwind(5)]
fn loopinv_insertion_u64_n2_offset1() {
    let mut v: [u64; 2] = kani::any();
    super::super::super::insertion_sort_shift_left(&mut v, 1, &mut reading_less_u64);
    kani::cover(true, "loopinv: insertion returns after the abstracted loop");
}

/// Copy of the outer loop of `insertion_sort_shift_left` with the same invariant and
/// modifies; the body reads and rewrites `*tail` instead of calling `insert_tail`.
fn outer_loop_copy_true<T>(v: &mut [T], offset: usize) {
    let len = v.len();
    if offset == 0 || offset > len {
        intrinsics::abort_immediate();
    }
    // SAFETY: as in `insertion_sort_shift_left`: offset <= len and tail != v_end in the body.
    unsafe {
        let v_base = v.as_mut_ptr();
        let v_end = v_base.add(len);
        let mut tail = v_base.add(offset);
        #[kani::loop_invariant(
            size_of::<T>() == 0
                || (crate::ub_checks::same_allocation(v_base, tail)
                    && crate::ub_checks::same_allocation(v_base, v_end)
                    && v_base.addr() < tail.addr()
                    && tail.addr() <= v_end.addr()
                    && (tail.addr() - v_base.addr()) % size_of::<T>() == 0)
        )]
        #[kani::loop_modifies(&tail, ptr::slice_from_raw_parts(v_base, len))]
        while tail != v_end {
            kani::cover(true, "loopinv copy true: abstracted step body reached");
            tail.write(tail.read());
            tail = tail.add(1);
        }
    }
}

/// The same copy whose invariant adds a conjunct that is false as a loop invariant: it holds
/// on entry at offset one and is broken by the first step (tail moves to the second element).
fn outer_loop_copy_false<T>(v: &mut [T], offset: usize) {
    let len = v.len();
    if offset == 0 || offset > len {
        intrinsics::abort_immediate();
    }
    // SAFETY: as in `insertion_sort_shift_left`: offset <= len and tail != v_end in the body.
    unsafe {
        let v_base = v.as_mut_ptr();
        let v_end = v_base.add(len);
        let mut tail = v_base.add(offset);
        #[kani::loop_invariant(
            size_of::<T>() == 0
                || (crate::ub_checks::same_allocation(v_base, tail)
                    && crate::ub_checks::same_allocation(v_base, v_end)
                    && v_base.addr() < tail.addr()
                    && tail.addr() <= v_end.addr()
                    && (tail.addr() - v_base.addr()) % size_of::<T>() == 0
                    && tail.addr() - v_base.addr() == size_of::<T>())
        )]
        #[kani::loop_modifies(&tail, ptr::slice_from_raw_parts(v_base, len))]
        while tail != v_end {
            kani::cover(true, "loopinv copy false: abstracted step body reached");
            tail.write(tail.read());
            tail = tail.add(1);
        }
    }
}

#[kani::proof]
#[kani::unwind(5)]
fn loopinv_copy_true() {
    let mut v: [u64; 2] = kani::any();
    outer_loop_copy_true(&mut v, 1);
    kani::cover(true, "loopinv copy true: returns after the abstracted loop");
}

#[kani::proof]
#[kani::unwind(5)]
fn loopinv_copy_false_control() {
    let mut v: [u64; 2] = kani::any();
    outer_loop_copy_false(&mut v, 1);
}
