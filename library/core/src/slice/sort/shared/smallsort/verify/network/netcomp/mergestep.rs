//! MERGESTEP: closed u8/U8Cmp step summaries of the real `merge_up` / `merge_down` and an actual
//! composed merge4 calibration. T = u8, F = U8Cmp, value StrictU8::CMP. Each step forwarder calls
//! the real raw helper and returns only the scalar decision `take_left`; one shared pure decoder
//! rebuilds the raw pointer tuple and is checked against the helper's actual result in the leaves.
//! The composed roots intercept the raw helpers through closed u8/U8Cmp adapters. Runtime helpers,
//! their `inline(always)` and the existing merge profile are unchanged. No N18/N32 or generic
//! FnMut order/frame claim: every restriction here is a closed proof domain.

use super::super::{StrictU8, count_matching_values};
use super::{U8Cmp, canonical};
use crate::mem::MaybeUninit;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{Profile, merge_profile};
use crate::slice::sort::shared::smallsort::{merge_down, merge_up};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

type RawStep = (*const u8, *const u8, *mut u8);

/// Shared pure decoder of a forward step: the raw tuple `merge_up` returns for `take_left`.
fn up_decode(l: *const u8, r: *const u8, d: *mut u8, take_left: bool) -> RawStep {
    (l.wrapping_add(take_left as usize), r.wrapping_add((!take_left) as usize), d.wrapping_add(1))
}

/// Shared pure decoder of a reverse step: the raw tuple `merge_down` returns for `take_left`.
fn down_decode(l: *const u8, r: *const u8, d: *mut u8, take_left: bool) -> RawStep {
    (l.wrapping_sub(take_left as usize), r.wrapping_sub((!take_left) as usize), d.wrapping_sub(1))
}

fn same_step(a: RawStep, b: RawStep) -> bool {
    a.0 == b.0 && a.1 == b.1 && a.2 == b.2
}

fn cell(p: *const u8) -> u8 {
    // SAFETY: callers pass a readable initialized cell (requires, or a checked written range).
    unsafe { *p }
}

// Pure decisions on full values; ties: up takes left, down takes right.
fn up_take_left(l: *const u8, r: *const u8) -> bool {
    cell(l) <= cell(r)
}

fn down_take_left(l: *const u8, r: *const u8) -> bool {
    cell(r) < cell(l)
}

fn up_selected(l: *const u8, r: *const u8) -> u8 {
    if up_take_left(l, r) { cell(l) } else { cell(r) }
}

fn down_selected(l: *const u8, r: *const u8) -> u8 {
    if down_take_left(l, r) { cell(l) } else { cell(r) }
}

/// Two distinct readable aligned cells of one source allocation; one writable destination cell
/// in another allocation. The destination value is never read (it may be uninitialized).
fn up_geometry(l: *const u8, r: *const u8, d: *mut u8) -> bool {
    !l.is_null()
        && !r.is_null()
        && !d.is_null()
        && l.is_aligned()
        && r.is_aligned()
        && d.is_aligned()
        && can_dereference(l)
        && can_dereference(r)
        && same_allocation(l, r)
        && l != r
        && can_write(d)
        && !same_allocation(l, d as *const u8)
}

/// Raw `merge_down` computes `dst.sub(1)`: its predecessor must be a writable cell of the same
/// destination allocation (so an allocation-start `d` is outside this domain). Not initialized.
fn down_geometry(l: *const u8, r: *const u8, d: *mut u8) -> bool {
    up_geometry(l, r, d)
        && same_allocation(d as *const u8, d.wrapping_sub(1) as *const u8)
        && can_write(d.wrapping_sub(1))
}

// Concrete step targets, declared before their PFCs; no probe/context reads or ghost writes.
#[kani::requires(canonical(cmp))]
#[kani::requires(up_geometry(left, right, dst))]
#[kani::modifies(dst)]
#[kani::ensures(|take_left: &bool| *take_left == old(up_take_left(left, right)))]
#[kani::ensures(|_| cell(dst as *const u8) == old(up_selected(left, right)))]
unsafe fn up_step_u8(left: *const u8, right: *const u8, dst: *mut u8, cmp: U8Cmp) -> bool {
    // SAFETY: the requires make both source cells readable initialized values.
    let (lv, rv) = unsafe { (*left, *right) };
    let mut actual: U8Cmp = cmp;
    // SAFETY: distinct readable source cells, writable destination cell in another allocation.
    let raw = unsafe { merge_up(left, right, dst, &mut actual) };
    let take_left = lv <= rv;
    kani::assert(
        same_step(raw, up_decode(left, right, dst, take_left)),
        "mergestep up step: actual raw tuple equals decoder",
    );
    take_left
}

#[kani::requires(canonical(cmp))]
#[kani::requires(down_geometry(left, right, dst))]
#[kani::modifies(dst)]
#[kani::ensures(|take_left: &bool| *take_left == old(down_take_left(left, right)))]
#[kani::ensures(|_| cell(dst as *const u8) == old(down_selected(left, right)))]
unsafe fn down_step_u8(left: *const u8, right: *const u8, dst: *mut u8, cmp: U8Cmp) -> bool {
    // SAFETY: the requires make both source cells readable initialized values.
    let (lv, rv) = unsafe { (*left, *right) };
    let mut actual: U8Cmp = cmp;
    // SAFETY: distinct readable source cells, writable destination cell and predecessor.
    let raw = unsafe { merge_down(left, right, dst, &mut actual) };
    let take_left = rv < lv;
    kani::assert(
        same_step(raw, down_decode(left, right, dst, take_left)),
        "mergestep down step: actual raw tuple equals decoder",
    );
    take_left
}

// Independent no-stub leaves: source18 any, partially initialized destination32.

/// Only `mask` cells receive `init` values; every other destination cell stays uninitialized.
fn partial_dst32(
    scratch: &mut MaybeUninit<[u8; 32]>,
    mask: &[bool; 32],
    init: &[u8; 32],
) -> *mut u8 {
    let base = scratch.as_mut_ptr() as *mut u8;
    let mut c = 0;
    while c < 32 {
        if mask[c] {
            // SAFETY: c < 32 inside the separate destination allocation.
            unsafe { base.add(c).write(init[c]) };
        }
        c += 1;
    }
    base
}

/// Reads only the written cell and cells initialized before the call; returns the written value.
fn check_step_leaf(
    src: &[u8; 18],
    pre: &[u8; 18],
    base: *mut u8,
    k: usize,
    mask: &[bool; 32],
    init: &[u8; 32],
    selected: u8,
    probe: u8,
) -> u8 {
    // SAFETY: the step wrote cell k < 32 on normal return.
    let out = unsafe { *base.add(k) };
    kani::assert(out == selected, "mergestep step leaf: written cell holds selected full value");
    kani::assert(
        (out == probe) == (selected == probe),
        "mergestep step leaf: written probe indicator equals selected source indicator",
    );
    let mut c = 0;
    while c < 32 {
        if c != k && mask[c] {
            // SAFETY: cell c < 32 was initialized before the call and is not the written cell.
            let now = unsafe { *base.add(c) };
            kani::assert(now == init[c], "mergestep step leaf: other initialized cells unchanged");
        }
        c += 1;
    }
    let mut c = 0;
    while c < 18 {
        kani::assert(src[c] == pre[c], "mergestep step leaf: source18 unchanged");
        c += 1;
    }
    out
}

#[kani::proof_for_contract(up_step_u8)]
#[kani::unwind(34)]
fn mergestep_up_leaf_u8() {
    let src: [u8; 18] = kani::any();
    let pre = src;
    let i: usize = kani::any_where(|&i| i < 18);
    let j: usize = kani::any_where(|&j| j < 18 && j != i);
    let k: usize = kani::any_where(|&k| k < 32);
    let mask: [bool; 32] = kani::any();
    let init: [u8; 32] = kani::any();
    let probe: u8 = kani::any();
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let base = partial_dst32(&mut scratch, &mask, &init);
    let s = src.as_ptr();
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: distinct cells i, j < 18 of source18; cell k < 32 of the separate scratch32.
    let take_left = unsafe { up_step_u8(s.add(i), s.add(j), base.add(k), cmp) };
    kani::assert(take_left == (pre[i] <= pre[j]), "mergestep up leaf: take_left iff left <= right");
    let selected = if take_left { pre[i] } else { pre[j] };
    let out = check_step_leaf(&src, &pre, base, k, &mask, &init, selected, probe);
    kani::cover(take_left, "mergestep up leaf: left selected");
    kani::cover(!take_left, "mergestep up leaf: right selected");
    kani::cover(pre[i] == pre[j], "mergestep up leaf: tie");
    kani::cover(out == probe, "mergestep up leaf: probe hits written value");
    kani::cover(out != probe, "mergestep up leaf: probe misses written value");
    kani::cover(i == 0 && j == 17, "mergestep up leaf: source cells 0 and 17");
    kani::cover(i == 17 && j == 0, "mergestep up leaf: source cells 17 and 0");
    kani::cover(k == 0, "mergestep up leaf: destination cell 0");
    kani::cover(k == 31, "mergestep up leaf: destination cell 31");
    kani::cover(!mask[k], "mergestep up leaf: written cell was uninitialized");
    kani::cover(mask[k], "mergestep up leaf: written cell was initialized");
}

#[kani::proof_for_contract(down_step_u8)]
#[kani::unwind(34)]
fn mergestep_down_leaf_u8() {
    let src: [u8; 18] = kani::any();
    let pre = src;
    let i: usize = kani::any_where(|&i| i < 18);
    let j: usize = kani::any_where(|&j| j < 18 && j != i);
    let k: usize = kani::any_where(|&k| k >= 1 && k < 32);
    let mask: [bool; 32] = kani::any();
    let init: [u8; 32] = kani::any();
    let probe: u8 = kani::any();
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let base = partial_dst32(&mut scratch, &mask, &init);
    let s = src.as_ptr();
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: distinct cells i, j < 18 of source18; cell 1 <= k < 32 of the separate scratch32.
    let take_left = unsafe { down_step_u8(s.add(i), s.add(j), base.add(k), cmp) };
    kani::assert(take_left == (pre[j] < pre[i]), "mergestep down leaf: take_left iff right < left");
    let selected = if take_left { pre[i] } else { pre[j] };
    let out = check_step_leaf(&src, &pre, base, k, &mask, &init, selected, probe);
    kani::cover(take_left, "mergestep down leaf: left selected");
    kani::cover(!take_left, "mergestep down leaf: right selected");
    kani::cover(pre[i] == pre[j], "mergestep down leaf: tie");
    kani::cover(out == probe, "mergestep down leaf: probe hits written value");
    kani::cover(out != probe, "mergestep down leaf: probe misses written value");
    kani::cover(i == 0 && j == 17, "mergestep down leaf: source cells 0 and 17");
    kani::cover(i == 17 && j == 0, "mergestep down leaf: source cells 17 and 0");
    kani::cover(k == 1, "mergestep down leaf: destination cell 1");
    kani::cover(k == 31, "mergestep down leaf: destination cell 31");
    kani::cover(!mask[k], "mergestep down leaf: written cell was uninitialized");
    kani::cover(mask[k], "mergestep down leaf: written cell was initialized");
    kani::cover(!mask[k - 1], "mergestep down leaf: predecessor uninitialized");
}

// Actual composed merge4: raw merge_up/down -> closed adapters -> verified step summaries.

const ACTIVE4: usize = 4;

/// Proof context, registered before the outer target and only read inside it.
#[derive(Clone, Copy)]
struct StepContext {
    src: *const u8,
    dst: *mut u8,
    active_len: usize,
    probe: u8,
    fail_up: bool,
    fail_down: bool,
}

static mut STEP_CONTEXT: StepContext = StepContext {
    src: ptr::null(),
    dst: ptr::null_mut(),
    active_len: 0,
    probe: 0,
    fail_up: false,
    fail_down: false,
};

fn step_context() -> StepContext {
    // SAFETY: proof-only single-threaded state, no references to the static are created.
    unsafe { *ptr::addr_of!(STEP_CONTEXT) }
}

fn register(src: &[u8; 18], dst: *mut u8, probe: u8, fail_up: bool, fail_down: bool) {
    let ctx =
        StepContext { src: src.as_ptr(), dst, active_len: ACTIVE4, probe, fail_up, fail_down };
    // SAFETY: proof-only state written outside the target, before the merge call.
    unsafe { *ptr::addr_of_mut!(STEP_CONTEXT) = ctx };
}

/// Index of `p` in `base[lo..hi]`, computed only after same-allocation and range checks.
fn index_in(base: *const u8, lo: usize, hi: usize, p: *const u8) -> Option<usize> {
    if !same_allocation(base, p) || p < base.wrapping_add(lo) || p >= base.wrapping_add(hi) {
        return None;
    }
    // SAFETY: one allocation and base + lo <= p < base + hi, inside the registered backing.
    Some((unsafe { p.offset_from(base) }) as usize)
}

/// Probe matches in `base[from..to]`; cells outside the range are never read.
fn count_cells(base: *const u8, from: usize, to: usize, probe: u8) -> usize {
    let mut n = 0;
    let mut c = 0;
    while c < ACTIVE4 {
        // SAFETY: c < ACTIVE4 and from <= c < to: a cell of a checked initialized range.
        if from <= c && c < to && unsafe { *base.add(c) } == probe {
            n += 1;
        }
        c += 1;
    }
    n
}

/// No strict inversion in `base[from..to]`; cells outside the range are never read.
fn cells_sorted(base: *const u8, from: usize, to: usize) -> bool {
    let mut ok = true;
    let mut c = 1;
    while c < ACTIVE4 {
        // SAFETY: from < c < to: both cells belong to a checked initialized range.
        if from < c && c < to && unsafe { *base.add(c) < *base.add(c - 1) } {
            ok = false;
        }
        c += 1;
    }
    ok
}

/// After an up step: written dst-prefix count equals the forward-consumed prefixes of both
/// halves. Assertions only; the two ledgers may overlap before the final std consumption check.
fn check_up_ledger(ctx: &StepContext, next: RawStep) {
    let (len, half) = (ctx.active_len, ctx.active_len / 2);
    let left_end = index_in(ctx.src, 0, half + 1, next.0);
    let right_end = index_in(ctx.src, half, len + 1, next.1);
    let dst_end = index_in(ctx.dst as *const u8, 0, len + 1, next.2 as *const u8);
    kani::assert(
        left_end.is_some() && right_end.is_some() && dst_end.is_some(),
        "mergestep up ledger: forward endpoints within bounds",
    );
    if let (Some(le), Some(re), Some(de)) = (left_end, right_end, dst_end) {
        let written = count_cells(ctx.dst, 0, de, ctx.probe);
        let consumed =
            count_cells(ctx.src, 0, le, ctx.probe) + count_cells(ctx.src, half, re, ctx.probe);
        kani::assert(
            written == consumed,
            "mergestep up ledger: written prefix count equals forward-consumed count",
        );
    }
}

/// After a down step: written dst-suffix count equals the reverse-consumed suffixes; then front
/// prefix order, back suffix order and the boundary. Reverse endpoints may lie one before a half,
/// so they are stepped with wrapping_add(1) before any distance is taken.
fn check_down_ledger(ctx: &StepContext, next: RawStep) {
    let (len, half) = (ctx.active_len, ctx.active_len / 2);
    let left_start = index_in(ctx.src, 0, half + 1, next.0.wrapping_add(1));
    let right_start = index_in(ctx.src, half, len + 1, next.1.wrapping_add(1));
    let dst_start = index_in(ctx.dst as *const u8, 0, len + 1, next.2.wrapping_add(1) as *const u8);
    kani::assert(
        left_start.is_some() && right_start.is_some() && dst_start.is_some(),
        "mergestep down ledger: reverse endpoints within bounds",
    );
    if let (Some(ls), Some(rs), Some(ds)) = (left_start, right_start, dst_start) {
        let written = count_cells(ctx.dst, ds, len, ctx.probe);
        let consumed =
            count_cells(ctx.src, ls, half, ctx.probe) + count_cells(ctx.src, rs, len, ctx.probe);
        kani::assert(
            written == consumed,
            "mergestep down ledger: written suffix count equals reverse-consumed count",
        );
        // The actual loop runs one merge_up before each merge_down (smallsort.rs source map), so
        // the written front prefix has the length of the written back suffix after this step.
        let front = len - ds;
        kani::assert(front <= ds, "mergestep down check: front prefix and back suffix disjoint");
        if front <= ds {
            let d = ctx.dst as *const u8;
            kani::assert(cells_sorted(d, 0, front), "mergestep down check: front prefix sorted");
            kani::assert(cells_sorted(d, ds, len), "mergestep down check: back suffix sorted");
            kani::assert(
                front == 0
                    || ds == len
                    || cell(d.wrapping_add(front - 1)) <= cell(d.wrapping_add(ds)),
                "mergestep down check: front last <= back first",
            );
        }
    }
}

/// Closed dispatch: only u8 / U8Cmp is implemented; no blanket or fallback implementation.
trait MergeStepBridge<F>: Sized {
    unsafe fn up(
        l: *const Self,
        r: *const Self,
        d: *mut Self,
        is_less: &mut F,
    ) -> (*const Self, *const Self, *mut Self);
    unsafe fn down(
        l: *const Self,
        r: *const Self,
        d: *mut Self,
        is_less: &mut F,
    ) -> (*const Self, *const Self, *mut Self);
}

impl MergeStepBridge<U8Cmp> for u8 {
    unsafe fn up(l: *const u8, r: *const u8, d: *mut u8, is_less: &mut U8Cmp) -> RawStep {
        kani::cover(true, "mergestep actual up adapter entered");
        let ctx = step_context();
        kani::assert(!ctx.fail_up, "mergestep actual up adapter binding control");
        let cmp = *is_less;
        kani::assert(canonical(cmp), "mergestep adapter: received canonical comparator");
        let (len, half) = (ctx.active_len, ctx.active_len / 2);
        kani::assert(
            len == ACTIVE4
                && index_in(ctx.src, 0, half, l).is_some()
                && index_in(ctx.src, half, len, r).is_some()
                && index_in(ctx.dst as *const u8, 0, len, d as *const u8).is_some(),
            "mergestep up adapter: actual pointers in registered halves and prefix",
        );
        // SAFETY: the actual pointers and received comparator; step requires are checked here.
        let take_left = unsafe { up_step_u8(l, r, d, cmp) };
        let next = up_decode(l, r, d, take_left);
        check_up_ledger(&ctx, next);
        next
    }

    unsafe fn down(l: *const u8, r: *const u8, d: *mut u8, is_less: &mut U8Cmp) -> RawStep {
        kani::cover(true, "mergestep actual down adapter entered");
        let ctx = step_context();
        kani::assert(!ctx.fail_down, "mergestep actual down adapter binding control");
        let cmp = *is_less;
        kani::assert(canonical(cmp), "mergestep adapter: received canonical comparator");
        let (len, half) = (ctx.active_len, ctx.active_len / 2);
        kani::assert(
            len == ACTIVE4
                && index_in(ctx.src, 0, half, l).is_some()
                && index_in(ctx.src, half, len, r).is_some()
                && index_in(ctx.dst as *const u8, 1, len, d as *const u8).is_some(),
            "mergestep down adapter: actual pointers in registered halves and prefix",
        );
        // SAFETY: the actual pointers and received comparator; step requires are checked here.
        let take_left = unsafe { down_step_u8(l, r, d, cmp) };
        let next = down_decode(l, r, d, take_left);
        check_down_ledger(&ctx, next);
        next
    }
}

// Same raw parameters, return and two type parameters; only the bridge bound narrows the proof.
unsafe fn up_adapter<T: MergeStepBridge<F>, F: FnMut(&T, &T) -> bool>(
    left_src: *const T,
    right_src: *const T,
    dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {
    // SAFETY: the sole closed implementation checks the actual arguments and forwards them.
    unsafe { T::up(left_src, right_src, dst, is_less) }
}

unsafe fn down_adapter<T: MergeStepBridge<F>, F: FnMut(&T, &T) -> bool>(
    left_src: *const T,
    right_src: *const T,
    dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {
    // SAFETY: the sole closed implementation checks the actual arguments and forwards them.
    unsafe { T::down(left_src, right_src, dst, is_less) }
}

fn prefix4_sorted(out: &[u8]) -> bool {
    let mut i = 1;
    while i < ACTIVE4 {
        if out[i] < out[i - 1] {
            return false;
        }
        i += 1;
    }
    true
}

/// Post-return checks of the positive and of the count control, with one typed full-value oracle.
fn check_merge4(src: &[u8; 18], pre: &[u8; 18], dst: *mut u8, probe: u8, fails: (bool, bool)) {
    kani::assert(StrictU8::probe() == probe, "mergestep merge4: StrictU8 probe unchanged");
    let ctx = step_context();
    kani::assert(
        ctx.src == src.as_ptr()
            && ctx.dst == dst
            && ctx.active_len == ACTIVE4
            && ctx.probe == probe
            && (ctx.fail_up, ctx.fail_down) == fails,
        "mergestep merge4: readonly context unchanged",
    );
    let mut i = 0;
    while i < 18 {
        kani::assert(src[i] == pre[i], "mergestep merge4: source18 unchanged");
        i += 1;
    }
    // SAFETY: a normal return wrote the whole prefix4; only that prefix is viewed.
    let out = unsafe { crate::slice::from_raw_parts(dst as *const u8, ACTIVE4) };
    kani::assert(prefix4_sorted(out), "mergestep merge4: destination prefix4 sorted");
    kani::assert(
        count_matching_values(&pre[..ACTIVE4], &probe) == count_matching_values(out, &probe),
        "mergestep merge4: source/destination prefix4 full-value count preserved",
    );
}

#[kani::proof_for_contract(super::super::super::merge::specfix::merge_profile)]
#[kani::stub(merge_up, up_adapter)]
#[kani::stub(merge_down, down_adapter)]
#[kani::stub_verified(up_step_u8)]
#[kani::stub_verified(down_step_u8)]
#[kani::unwind(34)]
fn mergestep_composed_merge4_u8() {
    StrictU8::set_probe(kani::any());
    let probe = StrictU8::probe();
    let src: [u8; 18] = kani::any();
    let pre = src;
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let dst = scratch.as_mut_ptr() as *mut u8;
    register(&src, dst, probe, false, false);
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: initialized source18 prefix4, separate scratch32 written at offset 0 for 4 cells.
    unsafe { merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp) };
    kani::cover(true, "mergestep merge4: returned");
    check_merge4(&src, &pre, dst, probe, (false, false));
    kani::cover(src[0] < src[2], "mergestep merge4: left first");
    kani::cover(src[2] < src[0], "mergestep merge4: right first");
    kani::cover(src[0] == src[2], "mergestep merge4: equal first values");
    let hits = count_matching_values(&pre[..ACTIVE4], &probe);
    kani::cover(hits > 0, "mergestep merge4: probe hits source prefix4");
    kani::cover(hits == 0, "mergestep merge4: probe misses source prefix4");
}

/// Narrow control setup only: source18 zero, probe 0, scratch32 uninitialized, canonical U8Cmp.
fn control_merge4(src: &[u8; 18], dst: *mut u8, fail_up: bool, fail_down: bool) {
    StrictU8::set_probe(0);
    register(src, dst, 0, fail_up, fail_down);
    let cmp: U8Cmp = StrictU8::CMP;
    kani::cover(true, "mergestep control: actual entry reached");
    // SAFETY: initialized source18 prefix4 with sorted halves, separate scratch32 prefix4.
    unsafe { merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp) };
    kani::cover(true, "mergestep control: merge returned");
}

#[kani::proof]
#[kani::stub(merge_up, up_adapter)]
#[kani::stub(merge_down, down_adapter)]
#[kani::stub_verified(up_step_u8)]
#[kani::stub_verified(down_step_u8)]
#[kani::unwind(34)]
fn mergestep_up_binding_negative_u8() {
    let src = [0u8; 18];
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    control_merge4(&src, scratch.as_mut_ptr() as *mut u8, true, false);
    // Only the up adapter's literal binding guard must fail.
}

#[kani::proof]
#[kani::stub(merge_up, up_adapter)]
#[kani::stub(merge_down, down_adapter)]
#[kani::stub_verified(up_step_u8)]
#[kani::stub_verified(down_step_u8)]
#[kani::unwind(34)]
fn mergestep_down_binding_negative_u8() {
    let src = [0u8; 18];
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    control_merge4(&src, scratch.as_mut_ptr() as *mut u8, false, true);
    // Only the down adapter's literal binding guard must fail.
}

#[kani::proof]
#[kani::stub(merge_up, up_adapter)]
#[kani::stub(merge_down, down_adapter)]
#[kani::stub_verified(up_step_u8)]
#[kani::stub_verified(down_step_u8)]
#[kani::unwind(34)]
fn mergestep_count_negative_u8() {
    let src = [0u8; 18];
    let pre = src;
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let dst = scratch.as_mut_ptr() as *mut u8;
    control_merge4(&src, dst, false, false);
    check_merge4(&src, &pre, dst, 0, (false, false));
    kani::cover(true, "mergestep calibration negative: returned before corruption");
    // SAFETY: cell 3 of the written prefix4 in the separate scratch32.
    unsafe { *dst.add(3) = 1 };
    // SAFETY: the prefix4 is initialized; only that prefix is viewed.
    let out = unsafe { crate::slice::from_raw_parts(dst as *const u8, ACTIVE4) };
    kani::assert(prefix4_sorted(out), "mergestep calibration negative: sorted after corruption");
    kani::cover(true, "mergestep calibration negative: corrupted count check reached");
    kani::assert(
        count_matching_values(&pre[..ACTIVE4], &0) == count_matching_values(out, &0),
        "mergestep calibration negative: full-value count preserved",
    );
}
