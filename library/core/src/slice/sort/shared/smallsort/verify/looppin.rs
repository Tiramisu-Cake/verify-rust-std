//! LOOPPIN: loop-contract calibration on Kani cd355b0b, selected only with controls cfg.
//! All domains have fixed backing storage. These checks establish neither arbitrary-length
//! SmallSort safety nor sortedness, permutation, callback frames or termination contracts.
//! The real runtime loops are unchanged; the pointer loop below is a diagnostic copy.

use super::super::insert_tail;
use crate::{kani, ptr};

/// Minimal array-writing loop with symbolic length, including the empty prefix.
#[kani::proof]
#[kani::unwind(8)]
fn calibration_true() {
    let mut backing: [u64; 2] = kani::any();
    let len: usize = kani::any();
    kani::assume(len <= backing.len());
    let mut index = 0;
    #[kani::loop_invariant(index <= len && len <= backing.len())]
    #[kani::loop_modifies(&index, &backing)]
    while index < len {
        backing[index] = 0;
        index += 1;
    }
    kani::assert(index == len, "looppin: calibration reaches the selected end");
    kani::cover(len == 0, "looppin: calibration empty prefix returns");
    kani::cover(len == 1, "looppin: calibration length one returns");
    kani::cover(len == 2, "looppin: calibration length two returns");
}

/// Identical setup, modifies and body; index == 0 holds at entry and fails after a step.
/// The expected failure is the invariant-step check, not a user assertion or bounds check.
#[kani::proof]
#[kani::unwind(8)]
fn calibration_false_control() {
    let mut backing: [u64; 2] = kani::any();
    let len: usize = kani::any();
    kani::assume(len <= backing.len());
    let mut index = 0;
    #[kani::loop_invariant(index <= len && len <= backing.len() && index == 0)]
    #[kani::loop_modifies(&index, &backing)]
    while index < len {
        backing[index] = 0;
        index += 1;
    }
}

/// Stateless reading comparator, shared by the local PFC and the copied-loop consumer.
fn reading_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: the helper must supply initialized readable references to u64 elements.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
    kani::any()
}

/// Match the consumer's exact u64/function-item instantiation and backing-five tail domain.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_u64_tail1_to4_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let before = backing;
    let tail: usize = kani::any();
    kani::assume(1 <= tail && tail < backing.len());
    let begin = backing.as_mut_ptr();
    // SAFETY: the inclusive prefix is initialized, aligned, readable and writable in one
    // allocation, with begin < begin.add(tail). Sortedness is not a safety premise.
    unsafe { insert_tail(begin, begin.add(tail), &mut reading_less_u64) };
    for i in 0..5 {
        kani::assert(i <= tail || backing[i] == before[i], "looppin: insert_tail frame");
    }
    kani::cover(tail == 1, "looppin: insert_tail offset one returns");
    kani::cover(tail == 2, "looppin: insert_tail offset two returns");
    kani::cover(tail == 3, "looppin: insert_tail offset three returns");
    kani::cover(tail == 4, "looppin: insert_tail offset four returns");
}

/// Copy of insertion_sort_shift_left's outer while, fixed to u64 and this comparator.
/// The checked caller supplies 1 <= offset <= len <= 5, as in the real helper's requires.
fn outer_loop_copy(v: &mut [u64], offset: usize) {
    let len = v.len();
    if offset == 0 || offset > len {
        crate::intrinsics::abort_immediate();
    }
    // SAFETY: caller provides an initialized exclusive slice and a nonzero in-range offset.
    unsafe {
        let v_base = v.as_mut_ptr();
        let v_end = v_base.add(len);
        let mut tail = v_base.add(offset);
        #[kani::loop_invariant(
            crate::ub_checks::same_allocation(v_base, tail)
                && crate::ub_checks::same_allocation(v_base, v_end)
                && v_base.addr() < tail.addr()
                && tail.addr() <= v_end.addr()
                && (tail.addr() - v_base.addr()) % crate::mem::size_of::<u64>() == 0
        )]
        #[kani::loop_modifies(&tail, ptr::slice_from_raw_parts_mut(v_base, len))]
        while tail != v_end {
            // SAFETY: the invariant plus the guard place tail strictly inside the slice;
            // the prefix through tail is readable/writable storage in the same allocation.
            insert_tail(v_base, tail, &mut reading_less_u64);
            tail = tail.add(1);
        }
        kani::assert(tail == v_end, "looppin: copied outer loop reaches the selected end");
    }
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn outer_loop_u64_symbolic_len_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let len: usize = kani::any();
    let offset: usize = kani::any();
    kani::assume(1 <= len && len <= backing.len());
    kani::assume(1 <= offset && offset <= len);
    outer_loop_copy(&mut backing[..len], offset);
    kani::cover(offset == len, "looppin: copied outer loop empty suffix returns");
    kani::cover(offset < len, "looppin: copied outer loop nonempty suffix returns");
    kani::cover(len == 5 && offset == 1, "looppin: copied outer loop maximal suffix returns");
}
