//! Threshold-composition pilot roots over the real SmallSort helpers.
//!
//! These are diagnostic candidates only. They do not establish proof credit.

use super::super::{insert_tail, small_sort_network, sort13_optimal, swap_if_less};
use super::sorting_model::KeyLess;
use super::sorting_q_model as qmodel;
use crate::kani;

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
