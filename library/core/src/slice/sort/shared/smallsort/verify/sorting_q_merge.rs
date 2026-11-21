//! Package A checks of the real leaves and presort paths for N18 and N19.
//! Package B checks the real merge and adds literal controls.
//! Package C checks the real network with the leaf and whole-merge summaries.

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
use super::super::bidirectional_merge;
use super::super::merge_up;
#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
use super::super::small_sort_network;
#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
use super::super::sort13_optimal;
#[cfg(not(kani_smallsort_q_merge_bad_tie))]
use super::super::{
    insert_tail, insertion_sort_shift_left, merge_down, sort9_optimal, swap_if_less,
};
use super::sorting_model::KeyLess;
use super::sorting_q_merge_model as model;
#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
use super::sorting_q_merge_model::merge_b;
#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
use super::sorting_q_merge_model::merge_wide;
use super::sorting_q_model as qmodel;
use crate::{kani, mem::MaybeUninit};

const BACKING: usize = 34;

fn check_active() {
    kani::assert(model::active::<u8, KeyLess<u8>>(), "MA_BYTE_MODEL_ACTIVE");
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "MA_Q_MODEL_ACTIVE");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
fn outside_span_unchanged(
    before: &[u8; BACKING],
    after: &[u8; BACKING],
    start: usize,
    end: usize,
) -> bool {
    after[..start] == before[..start] && after[end..] == before[end..]
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(36)]
fn ma_swap_byte_q() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    let base_index = if kani::any::<bool>() { 1 } else { 10 };
    let a: usize = kani::any();
    let b: usize = kani::any();
    // All 36 increasing pairs on both bases, including all 25 sort9 call sites.
    kani::assume(a < b && b < 9);
    let x = before[base_index + a];
    let y = before[base_index + b];

    // SAFETY: both indices designate distinct initialized writable bytes of v.
    unsafe { swap_if_less(v.as_mut_ptr().add(base_index), a, b, &mut f) };

    let after = (v[base_index + a], v[base_index + b]);
    kani::assert(after == (x.min(y), x.max(y)), "MA_SWAP_BYTE_POST");
    kani::assert(
        (after.0 >= q, after.1 >= q) == ((x >= q) && (y >= q), (x >= q) || (y >= q)),
        "MA_SWAP_Q_POST",
    );
    kani::assert(f.q() == q, "MA_SWAP_Q_FRAME");
    kani::assert(
        (0..BACKING).all(|i| i == base_index + a || i == base_index + b || v[i] == before[i]),
        "MA_SWAP_V34_FRAME",
    );
    kani::cover(base_index == 1, "MA_SWAP_BASE_01");
    kani::cover(base_index == 10, "MA_SWAP_BASE_10");
    kani::cover(y < x, "MA_SWAP_TAKEN");
    kani::cover(y >= x, "MA_SWAP_UNTAKEN");
    kani::cover(x == y && a != b, "MA_SWAP_EQUAL_BYTES");
    kani::cover((x >= q) != (y >= q), "MA_SWAP_MIXED_Q");
    kani::cover(q == 0, "MA_SWAP_Q_ZERO");
    kani::cover(q == u8::MAX, "MA_SWAP_Q_MAX");
    kani::cover(true, "MA_SWAP_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn ma_insert_right_b10_rel9() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    let backing_ptr = v.as_mut_ptr();
    // SAFETY: the literal pointers delimit initialized writable v[10..20].
    let (begin, tail) = unsafe { (backing_ptr.add(10), backing_ptr.add(19)) };
    let captured = qmodel::capture(begin, 10, &f);
    let prefix = &before[10..19];
    let numeric_prefix = model::numeric_order(prefix);

    // SAFETY: the Check precondition supplies q-monotonicity. The fixture
    // establishes all pointer and initialization requirements.
    unsafe { insert_tail(begin, tail, &mut f) };

    kani::assert(
        qmodel::insert_post(captured, begin, 10, &f),
        "MA_INSERT_Q_POST",
    );
    kani::assert(
        !numeric_prefix || model::numeric_order(&v[10..20]),
        "MA_INSERT_NUMERIC_ORDER",
    );
    kani::assert(f.q() == q, "MA_INSERT_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 10, 20),
        "MA_INSERT_V34_FRAME",
    );

    kani::cover(numeric_prefix, "MA_INSERT_NUMERIC_PREFIX");
    kani::cover(
        !numeric_prefix && prefix.windows(2).all(|pair| pair[0] < q || pair[1] >= q),
        "MA_INSERT_Q_MONOTONE_NON_NUMERIC_PREFIX",
    );
    kani::cover(
        numeric_prefix && before[19] >= before[18],
        "MA_INSERT_EARLY_RETURN",
    );
    kani::cover(
        numeric_prefix && before[19] < before[10],
        "MA_INSERT_FULL_SIFT",
    );
    kani::cover(q == 0, "MA_INSERT_Q_ZERO");
    kani::cover(q == u8::MAX, "MA_INSERT_Q_MAX");
    kani::cover(true, "MA_INSERT_USEFUL_RETURN");
}

fn merge_length_and_step() -> (usize, usize) {
    let n = if kani::any::<bool>() { 18 } else { 19 };
    let k: usize = kani::any();
    kani::assume(k <= 8);
    (n, k)
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
fn cover_step(n: usize, k: usize, x: u8, y: u8, q: u8) {
    kani::cover(n == 18, "MA_STEP_N18");
    kani::cover(n == 19, "MA_STEP_N19");
    kani::cover(k == 0, "MA_STEP_K0");
    kani::cover(k == 8, "MA_STEP_K8");
    kani::cover(x < y, "MA_STEP_LEFT_LT_RIGHT");
    kani::cover(y < x, "MA_STEP_RIGHT_LT_LEFT");
    kani::cover(x == y, "MA_STEP_EQUAL_BYTES");
    kani::cover((x >= q) != (y >= q), "MA_STEP_SPLIT_Q");
    kani::cover(q == 0, "MA_STEP_Q_ZERO");
    kani::cover(q == u8::MAX, "MA_STEP_Q_MAX");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof_for_contract(merge_up)]
#[kani::unwind(36)]
fn ma_merge_up() {
    check_up_step();
}

#[cfg(kani_smallsort_q_merge_bad_tie)]
#[kani::proof_for_contract(merge_up)]
#[kani::unwind(36)]
fn ma_merge_up_wrong_tie() {
    check_up_step();
}

fn check_up_step() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    let (n, k) = merge_length_and_step();
    let a: usize = kani::any();
    kani::assume(a <= k);
    let left = a;
    let right = 9 + (k - a);
    kani::assert(
        left < 9 && (9..n).contains(&right) && k < 9,
        "MA_UP_INPUT_OFFSETS",
    );
    let x = before[1 + left];
    let y = before[1 + right];
    // SAFETY: src is the interior base of the initialized V34 object.
    let src = unsafe { v.as_mut_ptr().add(1) }.cast_const();
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let scratch_base = scratch.as_mut_ptr().cast::<u8>();
    // SAFETY: k is in bounds of the separate 32-byte scratch object.
    let dst = unsafe { scratch_base.add(k) };

    #[cfg(kani_smallsort_q_merge_bad_tie)]
    kani::cover(x == y, "MA_UP_BAD_TIE_INPUT");
    // SAFETY: both source slots are initialized, the disjoint dst is writable,
    // and the two source and one destination increments stay in their allocations.
    let actual = unsafe { merge_up(src.add(left), src.add(right), dst, &mut f) };

    // SAFETY: the actual step just copied one initialized byte to this slot.
    let byte = unsafe { dst.read() };
    kani::assert(byte == x.min(y), "MA_UP_BYTE_POST");
    kani::assert((byte >= q) == ((x >= q) && (y >= q)), "MA_UP_Q_POST");
    kani::assert(f.q() == q, "MA_UP_Q_FRAME");
    kani::assert(v == before, "MA_UP_SOURCE_FRAME");
    #[cfg(not(kani_smallsort_q_merge_bad_tie))]
    {
        let left_next = left + usize::from(x <= y);
        let right_next = right + usize::from(y < x);
        kani::assert(
            actual
                == (
                    src.wrapping_add(left_next),
                    src.wrapping_add(right_next),
                    scratch_base.wrapping_add(k + 1),
                ),
            "MA_UP_CURSOR_POST",
        );
        kani::cover(
            n == 18 && right_next == 18 && actual.1 == src.wrapping_add(18),
            "MA_UP_N18_RIGHT_END",
        );
        kani::cover(
            n == 19 && right_next == 18 && actual.1 == src.wrapping_add(18),
            "MA_UP_N19_RIGHT_LAST",
        );
        kani::cover(
            k == 8 && actual.2 == scratch_base.wrapping_add(9),
            "MA_UP_DST_END",
        );
        cover_step(n, k, x, y, q);
    }
    #[cfg(kani_smallsort_q_merge_bad_tie)]
    let _ = actual;
    kani::cover(true, "MA_UP_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof_for_contract(merge_down)]
#[kani::unwind(36)]
fn ma_merge_down() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    let (n, k) = merge_length_and_step();
    let d: usize = kani::any();
    kani::assume(d <= k);
    let left = 8 - (k - d);
    let right = n - 1 - d;
    let dst_index = n - 1 - k;
    kani::assert(
        left < 9 && (9..n).contains(&right) && (n - 9..n).contains(&dst_index),
        "MA_DOWN_INPUT_OFFSETS",
    );
    let x = before[1 + left];
    let y = before[1 + right];
    let backing_ptr = v.as_mut_ptr().cast_const();
    // SAFETY: src is the interior base of the initialized V34 object.
    let src = unsafe { backing_ptr.add(1) };
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let scratch_base = scratch.as_mut_ptr().cast::<u8>();
    // SAFETY: both dst_index and dst_index - 1 are within scratch.
    let dst = unsafe { scratch_base.add(dst_index) };
    let dst_next = dst_index - 1;
    kani::assert((n - 10..n - 1).contains(&dst_next), "MA_DOWN_DST_SUB_RANGE");
    kani::assert(
        k != 8 || ((n == 18 && dst_next == 8) || (n == 19 && dst_next == 9)),
        "MA_DOWN_DST_SUB_LAST",
    );

    // SAFETY: both source slots are initialized, the disjoint dst is writable,
    // and dst.sub(1) is in bounds.
    let actual = unsafe { merge_down(src.add(left), src.add(right), dst, &mut f) };

    // SAFETY: the actual step just copied one initialized byte to this slot.
    let byte = unsafe { dst.read() };
    kani::assert(byte == x.max(y), "MA_DOWN_BYTE_POST");
    kani::assert((byte >= q) == ((x >= q) || (y >= q)), "MA_DOWN_Q_POST");
    kani::assert(f.q() == q, "MA_DOWN_Q_FRAME");
    kani::assert(v == before, "MA_DOWN_SOURCE_FRAME");
    // Absolute V34 offsets include the left sentinel at offset 0.
    let left_next = 1 + left - usize::from(y < x);
    let right_next = 1 + right - usize::from(x <= y);
    kani::assert(
        actual
            == (
                backing_ptr.wrapping_add(left_next),
                backing_ptr.wrapping_add(right_next),
                scratch_base.wrapping_add(dst_next),
            ),
        "MA_DOWN_CURSOR_POST",
    );
    kani::cover(
        left_next == 0 && actual.0 == backing_ptr,
        "MA_DOWN_LEFT_SENTINEL",
    );
    kani::cover(
        n == 18 && k == 8 && actual.2 == scratch_base.wrapping_add(8),
        "MA_DOWN_N18_DST_LAST",
    );
    kani::cover(
        n == 19 && k == 8 && actual.2 == scratch_base.wrapping_add(9),
        "MA_DOWN_N19_DST_LAST",
    );
    kani::cover(
        n == 18 && right_next == 1 + 8 && actual.1 == src.wrapping_add(8),
        "MA_DOWN_N18_RIGHT_SENTINEL",
    );
    kani::cover(
        n == 19 && right_next == 1 + 9 && actual.1 == src.wrapping_add(9),
        "MA_DOWN_N19_RIGHT_FIRST",
    );
    cover_step(n, k, x, y, q);
    kani::cover(true, "MA_DOWN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
fn check_half_q_and_frame(
    before: &[u8; BACKING],
    v: &[u8; BACKING],
    start: usize,
    end: usize,
    q: u8,
    f: &KeyLess<u8>,
) {
    let input = &before[start..end];
    let target = qmodel::order_target(input, q);
    kani::assert(
        qmodel::order_post(&v[start..end], q, &target),
        "MA_HALF_ORDER_Q_POST",
    );
    kani::assert(f.q() == q, "MA_HALF_Q_FRAME");
    kani::assert(
        outside_span_unchanged(before, v, start, end),
        "MA_HALF_V34_FRAME",
    );
    kani::cover(
        input.iter().any(|byte| *byte < q) && input.iter().any(|byte| *byte >= q),
        "MA_HALF_MIXED_THRESHOLD",
    );
    kani::cover(
        input.windows(2).any(|pair| pair[0] == pair[1]),
        "MA_HALF_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "MA_HALF_Q_ZERO");
    kani::cover(q == u8::MAX, "MA_HALF_Q_MAX");
    kani::cover(input.iter().all(|byte| *byte != q), "MA_HALF_Q_ABSENT");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn ma_h9_left_b01() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    sort9_optimal(&mut v[1..10], &mut f);

    kani::assert(model::numeric_order(&v[1..10]), "MA_L1_NUMERIC_ORDER");
    check_half_q_and_frame(&before, &v, 1, 10, q, &f);
    kani::cover(true, "MA_HALF_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn ma_h9_right_b10() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    sort9_optimal(&mut v[10..19], &mut f);

    kani::assert(model::numeric_order(&v[10..19]), "MA_R10_H9_NUMERIC_ORDER");
    check_half_q_and_frame(&before, &v, 10, 19, q, &f);
    kani::cover(true, "MA_HALF_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
fn sort_right_ten(v: &mut [u8; BACKING], f: &mut KeyLess<u8>) {
    let tail_byte = v[19];
    sort9_optimal(&mut v[10..20], f);

    let prefix_ordered = model::numeric_order(&v[10..19]);
    kani::assert(prefix_ordered, "MA_R10_PRESORT_NUMERIC_PREFIX");
    kani::assert(v[19] == tail_byte, "MA_R10_PRESORT_TAIL_FRAME");
    kani::cover(prefix_ordered, "MA_R10_INSERT_NUMERIC_PREFIX");

    insertion_sort_shift_left(&mut v[10..20], 9, f);
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn ma_h10_right_b10() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    sort_right_ten(&mut v, &mut f);

    kani::assert(model::numeric_order(&v[10..20]), "MA_R10_H10_NUMERIC_ORDER");
    check_half_q_and_frame(&before, &v, 10, 20, q, &f);
    kani::cover(true, "MA_HALF_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn ma_h10_right_corrupt_order() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    sort_right_ten(&mut v, &mut f);

    let corrupt = q == 2 && before[10..20].iter().all(|byte| *byte == 0);
    if corrupt {
        v[10] = 1;
        v[11] = 0;
    }
    check_half_q_and_frame(&before, &v, 10, 20, q, &f);
    kani::cover(corrupt && v[10] == 1 && v[11] == 0, "MA_R10_CORRUPT_PATH");
    kani::assert(
        model::numeric_order(&v[10..20]),
        "MA_R10_CORRUPT_NUMERIC_ORDER",
    );
    kani::cover(true, "MA_HALF_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
fn cover_merge_input(input: &[u8], q: u8) {
    kani::cover(q == 0, "MB_MERGE_Q_ZERO");
    kani::cover(q == u8::MAX, "MB_MERGE_Q_MAX");
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MB_MERGE_SPLIT_Q",
    );
    kani::cover(input[0] == input[9], "MB_MERGE_CROSS_HALF_TIE");
    kani::cover(input.iter().all(|&byte| byte != q), "MB_MERGE_Q_ABSENT");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mb_merge_n18() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    check_active();

    // SAFETY: the literal input is initialized and scratch is a separate writable allocation.
    unsafe { bidirectional_merge(&v[1..19], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MB_MERGE_Q_FRAME");
    kani::assert(v == before, "MB_MERGE_V34_SOURCE_FRAME");
    cover_merge_input(&before[1..19], q);
    kani::cover(true, "MB_MERGE_N18_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mb_merge_n19() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    check_active();

    // SAFETY: the literal input is initialized and scratch is a separate writable allocation.
    unsafe { bidirectional_merge(&v[1..20], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MB_MERGE_Q_FRAME");
    kani::assert(v == before, "MB_MERGE_V34_SOURCE_FRAME");
    cover_merge_input(&before[1..20], q);
    // Every normal return from this literal N19 call traverses the actual odd copy.
    kani::cover(true, "MB_MERGE_N19_ODD_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mb_pre_numeric_n18() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..19].fill(0);
    v[1] = 1;
    v[18] = 1;
    let q = 2;
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    check_active();

    let input = &v[1..19];
    let (left, right) = input.split_at(9);
    let threshold_order = |half: &[u8]| half.windows(2).all(|pair| pair[0] < q || pair[1] >= q);
    kani::cover(
        f.q() == 2 && input[0] == 1 && input[17] == 1 && input[1..17] == [0; 16],
        "MB_PRE_NUMERIC_N18_INPUT",
    );
    kani::cover(
        threshold_order(left) && threshold_order(right),
        "MB_PRE_NUMERIC_N18_Q_MONOTONE_HALVES",
    );
    kani::cover(
        !model::numeric_order(left),
        "MB_PRE_NUMERIC_N18_LEFT_INVERSION",
    );

    // SAFETY: source and destination satisfy the geometry. Replace checks the deliberately
    // false numeric precondition at this call site.
    unsafe { bidirectional_merge(input, scratch.as_mut_ptr().cast(), &mut f) };
}

#[cfg(not(any(kani_smallsort_q_merge_b, kani_smallsort_q_merge_bad_tie)))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn mb_h10_corrupt_literal() {
    let mut v: [u8; BACKING] = kani::any();
    v[10..20].fill(0);
    let before = v;
    let q = 2;
    let mut f = KeyLess::<u8>::with_q(q);
    check_active();

    sort_right_ten(&mut v, &mut f);

    v[10] = 1;
    v[11] = 0;
    let target = qmodel::order_target(&before[10..20], q);
    kani::assert(
        qmodel::order_post(&v[10..20], q, &target),
        "MA_HALF_ORDER_Q_POST",
    );
    kani::assert(f.q() == q, "MA_HALF_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 10, 20),
        "MA_HALF_V34_FRAME",
    );
    kani::cover(v[10] == 1 && v[11] == 0, "MB_H10_LITERAL_CORRUPT_PATH");
    kani::assert(
        model::numeric_order(&v[10..20]),
        "MB_H10_LITERAL_CORRUPT_NUMERIC_ORDER",
    );
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mc_network_n18_b01() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MC_N18_BYTE_MODEL_ACTIVE",
    );
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "MC_N18_Q_MODEL_ACTIVE");
    let captured = merge_b::merge_capture(&v[1..19], &f);

    small_sort_network(&mut v[1..19], &mut f);

    kani::assert(
        merge_b::merge_q_post(captured, v[1..19].as_mut_ptr(), &f),
        "MC_N18_QPOST",
    );
    kani::assert(f.q() == q, "MC_N18_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 19),
        "MC_N18_OUTSIDE_VALUE_FRAME",
    );
    let input = &before[1..19];
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MC_N18_MIXED_THRESHOLD",
    );
    kani::cover(
        input.windows(2).any(|w| w[0] == w[1]),
        "MC_N18_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "MC_N18_Q_ZERO");
    kani::cover(q == u8::MAX, "MC_N18_Q_MAX");
    kani::cover(input.iter().all(|&byte| byte != q), "MC_N18_Q_ABSENT");
    kani::cover(true, "MC_N18_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mc_network_n19_b01() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MC_N19_BYTE_MODEL_ACTIVE",
    );
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "MC_N19_Q_MODEL_ACTIVE");
    let captured = merge_b::merge_capture(&v[1..20], &f);

    small_sort_network(&mut v[1..20], &mut f);

    kani::assert(
        merge_b::merge_q_post(captured, v[1..20].as_mut_ptr(), &f),
        "MC_N19_QPOST",
    );
    kani::assert(f.q() == q, "MC_N19_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 20),
        "MC_N19_OUTSIDE_VALUE_FRAME",
    );
    let input = &before[1..20];
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MC_N19_MIXED_THRESHOLD",
    );
    kani::cover(
        input.windows(2).any(|w| w[0] == w[1]),
        "MC_N19_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "MC_N19_Q_ZERO");
    kani::cover(q == u8::MAX, "MC_N19_Q_MAX");
    kani::cover(input.iter().all(|&byte| byte != q), "MC_N19_Q_ABSENT");
    kani::cover(true, "MC_N19_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mc_network_n19_corrupt_literal() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..20].fill(0);
    let before = v;
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MC_N19_CORRUPT_BYTE_MODEL_ACTIVE",
    );
    kani::assert(
        qmodel::active::<u8, KeyLess<u8>>(),
        "MC_N19_CORRUPT_Q_MODEL_ACTIVE",
    );
    let captured = merge_b::merge_capture(&v[1..20], &f);

    small_sort_network(&mut v[1..20], &mut f);

    kani::cover(v[1] == 0, "MC_N19_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "MC_N19_CORRUPT_PATH");
    kani::assert(f.q() == q, "MC_N19_CORRUPT_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 20),
        "MC_N19_CORRUPT_OUTSIDE_VALUE_FRAME",
    );
    kani::assert(
        merge_b::merge_q_post(captured, v[1..20].as_mut_ptr(), &f),
        "MC_N19_CORRUPT_QPOST",
    );
}

macro_rules! define_presort_frame_and_covers {
    ($name:ident, $label:literal $(,)?) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        fn $name(
            before: &[u8; BACKING],
            v: &[u8; BACKING],
            start: usize,
            end: usize,
            q: u8,
            f: &KeyLess<u8>,
        ) {
            kani::assert(f.q() == q, concat!($label, "_Q_FRAME"));
            kani::assert(
                outside_span_unchanged(before, v, start, end),
                concat!($label, "_V34_FRAME"),
            );

            let input = &before[start..end];
            kani::cover(
                input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
                concat!($label, "_MIXED_THRESHOLD"),
            );
            kani::cover(
                input.windows(2).any(|pair| pair[0] == pair[1]),
                concat!($label, "_THRESHOLD_TIES"),
            );
            kani::cover(q == 0, concat!($label, "_Q_ZERO"));
            kani::cover(q == u8::MAX, concat!($label, "_Q_MAX"));
            kani::cover(
                input.iter().all(|&byte| byte != q),
                concat!($label, "_Q_ABSENT"),
            );
            kani::cover(!model::numeric_order(input), concat!($label, "_INPUT_INVERSION"));
            kani::cover(true, concat!($label, "_USEFUL_RETURN"));
        }
    };
}

define_presort_frame_and_covers!(check_sort9_frame_and_covers, "MD_SORT9");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn md_sort9_left_b01_len09() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[1..10], &mut f);

    check_sort9_frame_and_covers(&before, &v, 1, 10, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn md_sort9_right_b10_len09() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[10..19], &mut f);

    check_sort9_frame_and_covers(&before, &v, 10, 19, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn md_sort9_right_b10_len10() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[10..20], &mut f);

    // The right insertion will consume the untouched byte at offset 19.
    check_sort9_frame_and_covers(&before, &v, 10, 19, q, &f);
}

define_presort_frame_and_covers!(
    check_sort9_l1_actual_swaps_frame_and_covers,
    "MD_SORT9_L1_ACT",
);

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn md_sort9_left_b01_len09_actual_swaps() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[1..10], &mut f);

    check_sort9_l1_actual_swaps_frame_and_covers(&before, &v, 1, 10, q, &f);
}

define_presort_frame_and_covers!(
    check_sort9_r9_actual_swaps_frame_and_covers,
    "MD_SORT9_R9_ACT",
);

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn md_sort9_right_b10_len09_actual_swaps() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[10..19], &mut f);

    check_sort9_r9_actual_swaps_frame_and_covers(&before, &v, 10, 19, q, &f);
}

define_presort_frame_and_covers!(
    check_sort9_r10_actual_swaps_frame_and_covers,
    "MD_SORT9_R10_ACT",
);

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn md_sort9_right_b10_len10_actual_swaps() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[10..20], &mut f);

    // The right insertion will consume the untouched byte at offset 19.
    check_sort9_r10_actual_swaps_frame_and_covers(&before, &v, 10, 19, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn md_network_n18_b01() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MD_N18_BYTE_MODEL_ACTIVE",
    );
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "MD_N18_Q_MODEL_ACTIVE");
    let captured = merge_b::merge_capture(&v[1..19], &f);

    small_sort_network(&mut v[1..19], &mut f);

    kani::assert(
        merge_b::merge_q_post(captured, v[1..19].as_mut_ptr(), &f),
        "MD_N18_QPOST",
    );
    kani::assert(f.q() == q, "MD_N18_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 19),
        "MD_N18_OUTSIDE_VALUE_FRAME",
    );
    let input = &before[1..19];
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MD_N18_MIXED_THRESHOLD",
    );
    kani::cover(
        input.windows(2).any(|w| w[0] == w[1]),
        "MD_N18_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "MD_N18_Q_ZERO");
    kani::cover(q == u8::MAX, "MD_N18_Q_MAX");
    kani::cover(input.iter().all(|&byte| byte != q), "MD_N18_Q_ABSENT");
    kani::cover(true, "MD_N18_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn md_network_n19_b01() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MD_N19_BYTE_MODEL_ACTIVE",
    );
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "MD_N19_Q_MODEL_ACTIVE");
    let captured = merge_b::merge_capture(&v[1..20], &f);

    small_sort_network(&mut v[1..20], &mut f);

    kani::assert(
        merge_b::merge_q_post(captured, v[1..20].as_mut_ptr(), &f),
        "MD_N19_QPOST",
    );
    kani::assert(f.q() == q, "MD_N19_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 20),
        "MD_N19_OUTSIDE_VALUE_FRAME",
    );
    let input = &before[1..20];
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MD_N19_MIXED_THRESHOLD",
    );
    kani::cover(
        input.windows(2).any(|w| w[0] == w[1]),
        "MD_N19_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "MD_N19_Q_ZERO");
    kani::cover(q == u8::MAX, "MD_N19_Q_MAX");
    kani::cover(input.iter().all(|&byte| byte != q), "MD_N19_Q_ABSENT");
    kani::cover(true, "MD_N19_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn md_network_n19_corrupt_literal() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..20].fill(0);
    let before = v;
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(
        model::active::<u8, KeyLess<u8>>(),
        "MD_N19_CORRUPT_BYTE_MODEL_ACTIVE",
    );
    kani::assert(
        qmodel::active::<u8, KeyLess<u8>>(),
        "MD_N19_CORRUPT_Q_MODEL_ACTIVE",
    );
    let captured = merge_b::merge_capture(&v[1..20], &f);

    small_sort_network(&mut v[1..20], &mut f);

    kani::cover(v[1] == 0, "MD_N19_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "MD_N19_CORRUPT_PATH");
    kani::assert(f.q() == q, "MD_N19_CORRUPT_Q_FRAME");
    kani::assert(
        outside_span_unchanged(&before, &v, 1, 20),
        "MD_N19_CORRUPT_OUTSIDE_VALUE_FRAME",
    );
    kani::assert(
        merge_b::merge_q_post(captured, v[1..20].as_mut_ptr(), &f),
        "MD_N19_CORRUPT_QPOST",
    );
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort9_left_len10, "MW_S9_L10");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn mw_sort9_left_len10() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[1..11], &mut f);

    check_mw_sort9_left_len10(&before, &v, 1, 10, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort9_right_len10, "MW_S9_R10");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn mw_sort9_right_len10() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[11..21], &mut f);

    check_mw_sort9_right_len10(&before, &v, 11, 20, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort13_right_len13, "MW_S13_R13");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort13_optimal)]
#[kani::unwind(36)]
fn mw_sort13_right_len13() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort13_optimal(&mut v[13..26], &mut f);

    check_mw_sort13_right_len13(&before, &v, 13, 26, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort9_left_len12, "MW_S9_L12");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn mw_sort9_left_len12() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[1..13], &mut f);

    check_mw_sort9_left_len12(&before, &v, 1, 10, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort9_right_b13_len12, "MW_S9_R_B13_L12");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort9_optimal)]
#[kani::unwind(36)]
fn mw_sort9_right_b13_len12() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort9_optimal(&mut v[13..25], &mut f);

    check_mw_sort9_right_b13_len12(&before, &v, 13, 22, q, &f);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_presort_frame_and_covers!(check_mw_sort13_right_b14_len14, "MW_S13_R_B14_L14");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(sort13_optimal)]
#[kani::unwind(36)]
fn mw_sort13_right_b14_len14() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort13_optimal(&mut v[14..28], &mut f);

    check_mw_sort13_right_b14_len14(&before, &v, 14, 27, q, &f);
}

macro_rules! define_exact_wide_presort_check {
    ($name:ident, $check:ident, $sort:ident, $base:literal, $end:literal, $write_end:literal, $label:literal $(,)?) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        define_presort_frame_and_covers!($check, $label);

        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        #[kani::proof_for_contract($sort)]
        #[kani::unwind(36)]
        fn $name() {
            let mut v: [u8; BACKING] = kani::any();
            let before = v;
            let q: u8 = kani::any();
            let mut f = KeyLess::<u8>::with_q(q);

            $sort(&mut v[$base..$end], &mut f);

            $check(&before, &v, $base, $write_end, q, &f);
        }
    };
}

define_exact_wide_presort_check!(
    mw_sort9_left_b01_len11,
    check_mw_sort9_left_b01_len11,
    sort9_optimal,
    1,
    12,
    10,
    "MW_S9_L_B01_L11",
);

define_exact_wide_presort_check!(
    mw_sort9_right_b11_len11,
    check_mw_sort9_right_b11_len11,
    sort9_optimal,
    11,
    22,
    20,
    "MW_S9_R_B11_L11",
);

define_exact_wide_presort_check!(
    mw_sort9_right_b12_len11,
    check_mw_sort9_right_b12_len11,
    sort9_optimal,
    12,
    23,
    21,
    "MW_S9_R_B12_L11",
);

define_exact_wide_presort_check!(
    mw_sort9_right_b12_len12,
    check_mw_sort9_right_b12_len12,
    sort9_optimal,
    12,
    24,
    21,
    "MW_S9_R_B12_L12",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b14_len13,
    check_mw_sort13_right_b14_len13,
    sort13_optimal,
    14,
    27,
    27,
    "MW_S13_R_B14_L13",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b15_len14,
    check_mw_sort13_right_b15_len14,
    sort13_optimal,
    15,
    29,
    28,
    "MW_S13_R_B15_L14",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b15_len15,
    check_mw_sort13_right_b15_len15,
    sort13_optimal,
    15,
    30,
    28,
    "MW_S13_R_B15_L15",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b16_len15,
    check_mw_sort13_right_b16_len15,
    sort13_optimal,
    16,
    31,
    29,
    "MW_S13_R_B16_L15",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b16_len16,
    check_mw_sort13_right_b16_len16,
    sort13_optimal,
    16,
    32,
    29,
    "MW_S13_R_B16_L16",
);

define_exact_wide_presort_check!(
    mw_sort13_right_b17_len16,
    check_mw_sort13_right_b17_len16,
    sort13_optimal,
    17,
    33,
    30,
    "MW_S13_R_B17_L16",
);

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
fn q_monotone(input: &[u8], q: u8) -> bool {
    input.windows(2).all(|pair| pair[0] < q || pair[1] >= q)
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
fn check_wide_insert(
    before: &[u8; BACKING],
    after: &[u8; BACKING],
    base: usize,
    tail: usize,
    q: u8,
    f: &KeyLess<u8>,
) {
    let prefix = &before[base..tail];
    let numeric_prefix = model::numeric_order(prefix);
    kani::assert(
        !numeric_prefix || model::numeric_order(&after[base..=tail]),
        "MW_INSERT_NUMERIC_ORDER",
    );
    kani::assert(f.q() == q, "MW_INSERT_Q_FRAME");
    kani::assert(outside_span_unchanged(before, after, base, tail + 1), "MW_INSERT_V34_FRAME");
    kani::cover(numeric_prefix, "MW_INSERT_NUMERIC_PREFIX");
    kani::cover(
        !numeric_prefix && q_monotone(prefix, q),
        "MW_INSERT_Q_MONOTONE_NON_NUMERIC_PREFIX",
    );
    kani::cover(numeric_prefix && before[tail] >= before[tail - 1], "MW_INSERT_EARLY_RETURN");
    kani::cover(numeric_prefix && before[tail] < before[base], "MW_INSERT_FULL_SIFT");
    kani::cover(q == 0, "MW_INSERT_Q_ZERO");
    kani::cover(q == u8::MAX, "MW_INSERT_Q_MAX");
    kani::cover(true, "MW_INSERT_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn mw_insert_left_rel9_11() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    let rel: usize = kani::any();
    kani::assume((9..=11).contains(&rel));
    let backing_ptr = v.as_mut_ptr();
    // SAFETY: the three possible pairs delimit initialized writable bytes of v.
    let (begin, tail) = unsafe { (backing_ptr.add(1), backing_ptr.add(1 + rel)) };
    let captured = qmodel::capture(begin, rel + 1, &f);

    // SAFETY: the fixture establishes geometry and Check supplies q-monotonicity.
    unsafe { insert_tail(begin, tail, &mut f) };

    kani::assert(qmodel::insert_post(captured, begin, rel + 1, &f), "MW_INSERT_L_Q_POST");
    check_wide_insert(&before, &v, 1, 1 + rel, q, &f);
    kani::cover(rel == 9, "MW_INSERT_BASE1_REL9");
    kani::cover(rel == 10, "MW_INSERT_BASE1_REL10");
    kani::cover(rel == 11, "MW_INSERT_BASE1_REL11");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn mw_insert_right_b11_rel9() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    let backing_ptr = v.as_mut_ptr();
    // SAFETY: the pointers delimit initialized writable v[11..21].
    let (begin, tail) = unsafe { (backing_ptr.add(11), backing_ptr.add(20)) };
    let captured = qmodel::capture(begin, 10, &f);

    // SAFETY: the fixture establishes geometry and Check supplies q-monotonicity.
    unsafe { insert_tail(begin, tail, &mut f) };

    kani::assert(qmodel::insert_post(captured, begin, 10, &f), "MW_INSERT_R_Q_POST");
    check_wide_insert(&before, &v, 11, 20, q, &f);
    kani::cover(true, "MW_INSERT_BASE11_REL9");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
fn cover_wide_merge_input(input: &[u8], q: u8) {
    kani::cover(q == 0, "MW_MERGE_Q_ZERO");
    kani::cover(q == u8::MAX, "MW_MERGE_Q_MAX");
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MW_MERGE_SPLIT_Q",
    );
    kani::cover(input[0] == input[input.len() / 2], "MW_MERGE_CROSS_HALF_TIE");
    kani::cover(input.iter().all(|&byte| byte != q), "MW_MERGE_Q_ABSENT");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n20() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    // SAFETY: the input is initialized and scratch is a separate writable allocation.
    unsafe { bidirectional_merge(&v[1..21], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MW_MERGE_N20_Q_FRAME");
    kani::assert(v == before, "MW_MERGE_N20_V34_SOURCE_FRAME");
    let input = &before[1..21];
    cover_wide_merge_input(input, q);
    kani::cover(true, "MW_MERGE_N20_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n25() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    // SAFETY: the input is initialized and scratch is a separate writable allocation.
    unsafe { bidirectional_merge(&v[1..26], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MW_MERGE_N25_Q_FRAME");
    kani::assert(v == before, "MW_MERGE_N25_V34_SOURCE_FRAME");
    let input = &before[1..26];
    cover_wide_merge_input(input, q);
    // Normal return from N25 traverses the actual odd copy to scratch[12].
    kani::cover(true, "MW_MERGE_N25_ODD_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n24() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    // SAFETY: the input is initialized and scratch is a separate writable allocation.
    // The contract postcondition reads scratch[0..24] after both write streams.
    unsafe { bidirectional_merge(&v[1..25], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MW_MERGE_N24_Q_FRAME");
    kani::assert(v == before, "MW_MERGE_N24_V34_SOURCE_FRAME");
    cover_wide_merge_input(&before[1..25], q);
    kani::cover(true, "MW_MERGE_N24_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n27() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    // SAFETY: the input is initialized and scratch is a separate writable allocation.
    // The contract postcondition reads scratch[0..27], including odd slot 13.
    unsafe { bidirectional_merge(&v[1..28], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MW_MERGE_N27_Q_FRAME");
    kani::assert(v == before, "MW_MERGE_N27_V34_SOURCE_FRAME");
    cover_wide_merge_input(&before[1..28], q);
    kani::cover(true, "MW_MERGE_N27_ODD_USEFUL_RETURN");
}

macro_rules! define_exact_wide_merge_check {
    ($name:ident, $end:literal, $label:literal, $return_cover:literal $(,)?) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        #[kani::proof_for_contract(bidirectional_merge)]
        #[kani::unwind(36)]
        fn $name() {
            let v: [u8; BACKING] = kani::any();
            let before = v;
            let q: u8 = kani::any();
            let mut f = KeyLess::<u8>::with_q(q);
            let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

            // SAFETY: the input is initialized and scratch is a separate writable allocation.
            // The contract postcondition reads the entire active destination on return.
            unsafe { bidirectional_merge(&v[1..$end], scratch.as_mut_ptr().cast(), &mut f) };

            kani::assert(f.q() == q, concat!($label, "_Q_FRAME"));
            kani::assert(v == before, concat!($label, "_V34_SOURCE_FRAME"));
            cover_wide_merge_input(&before[1..$end], q);
            kani::cover(true, concat!($label, $return_cover));
        }
    };
}

define_exact_wide_merge_check!(mw_merge_n21, 22, "MW_MERGE_N21", "_ODD_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n22, 23, "MW_MERGE_N22", "_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n23, 24, "MW_MERGE_N23", "_ODD_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n26, 27, "MW_MERGE_N26", "_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n28, 29, "MW_MERGE_N28", "_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n29, 30, "MW_MERGE_N29", "_ODD_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n30, 31, "MW_MERGE_N30", "_USEFUL_RETURN");

define_exact_wide_merge_check!(mw_merge_n31, 32, "MW_MERGE_N31", "_ODD_USEFUL_RETURN");

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n32() {
    let v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    // SAFETY: the input is initialized and scratch is a separate writable allocation.
    unsafe { bidirectional_merge(&v[1..33], scratch.as_mut_ptr().cast(), &mut f) };

    kani::assert(f.q() == q, "MW_MERGE_N32_Q_FRAME");
    kani::assert(v == before, "MW_MERGE_N32_V34_SOURCE_FRAME");
    let input = &before[1..33];
    cover_wide_merge_input(input, q);
    kani::cover(input.iter().all(|&byte| byte < q), "MW_MERGE_N32_BELOW32");
    kani::cover(input.iter().all(|&byte| byte >= q), "MW_MERGE_N32_BELOW0");
    kani::cover(true, "MW_MERGE_N32_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
fn cover_wide_network_input(input: &[u8], q: u8) {
    kani::cover(
        input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
        "MW_NETWORK_MIXED_THRESHOLD",
    );
    kani::cover(input.windows(2).any(|pair| pair[0] == pair[1]), "MW_NETWORK_THRESHOLD_TIES");
    kani::cover(q == 0, "MW_NETWORK_Q_ZERO");
    kani::cover(q == u8::MAX, "MW_NETWORK_Q_MAX");
    kani::cover(input.iter().all(|&byte| byte != q), "MW_NETWORK_Q_ABSENT");
    kani::cover(true, "MW_NETWORK_USEFUL_RETURN");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_network_n20() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let captured = merge_wide::merge_capture(&v[1..21], &f);

    small_sort_network(&mut v[1..21], &mut f);

    kani::assert(merge_wide::merge_q_post(captured, v[1..21].as_mut_ptr(), &f), "MW_N20_QPOST");
    kani::assert(f.q() == q, "MW_N20_Q_FRAME");
    kani::assert(outside_span_unchanged(&before, &v, 1, 21), "MW_N20_OUTSIDE_VALUE_FRAME");
    cover_wide_network_input(&before[1..21], q);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_network_n25() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let captured = merge_wide::merge_capture(&v[1..26], &f);

    small_sort_network(&mut v[1..26], &mut f);

    kani::assert(merge_wide::merge_q_post(captured, v[1..26].as_mut_ptr(), &f), "MW_N25_QPOST");
    kani::assert(f.q() == q, "MW_N25_Q_FRAME");
    kani::assert(outside_span_unchanged(&before, &v, 1, 26), "MW_N25_OUTSIDE_VALUE_FRAME");
    cover_wide_network_input(&before[1..26], q);
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_network_n25_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..26].fill(0);
    let before = v;
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    let captured = merge_wide::merge_capture(&v[1..26], &f);
    kani::assert(captured.is_some(), "MW_N25_CORRUPT_CAPTURE_VALID");

    small_sort_network(&mut v[1..26], &mut f);

    kani::cover(v[1] == 0, "MW_N25_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "MW_N25_CORRUPT_PATH");
    kani::assert(f.q() == q, "MW_N25_CORRUPT_Q_FRAME");
    kani::assert(outside_span_unchanged(&before, &v, 1, 26), "MW_N25_CORRUPT_OUTSIDE_VALUE_FRAME");
    kani::assert(
        merge_wide::merge_q_post(captured, v[1..26].as_mut_ptr(), &f),
        "MW_N25_CORRUPT_QPOST",
    );
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn mw_merge_n32_numeric_pre() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..33].fill(0);
    v[1] = 1;
    let q = 2;
    let mut f = KeyLess::<u8>::with_q(q);
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();

    let input = &v[1..33];
    let dst = scratch.as_mut_ptr().cast::<u8>();
    let (left, right) = input.split_at(16);
    kani::assert(
        merge_wide::merge_geometry::<u8, KeyLess<u8>>(input, dst),
        "MW_N32_NUMERIC_PRE_GEOMETRY",
    );
    kani::cover(f.q() == 2 && input[0] == 1 && input[1..] == [0; 31], "MW_N32_NUMERIC_PRE_INPUT");
    kani::cover(q_monotone(left, q) && q_monotone(right, q), "MW_N32_NUMERIC_PRE_Q_MONOTONE");
    kani::cover(!model::numeric_order(left), "MW_N32_NUMERIC_PRE_LEFT_INVERSION");

    // SAFETY: the source and destination meet the geometry. Replace checks the
    // deliberately false numeric precondition at this call.
    unsafe { bidirectional_merge(input, dst, &mut f) };
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    kani_smallsort_q_no_merge_sort13,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
macro_rules! define_no_merge_sort13_roots {
    ($(
        $provider:ident, $check_frame:ident, $provider_label:literal;
        $consumer:ident, $consumer_label:literal, $end:literal $(, $insert:ident)?;
    )+) => {
        $(
            define_presort_frame_and_covers!($check_frame, $provider_label);

            #[kani::proof_for_contract(sort13_optimal)]
            #[kani::unwind(36)]
            fn $provider() {
                let mut v: [u8; BACKING] = kani::any();
                let before = v;
                let q: u8 = kani::any();
                let mut f = KeyLess::<u8>::with_q(q);

                sort13_optimal(&mut v[1..$end], &mut f);

                $check_frame(&before, &v, 1, 14, q, &f);
            }

            #[kani::proof]
            #[kani::stub_verified(sort13_optimal)]
            $(#[kani::stub_verified($insert)])?
            #[kani::unwind(36)]
            fn $consumer() {
                let mut v: [u8; BACKING] = kani::any();
                let before = v;
                let q: u8 = kani::any();
                let mut f = KeyLess::<u8>::with_q(q);
                kani::assert(
                    qmodel::active::<u8, KeyLess<u8>>(),
                    concat!($consumer_label, "_Q_MODEL_ACTIVE"),
                );
                kani::assert(
                    model::active::<u8, KeyLess<u8>>(),
                    concat!($consumer_label, "_BYTE_MODEL_ACTIVE"),
                );
                let input = &before[1..$end];
                let target = qmodel::order_target(input, q);

                small_sort_network(&mut v[1..$end], &mut f);

                kani::assert(
                    qmodel::order_post(&v[1..$end], q, &target),
                    concat!($consumer_label, "_QPOST"),
                );
                kani::assert(f.q() == q, concat!($consumer_label, "_Q_FRAME"));
                kani::assert(
                    outside_span_unchanged(&before, &v, 1, $end),
                    concat!($consumer_label, "_OUTSIDE_VALUE_FRAME"),
                );
                kani::cover(
                    input.iter().any(|&byte| byte < q) && input.iter().any(|&byte| byte >= q),
                    concat!($consumer_label, "_MIXED_THRESHOLD"),
                );
                kani::cover(
                    input.windows(2).any(|pair| pair[0] == pair[1]),
                    concat!($consumer_label, "_THRESHOLD_TIES"),
                );
                kani::cover(q == 0, concat!($consumer_label, "_Q_ZERO"));
                kani::cover(q == u8::MAX, concat!($consumer_label, "_Q_MAX"));
                kani::cover(
                    input.iter().all(|&byte| byte != q),
                    concat!($consumer_label, "_Q_ABSENT"),
                );
                kani::cover(true, concat!($consumer_label, "_USEFUL_RETURN"));
            }
        )+
    };
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    kani_smallsort_q_no_merge_sort13,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
define_no_merge_sort13_roots! {
    nm_sort13_left_len13, check_nm_sort13_left_len13, "NM_S13_L13";
    nm_network_n13, "NM_N13", 14;
    nm_sort13_left_len14, check_nm_sort13_left_len14, "NM_S13_L14";
    nm_network_n14, "NM_N14", 15, insert_tail;
    nm_sort13_left_len15, check_nm_sort13_left_len15, "NM_S13_L15";
    nm_network_n15, "NM_N15", 16, insert_tail;
    nm_sort13_left_len16, check_nm_sort13_left_len16, "NM_S13_L16";
    nm_network_n16, "NM_N16", 17, insert_tail;
    nm_sort13_left_len17, check_nm_sort13_left_len17, "NM_S13_L17";
    nm_network_n17, "NM_N17", 18, insert_tail;
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    kani_smallsort_q_no_merge_sort13,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort13_optimal)]
#[kani::unwind(36)]
fn nm_network_n13_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..14].fill(0);
    let before = v;
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&v[1..14], q);

    small_sort_network(&mut v[1..14], &mut f);

    kani::cover(v[1] == 0, "NM_N13_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "NM_N13_CORRUPT_PATH");
    kani::assert(f.q() == q, "NM_N13_CORRUPT_Q_FRAME");
    kani::assert(outside_span_unchanged(&before, &v, 1, 14), "NM_N13_CORRUPT_OUTSIDE_VALUE_FRAME");
    kani::assert(qmodel::order_post(&v[1..14], q, &target), "NM_N13_CORRUPT_QPOST");
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    kani_smallsort_q_no_merge_sort13,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn nm_network_n17_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..18].fill(0);
    let before = v;
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&v[1..18], q);

    small_sort_network(&mut v[1..18], &mut f);

    kani::cover(v[1] == 0, "NM_N17_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "NM_N17_CORRUPT_PATH");
    kani::assert(f.q() == q, "NM_N17_CORRUPT_Q_FRAME");
    kani::assert(outside_span_unchanged(&before, &v, 1, 18), "NM_N17_CORRUPT_OUTSIDE_VALUE_FRAME");
    kani::assert(qmodel::order_post(&v[1..18], q, &target), "NM_N17_CORRUPT_QPOST");
}

macro_rules! define_literal_wide_insert_check {
    ($name:ident, $rel:literal, $geometry:literal) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        #[kani::proof_for_contract(insert_tail)]
        #[kani::unwind(36)]
        fn $name() {
            let mut v: [u8; BACKING] = kani::any();
            let before = v;
            let q: u8 = kani::any();
            let mut f = KeyLess::<u8>::with_q(q);
            let backing_ptr = v.as_mut_ptr();
            // SAFETY: both literal offsets are within initialized writable v.
            let (begin, tail) = unsafe { (backing_ptr.add(1), backing_ptr.add(1 + $rel)) };
            let captured = qmodel::capture(begin, $rel + 1, &f);

            // SAFETY: the fixture establishes geometry and Check supplies q-monotonicity.
            unsafe { insert_tail(begin, tail, &mut f) };

            kani::assert(qmodel::insert_post(captured, begin, $rel + 1, &f), "MW_INSERT_L_Q_POST");
            check_wide_insert(&before, &v, 1, 1 + $rel, q, &f);
            kani::cover(true, $geometry);
        }
    };
}

define_literal_wide_insert_check!(mw_insert_left_literal_rel9, 9, "MW_INSERT_BASE1_REL9");
define_literal_wide_insert_check!(mw_insert_left_literal_rel10, 10, "MW_INSERT_BASE1_REL10");
define_literal_wide_insert_check!(mw_insert_left_literal_rel11, 11, "MW_INSERT_BASE1_REL11");

macro_rules! define_compact_wide_network {
    ($name:ident, $end:literal, $label:literal; $($stub:ident),+ $(,)?) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        #[kani::proof]
        $(#[kani::stub_verified($stub)])+
        #[kani::unwind(36)]
        fn $name() {
            let mut v: [u8; BACKING] = kani::any();
            let q: u8 = kani::any();
            let mut f = KeyLess::<u8>::with_q(q);
            let captured = merge_wide::merge_capture(&v[1..$end], &f);

            let outside_first = v[0];
            let mut outside_tail = [0; BACKING - $end];
            outside_tail.copy_from_slice(&v[$end..]);
            let mut previous = v[1];
            let mut has_below = previous < q;
            let mut has_at_or_above = previous >= q;
            let mut q_absent = previous != q;
            let mut has_tie = false;
            let mut i = 2;
            while i < $end {
                let byte = v[i];
                has_below |= byte < q;
                has_at_or_above |= byte >= q;
                q_absent &= byte != q;
                has_tie |= previous == byte;
                previous = byte;
                i += 1;
            }
            let mixed_threshold = has_below && has_at_or_above;
            let q_zero = q == 0;
            let q_max = q == u8::MAX;

            small_sort_network(&mut v[1..$end], &mut f);

            kani::assert(
                merge_wide::merge_q_post(captured, v[1..$end].as_mut_ptr(), &f),
                concat!($label, "_QPOST"),
            );
            kani::assert(f.q() == q, concat!($label, "_Q_FRAME"));
            kani::assert(
                v[0] == outside_first && v[$end..] == outside_tail,
                concat!($label, "_OUTSIDE_VALUE_FRAME"),
            );
            kani::cover(mixed_threshold, "MW_NETWORK_MIXED_THRESHOLD");
            kani::cover(has_tie, "MW_NETWORK_THRESHOLD_TIES");
            kani::cover(q_zero, "MW_NETWORK_Q_ZERO");
            kani::cover(q_max, "MW_NETWORK_Q_MAX");
            kani::cover(q_absent, "MW_NETWORK_Q_ABSENT");
            kani::cover(true, "MW_NETWORK_USEFUL_RETURN");
        }
    };
}

define_compact_wide_network!(compact_network_n25, 26, "COMPACT_N25";
    sort9_optimal, sort13_optimal, insert_tail, bidirectional_merge);
define_compact_wide_network!(compact_network_n20, 21, "COMPACT_N20";
    sort9_optimal, insert_tail, bidirectional_merge);
define_compact_wide_network!(compact_network_n20_actual_insert, 21, "COMPACT_N20";
    sort9_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n25_actual_insert, 26, "COMPACT_N25_ACT_INSERT";
    sort9_optimal, sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n24_actual_insert, 25, "COMPACT_N24_ACT_INSERT";
    sort9_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n27_actual_insert, 28, "COMPACT_N27_ACT_INSERT";
    sort13_optimal, bidirectional_merge);

define_compact_wide_network!(compact_network_n21_actual_insert, 22, "COMPACT_N21_ACT_INSERT";
    sort9_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n22_actual_insert, 23, "COMPACT_N22_ACT_INSERT";
    sort9_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n23_actual_insert, 24, "COMPACT_N23_ACT_INSERT";
    sort9_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n26_actual_insert, 27, "COMPACT_N26_ACT_INSERT";
    sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n28_actual_insert, 29, "COMPACT_N28_ACT_INSERT";
    sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n29_actual_insert, 30, "COMPACT_N29_ACT_INSERT";
    sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n30_actual_insert, 31, "COMPACT_N30_ACT_INSERT";
    sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n31_actual_insert, 32, "COMPACT_N31_ACT_INSERT";
    sort13_optimal, bidirectional_merge);
define_compact_wide_network!(compact_network_n32_actual_insert, 33, "COMPACT_N32_ACT_INSERT";
    sort13_optimal, bidirectional_merge);

macro_rules! define_compact_wide_actual_insert_control {
    ($name:ident, $end:literal, $label:literal; $($stub:ident),+ $(,)?) => {
        #[cfg(all(
            kani_smallsort_q_merge_b,
            kani_smallsort_q_merge_sort9,
            kani_smallsort_q_merge_wide,
            not(any(
                kani_smallsort_s2_assumed,
                kani_smallsort_q_controls,
                kani_smallsort_q_merge_bad_tie
            )),
        ))]
        #[kani::proof]
        $(#[kani::stub_verified($stub)])+
        #[kani::unwind(36)]
        fn $name() {
            let mut v: [u8; BACKING] = kani::any();
            v[1..$end].fill(0);
            let outside_first = v[0];
            let mut outside_tail = [0; BACKING - $end];
            outside_tail.copy_from_slice(&v[$end..]);
            let q = 1;
            let mut f = KeyLess::<u8>::with_q(q);
            let captured = merge_wide::merge_capture(&v[1..$end], &f);
            kani::assert(captured.is_some(), concat!($label, "_CAPTURE_VALID"));

            small_sort_network(&mut v[1..$end], &mut f);

            kani::cover(v[1] == 0, concat!($label, "_USEFUL_RETURN"));
            v[1] = 255;
            kani::cover(v[1] == 255, concat!($label, "_PATH"));
            kani::assert(f.q() == q, concat!($label, "_Q_FRAME"));
            kani::assert(
                v[0] == outside_first && v[$end..] == outside_tail,
                concat!($label, "_OUTSIDE_VALUE_FRAME"),
            );
            kani::assert(
                merge_wide::merge_q_post(captured, v[1..$end].as_mut_ptr(), &f),
                concat!($label, "_QPOST"),
            );
        }
    };
}

define_compact_wide_actual_insert_control!(
    compact_network_n20_actual_insert_corrupt, 21, "COMPACT_N20_ACT_INSERT_CORRUPT";
    sort9_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n25_actual_insert_corrupt, 26, "COMPACT_N25_ACT_INSERT_CORRUPT";
    sort9_optimal, sort13_optimal, bidirectional_merge,
);

define_compact_wide_actual_insert_control!(
    compact_network_n21_actual_insert_corrupt, 22, "COMPACT_N21_ACT_INSERT_CORRUPT";
    sort9_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n22_actual_insert_corrupt, 23, "COMPACT_N22_ACT_INSERT_CORRUPT";
    sort9_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n23_actual_insert_corrupt, 24, "COMPACT_N23_ACT_INSERT_CORRUPT";
    sort9_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n24_actual_insert_corrupt, 25, "COMPACT_N24_ACT_INSERT_CORRUPT";
    sort9_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n26_actual_insert_corrupt, 27, "COMPACT_N26_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n27_actual_insert_corrupt, 28, "COMPACT_N27_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n28_actual_insert_corrupt, 29, "COMPACT_N28_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n29_actual_insert_corrupt, 30, "COMPACT_N29_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n30_actual_insert_corrupt, 31, "COMPACT_N30_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n31_actual_insert_corrupt, 32, "COMPACT_N31_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);
define_compact_wide_actual_insert_control!(
    compact_network_n32_actual_insert_corrupt, 33, "COMPACT_N32_ACT_INSERT_CORRUPT";
    sort13_optimal, bidirectional_merge,
);

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn compact_network_n25_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..26].fill(0);
    let outside_first = v[0];
    let mut outside_tail = [0; BACKING - 26];
    outside_tail.copy_from_slice(&v[26..]);
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    let captured = merge_wide::merge_capture(&v[1..26], &f);
    kani::assert(captured.is_some(), "COMPACT_N25_CORRUPT_CAPTURE_VALID");

    small_sort_network(&mut v[1..26], &mut f);

    kani::cover(v[1] == 0, "COMPACT_N25_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "COMPACT_N25_CORRUPT_PATH");
    kani::assert(f.q() == q, "COMPACT_N25_CORRUPT_Q_FRAME");
    kani::assert(
        v[0] == outside_first && v[26..] == outside_tail,
        "COMPACT_N25_CORRUPT_OUTSIDE_VALUE_FRAME",
    );
    kani::assert(
        merge_wide::merge_q_post(captured, v[1..26].as_mut_ptr(), &f),
        "COMPACT_N25_CORRUPT_QPOST",
    );
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
#[kani::proof]
#[kani::stub_verified(sort9_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(36)]
fn compact_network_n20_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    v[1..21].fill(0);
    let outside_first = v[0];
    let mut outside_tail = [0; BACKING - 21];
    outside_tail.copy_from_slice(&v[21..]);
    let q = 1;
    let mut f = KeyLess::<u8>::with_q(q);
    let captured = merge_wide::merge_capture(&v[1..21], &f);
    kani::assert(captured.is_some(), "COMPACT_N20_CORRUPT_CAPTURE_VALID");

    small_sort_network(&mut v[1..21], &mut f);

    kani::cover(v[1] == 0, "COMPACT_N20_CORRUPT_USEFUL_RETURN");
    v[1] = 255;
    kani::cover(v[1] == 255, "COMPACT_N20_CORRUPT_PATH");
    kani::assert(f.q() == q, "COMPACT_N20_CORRUPT_Q_FRAME");
    kani::assert(
        v[0] == outside_first && v[21..] == outside_tail,
        "COMPACT_N20_CORRUPT_OUTSIDE_VALUE_FRAME",
    );
    kani::assert(
        merge_wide::merge_q_post(captured, v[1..21].as_mut_ptr(), &f),
        "COMPACT_N20_CORRUPT_QPOST",
    );
}
