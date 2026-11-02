//! U64-N13: actual unstable u64 N13 route, explicit fn-pointer F, pair/frame/count composition.
//! Only the composed roots replace raw swap calls. The independent PFC executes the real helper.
//! Own exact-13 target, leaf, context and adapter; the parent's N9 items are neither called nor
//! changed. Only the parent's U64Cmp/canonical/always_true_u64 and pure network helpers are used.

use super::{U64Cmp, always_true_u64, canonical};
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{
    Profile, pair_models, swap_geometry, swap_ordered, swap_transfer,
};
use crate::slice::sort::shared::smallsort::verify::network::{
    StrictU64, count_matching_values, is_sorted_by, prefix_unchanged,
};
use crate::slice::sort::shared::smallsort::{UnstableSmallSortTypeImpl, swap_if_less};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

fn region13_u64(v: *mut u64, a: usize, b: usize) -> bool {
    a < 13
        && b < 13
        && !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u64, 13))
        && can_write(ptr::slice_from_raw_parts_mut(v, 13))
        && same_allocation(v as *const u64, v.wrapping_add(12) as *const u64)
        && swap_geometry(v, a, b)
}

fn count13_u64(v: *const u64, probe: u64) -> usize {
    // SAFETY: all callers establish a readable initialized thirteen-element region first.
    let values = unsafe { crate::slice::from_raw_parts(v, 13) };
    count_matching_values(values, &probe)
}

// Concrete metadata target, declared before its PFC; no context reads or ghost writes here.
#[kani::requires(canonical(cmp))]
#[kani::requires(region13_u64(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<StrictU64>(old(pair_models::<StrictU64>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<StrictU64>(v, a, b))]
#[kani::ensures(|_| old(count13_u64(v, probe)) == count13_u64(v, probe))]
unsafe fn swap_u64_net13(v: *mut u64, a: usize, b: usize, cmp: U64Cmp, probe: u64) {
    let mut actual: U64Cmp = cmp;
    // SAFETY: exact region, distinct valid positions and received canonical fn-pointer.
    unsafe { swap_if_less(v, a, b, &mut actual) };
}

#[kani::proof_for_contract(swap_u64_net13)]
#[kani::unwind(25)]
fn u64thirteen_leaf_u64_n13() {
    let mut v: [u64; 13] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let a: usize = kani::any_where(|&i| i < 13);
    let b: usize = kani::any_where(|&i| i < 13 && i != a);
    let cmp: U64Cmp = StrictU64::CMP;
    let taken = pre[b] < pre[a];
    // SAFETY: full initialized exact backing13, offset0, arbitrary distinct in-bounds pair.
    unsafe { swap_u64_net13(v.as_mut_ptr(), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "u64thirteen leaf N13: pair transfer");
    kani::assert(v[a] <= v[b], "u64thirteen leaf N13: pair ordered");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64thirteen leaf N13: full-value count preserved",
    );
    let mut i = 0;
    while i < 13 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "u64thirteen leaf N13: other values unchanged");
        }
        i += 1;
    }
    kani::cover(taken, "u64thirteen leaf N13: swap taken");
    kani::cover(!taken, "u64thirteen leaf N13: swap not taken");
    kani::cover(a == 0 && b == 12, "u64thirteen leaf N13: first to last");
    kani::cover(a == 12 && b == 0, "u64thirteen leaf N13: last to first");
    kani::cover(a > 0 && a < 12 && b > 0 && b < 12, "u64thirteen leaf N13: interior pair");
    kani::cover(count_matching_values(&pre, &probe) > 0, "u64thirteen leaf N13: probe hits input");
    kani::cover(
        count_matching_values(&pre, &probe) == 0,
        "u64thirteen leaf N13: probe misses input",
    );
}

#[derive(Clone, Copy)]
struct ContextU64Thirteen {
    base: *mut u64,
    probe: u64,
    initial_count: usize,
    hits: usize,
}

static mut CONTEXT_U64_THIRTEEN: ContextU64Thirteen =
    ContextU64Thirteen { base: ptr::null_mut(), probe: 0, initial_count: 0, hits: 0 };

fn context13() -> ContextU64Thirteen {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT_U64_THIRTEEN) }
}

fn register13(v: &mut [u64; 13], probe: u64) {
    let ctx = ContextU64Thirteen {
        base: v.as_mut_ptr(),
        probe,
        initial_count: count_matching_values(v, &probe),
        hits: 0,
    };
    // SAFETY: caller owns initialized exact array; invoked before the trait entry, outside PFC.
    unsafe { *ptr::addr_of_mut!(CONTEXT_U64_THIRTEEN) = ctx };
}

/// Closed dispatch: only u64 / U64Cmp is implemented; no blanket or fallback implementation.
trait SwapBridgeU64Thirteen<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridgeU64Thirteen<U64Cmp> for u64 {
    unsafe fn exchange(v: *mut u64, a: usize, b: usize, is_less: &mut U64Cmp) {
        kani::cover(true, "u64thirteen N13: adapter entered");
        let ctx = context13();
        kani::assert(v == ctx.base, "u64thirteen N13: actual base matches registered root");
        kani::assert(
            a < 13 && b < 13 && a != b,
            "u64thirteen N13: actual pair distinct and in range",
        );
        let accepted = canonical(*is_less);
        kani::assert(accepted, "u64thirteen canonical comparator required");
        if !accepted {
            return;
        }
        // SAFETY: same actual array/indices/comparator, with memory requires checked at the call.
        // Probe is by value; the verified target cannot write context or the hit counter.
        unsafe { swap_u64_net13(v, a, b, *is_less, ctx.probe) };
        // SAFETY: dedicated proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_U64_THIRTEEN.hits) += 1 };
        kani::assert(
            count13_u64(v, ctx.probe) == ctx.initial_count,
            "u64thirteen N13: count invariant after actual exchange",
        );
    }
}

// Same raw parameters, return and two type parameters; only the bridge bound narrows the proof.
unsafe fn adapter_u64thirteen<T: SwapBridgeU64Thirteen<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

fn check_context13(v: *mut u64, probe: u64, initial_count: usize) {
    let ctx = context13();
    kani::assert(ctx.hits == 45, "u64thirteen N13: complete actual hit count");
    kani::assert(ctx.base == v, "u64thirteen N13: context base frame");
    kani::assert(ctx.probe == probe, "u64thirteen N13: context probe frame");
    kani::assert(
        ctx.initial_count == initial_count,
        "u64thirteen N13: context initial-count frame",
    );
}

// Shared composed actual-entry caller for the positive and count control; assertions only.
// It never selects or reimplements a network algorithm.
fn run13(v: &mut [u64; 13], probe: u64, cmp: &mut U64Cmp) {
    let base = v.as_mut_ptr();
    let initial_count = count_matching_values(v, &probe);
    register13(v, probe);
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "u64thirteen N13: canonical comparator unchanged");
    check_context13(base, probe, initial_count);
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64thirteen)]
#[kani::stub_verified(swap_u64_net13)]
#[kani::unwind(25)]
fn u64thirteen_composed_u64_n13() {
    let mut v: [u64; 13] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp: U64Cmp = StrictU64::CMP;
    run13(&mut v, probe, &mut cmp);
    kani::cover(context13().hits == 45, "u64thirteen N13: all actual exchanges intercepted");
    kani::assert(is_sorted_by(&v, &mut cmp), "u64thirteen N13: sorted output");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64thirteen N13: full-value count preserved",
    );
    kani::cover(!prefix_unchanged(&v, &pre, 0), "u64thirteen N13: sort moves elements");
    kani::cover(count_matching_values(&pre, &probe) > 0, "u64thirteen N13: probe hits input");
    kani::cover(count_matching_values(&pre, &probe) == 0, "u64thirteen N13: probe misses input");
    let mut duplicates = false;
    let mut i = 1;
    while i < 13 {
        duplicates |= v[i] == v[i - 1];
        i += 1;
    }
    kani::cover(duplicates, "u64thirteen N13: duplicates present");
    kani::cover(
        probe > u8::MAX as u64 && count_matching_values(&pre, &probe) > 0,
        "u64thirteen N13: high-bit probe hits input",
    );
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64thirteen)]
#[kani::stub_verified(swap_u64_net13)]
#[kani::unwind(25)]
fn u64thirteen_wrong_cmp_u64_n13() {
    let mut v: [u64; 13] = kani::any();
    let probe: u64 = kani::any();
    register13(&mut v, probe);
    let mut cmp: U64Cmp = always_true_u64;
    kani::cover(true, "u64thirteen N13 wrong comparator: actual entry reached");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No sorted/count/hit result assertion: only the adapter's literal canonical guard must fail.
}

#[kani::proof]
#[kani::stub(swap_if_less, adapter_u64thirteen)]
#[kani::stub_verified(swap_u64_net13)]
#[kani::unwind(25)]
fn u64thirteen_count_negative_u64_n13() {
    const P: u64 = 1u64 << 40;
    let mut v = [P; 13];
    let pre = v;
    let probe = P;
    let mut cmp: U64Cmp = StrictU64::CMP;
    run13(&mut v, probe, &mut cmp);
    kani::cover(true, "u64thirteen N13 negative: sort returned before corruption");
    // Larger value with the same low 32 bits: order stays, count(P) drops from thirteen to twelve.
    v[12] = 1u64 << 41;
    kani::assert(is_sorted_by(&v, &mut cmp), "u64thirteen N13 negative: sorted after corruption");
    kani::cover(true, "u64thirteen N13 negative: corrupted count check reached");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64thirteen N13 negative: full-value count preserved",
    );
}
