//! Seven-root bridge: bounded full-byte normal-return candidates, no proof credit.
//! Cell bytes are logical whole values; no trait-dispatch or mutable-comparator theorem.
use super::super::{insert_tail, sort9_optimal, small_sort_fallback, small_sort_network};
use super::sorting_model::{KeyLess, enabled, snapshot, post};
use super::{sorting_s2_span as span, sorting_s2_swap as pair};
use crate::{kani, cell::Cell};

fn active_u8() -> bool {
    enabled::<u8, KeyLess<u8>>() && span::active::<u8, KeyLess<u8>>()
        && pair::enabled::<u8, KeyLess<u8>>()
}
fn descending(v: &[u8]) -> bool {
    let mut i = 1;
    while i < v.len() {
        if v[i - 1] <= v[i] { return false; }
        i += 1;
    }
    true
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(36)]
fn i_p01_b01_fullu8() {
    kani::assert(active_u8(), "B1_I_ACTIVE");
    let mut v: [u8; 34] = kani::any();
    let before = v;
    let begin = 1;
    let tail = 1;
    let p = unsafe { v.as_mut_ptr().add(begin) };
    unsafe { insert_tail(p, p.add(tail), &mut KeyLess::<u8>::new()) };
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[1..3]), &v[1..3]), "B1_I_SORTED_FULL_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 3) || v[i] == before[i], "B1_I_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 3));
    kani::assert(v[canary] == before[canary], "B1_I_CANARY");
    kani::cover(before[2] >= before[1], "B1_I_EARLY_RETURN");
    kani::cover(before[2] < before[1], "B1_I_FULL_SIFT");
    kani::cover(before[2] == before[1], "B1_I_DUPLICATE");
    kani::cover(v[1] < v[2], "B1_I_NONCONSTANT");
    kani::cover(true, "B1_I_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn sort9_v34_b01_len09_real() {
    kani::assert(active_u8(), "B1_S9_ACTIVE");
    let mut v: [u8; 34] = kani::any();
    let before = v;
    sort9_optimal(&mut v[1..10], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[1..10]), &v[1..10]), "B1_S9_SORTED_FULL_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 10) || v[i] == before[i], "B1_S9_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 10));
    kani::assert(v[canary] == before[canary], "B1_S9_CANARY");
    kani::cover(before[1] > before[9], "B1_S9_UNSORTED");
    kani::cover(before[1] == before[9], "B1_S9_DUPLICATE");
    kani::cover(v[1] < v[9], "B1_S9_NONCONSTANT");
    kani::cover(descending(&before[1..10]), "B1_S9_DESCENDING");
    kani::cover(true, "B1_S9_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn fallback_cell_b01_n00_16() {
    kani::assert(enabled::<Cell<u8>, KeyLess<Cell<u8>>>(), "B1_F_ACTIVE");
    let bytes: [u8; 34] = kani::any();
    let mut v = [const { Cell::new(0u8) }; 34];
    for i in 0..34 { v[i].set(bytes[i]); }
    let n: usize = kani::any();
    kani::assume(n <= 16);
    let before = snapshot::<Cell<u8>, KeyLess<Cell<u8>>>(&v[1..1 + n]);
    small_sort_fallback(&mut v[1..1 + n], &mut KeyLess::<Cell<u8>>::new());
    kani::assert(post::<Cell<u8>, KeyLess<Cell<u8>>>(before, &v[1..1 + n]), "B1_F_SORTED_FULL_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i].get() == bytes[i], "B1_F_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary].get() == bytes[canary], "B1_F_CANARY");
    kani::cover(n == 0, "B1_F_N00");
    kani::cover(n == 1, "B1_F_N01");
    kani::cover(n == 2, "B1_F_N02");
    kani::cover(n == 3, "B1_F_N03");
    kani::cover(n == 4, "B1_F_N04");
    kani::cover(n == 5, "B1_F_N05");
    kani::cover(n == 6, "B1_F_N06");
    kani::cover(n == 7, "B1_F_N07");
    kani::cover(n == 8, "B1_F_N08");
    kani::cover(n == 9, "B1_F_N09");
    kani::cover(n == 10, "B1_F_N10");
    kani::cover(n == 11, "B1_F_N11");
    kani::cover(n == 12, "B1_F_N12");
    kani::cover(n == 13, "B1_F_N13");
    kani::cover(n == 14, "B1_F_N14");
    kani::cover(n == 15, "B1_F_N15");
    kani::cover(n == 16, "B1_F_N16");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "B1_F_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "B1_F_DUPLICATE");
    kani::cover(n >= 2 && v[1].get() < v[n].get(), "B1_F_NONCONSTANT");
    kani::cover(n == 16 && descending(&bytes[1..17]), "B1_F_MAX_DESCENDING");
    kani::cover(true, "B1_F_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn network_u8_b01_n00_08() {
    kani::assert(active_u8(), "B1_N_ACTIVE");
    let mut v: [u8; 34] = kani::any();
    let before = v;
    let n: usize = kani::any();
    kani::assume(n <= 8);
    small_sort_network(&mut v[1..1 + n], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(snapshot::<u8, KeyLess<u8>>(&before[1..1 + n]), &v[1..1 + n]), "B1_N_SORTED_FULL_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == before[i], "B1_N_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == before[canary], "B1_N_CANARY");
    kani::cover(n == 0, "B1_N_N00");
    kani::cover(n == 1, "B1_N_N01");
    kani::cover(n == 2, "B1_N_N02");
    kani::cover(n == 3, "B1_N_N03");
    kani::cover(n == 4, "B1_N_N04");
    kani::cover(n == 5, "B1_N_N05");
    kani::cover(n == 6, "B1_N_N06");
    kani::cover(n == 7, "B1_N_N07");
    kani::cover(n == 8, "B1_N_N08");
    kani::cover(n >= 2 && before[1] > before[n], "B1_N_UNSORTED");
    kani::cover(n >= 2 && before[1] == before[n], "B1_N_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "B1_N_NONCONSTANT");
    kani::cover(n == 8 && descending(&before[1..9]), "B1_N_MAX_DESCENDING");
    kani::cover(true, "B1_N_USEFUL_RETURN");
}
