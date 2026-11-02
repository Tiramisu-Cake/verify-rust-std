//! NETTEN-CALLER: actual `<u8 as UnstableSmallSortTypeImpl>::small_sort` N10 composed from the
//! two NETTEN leaves. The real network runs sort9 on prefix9 (25 raw swap_if_less), then
//! insertion offset9 runs one raw insert_tail(begin0, tail9) and returns (no merge).
//! Composed roots replace only those two raw helpers by closed u8/U8Cmp adapters that check the
//! actual arguments and forward them unchanged to the verified swap_net9 / insert_tail_profile.
//! T=u8, F=U8Cmp, value StrictU8::CMP (reified strict_less::<u8>); one shared probe.
//! No kani::cover in any helper or adapter: covers live only in the roots.

use super::super::super::{StrictU8, count_matching_values};
use super::super::{U8Cmp, canonical, count9, swap_net9};
use super::sorted10;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{
    Profile, insert_tail_profile, model_count, model_sorted,
};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

/// Phase-aware proof context. Snapshot fields are written once by `register10`; only the adapter
/// instrumentation writes the two hit counters, always outside the contracted targets.
#[derive(Clone, Copy)]
struct ContextTen {
    root: *mut u8,
    probe: u8,
    initial_prefix_count9: usize,
    initial_count10: usize,
    initial_tail: u8,
    swap_hits: usize,
    insert_hits: usize,
    fail_swap: bool,
    fail_insert: bool,
}

static mut CONTEXT_TEN: ContextTen = ContextTen {
    root: ptr::null_mut(),
    probe: 0,
    initial_prefix_count9: 0,
    initial_count10: 0,
    initial_tail: 0,
    swap_hits: 0,
    insert_hits: 0,
    fail_swap: false,
    fail_insert: false,
};

fn context10() -> ContextTen {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT_TEN) }
}

/// The whole exact backing10 from `v`: one allocation, readable and writable.
fn backing10(v: *mut u8) -> bool {
    !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u8, 10))
        && can_write(ptr::slice_from_raw_parts_mut(v, 10))
        && same_allocation(v as *const u8, v.wrapping_add(9) as *const u8)
}

/// Outside every contracted target, before the actual entry: one chosen probe fills both the
/// context and the StrictU8 profile probe; snapshots, zero counters and control flags.
fn register10(v: &mut [u8; 10], probe: u8, fail_swap: bool, fail_insert: bool) -> ContextTen {
    let initial_prefix_count9 = count_matching_values(&v[..9], &probe);
    let initial_tail = v[9];
    let initial_count10 = initial_prefix_count9 + (initial_tail == probe) as usize;
    kani::assert(
        initial_count10 == count_matching_values(v, &probe),
        "nettencall register: prefix9 plus tail equals whole count10",
    );
    let ctx = ContextTen {
        root: v.as_mut_ptr(),
        probe,
        initial_prefix_count9,
        initial_count10,
        initial_tail,
        swap_hits: 0,
        insert_hits: 0,
        fail_swap,
        fail_insert,
    };
    StrictU8::set_probe(probe);
    // SAFETY: caller owns the initialized exact array; invoked before the trait entry.
    unsafe { *ptr::addr_of_mut!(CONTEXT_TEN) = ctx };
    ctx
}

/// Closed dispatch: only u8 / U8Cmp is implemented; no blanket or fallback implementation.
trait SwapBridge10<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridge10<U8Cmp> for u8 {
    unsafe fn exchange(v: *mut u8, a: usize, b: usize, is_less: &mut U8Cmp) {
        let ctx = context10();
        kani::assert(v == ctx.root, "nettencall swap: actual base is the registered root");
        kani::assert(a < 9 && b < 9 && a != b, "nettencall swap: actual pair distinct in prefix9");
        kani::assert(canonical(*is_less), "nettencall swap: received comparator canonical");
        kani::assert(backing10(v), "nettencall swap: actual base spans backing10");
        kani::assert(StrictU8::probe() == ctx.probe, "nettencall swap: profile probe frame");
        kani::assert(ctx.insert_hits == 0, "nettencall swap: swaps precede insertion");
        kani::assert(!ctx.fail_swap, "nettencall actual swap adapter binding control");
        // SAFETY: same actual base/indices/comparator; swap_net9's requires are checked here.
        // The probe is by value; the verified target cannot write the context or its counters.
        unsafe { swap_net9(v, a, b, *is_less, ctx.probe) };
        // SAFETY: proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_TEN.swap_hits) += 1 };
        kani::assert(
            count9(v, ctx.probe) == ctx.initial_prefix_count9,
            "nettencall swap: prefix9 count invariant",
        );
        // SAFETY: v is the checked actual root of the initialized backing10.
        let tail = unsafe { *v.add(9) };
        kani::assert(tail == ctx.initial_tail, "nettencall swap: tail9 frame");
    }
}

// Same raw parameters, return and type parameters as swap_if_less; the bound only narrows.
unsafe fn swap_adapter10<T: SwapBridge10<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

/// Closed dispatch: only u8 / U8Cmp is implemented; no blanket or fallback implementation.
trait InsertBridge10<F>: Sized {
    unsafe fn insert(begin: *mut Self, tail: *mut Self, is_less: &mut F);
}

impl InsertBridge10<U8Cmp> for u8 {
    unsafe fn insert(begin: *mut u8, tail: *mut u8, is_less: &mut U8Cmp) {
        let ctx = context10();
        kani::assert(begin == ctx.root, "nettencall insert: actual begin is the registered root");
        kani::assert(tail == begin.wrapping_add(9), "nettencall insert: actual tail is begin+9");
        kani::assert(canonical(*is_less), "nettencall insert: received comparator canonical");
        kani::assert(ctx.swap_hits == 25, "nettencall insert: all 25 swaps precede insertion");
        kani::assert(ctx.insert_hits == 0, "nettencall insert: single insertion");
        kani::assert(backing10(begin), "nettencall insert: region10 allocated and writable");
        kani::assert(StrictU8::probe() == ctx.probe, "nettencall insert: profile probe frame");
        // The real network must establish the profile's sorted-prefix premise; never assumed.
        kani::assert(
            model_sorted::<StrictU8>(begin, 9),
            "nettencall insert: prefix9 sorted by the real network",
        );
        kani::assert(
            count9(begin, ctx.probe) == ctx.initial_prefix_count9,
            "nettencall insert: prefix9 count before insertion",
        );
        // SAFETY: tail is begin+9 inside the checked initialized backing10.
        let tail_value = unsafe { *tail };
        kani::assert(
            tail_value == ctx.initial_tail,
            "nettencall insert: tail9 frame before insertion",
        );
        kani::assert(
            model_count::<StrictU8>(begin, 10) == ctx.initial_count10,
            "nettencall insert: count10 before insertion",
        );
        kani::assert(!ctx.fail_insert, "nettencall actual insert adapter binding control");
        // SAFETY: same actual begin/tail/comparator; the profile's requires are checked here.
        unsafe { insert_tail_profile::<StrictU8>(begin, tail, *is_less) };
        // SAFETY: proof instrumentation outside the target's region10 write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_TEN.insert_hits) += 1 };
        // Tail and prefix9 count may change now; only the whole region is constrained.
        kani::assert(model_sorted::<StrictU8>(begin, 10), "nettencall insert: region10 sorted");
        kani::assert(
            model_count::<StrictU8>(begin, 10) == ctx.initial_count10,
            "nettencall insert: count10 after insertion",
        );
        kani::assert(StrictU8::probe() == ctx.probe, "nettencall insert: probe after insertion");
    }
}

// Same raw parameters, return and type parameters as insert_tail; the bound only narrows.
unsafe fn insert_adapter10<T: InsertBridge10<F>, F: FnMut(&T, &T) -> bool>(
    begin: *mut T,
    tail: *mut T,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::insert(begin, tail, is_less) };
}

/// Exact hit counts and frame of every snapshot field after the actual entry returned.
fn check_context10(registered: ContextTen, v: *mut u8, probe: u8) {
    let ctx = context10();
    kani::assert(ctx.swap_hits == 25, "nettencall: exactly 25 actual swaps");
    kani::assert(ctx.insert_hits == 1, "nettencall: exactly one actual insert_tail");
    kani::assert(ctx.root == v && ctx.root == registered.root, "nettencall: root frame");
    kani::assert(ctx.probe == probe && ctx.probe == registered.probe, "nettencall: probe frame");
    kani::assert(StrictU8::probe() == probe, "nettencall: profile probe frame");
    kani::assert(
        ctx.initial_prefix_count9 == registered.initial_prefix_count9
            && ctx.initial_count10 == registered.initial_count10
            && ctx.initial_tail == registered.initial_tail,
        "nettencall: snapshot frame",
    );
    kani::assert(
        ctx.fail_swap == registered.fail_swap && ctx.fail_insert == registered.fail_insert,
        "nettencall: control flag frame",
    );
}

// Shared actual-entry caller for the positive and count control (flags false). It never selects
// or reimplements the network or the insertion.
fn run10(v: &mut [u8; 10], probe: u8, cmp: &mut U8Cmp) {
    let base = v.as_mut_ptr();
    let registered = register10(v, probe, false, false);
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "nettencall: canonical outer comparator unchanged");
    check_context10(registered, base, probe);
}

/// Pure typed final posts against the pre-state snapshot; never calls the comparator.
fn check_final10(v: &[u8; 10], pre: &[u8; 10], probe: u8) {
    kani::assert(sorted10(v), "nettencall: final sorted10");
    kani::assert(
        count_matching_values(pre, &probe) == count_matching_values(v, &probe),
        "nettencall: final full-value count preserved",
    );
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]
#[kani::stub_verified(super::super::swap_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn nettencall_positive_u8_n10() {
    let mut v: [u8; 10] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let mut cmp: U8Cmp = StrictU8::CMP;
    run10(&mut v, probe, &mut cmp);
    check_final10(&v, &pre, probe);
    kani::cover(true, "nettencall positive: returned");
    let mut descending = false;
    let mut duplicate = false;
    let mut tail_min = true;
    let mut i = 0;
    while i < 10 {
        if i > 0 && pre[i] < pre[i - 1] {
            descending = true;
        }
        let mut j = i + 1;
        while j < 10 {
            duplicate |= pre[i] == pre[j];
            j += 1;
        }
        if i < 9 && pre[9] >= pre[i] {
            tail_min = false;
        }
        i += 1;
    }
    let hits10 = count_matching_values(&pre, &probe);
    let hits9 = count_matching_values(&pre[..9], &probe);
    let ctx = context10();
    kani::cover(descending, "nettencall positive: input has descending adjacent pair");
    kani::cover(hits10 > 0, "nettencall positive: probe hits pre10");
    kani::cover(hits10 == 0, "nettencall positive: probe misses pre10");
    kani::cover(duplicate, "nettencall positive: pre10 has duplicate value");
    kani::cover(
        probe == pre[9] && hits9 == 0,
        "nettencall positive: probe hits only original tail",
    );
    kani::cover(ctx.swap_hits == 25 && ctx.insert_hits == 1, "nettencall positive: all hits");
    kani::cover(tail_min, "nettencall positive: tail-min input returned");
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]
#[kani::stub_verified(super::super::swap_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn nettencall_swap_binding_negative_u8_n10() {
    let mut v = [0u8; 10];
    let mut cmp: U8Cmp = StrictU8::CMP;
    register10(&mut v, 0, true, false);
    kani::cover(true, "nettencall swap control: actual entry reached");
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No post-return obligations: only the swap adapter's literal marker must fail.
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]
#[kani::stub_verified(super::super::swap_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn nettencall_insert_binding_negative_u8_n10() {
    let mut v = [0u8; 10];
    let mut cmp: U8Cmp = StrictU8::CMP;
    register10(&mut v, 0, false, true);
    kani::cover(true, "nettencall insert control: actual entry reached");
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No post-return obligations: only the insert adapter's literal marker must fail.
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter10)]
#[kani::stub_verified(super::super::swap_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter10)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn nettencall_count_negative_u8_n10() {
    let mut v = [0u8; 10];
    let pre = v;
    let probe = 0u8;
    let mut cmp: U8Cmp = StrictU8::CMP;
    run10(&mut v, probe, &mut cmp);
    check_final10(&v, &pre, probe);
    kani::cover(true, "nettencall negative: returned before corruption");
    v[9] = 1;
    kani::assert(sorted10(&v), "nettencall negative: sorted after corruption");
    kani::cover(true, "nettencall negative: count check reached");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "nettencall negative: full-value count preserved",
    );
}
