//! C diagnostic controls. Opt-in only; stock PASS of N2 is an ALIAS_GAP, never Rust permission.
//! No summaries, abort stubs, comparator guards, or algorithm/model changes.
use super::super::{bidirectional_merge, insert_tail, insertion_sort_shift_left};
use crate::cell::Cell;
use crate::mem::{ManuallyDrop, MaybeUninit};
use crate::{kani, ptr};

fn merge_fixture<const WRITE: bool>() {
    let mut backing = [2u64, 1u64];
    // Preserve a mutable raw pointer before creating any shared source reference.
    let raw = backing.as_mut_ptr();
    let source = &backing[..];
    let mut dst = [MaybeUninit::<u64>::uninit(); 2];
    let mut less = |a: &u64, b: &u64| {
        // Negative-only writes deliberately violate live shared permissions and the real
        // merge's dst-only frame. The closure capture itself is never modified.
        unsafe {
            let av = ptr::read_volatile(a);
            let bv = ptr::read_volatile(b);
            kani::assert(ptr::eq(a, raw.add(1)), "C_MERGE_ARGUMENT_IS_SOURCE_SLOT");
            kani::cover(true, "C_merge_callback");
            if WRITE {
                ptr::write_volatile(raw.add(1), av ^ 1);
                kani::cover(true, "C_N1_transient_write");
                ptr::write_volatile(raw.add(1), av);
            }
            let restored = ptr::read_volatile(a);
            kani::assert(restored == av, "C_MERGE_LIVE_REFERENCE_RESTORED");
            kani::cover(true, "C_merge_live_read_after_restore");
            av < bv
        }
    };
    // Two initialized singleton halves and disjoint writable MU destination. PFC is the
    // real helper, not this fixture: source is deliberately absent from its write set.
    unsafe { bidirectional_merge(source, dst.as_mut_ptr().cast(), &mut less) };
    kani::assert(backing == [2, 1], "C_MERGE_SOURCE_FINAL");
    kani::assert(unsafe { dst[0].assume_init() == 1 && dst[1].assume_init() == 2 }, "C_MERGE_OUTPUT");
    kani::cover(true, "C_merge_return");
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(8)]
fn c_merge_source_write_restore() { merge_fixture::<true>(); }

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(8)]
fn c_merge_source_read_only() { merge_fixture::<false>(); }

// Both variants execute the same real helper graph. Exactly the input pair is writable;
// the preexisting raw alias is not derived by casting a callback's shared reference.
#[kani::modifies(v)]
fn callback_outer<const WRITE: bool>(v: &mut [u8; 2], tail: *mut u8) {
    let mut less = |a: &u8, b: &u8| unsafe {
        let av = ptr::read_volatile(a);
        let bv = ptr::read_volatile(b);
        kani::assert(ptr::eq(a, tail), "C_N2_ARGUMENT_IS_TAIL");
        kani::cover(true, "C_outer_callback");
        if WRITE {
            ptr::write_volatile(tail, av ^ 1);
            kani::cover(true, "C_N2_transient_write");
            ptr::write_volatile(tail, av);
        }
        kani::assert(ptr::read_volatile(a) == av, "C_OUTER_LIVE_REFERENCE_RESTORED");
        kani::cover(true, "C_outer_live_read_after_restore");
        av < bv
    };
    insertion_sort_shift_left(v, 1, &mut less);
}

fn outer_fixture<const WRITE: bool>() {
    let mut v = [2u8, 1];
    let tail = unsafe { v.as_mut_ptr().add(1) };
    callback_outer::<WRITE>(&mut v, tail);
    kani::assert(v == [1, 2], "C_OUTER_OUTPUT");
    kani::cover(true, "C_outer_return");
}

#[kani::proof_for_contract(callback_outer::<true>)]
#[kani::unwind(8)]
fn c_callback_live_shared_in_outer_frame() { outer_fixture::<true>(); }

#[kani::proof_for_contract(callback_outer::<false>)]
#[kani::unwind(8)]
fn c_callback_read_only_in_outer_frame() { outer_fixture::<false>(); }

#[kani::modifies(v, counter)]
fn external_mut(v: &mut [u8; 2], counter: &mut u8) {
    let mut less = |a: &u8, b: &u8| {
        *counter = counter.wrapping_add(1);
        kani::cover(*counter == 1, "C_L3_mut_changed");
        unsafe { ptr::read_volatile(a) < ptr::read_volatile(b) }
    };
    insertion_sort_shift_left(v, 1, &mut less);
}

#[kani::proof_for_contract(external_mut)]
#[kani::unwind(8)]
fn c_external_mut_state() {
    // Separate allocations and safe exclusive references establish disjointness.
    let mut v = [2u8, 1];
    let mut counter = 0;
    external_mut(&mut v, &mut counter);
    kani::assert(v == [1, 2] && counter == 1, "C_L3_MUT_OUTPUT");
    kani::cover(true, "C_L3_mut_return");
}

#[kani::modifies(v, counter.as_ptr())]
fn external_cell(v: &mut [u8; 2], counter: &Cell<u8>) {
    let mut less = |a: &u8, b: &u8| {
        counter.set(counter.get().wrapping_add(1));
        kani::cover(counter.get() == 1, "C_L3_cell_changed");
        unsafe { ptr::read_volatile(a) < ptr::read_volatile(b) }
    };
    insertion_sort_shift_left(v, 1, &mut less);
}

#[kani::proof_for_contract(external_cell)]
#[kani::unwind(8)]
fn c_external_cell_state() {
    let mut v = [2u8, 1];
    let counter = Cell::new(0);
    external_cell(&mut v, &counter);
    kani::assert(v == [1, 2] && counter.get() == 1, "C_L3_CELL_OUTPUT");
    kani::cover(true, "C_L3_cell_return");
}

#[kani::proof]
#[kani::unwind(12)]
fn c_insert_tail_local_lifetime() {
    // N3 descending, followed by one further insertion after the local MD/guard lifetime.
    // The last element is a suffix canary outside both active prefixes.
    let mut v = [3u8, 2, 1, 0, 99];
    let base = v.as_mut_ptr();
    let mut less = |a: &u8, b: &u8| unsafe {
        let av = ptr::read_volatile(a);
        let bv = ptr::read_volatile(b);
        // During the second insertion, a=1 is the local MD tmp, b=2 is the preceding
        // source. Unlike &tail in the initial comparison, a lies outside caller v.
        let is_tmp = (a as *const u8) != base && (a as *const u8) != base.add(1)
            && (a as *const u8) != base.add(2) && (a as *const u8) != base.add(3)
            && (a as *const u8) != base.add(4);
        kani::cover(is_tmp && av == 1 && bv == 2, "C_L4_tmp_comparison_after_gap_shift");
        av < bv
    };
    // Explicit real first insertion followed by the real loop's next insertion (tail2).
    unsafe { insert_tail(base, base.add(1), &mut less) };
    insertion_sort_shift_left(&mut v[..3], 2, &mut less);
    kani::assert(v[..3] == [1, 2, 3], "C_L4_N3_COPY_BACK");
    kani::cover(v[..3] == [1, 2, 3], "C_L4_gap_shift_and_copy_back");
    insertion_sort_shift_left(&mut v[..4], 3, &mut less);
    kani::assert(v == [0, 1, 2, 3, 99], "C_L4_OUTPUT_PERMUTATION_SUFFIX");
    kani::cover(true, "C_L4_next_insertion_return");
}

#[kani::proof]
fn c_local_storage_reuse() {
    let mut storage = MaybeUninit::new(ManuallyDrop::new(7u8));
    {
        let live = unsafe { storage.assume_init_ref() };
        kani::assert(unsafe { ptr::read_volatile(&**live) } == 7, "C_L4_FIRST_LIVE_READ");
        kani::cover(true, "C_L4_scoped_read");
    }
    // The old borrow ends before reuse. No escaped pointer/reference is read afterwards.
    storage.write(ManuallyDrop::new(9u8));
    let fresh = unsafe { storage.assume_init_ref() };
    kani::assert(unsafe { ptr::read_volatile(&**fresh) } == 9, "C_L4_FRESH_LIVE_READ");
    kani::cover(true, "C_L4_reinitialized_read_return");
}
