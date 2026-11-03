//! Opt-in N2 forwarding contracts for the two remaining trait entries, same form as the parent:
//! u8 through the Stable Freeze impl (general with caller scratch) and Cell<u8> through the
//! Unstable blanket impl (fallback insertion). No specification calls the comparator.

use super::super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
use super::{
    always_true, byte_less, canonical, canonical_guard, cell_less, input_covers, pair_count,
    pair_region, pair_sorted,
};
use crate::cell::Cell;
use crate::mem::MaybeUninit;
use crate::ub_checks::{can_write, same_allocation};
use crate::{kani, ptr, slice};

// Raw scratch keeps the exclusivity of two &mut slices, as `stable_region`. The Freeze route
// aborts when scratch.len() < len + 16, so that minimum is part of the precondition.
fn freeze_scratch<const N: usize>(v: *mut u8, scratch: *mut MaybeUninit<u8>, len: usize) -> bool {
    len >= N + 16
        && can_write(ptr::slice_from_raw_parts_mut(scratch, len))
        && (!same_allocation(v as *const u8, scratch.cast::<u8>() as *const u8) || {
            // SAFETY: both nonempty regions are live and in the same allocation.
            // MaybeUninit<u8> and u8 have identical size and alignment.
            let d = unsafe { scratch.cast::<u8>().offset_from(v) };
            if d >= 0 { d as usize >= N } else { d.unsigned_abs() >= len }
        })
}

// u8 is Freeze: the specialized Stable entry runs small_sort_general_with_scratch. At N2 it copies
// two singleton halves into scratch[0..2] and merges them back into v; both regions are written.
#[kani::requires(pair_region(v) && freeze_scratch::<2>(v, scratch, scratch_len))]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(
    ptr::slice_from_raw_parts_mut(v, 2),
    ptr::slice_from_raw_parts_mut(scratch, scratch_len)
)]
#[kani::ensures(|_| pair_sorted(v))]
#[kani::ensures(|_| old(pair_count(v, probe)) == pair_count(v, probe))]
unsafe fn stable_freeze_byte(
    v: *mut u8,
    scratch: *mut MaybeUninit<u8>,
    scratch_len: usize,
    cmp: fn(&u8, &u8) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: the requires establish two initialized writable elements and a disjoint
    // writable scratch of scratch_len slots.
    let (v, scratch) = unsafe {
        (slice::from_raw_parts_mut(v, 2), slice::from_raw_parts_mut(scratch, scratch_len))
    };
    let mut is_less = cmp;
    <u8 as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

// Cell is !Freeze: the blanket Unstable entry runs small_sort_fallback, insertion from index 1.
#[kani::requires(pair_region(v))]
#[kani::requires(canonical(cmp, cell_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 2))]
#[kani::ensures(|_| pair_sorted(v))]
#[kani::ensures(|_| old(pair_count(v, probe)) == pair_count(v, probe))]
unsafe fn unstable_cell(v: *mut Cell<u8>, cmp: fn(&Cell<u8>, &Cell<u8>) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, cell_less)) {
        return;
    }
    // SAFETY: the requires establish exactly two initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 2) };
    let mut is_less = cmp;
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less);
}

#[kani::proof_for_contract(stable_freeze_byte)]
#[kani::unwind(16)]
fn stable_freeze_byte_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, right];
    // Unwritten stack slots: arbitrary contents, never read by the specifications.
    let mut scratch = [MaybeUninit::<u8>::uninit(); 19];
    let scratch_len: usize = kani::any_where(|n: &usize| *n == 18 || *n == 19);
    // SAFETY: active pair in initialized backing4; separate scratch; canonical pointer.
    unsafe {
        stable_freeze_byte(
            v[1..3].as_mut_ptr(),
            scratch.as_mut_ptr(),
            scratch_len,
            byte_less,
            probe,
        )
    };
    kani::assert(v[0] == left && v[3] == right, "wrap stable Freeze input frame");
    // SAFETY: at N2 the general route copies both singleton halves to scratch[0..2]; the default
    // insertion route would leave these slots unwritten. A harness check, not a specification.
    let halves = unsafe { [scratch[0].assume_init(), scratch[1].assume_init()] };
    kani::assert(halves == [a, b], "wrap stable Freeze route wrote scratch halves");
    kani::cover(scratch_len == 18, "wrap stable Freeze minimum scratch returns");
    kani::cover(scratch_len == 19, "wrap stable Freeze longer scratch returns");
    input_covers(a, b, probe);
    kani::cover(true, "wrap stable Freeze u8 trait entry returns");
}

#[kani::proof_for_contract(unstable_cell)]
#[kani::unwind(16)]
fn unstable_cell_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [Cell::new(left), Cell::new(a), Cell::new(b), Cell::new(right)];
    // SAFETY: active pair in initialized backing4; canonical pointer.
    unsafe { unstable_cell(v[1..3].as_mut_ptr(), cell_less, probe) };
    kani::assert(v[0].get() == left && v[3].get() == right, "wrap unstable Cell input frame");
    input_covers(a, b, probe);
    kani::cover(true, "wrap unstable Cell trait entry returns");
}

// Plain real-body calls, one nondeterministic branch per new wrapper; the parent's literal guard
// must be the only failure. The parent `rejects_always_true` stays unchanged.
#[kani::proof]
#[kani::unwind(16)]
fn rejects_always_true_more() {
    let [a, b]: [u8; 2] = kani::any();
    let probe: u8 = kani::any();
    if kani::any() {
        let mut v = [a, b];
        let mut scratch = [MaybeUninit::<u8>::uninit(); 18];
        kani::cover(true, "wrap invalid stable Freeze comparator reaches guard");
        // SAFETY: valid pair and disjoint scratch18; only canonical identity is rejected.
        unsafe {
            stable_freeze_byte(v.as_mut_ptr(), scratch.as_mut_ptr(), 18, always_true::<u8>, probe)
        };
    } else {
        let mut v = [Cell::new(a), Cell::new(b)];
        kani::cover(true, "wrap invalid unstable Cell comparator reaches guard");
        // SAFETY: valid pair; only canonical identity is deliberately rejected.
        unsafe { unstable_cell(v.as_mut_ptr(), always_true::<Cell<u8>>, probe) };
    }
}
