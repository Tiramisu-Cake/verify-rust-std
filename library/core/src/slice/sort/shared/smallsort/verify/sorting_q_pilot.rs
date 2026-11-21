//! Threshold-composition pilot roots over the real SmallSort helpers.
//!
//! These are diagnostic candidates only. They do not establish proof credit.

use super::super::{insert_tail, small_sort_network, sort13_optimal, swap_if_less};
use super::sorting_model::KeyLess;
use super::sorting_q_model as qmodel;
use crate::{intrinsics, kani, ptr};

const BACKING: usize = 34;

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(36)]
fn p1_swap_u8_v34_q_any() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P1_ACTIVE");
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < 13 && b < 13);
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let base_offset: usize = kani::any();
    kani::assume(base_offset <= 20);
    let base = unsafe { v.as_mut_ptr().add(base_offset) };
    let captured = qmodel::swap_capture(base, a, b, &f);

    // SAFETY: a and b are in-bounds initialized writable positions in v[base_offset..].
    unsafe { swap_if_less(base, a, b, &mut f) };

    #[cfg(not(kani_smallsort_q_controls))]
    kani::assert(qmodel::swap_post(captured, base, a, b, &f), "P1_SWAP_QPOST");
    kani::assert(f.q() == q, "P1_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            i == base_offset + a || i == base_offset + b || v[i] == before[i],
            "P1_FRAME",
        );
    }
    kani::cover(base_offset == 0, "P1_BASE_ZERO");
    kani::cover(base_offset == 20, "P1_BASE_TWENTY");
    kani::cover(a == b, "P1_EQUAL_INDICES");
    kani::cover(
        (before[base_offset + a] >= q) != (before[base_offset + b] >= q),
        "P1_SPLIT_THRESHOLD",
    );
    kani::cover(
        before[base_offset + b] < before[base_offset + a],
        "P1_SWAP_TAKEN",
    );
    kani::cover(
        before[base_offset + b] >= before[base_offset + a],
        "P1_SWAP_UNTAKEN",
    );
    kani::cover(q == 0, "P1_Q_ZERO");
    kani::cover(q == u8::MAX, "P1_Q_MAX");
    kani::cover(
        before[base_offset + a] != q && before[base_offset + b] != q,
        "P1_Q_ABSENT",
    );
    kani::cover(true, "P1_USEFUL_RETURN");
}
#[kani::proof_for_contract(sort13_optimal)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn p2_sort13_u8_b01_len17_q_any() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P2_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    sort13_optimal(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..14], q, &target), "P2_ORDER_QPOST");
    kani::assert(f.q() == q, "P2_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "P2_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "P2_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..14].windows(2).any(|w| w[0] == w[1]),
        "P2_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "P2_Q_ZERO");
    kani::cover(q == u8::MAX, "P2_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "P2_Q_ABSENT");
    kani::cover(true, "P2_USEFUL_RETURN");
}

#[kani::proof_for_contract(sort13_optimal)]
#[kani::unwind(36)]
fn p2b_sort13_u8_b01_len17_q_any_actual_swaps() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P2_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    sort13_optimal(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..14], q, &target), "P2_ORDER_QPOST");
    kani::assert(f.q() == q, "P2_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "P2_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "P2_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "P2_THRESHOLD_TIES");
    kani::cover(q == 0, "P2_Q_ZERO");
    kani::cover(q == u8::MAX, "P2_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "P2_Q_ABSENT");
    kani::cover(true, "P2_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn d13_body_v34() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "D13_BODY_V34_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    kani::assert(v[1..18].len() == 17, "D13_BODY_V34_LEN");
    let captured = qmodel::prefix_capture(&v[1..18], &f);

    sort13_optimal(&mut v[1..18], &mut f);

    kani::assert(qmodel::prefix_post(captured, &v[1..18], &f), "D13_BODY_V34_PREFIX_POST");
    kani::assert(qmodel::order_post(&v[1..14], q, &target), "D13_BODY_V34_ORDER_QPOST");
    kani::assert(f.q() == q, "D13_BODY_V34_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "D13_BODY_V34_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "D13_BODY_V34_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "D13_BODY_V34_THRESHOLD_TIES");
    kani::cover(q == 0, "D13_BODY_V34_Q_ZERO");
    kani::cover(q == u8::MAX, "D13_BODY_V34_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "D13_BODY_V34_Q_ABSENT");
    kani::cover(true, "D13_BODY_V34_USEFUL_RETURN");
}

#[kani::proof_for_contract(sort13_optimal)]
#[kani::unwind(36)]
fn d13_check_v19() {
    let mut v: [u8; 19] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "D13_CHECK_V19_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    sort13_optimal(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..14], q, &target), "D13_CHECK_V19_ORDER_QPOST");
    kani::assert(f.q() == q, "D13_CHECK_V19_Q_FRAME");
    for i in 0..19 {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "D13_CHECK_V19_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "D13_CHECK_V19_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "D13_CHECK_V19_THRESHOLD_TIES");
    kani::cover(q == 0, "D13_CHECK_V19_Q_ZERO");
    kani::cover(q == u8::MAX, "D13_CHECK_V19_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "D13_CHECK_V19_Q_ABSENT");
    kani::cover(true, "D13_CHECK_V19_USEFUL_RETURN");
}

// First 17 comparators of sort13_optimal, in source order.
#[kani::requires(v.len() == 17)]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v.as_mut_ptr(), crate::cmp::min(13, v.len())))]
#[kani::ensures(|_| qmodel::prefix_count_post(old(qmodel::prefix_count_capture(v, is_less)), v, is_less))]
fn sort13_prefix17(v: &mut [u8], is_less: &mut KeyLess<u8>) {
    if v.len() < 13 {
        intrinsics::abort_immediate();
    }

    let v_base = v.as_mut_ptr();

    // SAFETY: the length check guarantees every literal index is in bounds.
    unsafe {
        swap_if_less(v_base, 0, 12, is_less);
        swap_if_less(v_base, 1, 10, is_less);
        swap_if_less(v_base, 2, 9, is_less);
        swap_if_less(v_base, 3, 7, is_less);
        swap_if_less(v_base, 5, 11, is_less);
        swap_if_less(v_base, 6, 8, is_less);
        swap_if_less(v_base, 1, 6, is_less);
        swap_if_less(v_base, 2, 3, is_less);
        swap_if_less(v_base, 4, 11, is_less);
        swap_if_less(v_base, 7, 9, is_less);
        swap_if_less(v_base, 8, 10, is_less);
        swap_if_less(v_base, 0, 4, is_less);
        swap_if_less(v_base, 1, 2, is_less);
        swap_if_less(v_base, 3, 6, is_less);
        swap_if_less(v_base, 7, 8, is_less);
        swap_if_less(v_base, 9, 10, is_less);
        swap_if_less(v_base, 11, 12, is_less);
    }
}

#[kani::proof_for_contract(sort13_prefix17)]
#[kani::unwind(36)]
fn d13_check_p17() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "D13_CHECK_P17_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort13_prefix17(&mut v[1..18], &mut f);

    kani::assert(f.q() == q, "D13_CHECK_P17_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "D13_CHECK_P17_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "D13_CHECK_P17_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "D13_CHECK_P17_THRESHOLD_TIES");
    kani::cover(q == 0, "D13_CHECK_P17_Q_ZERO");
    kani::cover(q == u8::MAX, "D13_CHECK_P17_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "D13_CHECK_P17_Q_ABSENT");
    kani::cover(true, "D13_CHECK_P17_USEFUL_RETURN");
}

// First 31 comparators of sort13_optimal, in source order.
#[kani::requires(v.len() == 17)]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v.as_mut_ptr(), crate::cmp::min(13, v.len())))]
#[kani::ensures(|_| qmodel::prefix_count_post(old(qmodel::prefix_count_capture(v, is_less)), v, is_less))]
fn sort13_prefix31(v: &mut [u8], is_less: &mut KeyLess<u8>) {
    if v.len() < 13 {
        intrinsics::abort_immediate();
    }

    let v_base = v.as_mut_ptr();

    // SAFETY: the length check guarantees every literal index is in bounds.
    unsafe {
        swap_if_less(v_base, 0, 12, is_less);
        swap_if_less(v_base, 1, 10, is_less);
        swap_if_less(v_base, 2, 9, is_less);
        swap_if_less(v_base, 3, 7, is_less);
        swap_if_less(v_base, 5, 11, is_less);
        swap_if_less(v_base, 6, 8, is_less);
        swap_if_less(v_base, 1, 6, is_less);
        swap_if_less(v_base, 2, 3, is_less);
        swap_if_less(v_base, 4, 11, is_less);
        swap_if_less(v_base, 7, 9, is_less);
        swap_if_less(v_base, 8, 10, is_less);
        swap_if_less(v_base, 0, 4, is_less);
        swap_if_less(v_base, 1, 2, is_less);
        swap_if_less(v_base, 3, 6, is_less);
        swap_if_less(v_base, 7, 8, is_less);
        swap_if_less(v_base, 9, 10, is_less);
        swap_if_less(v_base, 11, 12, is_less);
        swap_if_less(v_base, 4, 6, is_less);
        swap_if_less(v_base, 5, 9, is_less);
        swap_if_less(v_base, 8, 11, is_less);
        swap_if_less(v_base, 10, 12, is_less);
        swap_if_less(v_base, 0, 5, is_less);
        swap_if_less(v_base, 3, 8, is_less);
        swap_if_less(v_base, 4, 7, is_less);
        swap_if_less(v_base, 6, 11, is_less);
        swap_if_less(v_base, 9, 10, is_less);
        swap_if_less(v_base, 0, 1, is_less);
        swap_if_less(v_base, 2, 5, is_less);
        swap_if_less(v_base, 6, 9, is_less);
        swap_if_less(v_base, 7, 8, is_less);
        swap_if_less(v_base, 10, 11, is_less);
    }
}

#[kani::proof_for_contract(sort13_prefix31)]
#[kani::unwind(36)]
fn d13_check_p31() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "D13_CHECK_P31_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    sort13_prefix31(&mut v[1..18], &mut f);

    kani::assert(f.q() == q, "D13_CHECK_P31_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "D13_CHECK_P31_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "D13_CHECK_P31_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "D13_CHECK_P31_THRESHOLD_TIES");
    kani::cover(q == 0, "D13_CHECK_P31_Q_ZERO");
    kani::cover(q == u8::MAX, "D13_CHECK_P31_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "D13_CHECK_P31_Q_ABSENT");
    kani::cover(true, "D13_CHECK_P31_USEFUL_RETURN");
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn p3_insert_u8_b01_rel1_16_q_any() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P3_ACTIVE");
    let tail: usize = kani::any();
    kani::assume((1..=16).contains(&tail));
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let base = unsafe { v.as_mut_ptr().add(1) };
    let len = tail + 1;
    let captured = qmodel::capture(base, len, &f);

    // SAFETY: the contract precondition supplies the initialized, writable inclusive span.
    unsafe { insert_tail(base, base.add(tail), &mut f) };

    kani::assert(
        qmodel::insert_post(captured, base, len, &f),
        "P3_INSERT_QPOST",
    );
    kani::assert(f.q() == q, "P3_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..1 + len).contains(&i) || v[i] == before[i], "P3_FRAME");
    }
    kani::cover(tail == 1, "P3_TAIL_01");
    kani::cover(tail == 2, "P3_TAIL_02");
    kani::cover(tail == 3, "P3_TAIL_03");
    kani::cover(tail == 4, "P3_TAIL_04");
    kani::cover(tail == 5, "P3_TAIL_05");
    kani::cover(tail == 6, "P3_TAIL_06");
    kani::cover(tail == 7, "P3_TAIL_07");
    kani::cover(tail == 8, "P3_TAIL_08");
    kani::cover(tail == 9, "P3_TAIL_09");
    kani::cover(tail == 10, "P3_TAIL_10");
    kani::cover(tail == 11, "P3_TAIL_11");
    kani::cover(tail == 12, "P3_TAIL_12");
    kani::cover(tail == 13, "P3_TAIL_13");
    kani::cover(tail == 14, "P3_TAIL_14");
    kani::cover(tail == 15, "P3_TAIL_15");
    kani::cover(tail == 16, "P3_TAIL_16");
    kani::cover(before[1 + tail] >= before[tail], "P3_EARLY_RETURN");
    let mut full_sift = tail > 0;
    let mut non_numeric_order = false;
    for i in 0..tail {
        full_sift = full_sift && before[1 + tail] < before[1 + i];
    }
    for i in 0..tail.saturating_sub(1) {
        non_numeric_order = non_numeric_order
            || (before[1 + i] > before[2 + i] && (before[1 + i] >= q) == (before[2 + i] >= q));
    }
    kani::cover(full_sift, "P3_FULL_SIFT");
    kani::cover(non_numeric_order, "P3_Q_MONOTONE_NON_NUMERIC_ORDER");
    kani::cover(q == 0, "P3_Q_ZERO");
    kani::cover(q == u8::MAX, "P3_Q_MAX");
    kani::cover(before[1..1 + len].iter().all(|x| *x != q), "P3_Q_ABSENT");
    kani::cover(
        (before[1] >= q) != (before[1 + tail] >= q),
        "P3_SPLIT_THRESHOLD",
    );
    kani::cover(true, "P3_USEFUL_RETURN");
}

#[kani::proof]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn p4_network_u8_b01_n17_q_any() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P4_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..18], q);

    small_sort_network(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..18], q, &target), "P4_QPOST");
    kani::assert(f.q() == q, "P4_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..18).contains(&i) || v[i] == before[i],
            "P4_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..18].iter().any(|x| *x < q) && before[1..18].iter().any(|x| *x >= q),
        "P4_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..18].windows(2).any(|w| w[0] == w[1]),
        "P4_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "P4_Q_ZERO");
    kani::cover(q == u8::MAX, "P4_Q_MAX");
    kani::cover(before[1..18].iter().all(|x| *x != q), "P4_Q_ABSENT");
    kani::cover(true, "P4_USEFUL_RETURN");
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn q13_plain_stub_swap() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "Q13_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    sort13_optimal(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..14], q, &target), "Q13_PLAIN_ORDER_QPOST");
    kani::assert(f.q() == q, "Q13_PLAIN_Q_FRAME");
    kani::assert(v[14..18] == before[14..18], "Q13_PLAIN_TAIL_BYTES");
    for i in 0..BACKING {
        kani::assert((1..14).contains(&i) || v[i] == before[i], "Q13_PLAIN_FRAME");
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "Q13_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(before[1..14].windows(2).any(|w| w[0] == w[1]), "Q13_PLAIN_THRESHOLD_TIES");
    kani::cover(q == 0, "Q13_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "Q13_PLAIN_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "Q13_PLAIN_Q_ABSENT");
    kani::cover(true, "Q13_PLAIN_USEFUL_RETURN");
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n17_plain_stub_swap_insert() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N17_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..18], q);

    small_sort_network(&mut v[1..18], &mut f);

    kani::assert(qmodel::order_post(&v[1..18], q, &target), "N17_PLAIN_QPOST");
    kani::assert(f.q() == q, "N17_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert((1..18).contains(&i) || v[i] == before[i], "N17_PLAIN_OUTSIDE_VALUE_FRAME");
    }
    kani::cover(
        before[1..18].iter().any(|x| *x < q) && before[1..18].iter().any(|x| *x >= q),
        "N17_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(before[1..18].windows(2).any(|w| w[0] == w[1]), "N17_PLAIN_THRESHOLD_TIES");
    kani::cover(q == 0, "N17_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N17_PLAIN_Q_MAX");
    kani::cover(before[1..18].iter().all(|x| *x != q), "N17_PLAIN_Q_ABSENT");
    kani::cover(true, "N17_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::unwind(36)]
fn n01_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N01_PLAIN_ACTIVE");
    let n = kani::any::<bool>() as usize;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..1 + n], q);

    small_sort_network(&mut v[1..1 + n], &mut f);

    kani::assert(v == before, "N01_PLAIN_UNCHANGED");
    kani::assert(
        qmodel::order_post(&v[1..1 + n], q, &target),
        "N01_PLAIN_QPOST",
    );
    kani::assert(f.q() == q, "N01_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..1 + n).contains(&i) || v[i] == before[i],
            "N01_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(n == 0, "N01_PLAIN_LEN0_RETURN");
    kani::cover(n == 1, "N01_PLAIN_LEN1_RETURN");
    kani::cover(q == 0, "N01_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N01_PLAIN_Q_MAX");
    kani::cover(n == 1 && before[1] != q, "N01_PLAIN_Q_ABSENT");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n02_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N02_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..3], q);

    small_sort_network(&mut v[1..3], &mut f);

    kani::assert(qmodel::order_post(&v[1..3], q, &target), "N02_PLAIN_QPOST");
    kani::assert(f.q() == q, "N02_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..3).contains(&i) || v[i] == before[i],
            "N02_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..3].iter().any(|x| *x < q) && before[1..3].iter().any(|x| *x >= q),
        "N02_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..3].windows(2).any(|w| w[0] == w[1]),
        "N02_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N02_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N02_PLAIN_Q_MAX");
    kani::cover(before[1..3].iter().all(|x| *x != q), "N02_PLAIN_Q_ABSENT");
    kani::cover(true, "N02_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n08_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N08_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..9], q);

    small_sort_network(&mut v[1..9], &mut f);

    kani::assert(qmodel::order_post(&v[1..9], q, &target), "N08_PLAIN_QPOST");
    kani::assert(f.q() == q, "N08_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..9).contains(&i) || v[i] == before[i],
            "N08_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..9].iter().any(|x| *x < q) && before[1..9].iter().any(|x| *x >= q),
        "N08_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..9].windows(2).any(|w| w[0] == w[1]),
        "N08_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N08_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N08_PLAIN_Q_MAX");
    kani::cover(before[1..9].iter().all(|x| *x != q), "N08_PLAIN_Q_ABSENT");
    kani::cover(true, "N08_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn n09_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N09_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..10], q);

    small_sort_network(&mut v[1..10], &mut f);

    kani::assert(qmodel::order_post(&v[1..10], q, &target), "N09_PLAIN_QPOST");
    kani::assert(f.q() == q, "N09_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..10).contains(&i) || v[i] == before[i],
            "N09_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..10].iter().any(|x| *x < q) && before[1..10].iter().any(|x| *x >= q),
        "N09_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..10].windows(2).any(|w| w[0] == w[1]),
        "N09_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N09_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N09_PLAIN_Q_MAX");
    kani::cover(before[1..10].iter().all(|x| *x != q), "N09_PLAIN_Q_ABSENT");
    kani::cover(true, "N09_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n12_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N12_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..13], q);

    small_sort_network(&mut v[1..13], &mut f);

    kani::assert(qmodel::order_post(&v[1..13], q, &target), "N12_PLAIN_QPOST");
    kani::assert(f.q() == q, "N12_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..13).contains(&i) || v[i] == before[i],
            "N12_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..13].iter().any(|x| *x < q) && before[1..13].iter().any(|x| *x >= q),
        "N12_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..13].windows(2).any(|w| w[0] == w[1]),
        "N12_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N12_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N12_PLAIN_Q_MAX");
    kani::cover(before[1..13].iter().all(|x| *x != q), "N12_PLAIN_Q_ABSENT");
    kani::cover(true, "N12_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(36)]
fn n13_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N13_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..14], q);

    small_sort_network(&mut v[1..14], &mut f);

    kani::assert(qmodel::order_post(&v[1..14], q, &target), "N13_PLAIN_QPOST");
    kani::assert(f.q() == q, "N13_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..14).contains(&i) || v[i] == before[i],
            "N13_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..14].iter().any(|x| *x < q) && before[1..14].iter().any(|x| *x >= q),
        "N13_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..14].windows(2).any(|w| w[0] == w[1]),
        "N13_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N13_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N13_PLAIN_Q_MAX");
    kani::cover(before[1..14].iter().all(|x| *x != q), "N13_PLAIN_Q_ABSENT");
    kani::cover(true, "N13_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n16_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N16_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..17], q);

    small_sort_network(&mut v[1..17], &mut f);

    kani::assert(qmodel::order_post(&v[1..17], q, &target), "N16_PLAIN_QPOST");
    kani::assert(f.q() == q, "N16_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..17).contains(&i) || v[i] == before[i],
            "N16_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..17].iter().any(|x| *x < q) && before[1..17].iter().any(|x| *x >= q),
        "N16_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..17].windows(2).any(|w| w[0] == w[1]),
        "N16_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N16_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N16_PLAIN_Q_MAX");
    kani::cover(before[1..17].iter().all(|x| *x != q), "N16_PLAIN_Q_ABSENT");
    kani::cover(true, "N16_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::unwind(36)]
fn n00_literal_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N00_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    small_sort_network(&mut v[1..1], &mut f);

    kani::assert(v == before, "N00_PLAIN_UNCHANGED");
    kani::assert(f.q() == q, "N00_PLAIN_Q_FRAME");
    kani::cover(q == 0, "N00_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N00_PLAIN_Q_MAX");
    kani::cover(true, "N00_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::unwind(36)]
fn n01_literal_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(
        qmodel::active::<u8, KeyLess<u8>>(),
        "N01_LITERAL_PLAIN_ACTIVE",
    );
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);

    small_sort_network(&mut v[1..2], &mut f);

    kani::assert(v == before, "N01_LITERAL_PLAIN_UNCHANGED");
    kani::assert(f.q() == q, "N01_LITERAL_PLAIN_Q_FRAME");
    kani::cover(q == 0, "N01_LITERAL_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N01_LITERAL_PLAIN_Q_MAX");
    kani::cover(before[1] != q, "N01_LITERAL_PLAIN_Q_ABSENT");
    kani::cover(true, "N01_LITERAL_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n03_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N03_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..4], q);

    small_sort_network(&mut v[1..4], &mut f);

    kani::assert(qmodel::order_post(&v[1..4], q, &target), "N03_PLAIN_QPOST");
    kani::assert(f.q() == q, "N03_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..4).contains(&i) || v[i] == before[i],
            "N03_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..4].iter().any(|x| *x < q) && before[1..4].iter().any(|x| *x >= q),
        "N03_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..4].windows(2).any(|w| w[0] == w[1]),
        "N03_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N03_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N03_PLAIN_Q_MAX");
    kani::cover(before[1..4].iter().all(|x| *x != q), "N03_PLAIN_Q_ABSENT");
    kani::cover(true, "N03_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n04_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N04_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..5], q);

    small_sort_network(&mut v[1..5], &mut f);

    kani::assert(qmodel::order_post(&v[1..5], q, &target), "N04_PLAIN_QPOST");
    kani::assert(f.q() == q, "N04_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..5).contains(&i) || v[i] == before[i],
            "N04_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..5].iter().any(|x| *x < q) && before[1..5].iter().any(|x| *x >= q),
        "N04_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..5].windows(2).any(|w| w[0] == w[1]),
        "N04_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N04_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N04_PLAIN_Q_MAX");
    kani::cover(before[1..5].iter().all(|x| *x != q), "N04_PLAIN_Q_ABSENT");
    kani::cover(true, "N04_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n05_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N05_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..6], q);

    small_sort_network(&mut v[1..6], &mut f);

    kani::assert(qmodel::order_post(&v[1..6], q, &target), "N05_PLAIN_QPOST");
    kani::assert(f.q() == q, "N05_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..6).contains(&i) || v[i] == before[i],
            "N05_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..6].iter().any(|x| *x < q) && before[1..6].iter().any(|x| *x >= q),
        "N05_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..6].windows(2).any(|w| w[0] == w[1]),
        "N05_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N05_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N05_PLAIN_Q_MAX");
    kani::cover(before[1..6].iter().all(|x| *x != q), "N05_PLAIN_Q_ABSENT");
    kani::cover(true, "N05_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n06_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N06_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..7], q);

    small_sort_network(&mut v[1..7], &mut f);

    kani::assert(qmodel::order_post(&v[1..7], q, &target), "N06_PLAIN_QPOST");
    kani::assert(f.q() == q, "N06_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..7).contains(&i) || v[i] == before[i],
            "N06_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..7].iter().any(|x| *x < q) && before[1..7].iter().any(|x| *x >= q),
        "N06_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..7].windows(2).any(|w| w[0] == w[1]),
        "N06_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N06_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N06_PLAIN_Q_MAX");
    kani::cover(before[1..7].iter().all(|x| *x != q), "N06_PLAIN_Q_ABSENT");
    kani::cover(true, "N06_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n07_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N07_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..8], q);

    small_sort_network(&mut v[1..8], &mut f);

    kani::assert(qmodel::order_post(&v[1..8], q, &target), "N07_PLAIN_QPOST");
    kani::assert(f.q() == q, "N07_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..8).contains(&i) || v[i] == before[i],
            "N07_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..8].iter().any(|x| *x < q) && before[1..8].iter().any(|x| *x >= q),
        "N07_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..8].windows(2).any(|w| w[0] == w[1]),
        "N07_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N07_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N07_PLAIN_Q_MAX");
    kani::cover(before[1..8].iter().all(|x| *x != q), "N07_PLAIN_Q_ABSENT");
    kani::cover(true, "N07_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n10_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N10_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..11], q);

    small_sort_network(&mut v[1..11], &mut f);

    kani::assert(qmodel::order_post(&v[1..11], q, &target), "N10_PLAIN_QPOST");
    kani::assert(f.q() == q, "N10_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..11).contains(&i) || v[i] == before[i],
            "N10_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..11].iter().any(|x| *x < q) && before[1..11].iter().any(|x| *x >= q),
        "N10_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..11].windows(2).any(|w| w[0] == w[1]),
        "N10_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N10_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N10_PLAIN_Q_MAX");
    kani::cover(before[1..11].iter().all(|x| *x != q), "N10_PLAIN_Q_ABSENT");
    kani::cover(true, "N10_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n11_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N11_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..12], q);

    small_sort_network(&mut v[1..12], &mut f);

    kani::assert(qmodel::order_post(&v[1..12], q, &target), "N11_PLAIN_QPOST");
    kani::assert(f.q() == q, "N11_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..12).contains(&i) || v[i] == before[i],
            "N11_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..12].iter().any(|x| *x < q) && before[1..12].iter().any(|x| *x >= q),
        "N11_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..12].windows(2).any(|w| w[0] == w[1]),
        "N11_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N11_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N11_PLAIN_Q_MAX");
    kani::cover(before[1..12].iter().all(|x| *x != q), "N11_PLAIN_Q_ABSENT");
    kani::cover(true, "N11_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n14_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N14_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..15], q);

    small_sort_network(&mut v[1..15], &mut f);

    kani::assert(qmodel::order_post(&v[1..15], q, &target), "N14_PLAIN_QPOST");
    kani::assert(f.q() == q, "N14_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..15).contains(&i) || v[i] == before[i],
            "N14_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..15].iter().any(|x| *x < q) && before[1..15].iter().any(|x| *x >= q),
        "N14_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..15].windows(2).any(|w| w[0] == w[1]),
        "N14_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N14_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N14_PLAIN_Q_MAX");
    kani::cover(before[1..15].iter().all(|x| *x != q), "N14_PLAIN_Q_ABSENT");
    kani::cover(true, "N14_PLAIN_USEFUL_RETURN");
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn n15_plain_no_merge() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "N15_PLAIN_ACTIVE");
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    let target = qmodel::order_target(&before[1..16], q);

    small_sort_network(&mut v[1..16], &mut f);

    kani::assert(qmodel::order_post(&v[1..16], q, &target), "N15_PLAIN_QPOST");
    kani::assert(f.q() == q, "N15_PLAIN_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            (1..16).contains(&i) || v[i] == before[i],
            "N15_PLAIN_OUTSIDE_VALUE_FRAME",
        );
    }
    kani::cover(
        before[1..16].iter().any(|x| *x < q) && before[1..16].iter().any(|x| *x >= q),
        "N15_PLAIN_MIXED_THRESHOLD",
    );
    kani::cover(
        before[1..16].windows(2).any(|w| w[0] == w[1]),
        "N15_PLAIN_THRESHOLD_TIES",
    );
    kani::cover(q == 0, "N15_PLAIN_Q_ZERO");
    kani::cover(q == u8::MAX, "N15_PLAIN_Q_MAX");
    kani::cover(before[1..16].iter().all(|x| *x != q), "N15_PLAIN_Q_ABSENT");
    kani::cover(true, "N15_PLAIN_USEFUL_RETURN");
}
