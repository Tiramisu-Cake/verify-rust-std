//! Opt-in N2 forwarding contracts for the two remaining trait entries, same form as the parent:
//! u8 through the Stable Freeze impl (general with caller scratch) and Cell<u8> through the
//! Unstable blanket impl (fallback insertion); then fixed-N4 wrappers for all five domains.
//! No specification calls the comparator.

use super::super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
};
use super::{
    Model, NonCopyU8, always_true, byte_less, canonical, canonical_guard, cell_less, input_covers,
    noncopy_less, pair_count, pair_region, pair_sorted,
};
use crate::cell::Cell;
use crate::mem::MaybeUninit;
use crate::ub_checks::{can_dereference, can_write, same_allocation};
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

// N4: the same models, comparators and probe over a fixed four-element span in backing6.
fn span_region<T, const N: usize>(v: *mut T) -> bool {
    can_dereference(ptr::slice_from_raw_parts(v, N))
        && can_write(ptr::slice_from_raw_parts_mut(v, N))
}

// Both read only the N initialized input elements, never any scratch or uninit slot.
fn span_sorted<T: Model, const N: usize>(v: *const T) -> bool {
    // SAFETY: the wrapper requires establish a readable initialized N-element span.
    let v = unsafe { slice::from_raw_parts(v, N) };
    let mut i = 1;
    while i < N {
        if (v[i - 1].model() >> 1) > (v[i].model() >> 1) {
            return false;
        }
        i += 1;
    }
    true
}

fn span_count<T: Model, const N: usize>(v: *const T, probe: u8) -> usize {
    // SAFETY: the wrapper requires establish a readable initialized N-element span.
    let v = unsafe { slice::from_raw_parts(v, N) };
    let (mut n, mut i) = (0, 0);
    while i < N {
        n += (v[i].model() == probe) as usize;
        i += 1;
    }
    n
}

// `stable_region` with an N-element input span.
fn stable_region_n<const N: usize>(v: *mut Cell<u8>, scratch: &[MaybeUninit<Cell<u8>>]) -> bool {
    span_region::<Cell<u8>, N>(v)
        && (scratch.is_empty()
            || !same_allocation(v as *const Cell<u8>, scratch.as_ptr().cast::<Cell<u8>>())
            || {
                // SAFETY: both nonempty regions are live and in the same allocation.
                // MaybeUninit<Cell<u8>> and Cell<u8> have identical size and alignment.
                let d = unsafe { scratch.as_ptr().cast::<Cell<u8>>().offset_from(v) };
                if d >= 0 { d as usize >= N } else { d.unsigned_abs() >= scratch.len() }
            })
}

// Cell, Stable default: insertion from index 1; scratch ignored and outside modifies.
#[kani::requires(stable_region_n::<4>(v, scratch))]
#[kani::requires(canonical(cmp, cell_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 4))]
#[kani::ensures(|_| span_sorted::<_, 4>(v))]
#[kani::ensures(|_| old(span_count::<_, 4>(v, probe)) == span_count::<_, 4>(v, probe))]
unsafe fn stable_cell_n4(
    v: *mut Cell<u8>,
    scratch: &mut [MaybeUninit<Cell<u8>>],
    cmp: fn(&Cell<u8>, &Cell<u8>) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, cell_less)) {
        return;
    }
    // SAFETY: the requires establish exactly four initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 4) };
    let mut is_less = cmp;
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

// u8, Unstable Freeze Copy: network, len < 18 so no merge; presorted 1, insertion from index 1.
#[kani::requires(span_region::<u8, 4>(v))]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 4))]
#[kani::ensures(|_| span_sorted::<_, 4>(v))]
#[kani::ensures(|_| old(span_count::<_, 4>(v, probe)) == span_count::<_, 4>(v, probe))]
unsafe fn unstable_byte_n4(v: *mut u8, cmp: fn(&u8, &u8) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: the requires establish exactly four initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 4) };
    let mut is_less = cmp;
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less);
}

// NonCopyU8, Freeze default: general with private scratch48; halves of two, each one insert_tail.
#[kani::requires(span_region::<NonCopyU8, 4>(v))]
#[kani::requires(canonical(cmp, noncopy_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 4))]
#[kani::ensures(|_| span_sorted::<_, 4>(v))]
#[kani::ensures(|_| old(span_count::<_, 4>(v, probe)) == span_count::<_, 4>(v, probe))]
unsafe fn freeze_noncopy_n4(v: *mut NonCopyU8, cmp: fn(&NonCopyU8, &NonCopyU8) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, noncopy_less)) {
        return;
    }
    // SAFETY: the requires establish exactly four initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 4) };
    let mut is_less = cmp;
    <NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut is_less);
}

// u8, Stable Freeze: general with caller scratch >= 20; writes scratch[0..4] and v.
#[kani::requires(span_region::<u8, 4>(v) && freeze_scratch::<4>(v, scratch, scratch_len))]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(
    ptr::slice_from_raw_parts_mut(v, 4),
    ptr::slice_from_raw_parts_mut(scratch, scratch_len)
)]
#[kani::ensures(|_| span_sorted::<_, 4>(v))]
#[kani::ensures(|_| old(span_count::<_, 4>(v, probe)) == span_count::<_, 4>(v, probe))]
unsafe fn stable_freeze_byte_n4(
    v: *mut u8,
    scratch: *mut MaybeUninit<u8>,
    scratch_len: usize,
    cmp: fn(&u8, &u8) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: the requires establish four initialized writable elements and a disjoint
    // writable scratch of scratch_len slots.
    let (v, scratch) = unsafe {
        (slice::from_raw_parts_mut(v, 4), slice::from_raw_parts_mut(scratch, scratch_len))
    };
    let mut is_less = cmp;
    <u8 as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

// Cell, Unstable blanket: small_sort_fallback, insertion from index 1.
#[kani::requires(span_region::<Cell<u8>, 4>(v))]
#[kani::requires(canonical(cmp, cell_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, 4))]
#[kani::ensures(|_| span_sorted::<_, 4>(v))]
#[kani::ensures(|_| old(span_count::<_, 4>(v, probe)) == span_count::<_, 4>(v, probe))]
unsafe fn unstable_cell_n4(v: *mut Cell<u8>, cmp: fn(&Cell<u8>, &Cell<u8>) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, cell_less)) {
        return;
    }
    // SAFETY: the requires establish exactly four initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, 4) };
    let mut is_less = cmp;
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less);
}

// The N2 input covers on the first pair plus a strictly reversed input needing several moves.
fn n4_covers(a: u8, b: u8, c: u8, d: u8, probe: u8) {
    input_covers(a, b, probe);
    let (a, b, c, d) = (a >> 1, b >> 1, c >> 1, d >> 1);
    kani::cover(a > b && b > c && c > d, "wrap N4 strictly reversed keys return");
}

#[kani::proof_for_contract(stable_cell_n4)]
#[kani::unwind(16)]
fn stable_cell_n4_backing6() {
    let [left, a, b, c, d, right]: [u8; 6] = kani::any();
    let probe: u8 = kani::any();
    let mut v =
        [Cell::new(left), Cell::new(a), Cell::new(b), Cell::new(c), Cell::new(d), Cell::new(right)];
    let mut scratch = [MaybeUninit::new(Cell::new(kani::any())), MaybeUninit::uninit()];
    let scratch_len: usize = kani::any_where(|n: &usize| *n <= 2);
    // SAFETY: this slot was initialized above; Cell has no padding and get reads its full value.
    let scratch_before = unsafe { scratch[0].assume_init_ref() }.get();
    // SAFETY: active span in initialized backing6; separate valid scratch; canonical pointer.
    unsafe { stable_cell_n4(v[1..5].as_mut_ptr(), &mut scratch[..scratch_len], cell_less, probe) };
    kani::assert(v[0].get() == left && v[5].get() == right, "wrap N4 stable input frame");
    // SAFETY: the default Cell route does not write scratch; only the input may be modified.
    let scratch_after = unsafe { scratch[0].assume_init_ref() }.get();
    kani::assert(scratch_before == scratch_after, "wrap N4 stable scratch frame");
    kani::cover(scratch_len == 0, "wrap N4 stable empty scratch returns");
    kani::cover(scratch_len == 2, "wrap N4 stable unread uninit scratch tail returns");
    n4_covers(a, b, c, d, probe);
    kani::cover(true, "wrap N4 stable Cell trait entry returns");
}

#[kani::proof_for_contract(unstable_byte_n4)]
#[kani::unwind(16)]
fn unstable_byte_n4_backing6() {
    let [left, a, b, c, d, right]: [u8; 6] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, c, d, right];
    // SAFETY: active span in initialized backing6; canonical pointer.
    unsafe { unstable_byte_n4(v[1..5].as_mut_ptr(), byte_less, probe) };
    kani::assert(v[0] == left && v[5] == right, "wrap N4 unstable input frame");
    n4_covers(a, b, c, d, probe);
    kani::cover(true, "wrap N4 unstable u8 trait entry returns");
}

#[kani::proof_for_contract(freeze_noncopy_n4)]
#[kani::unwind(16)]
fn freeze_noncopy_n4_backing6() {
    let [left, a, b, c, d, right]: [u8; 6] = kani::any();
    let probe: u8 = kani::any();
    let mut v =
        [NonCopyU8(left), NonCopyU8(a), NonCopyU8(b), NonCopyU8(c), NonCopyU8(d), NonCopyU8(right)];
    // SAFETY: active span in initialized backing6; canonical pointer.
    unsafe { freeze_noncopy_n4(v[1..5].as_mut_ptr(), noncopy_less, probe) };
    kani::assert(v[0].0 == left && v[5].0 == right, "wrap N4 Freeze input frame");
    n4_covers(a, b, c, d, probe);
    kani::cover(true, "wrap N4 Freeze NonCopyU8 trait entry returns");
}

// Stable insertion of one pair, as insert_tail does in each scratch half.
fn ordered_pair(x: u8, y: u8) -> [u8; 2] {
    if (y >> 1) < (x >> 1) { [y, x] } else { [x, y] }
}

#[kani::proof_for_contract(stable_freeze_byte_n4)]
#[kani::unwind(16)]
fn stable_freeze_byte_n4_backing6() {
    let [left, a, b, c, d, right]: [u8; 6] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, c, d, right];
    // Unwritten stack slots: arbitrary contents, never read by the specifications.
    let mut scratch = [MaybeUninit::<u8>::uninit(); 21];
    let scratch_len: usize = kani::any_where(|n: &usize| *n == 20 || *n == 21);
    // SAFETY: active span in initialized backing6; separate scratch; canonical pointer.
    unsafe {
        stable_freeze_byte_n4(
            v[1..5].as_mut_ptr(),
            scratch.as_mut_ptr(),
            scratch_len,
            byte_less,
            probe,
        )
    };
    kani::assert(v[0] == left && v[5] == right, "wrap N4 stable Freeze input frame");
    // SAFETY: at N4 the general route leaves each sorted half of two in scratch[0..4]; the
    // default insertion route would leave these slots unwritten. A harness check only.
    let s = unsafe {
        [
            scratch[0].assume_init(),
            scratch[1].assume_init(),
            scratch[2].assume_init(),
            scratch[3].assume_init(),
        ]
    };
    let (lo, hi) = (ordered_pair(a, b), ordered_pair(c, d));
    kani::assert(s == [lo[0], lo[1], hi[0], hi[1]], "wrap N4 stable Freeze route wrote halves");
    kani::cover(scratch_len == 20, "wrap N4 stable Freeze minimum scratch returns");
    kani::cover(scratch_len == 21, "wrap N4 stable Freeze longer scratch returns");
    n4_covers(a, b, c, d, probe);
    kani::cover(true, "wrap N4 stable Freeze u8 trait entry returns");
}

#[kani::proof_for_contract(unstable_cell_n4)]
#[kani::unwind(16)]
fn unstable_cell_n4_backing6() {
    let [left, a, b, c, d, right]: [u8; 6] = kani::any();
    let probe: u8 = kani::any();
    let mut v =
        [Cell::new(left), Cell::new(a), Cell::new(b), Cell::new(c), Cell::new(d), Cell::new(right)];
    // SAFETY: active span in initialized backing6; canonical pointer.
    unsafe { unstable_cell_n4(v[1..5].as_mut_ptr(), cell_less, probe) };
    kani::assert(v[0].get() == left && v[5].get() == right, "wrap N4 unstable Cell input frame");
    n4_covers(a, b, c, d, probe);
    kani::cover(true, "wrap N4 unstable Cell trait entry returns");
}
