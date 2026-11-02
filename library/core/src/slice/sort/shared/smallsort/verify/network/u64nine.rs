//! U64-N9: actual unstable u64 N9 route, explicit fn-pointer F, pair/frame/count composition.
//! Only the composed roots replace raw swap calls. The independent PFC executes the real helper.
//! Separate typed domain: no u8 target, context or summary is shared or reused.

use super::{StrictU64, count_matching_values, is_sorted_by, prefix_unchanged};
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{
    Profile, pair_models, specfix_canonical_comparator, swap_geometry, swap_ordered, swap_transfer,
};
use crate::slice::sort::shared::smallsort::{UnstableSmallSortTypeImpl, swap_if_less};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

type U64Cmp = fn(&u64, &u64) -> bool;

fn canonical(cmp: U64Cmp) -> bool {
    specfix_canonical_comparator::<StrictU64>(cmp)
}

fn region9_u64(v: *mut u64, a: usize, b: usize) -> bool {
    a < 9
        && b < 9
        && !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u64, 9))
        && can_write(ptr::slice_from_raw_parts_mut(v, 9))
        && same_allocation(v as *const u64, v.wrapping_add(8) as *const u64)
        && swap_geometry(v, a, b)
}

fn count9_u64(v: *const u64, probe: u64) -> usize {
    // SAFETY: all callers establish a readable initialized nine-element region first.
    let values = unsafe { crate::slice::from_raw_parts(v, 9) };
    count_matching_values(values, &probe)
}

// Concrete metadata target, declared before its PFC; no context reads or ghost writes here.
#[kani::requires(canonical(cmp))]
#[kani::requires(region9_u64(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<StrictU64>(old(pair_models::<StrictU64>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<StrictU64>(v, a, b))]
#[kani::ensures(|_| old(count9_u64(v, probe)) == count9_u64(v, probe))]
unsafe fn swap_u64_net9(v: *mut u64, a: usize, b: usize, cmp: U64Cmp, probe: u64) {
    let mut actual: U64Cmp = cmp;
    // SAFETY: exact region, distinct valid positions and received canonical fn-pointer.
    unsafe { swap_if_less(v, a, b, &mut actual) };
}

#[kani::proof_for_contract(swap_u64_net9)]
#[kani::unwind(25)]
fn u64nine_leaf_u64_n9() {
    let mut v: [u64; 9] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let a: usize = kani::any_where(|&i| i < 9);
    let b: usize = kani::any_where(|&i| i < 9 && i != a);
    let cmp: U64Cmp = StrictU64::CMP;
    let taken = pre[b] < pre[a];
    // SAFETY: full initialized exact backing9, offset0, arbitrary distinct in-bounds pair.
    unsafe { swap_u64_net9(v.as_mut_ptr(), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "u64nine leaf N9: pair transfer");
    kani::assert(v[a] <= v[b], "u64nine leaf N9: pair ordered");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64nine leaf N9: full-value count preserved",
    );
    let mut i = 0;
    while i < 9 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "u64nine leaf N9: other values unchanged");
        }
        i += 1;
    }
    kani::cover(taken, "u64nine leaf N9: swap taken");
    kani::cover(!taken, "u64nine leaf N9: swap not taken");
    kani::cover(a == 0 && b == 8, "u64nine leaf N9: first to last");
    kani::cover(a == 8 && b == 0, "u64nine leaf N9: last to first");
    kani::cover(a > 0 && a < 8 && b > 0 && b < 8, "u64nine leaf N9: interior pair");
    kani::cover(count_matching_values(&pre, &probe) > 0, "u64nine leaf N9: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "u64nine leaf N9: probe misses input");
}

#[derive(Clone, Copy)]
struct ContextU64Nine {
    base: *mut u64,
    probe: u64,
    initial_count: usize,
    hits: usize,
}

static mut CONTEXT_U64_NINE: ContextU64Nine =
    ContextU64Nine { base: ptr::null_mut(), probe: 0, initial_count: 0, hits: 0 };

fn context() -> ContextU64Nine {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT_U64_NINE) }
}

fn register(v: &mut [u64; 9], probe: u64) {
    let ctx = ContextU64Nine {
        base: v.as_mut_ptr(),
        probe,
        initial_count: count_matching_values(v, &probe),
        hits: 0,
    };
    // SAFETY: caller owns initialized exact array; invoked before the trait entry, outside PFC.
    unsafe { *ptr::addr_of_mut!(CONTEXT_U64_NINE) = ctx };
}

/// Closed dispatch: only u64 / U64Cmp is implemented; no blanket or fallback implementation.
trait SwapBridgeU64Nine<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridgeU64Nine<U64Cmp> for u64 {
    unsafe fn exchange(v: *mut u64, a: usize, b: usize, is_less: &mut U64Cmp) {
        kani::cover(true, "u64nine N9: adapter entered");
        let ctx = context();
        kani::assert(v == ctx.base, "u64nine N9: actual base matches registered root");
        kani::assert(a < 9 && b < 9 && a != b, "u64nine N9: actual pair distinct and in range");
        let accepted = canonical(*is_less);
        kani::assert(accepted, "u64nine canonical comparator required");
        if !accepted {
            return;
        }
        // SAFETY: same actual array/indices/comparator, with memory requires checked at the call.
        // Probe is by value; the verified target cannot write context or the hit counter.
        unsafe { swap_u64_net9(v, a, b, *is_less, ctx.probe) };
        // SAFETY: dedicated proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_U64_NINE.hits) += 1 };
        kani::assert(
            count9_u64(v, ctx.probe) == ctx.initial_count,
            "u64nine N9: count invariant after actual exchange",
        );
    }
}

// Same raw parameters, return and two type parameters; only the bridge bound narrows the proof.
unsafe fn adapter_u64nine<T: SwapBridgeU64Nine<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

fn check_context(v: *mut u64, probe: u64, initial_count: usize) {
    let ctx = context();
    kani::assert(ctx.hits == 25, "u64nine N9: complete actual hit count");
    kani::assert(ctx.base == v, "u64nine N9: context base frame");
    kani::assert(ctx.probe == probe, "u64nine N9: context probe frame");
    kani::assert(ctx.initial_count == initial_count, "u64nine N9: context initial-count frame");
}

// Shared composed actual-entry caller for the positive and count control; assertions only.
// It never selects or reimplements a network algorithm.
fn run9(v: &mut [u64; 9], probe: u64, cmp: &mut U64Cmp) {
    let base = v.as_mut_ptr();
    let initial_count = count_matching_values(v, &probe);
    register(v, probe);
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "u64nine N9: canonical comparator unchanged");
    check_context(base, probe, initial_count);
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64nine)]
#[kani::stub_verified(swap_u64_net9)]
#[kani::unwind(25)]
fn u64nine_composed_u64_n9() {
    let mut v: [u64; 9] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp: U64Cmp = StrictU64::CMP;
    run9(&mut v, probe, &mut cmp);
    kani::cover(context().hits == 25, "u64nine N9: all actual exchanges intercepted");
    kani::assert(is_sorted_by(&v, &mut cmp), "u64nine N9: sorted output");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64nine N9: full-value count preserved",
    );
    kani::cover(!prefix_unchanged(&v, &pre, 0), "u64nine N9: sort moves elements");
    kani::cover(count_matching_values(&pre, &probe) > 0, "u64nine N9: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "u64nine N9: probe misses input");
    let mut duplicates = false;
    let mut i = 1;
    while i < 9 {
        duplicates |= v[i] == v[i - 1];
        i += 1;
    }
    kani::cover(duplicates, "u64nine N9: duplicates present");
    kani::cover(
        probe > u8::MAX as u64 && count_matching_values(&pre, &probe) > 0,
        "u64nine N9: high-bit probe hits input",
    );
}

fn always_true_u64(_: &u64, _: &u64) -> bool {
    true
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64nine)]
#[kani::stub_verified(swap_u64_net9)]
#[kani::unwind(25)]
fn u64nine_wrong_cmp_u64_n9() {
    let mut v: [u64; 9] = kani::any();
    let probe: u64 = kani::any();
    register(&mut v, probe);
    let mut cmp: U64Cmp = always_true_u64;
    kani::cover(true, "u64nine N9 wrong comparator: actual entry reached");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No sorted/count/hit result assertion: only the adapter's literal canonical guard must fail.
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64nine)]
#[kani::stub_verified(swap_u64_net9)]
#[kani::unwind(25)]
fn u64nine_count_negative_u64_n9() {
    const P: u64 = 1u64 << 40;
    let mut v = [P; 9];
    let pre = v;
    let probe = P;
    let mut cmp: U64Cmp = StrictU64::CMP;
    run9(&mut v, probe, &mut cmp);
    kani::cover(true, "u64nine N9 negative: sort returned before corruption");
    // Larger value with the same low 32 bits: order stays, count(P) drops from nine to eight.
    v[8] = 1u64 << 41;
    kani::assert(is_sorted_by(&v, &mut cmp), "u64nine N9 negative: sorted after corruption");
    kani::cover(true, "u64nine N9 negative: corrupted count check reached");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64nine N9 negative: full-value count preserved",
    );
}
