//! G1: actual unstable u8 N9 route, explicit fn-pointer F, pair/frame/count composition.
//! Only the composed roots replace raw swap calls. The independent PFC executes the real helper.

use super::{StrictU8, count_matching_values, is_sorted_by, prefix_unchanged};
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{
    Profile, pair_models, specfix_canonical_comparator, swap_geometry, swap_ordered, swap_transfer,
};
use crate::slice::sort::shared::smallsort::{UnstableSmallSortTypeImpl, swap_if_less};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

type U8Cmp = fn(&u8, &u8) -> bool;

fn canonical(cmp: U8Cmp) -> bool {
    specfix_canonical_comparator::<StrictU8>(cmp)
}

fn region9(v: *mut u8, a: usize, b: usize) -> bool {
    a < 9
        && b < 9
        && !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u8, 9))
        && can_write(ptr::slice_from_raw_parts_mut(v, 9))
        && same_allocation(v as *const u8, v.wrapping_add(8) as *const u8)
        && swap_geometry(v, a, b)
}

fn count9(v: *const u8, probe: u8) -> usize {
    // SAFETY: all callers establish a readable initialized nine-element region first.
    let values = unsafe { crate::slice::from_raw_parts(v, 9) };
    count_matching_values(values, &probe)
}

// Concrete metadata target, declared before its PFC; no context reads or ghost writes here.
#[kani::requires(canonical(cmp))]
#[kani::requires(region9(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<StrictU8>(old(pair_models::<StrictU8>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<StrictU8>(v, a, b))]
#[kani::ensures(|_| old(count9(v, probe)) == count9(v, probe))]
unsafe fn swap_net9(v: *mut u8, a: usize, b: usize, cmp: U8Cmp, probe: u8) {
    let mut actual: U8Cmp = cmp;
    // SAFETY: exact region, distinct valid positions and received canonical fn-pointer.
    unsafe { swap_if_less(v, a, b, &mut actual) };
}

#[kani::proof_for_contract(swap_net9)]
#[kani::unwind(25)]
fn netcomp_leaf_u8_n9() {
    let mut v: [u8; 9] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let a: usize = kani::any_where(|&i| i < 9);
    let b: usize = kani::any_where(|&i| i < 9 && i != a);
    let cmp: U8Cmp = StrictU8::CMP;
    let taken = pre[b] < pre[a];
    // SAFETY: full initialized exact backing9, offset0, arbitrary distinct in-bounds pair.
    unsafe { swap_net9(v.as_mut_ptr(), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "netcomp leaf N9: pair transfer");
    kani::assert(v[a] <= v[b], "netcomp leaf N9: pair ordered");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp leaf N9: full-value count preserved",
    );
    let mut i = 0;
    while i < 9 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "netcomp leaf N9: other values unchanged");
        }
        i += 1;
    }
    kani::cover(taken, "netcomp leaf N9: swap taken");
    kani::cover(!taken, "netcomp leaf N9: swap not taken");
    kani::cover(a == 0 && b == 8, "netcomp leaf N9: first to last");
    kani::cover(a == 8 && b == 0, "netcomp leaf N9: last to first");
    kani::cover(a > 0 && a < 8 && b > 0 && b < 8, "netcomp leaf N9: interior pair");
    kani::cover(count_matching_values(&pre, &probe) > 0, "netcomp leaf N9: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "netcomp leaf N9: probe misses input");
}

#[derive(Clone, Copy)]
struct Context9 {
    base: *mut u8,
    probe: u8,
    initial_count: usize,
    hits: usize,
}

static mut CONTEXT9: Context9 =
    Context9 { base: ptr::null_mut(), probe: 0, initial_count: 0, hits: 0 };

fn context9() -> Context9 {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT9) }
}

fn register9(v: &mut [u8; 9], probe: u8) {
    let ctx = Context9 {
        base: v.as_mut_ptr(),
        probe,
        initial_count: count_matching_values(v, &probe),
        hits: 0,
    };
    // SAFETY: caller owns initialized exact array; invoked before the trait entry, outside PFC.
    unsafe { *ptr::addr_of_mut!(CONTEXT9) = ctx };
}

/// Closed dispatch: only u8 / U8Cmp is implemented; no blanket or fallback implementation.
trait SwapBridge9<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridge9<U8Cmp> for u8 {
    unsafe fn exchange(v: *mut u8, a: usize, b: usize, is_less: &mut U8Cmp) {
        kani::cover(true, "netcomp N9: adapter entered");
        let ctx = context9();
        kani::assert(v == ctx.base, "netcomp N9: actual base matches registered root");
        kani::assert(a < 9 && b < 9 && a != b, "netcomp N9: actual pair distinct and in range");
        let accepted = canonical(*is_less);
        kani::assert(accepted, "netcomp canonical comparator required");
        if !accepted {
            return;
        }
        // SAFETY: same actual array/indices/comparator, with memory requires checked at the call.
        // Probe is by value; the verified target cannot write context or the hit counter.
        unsafe { swap_net9(v, a, b, *is_less, ctx.probe) };
        // SAFETY: dedicated proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT9.hits) += 1 };
        kani::assert(
            count9(v, ctx.probe) == ctx.initial_count,
            "netcomp N9: count invariant after actual exchange",
        );
    }
}

// Same raw parameters, return and two type parameters; only the bridge bound narrows the proof.
unsafe fn adapter9<T: SwapBridge9<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

fn check_context9(v: *mut u8, probe: u8, initial_count: usize) {
    let ctx = context9();
    kani::assert(ctx.hits == 25, "netcomp N9: complete actual hit count");
    kani::assert(ctx.base == v, "netcomp N9: context base frame");
    kani::assert(ctx.probe == probe, "netcomp N9: context probe frame");
    kani::assert(ctx.initial_count == initial_count, "netcomp N9: context initial-count frame");
}

// Shared actual-entry caller for both positives and count control. The composed flag changes only
// proof-owned instrumentation. It never selects or reimplements a network algorithm.
fn run9(v: &mut [u8; 9], probe: u8, cmp: &mut U8Cmp, composed: bool) {
    let base = v.as_mut_ptr();
    let initial_count = count_matching_values(v, &probe);
    if composed {
        register9(v, probe);
    }
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "netcomp N9: canonical comparator unchanged");
    if composed {
        check_context9(base, probe, initial_count);
    }
}

fn positive9(composed: bool) {
    let mut v: [u8; 9] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let mut cmp: U8Cmp = StrictU8::CMP;
    run9(&mut v, probe, &mut cmp, composed);
    kani::assert(is_sorted_by(&v, &mut cmp), "netcomp N9: sorted output");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp N9: full-value count preserved",
    );
    kani::cover(!prefix_unchanged(&v, &pre, 0), "netcomp N9: sort moves elements");
    kani::cover(count_matching_values(&pre, &probe) > 0, "netcomp N9: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "netcomp N9: probe misses input");
    let mut duplicates = false;
    let mut i = 1;
    while i < 9 {
        duplicates |= v[i] == v[i - 1];
        i += 1;
    }
    kani::cover(duplicates, "netcomp N9: duplicates present");
}

#[kani::proof]
#[kani::unwind(25)]
fn netcomp_direct_u8_n9() {
    positive9(false);
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter9)]
#[kani::stub_verified(swap_net9)]
#[kani::unwind(25)]
fn netcomp_composed_u8_n9() {
    positive9(true);
    kani::cover(context9().hits == 25, "netcomp N9: all actual exchanges intercepted");
}

fn always_true_u8(_: &u8, _: &u8) -> bool {
    true
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter9)]
#[kani::stub_verified(swap_net9)]
#[kani::unwind(25)]
fn netcomp_wrong_cmp_u8_n9() {
    let mut v: [u8; 9] = kani::any();
    let probe: u8 = kani::any();
    register9(&mut v, probe);
    let mut cmp: U8Cmp = always_true_u8;
    kani::cover(true, "netcomp N9 wrong comparator: actual entry reached");
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No sorted/count result assertion: only the adapter's literal canonical guard must fail.
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter9)]
#[kani::stub_verified(swap_net9)]
#[kani::unwind(25)]
fn netcomp_count_negative_u8_n9() {
    let mut v = [0u8; 9];
    let pre = v;
    let probe = 0u8;
    let mut cmp: U8Cmp = StrictU8::CMP;
    run9(&mut v, probe, &mut cmp, true);
    kani::cover(true, "netcomp N9 negative: sort returned before corruption");
    v[8] = 1;
    kani::assert(is_sorted_by(&v, &mut cmp), "netcomp N9 negative: sorted after corruption");
    kani::cover(true, "netcomp N9 negative: corrupted count check reached");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp N9 negative: full-value count preserved",
    );
}

// N13 is a separate exact backing, target, leaf and context; N9 dependencies stay intact.

fn region13(v: *mut u8, a: usize, b: usize) -> bool {
    a < 13
        && b < 13
        && !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u8, 13))
        && can_write(ptr::slice_from_raw_parts_mut(v, 13))
        && same_allocation(v as *const u8, v.wrapping_add(12) as *const u8)
        && swap_geometry(v, a, b)
}

fn count13(v: *const u8, probe: u8) -> usize {
    // SAFETY: all callers establish a readable initialized thirteen-element region first.
    let values = unsafe { crate::slice::from_raw_parts(v, 13) };
    count_matching_values(values, &probe)
}

// Concrete metadata target, declared before its PFC; no context reads or ghost writes here.
#[kani::requires(canonical(cmp))]
#[kani::requires(region13(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<StrictU8>(old(pair_models::<StrictU8>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<StrictU8>(v, a, b))]
#[kani::ensures(|_| old(count13(v, probe)) == count13(v, probe))]
unsafe fn swap_net13(v: *mut u8, a: usize, b: usize, cmp: U8Cmp, probe: u8) {
    let mut actual: U8Cmp = cmp;
    // SAFETY: exact region, distinct valid positions and received canonical fn-pointer.
    unsafe { swap_if_less(v, a, b, &mut actual) };
}

#[kani::proof_for_contract(swap_net13)]
#[kani::unwind(25)]
fn netcomp_leaf_u8_n13() {
    let mut v: [u8; 13] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let a: usize = kani::any_where(|&i| i < 13);
    let b: usize = kani::any_where(|&i| i < 13 && i != a);
    let cmp: U8Cmp = StrictU8::CMP;
    let taken = pre[b] < pre[a];
    // SAFETY: full initialized exact backing13, offset0, arbitrary distinct in-bounds pair.
    unsafe { swap_net13(v.as_mut_ptr(), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "netcomp leaf N13: pair transfer");
    kani::assert(v[a] <= v[b], "netcomp leaf N13: pair ordered");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp leaf N13: full-value count preserved",
    );
    let mut i = 0;
    while i < 13 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "netcomp leaf N13: other values unchanged");
        }
        i += 1;
    }
    kani::cover(taken, "netcomp leaf N13: swap taken");
    kani::cover(!taken, "netcomp leaf N13: swap not taken");
    kani::cover(a == 0 && b == 12, "netcomp leaf N13: first to last");
    kani::cover(a == 12 && b == 0, "netcomp leaf N13: last to first");
    kani::cover(a > 0 && a < 12 && b > 0 && b < 12, "netcomp leaf N13: interior pair");
    kani::cover(count_matching_values(&pre, &probe) > 0, "netcomp leaf N13: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "netcomp leaf N13: probe misses input");
}

#[derive(Clone, Copy)]
struct Context13 {
    base: *mut u8,
    probe: u8,
    initial_count: usize,
    hits: usize,
}

static mut CONTEXT13: Context13 =
    Context13 { base: ptr::null_mut(), probe: 0, initial_count: 0, hits: 0 };

fn context13() -> Context13 {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT13) }
}

fn register13(v: &mut [u8; 13], probe: u8) {
    let ctx = Context13 {
        base: v.as_mut_ptr(),
        probe,
        initial_count: count_matching_values(v, &probe),
        hits: 0,
    };
    // SAFETY: caller owns initialized exact array; invoked before the trait entry, outside PFC.
    unsafe { *ptr::addr_of_mut!(CONTEXT13) = ctx };
}

/// Closed dispatch: only u8 / U8Cmp is implemented; no blanket or fallback implementation.
trait SwapBridge13<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridge13<U8Cmp> for u8 {
    unsafe fn exchange(v: *mut u8, a: usize, b: usize, is_less: &mut U8Cmp) {
        kani::cover(true, "netcomp N13: adapter entered");
        let ctx = context13();
        kani::assert(v == ctx.base, "netcomp N13: actual base matches registered root");
        kani::assert(a < 13 && b < 13 && a != b, "netcomp N13: actual pair distinct and in range");
        let accepted = canonical(*is_less);
        kani::assert(accepted, "netcomp canonical comparator required");
        if !accepted {
            return;
        }
        // SAFETY: same actual array/indices/comparator, with memory requires checked at the call.
        // Probe is by value; the verified target cannot write context or the hit counter.
        unsafe { swap_net13(v, a, b, *is_less, ctx.probe) };
        // SAFETY: dedicated proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT13.hits) += 1 };
        kani::assert(
            count13(v, ctx.probe) == ctx.initial_count,
            "netcomp N13: count invariant after actual exchange",
        );
    }
}

// Same raw parameters, return and two type parameters; only the bridge bound narrows the proof.
unsafe fn adapter13<T: SwapBridge13<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

fn check_context13(v: *mut u8, probe: u8, initial_count: usize) {
    let ctx = context13();
    kani::assert(ctx.hits == 45, "netcomp N13: complete actual hit count");
    kani::assert(ctx.base == v, "netcomp N13: context base frame");
    kani::assert(ctx.probe == probe, "netcomp N13: context probe frame");
    kani::assert(ctx.initial_count == initial_count, "netcomp N13: context initial-count frame");
}

// Separate N13 actual-entry caller and count control; no network algorithm is reimplemented.
fn run13(v: &mut [u8; 13], probe: u8, cmp: &mut U8Cmp) {
    let base = v.as_mut_ptr();
    let initial_count = count_matching_values(v, &probe);
    register13(v, probe);
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "netcomp N13: canonical comparator unchanged");
    check_context13(base, probe, initial_count);
}

fn positive13() {
    let mut v: [u8; 13] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let mut cmp: U8Cmp = StrictU8::CMP;
    run13(&mut v, probe, &mut cmp);
    kani::assert(is_sorted_by(&v, &mut cmp), "netcomp N13: sorted output");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp N13: full-value count preserved",
    );
    kani::cover(!prefix_unchanged(&v, &pre, 0), "netcomp N13: sort moves elements");
    kani::cover(count_matching_values(&pre, &probe) > 0, "netcomp N13: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "netcomp N13: probe misses input");
    let mut duplicates = false;
    let mut i = 1;
    while i < 13 {
        duplicates |= v[i] == v[i - 1];
        i += 1;
    }
    kani::cover(duplicates, "netcomp N13: duplicates present");
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter13)]
#[kani::stub_verified(swap_net13)]
#[kani::unwind(25)]
fn netcomp_composed_u8_n13() {
    positive13();
    kani::cover(context13().hits == 45, "netcomp N13: all actual exchanges intercepted");
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter13)]
#[kani::stub_verified(swap_net13)]
#[kani::unwind(25)]
fn netcomp_wrong_cmp_u8_n13() {
    let mut v: [u8; 13] = kani::any();
    let probe: u8 = kani::any();
    register13(&mut v, probe);
    let mut cmp: U8Cmp = always_true_u8;
    kani::cover(true, "netcomp N13 wrong comparator: actual entry reached");
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No sorted/count result assertion: only the adapter's literal canonical guard must fail.
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter13)]
#[kani::stub_verified(swap_net13)]
#[kani::unwind(25)]
fn netcomp_count_negative_u8_n13() {
    let mut v = [0u8; 13];
    let pre = v;
    let probe = 0u8;
    let mut cmp: U8Cmp = StrictU8::CMP;
    run13(&mut v, probe, &mut cmp);
    kani::cover(true, "netcomp N13 negative: sort returned before corruption");
    v[12] = 1;
    kani::assert(is_sorted_by(&v, &mut cmp), "netcomp N13 negative: sorted after corruption");
    kani::cover(true, "netcomp N13 negative: corrupted count check reached");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netcomp N13 negative: full-value count preserved",
    );
}
