//! Deliberate false-OR mutant controls for the threshold swap postcondition.

use super::super::{insert_tail, small_sort_network, sort13_optimal, swap_if_less};
use super::sorting_model::KeyLess;
use super::sorting_q_model as qmodel;
use crate::kani;

const BACKING: usize = 34;

#[cfg(kani_smallsort_q_controls)]
fn exercise_false_or(q: u8, cover_split_threshold: bool) {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P5_SWAP_ACTIVE");
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < 13 && b < 13);
    let mut f = KeyLess::<u8>::with_q(q);
    let base_offset: usize = kani::any();
    kani::assume(base_offset <= 20);
    let base = unsafe { v.as_mut_ptr().add(base_offset) };

    // SAFETY: a and b are in-bounds initialized writable positions in v[base_offset..].
    unsafe { swap_if_less(base, a, b, &mut f) };

    kani::assert(f.q() == q, "P5_SWAP_Q_FRAME");
    for i in 0..BACKING {
        kani::assert(
            i == base_offset + a || i == base_offset + b || v[i] == before[i],
            "P5_SWAP_FRAME",
        );
    }
    kani::cover(base_offset == 0, "P5_SWAP_BASE_ZERO");
    kani::cover(base_offset == 20, "P5_SWAP_BASE_TWENTY");
    if cover_split_threshold {
        kani::cover(
            (before[base_offset + a] >= q) != (before[base_offset + b] >= q),
            "P5_SWAP_SPLIT_THRESHOLD",
        );
    }
    kani::cover(true, "P5_SWAP_USEFUL_RETURN");
}

#[cfg(kani_smallsort_q_controls)]
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(36)]
fn p5_swap_false_or_q_any() {
    let q: u8 = kani::any();
    exercise_false_or(q, true);
}

#[cfg(kani_smallsort_q_controls)]
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(36)]
fn p5_swap_false_or_q_fixed0() {
    exercise_false_or(0, false);
}

#[cfg(not(kani_smallsort_q_controls))]
#[kani::proof]
#[kani::stub_verified(sort13_optimal)]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(36)]
fn p5_network_n17_qpost_corrupt() {
    let mut v: [u8; BACKING] = kani::any();
    let before = v;
    let q: u8 = kani::any();
    let mut f = KeyLess::<u8>::with_q(q);
    kani::assert(qmodel::active::<u8, KeyLess<u8>>(), "P5C_ACTIVE");
    let target = qmodel::order_target(&v[1..18], q);
    let all_zero = v[1..18].iter().all(|x| *x == 0);

    small_sort_network(&mut v[1..18], &mut f);
    if all_zero {
        v[1] = u8::MAX;
    }

    kani::cover(all_zero, "P5C_ALL_ZERO_INPUT");
    kani::cover(all_zero && q == 1, "P5C_Q_ONE_CORRUPTION_PATH");
    for i in 0..BACKING {
        kani::assert((1..18).contains(&i) || v[i] == before[i], "P5C_OUTSIDE_VALUE_FRAME");
    }
    kani::assert(f.q() == q, "P5C_Q_FRAME");
    kani::cover(true, "P5C_USEFUL_RETURN");
    kani::assert(qmodel::order_post(&v[1..18], q, &target), "P5C_CORRUPT_QPOST");
}
