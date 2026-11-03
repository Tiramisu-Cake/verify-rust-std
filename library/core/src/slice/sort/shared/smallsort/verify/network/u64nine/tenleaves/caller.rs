//! U64-TEN-CALLER: actual `<u64 as UnstableSmallSortTypeImpl>::small_sort` N10 composed from the
//! two U64-TEN-LEAVES leaves. The real network runs sort9 on prefix9 (25 raw swap_if_less), then
//! insertion offset9 runs one raw insert_tail(begin0, tail9) and returns (no merge).
//! Composed roots replace only those two raw helpers by closed u64/U64Cmp adapters that check the
//! actual arguments and forward them unchanged to the verified swap_u64_net9 / insert_tail_profile.
//! T=u64, F=U64Cmp, value StrictU64::CMP (reified strict_less::<u64>); one shared full-u64 probe.
//! No kani::cover in any helper or adapter: covers live only in the roots.

use super::super::super::{StrictU64, count_matching_values};
use super::super::{U64Cmp, canonical, count9_u64, swap_u64_net9};
use super::sorted10_u64;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{
    Profile, insert_tail_profile, model_count, model_sorted,
};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

/// Phase-aware proof context. Snapshot fields are written once by `register_u64ten`; only the
/// adapter instrumentation writes the two hit counters, always outside the contracted targets.
#[derive(Clone, Copy)]
struct ContextU64Ten {
    root: *mut u64,
    probe: u64,
    initial_prefix_count9: usize,
    initial_count10: usize,
    initial_tail: u64,
    swap_hits: usize,
    insert_hits: usize,
    fail_swap: bool,
    fail_insert: bool,
}

static mut CONTEXT_U64_TEN: ContextU64Ten = ContextU64Ten {
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

fn context_u64ten() -> ContextU64Ten {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(CONTEXT_U64_TEN) }
}

/// The whole exact backing10 from `v`: one allocation, aligned, readable and writable.
fn backing10_u64(v: *mut u64) -> bool {
    !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v as *const u64, 10))
        && can_write(ptr::slice_from_raw_parts_mut(v, 10))
        && same_allocation(v as *const u64, v.wrapping_add(9) as *const u64)
}

/// The one typed full-u64 count predicate of the final posts and the count control.
fn count10_preserved_u64(pre: &[u64; 10], v: &[u64; 10], probe: u64) -> bool {
    count_matching_values(pre, &probe) == count_matching_values(v, &probe)
}

/// Outside every contracted target, before the actual entry: one chosen probe fills both the
/// context and the StrictU64 profile probe; snapshots, zero counters and control flags.
fn register_u64ten(
    v: &mut [u64; 10],
    probe: u64,
    fail_swap: bool,
    fail_insert: bool,
) -> ContextU64Ten {
    let initial_prefix_count9 = count_matching_values(&v[..9], &probe);
    let initial_tail = v[9];
    let initial_count10 = initial_prefix_count9 + (initial_tail == probe) as usize;
    kani::assert(
        initial_count10 == count_matching_values(v, &probe),
        "u64tencall register: prefix9 plus tail equals whole count10",
    );
    let ctx = ContextU64Ten {
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
    StrictU64::set_probe(probe);
    // SAFETY: caller owns the initialized exact array; invoked before the trait entry.
    unsafe { *ptr::addr_of_mut!(CONTEXT_U64_TEN) = ctx };
    ctx
}

/// Closed dispatch: only u64 / U64Cmp is implemented; no blanket or fallback implementation.
trait SwapBridgeU64Ten<F>: Sized {
    unsafe fn exchange(v: *mut Self, a: usize, b: usize, is_less: &mut F);
}

impl SwapBridgeU64Ten<U64Cmp> for u64 {
    unsafe fn exchange(v: *mut u64, a: usize, b: usize, is_less: &mut U64Cmp) {
        let ctx = context_u64ten();
        kani::assert(v == ctx.root, "u64tencall swap: actual base is the registered root");
        kani::assert(a < 9 && b < 9 && a != b, "u64tencall swap: actual pair distinct in prefix9");
        kani::assert(canonical(*is_less), "u64tencall swap: received comparator canonical");
        kani::assert(backing10_u64(v), "u64tencall swap: actual base spans backing10");
        kani::assert(StrictU64::probe() == ctx.probe, "u64tencall swap: profile probe frame");
        kani::assert(ctx.insert_hits == 0, "u64tencall swap: swaps precede insertion");
        kani::assert(!ctx.fail_swap, "u64tencall actual swap adapter binding control");
        // SAFETY: same actual base/indices/comparator; swap_u64_net9's requires are checked here.
        // The probe is by value; the verified target cannot write the context or its counters.
        unsafe { swap_u64_net9(v, a, b, *is_less, ctx.probe) };
        // SAFETY: proof instrumentation outside the target's pair-only write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_U64_TEN.swap_hits) += 1 };
        kani::assert(
            count9_u64(v, ctx.probe) == ctx.initial_prefix_count9,
            "u64tencall swap: prefix9 count invariant",
        );
        // SAFETY: v is the checked actual root of the initialized backing10.
        let tail = unsafe { *v.add(9) };
        kani::assert(tail == ctx.initial_tail, "u64tencall swap: tail9 frame");
    }
}

// Same raw parameters, return and type parameters as swap_if_less; the bound only narrows.
unsafe fn swap_adapter_u64ten<T: SwapBridgeU64Ten<F>, F: FnMut(&T, &T) -> bool>(
    v: *mut T,
    a: usize,
    b: usize,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::exchange(v, a, b, is_less) };
}

/// Closed dispatch: only u64 / U64Cmp is implemented; no blanket or fallback implementation.
trait InsertBridgeU64Ten<F>: Sized {
    unsafe fn insert(begin: *mut Self, tail: *mut Self, is_less: &mut F);
}

impl InsertBridgeU64Ten<U64Cmp> for u64 {
    unsafe fn insert(begin: *mut u64, tail: *mut u64, is_less: &mut U64Cmp) {
        let ctx = context_u64ten();
        kani::assert(begin == ctx.root, "u64tencall insert: actual begin is the registered root");
        kani::assert(tail == begin.wrapping_add(9), "u64tencall insert: actual tail is begin+9");
        kani::assert(canonical(*is_less), "u64tencall insert: received comparator canonical");
        kani::assert(ctx.swap_hits == 25, "u64tencall insert: all 25 swaps precede insertion");
        kani::assert(ctx.insert_hits == 0, "u64tencall insert: single insertion");
        kani::assert(backing10_u64(begin), "u64tencall insert: region10 allocated and writable");
        kani::assert(StrictU64::probe() == ctx.probe, "u64tencall insert: profile probe frame");
        // The real network must establish the profile's sorted-prefix premise; never assumed.
        kani::assert(
            model_sorted::<StrictU64>(begin, 9),
            "u64tencall insert: prefix9 sorted by the real network",
        );
        kani::assert(
            count9_u64(begin, ctx.probe) == ctx.initial_prefix_count9,
            "u64tencall insert: prefix9 count before insertion",
        );
        // SAFETY: tail is begin+9 inside the checked initialized backing10.
        let tail_value = unsafe { *tail };
        kani::assert(
            tail_value == ctx.initial_tail,
            "u64tencall insert: tail9 frame before insertion",
        );
        kani::assert(
            model_count::<StrictU64>(begin, 10) == ctx.initial_count10,
            "u64tencall insert: count10 before insertion",
        );
        kani::assert(!ctx.fail_insert, "u64tencall actual insert adapter binding control");
        // SAFETY: same actual begin/tail/comparator; the profile's requires are checked here.
        unsafe { insert_tail_profile::<StrictU64>(begin, tail, *is_less) };
        // SAFETY: proof instrumentation outside the target's region10 write set.
        unsafe { *ptr::addr_of_mut!(CONTEXT_U64_TEN.insert_hits) += 1 };
        // Tail and prefix9 count may change now; only the whole region is constrained.
        kani::assert(model_sorted::<StrictU64>(begin, 10), "u64tencall insert: region10 sorted");
        kani::assert(
            model_count::<StrictU64>(begin, 10) == ctx.initial_count10,
            "u64tencall insert: count10 after insertion",
        );
        kani::assert(StrictU64::probe() == ctx.probe, "u64tencall insert: probe after insertion");
    }
}

// Same raw parameters, return and type parameters as insert_tail; the bound only narrows.
unsafe fn insert_adapter_u64ten<T: InsertBridgeU64Ten<F>, F: FnMut(&T, &T) -> bool>(
    begin: *mut T,
    tail: *mut T,
    is_less: &mut F,
) {
    // SAFETY: the sole closed implementation checks actual arguments and forwards them unchanged.
    unsafe { T::insert(begin, tail, is_less) };
}

/// Exact hit counts and frame of every snapshot field after the actual entry returned.
fn check_context_u64ten(registered: ContextU64Ten, v: *mut u64, probe: u64) {
    let ctx = context_u64ten();
    kani::assert(ctx.swap_hits == 25, "u64tencall: exactly 25 actual swaps");
    kani::assert(ctx.insert_hits == 1, "u64tencall: exactly one actual insert_tail");
    kani::assert(ctx.root == v && ctx.root == registered.root, "u64tencall: root frame");
    kani::assert(ctx.probe == probe && ctx.probe == registered.probe, "u64tencall: probe frame");
    kani::assert(StrictU64::probe() == probe, "u64tencall: profile probe frame");
    kani::assert(
        ctx.initial_prefix_count9 == registered.initial_prefix_count9
            && ctx.initial_count10 == registered.initial_count10
            && ctx.initial_tail == registered.initial_tail,
        "u64tencall: snapshot frame",
    );
    kani::assert(
        ctx.fail_swap == registered.fail_swap && ctx.fail_insert == registered.fail_insert,
        "u64tencall: control flag frame",
    );
}

// Shared actual-entry caller for the positive and count control (flags false). It never selects
// or reimplements the network or the insertion.
fn run_u64ten(v: &mut [u64; 10], probe: u64, cmp: &mut U64Cmp) {
    let base = v.as_mut_ptr();
    let registered = register_u64ten(v, probe, false, false);
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, cmp);
    kani::assert(canonical(*cmp), "u64tencall: canonical outer comparator unchanged");
    check_context_u64ten(registered, base, probe);
}

/// Pure typed final posts against the pre-state snapshot; never calls the comparator.
fn check_final_u64ten(v: &[u64; 10], pre: &[u64; 10], probe: u64) {
    kani::assert(sorted10_u64(v), "u64tencall: final sorted10");
    kani::assert(
        count10_preserved_u64(pre, v, probe),
        "u64tencall: final full-value count preserved",
    );
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]
#[kani::stub_verified(super::super::swap_u64_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn u64tencall_positive_u64_n10() {
    let mut v: [u64; 10] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp: U64Cmp = StrictU64::CMP;
    run_u64ten(&mut v, probe, &mut cmp);
    check_final_u64ten(&v, &pre, probe);
    kani::cover(true, "u64tencall positive: returned");
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
    let ctx = context_u64ten();
    kani::cover(descending, "u64tencall positive: input has descending adjacent pair");
    kani::cover(hits10 > 0, "u64tencall positive: probe hits pre10");
    kani::cover(hits10 == 0, "u64tencall positive: probe misses pre10");
    kani::cover(duplicate, "u64tencall positive: pre10 has duplicate value");
    kani::cover(
        probe == pre[9] && hits9 == 0,
        "u64tencall positive: probe hits only original tail",
    );
    kani::cover(ctx.swap_hits == 25 && ctx.insert_hits == 1, "u64tencall positive: all hits");
    kani::cover(tail_min, "u64tencall positive: tail-min input returned");
    kani::cover(
        probe >= (1u64 << 40) && hits10 > 0,
        "u64tencall positive: high-bit probe hits pre10",
    );
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]
#[kani::stub_verified(super::super::swap_u64_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn u64tencall_swap_binding_negative_u64_n10() {
    let mut v = [0u64; 10];
    let mut cmp: U64Cmp = StrictU64::CMP;
    register_u64ten(&mut v, 0, true, false);
    kani::cover(true, "u64tencall swap control: actual entry reached");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No post-return obligations: only the swap adapter's literal marker must fail.
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]
#[kani::stub_verified(super::super::swap_u64_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn u64tencall_insert_binding_negative_u64_n10() {
    let mut v = [0u64; 10];
    let mut cmp: U64Cmp = StrictU64::CMP;
    register_u64ten(&mut v, 0, false, true);
    kani::cover(true, "u64tencall insert control: actual entry reached");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    // No post-return obligations: only the insert adapter's literal marker must fail.
}

#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]
#[kani::stub_verified(super::super::swap_u64_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn u64tencall_count_negative_u64_n10() {
    const P: u64 = 1u64 << 40;
    const Q: u64 = 1u64 << 41;
    let mut v = [P; 10];
    let pre = v;
    let probe = P;
    let mut cmp: U64Cmp = StrictU64::CMP;
    run_u64ten(&mut v, probe, &mut cmp);
    check_final_u64ten(&v, &pre, probe);
    kani::cover(true, "u64tencall negative: returned before corruption");
    // Larger value with the same low 32 bits: order stays, count(P) drops from ten to nine.
    v[9] = Q;
    kani::assert(sorted10_u64(&v), "u64tencall negative: sorted after corruption");
    kani::cover(true, "u64tencall negative: count check reached");
    kani::assert(
        count10_preserved_u64(&pre, &v, probe),
        "u64tencall negative: full-value count preserved",
    );
}

// COVERCOST diagnostic (memory only, no proof credit): byte clone of u64tencall_positive_u64_n10
// with every kani::cover of the root body removed; nothing else differs. Helpers and adapters
// above are shared unchanged and contain no kani::cover.
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::swap_if_less, swap_adapter_u64ten)]
#[kani::stub_verified(super::super::swap_u64_net9)]
#[kani::stub(crate::slice::sort::shared::smallsort::insert_tail, insert_adapter_u64ten)]
#[kani::stub_verified(super::super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
#[allow(unused_variables, unused_assignments)]
fn u64tencall_positive_nocover_u64_n10() {
    let mut v: [u64; 10] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp: U64Cmp = StrictU64::CMP;
    run_u64ten(&mut v, probe, &mut cmp);
    check_final_u64ten(&v, &pre, probe);
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
    let ctx = context_u64ten();
}
