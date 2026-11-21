//! Package A checks of the real leaves and presort paths for N18 and N19.

use super::super::merge_up;
#[cfg(not(kani_smallsort_q_merge_bad_tie))]
use super::super::{
    insert_tail, insertion_sort_shift_left, merge_down, sort9_optimal, swap_if_less,
};
use super::sorting_model::KeyLess;
use super::sorting_q_merge_model as model;
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
