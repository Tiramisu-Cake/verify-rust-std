//! S4P3 concrete-call network boundaries: finite normal-return candidates, no proof credit.
//! All 34 logical bytes are independent; initialized V34, base1, no summaries.
use super::super::small_sort_network;
use super::sorting_model::{KeyLess, enabled, snapshot, post};
use super::{sorting_s2_span as span, sorting_s2_swap as pair};
use crate::kani;

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

#[kani::proof]
#[kani::unwind(36)]
fn s4p3_network_b01_n08_fullbyte() {
    kani::assert(active_u8(), "S4P3_N_08_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = 8;
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..9]);
    small_sort_network(&mut v[1..9], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..9]), "S4P3_N_08_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P3_N_08_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P3_N_08_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 8, "S4P3_N_08_N08");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P3_N_08_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P3_N_08_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P3_N_08_NONCONSTANT");
    kani::cover(n == 8 && descending(&bytes[1..9]), "S4P3_N_08_MAX_DESCENDING");
    kani::cover(true, "S4P3_N_08_USEFUL_RETURN");
}
#[kani::proof]
#[kani::unwind(36)]
fn s4p3_network_b01_n09_fullbyte() {
    kani::assert(active_u8(), "S4P3_N_09_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = 9;
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..10]);
    small_sort_network(&mut v[1..10], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..10]), "S4P3_N_09_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P3_N_09_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P3_N_09_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 9, "S4P3_N_09_N09");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P3_N_09_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P3_N_09_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P3_N_09_NONCONSTANT");
    kani::cover(n == 9 && descending(&bytes[1..10]), "S4P3_N_09_MAX_DESCENDING");
    kani::cover(true, "S4P3_N_09_USEFUL_RETURN");
}
#[kani::proof]
#[kani::unwind(36)]
fn s4p3_network_b01_n13_fullbyte() {
    kani::assert(active_u8(), "S4P3_N_13_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = 13;
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..14]);
    small_sort_network(&mut v[1..14], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..14]), "S4P3_N_13_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P3_N_13_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P3_N_13_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 13, "S4P3_N_13_N13");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P3_N_13_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P3_N_13_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P3_N_13_NONCONSTANT");
    kani::cover(n == 13 && descending(&bytes[1..14]), "S4P3_N_13_MAX_DESCENDING");
    kani::cover(true, "S4P3_N_13_USEFUL_RETURN");
}
#[kani::proof]
#[kani::unwind(36)]
fn s4p3_network_b01_n17_fullbyte() {
    kani::assert(active_u8(), "S4P3_N_17_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = 17;
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..18]);
    small_sort_network(&mut v[1..18], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..18]), "S4P3_N_17_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P3_N_17_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P3_N_17_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 17, "S4P3_N_17_N17");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P3_N_17_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P3_N_17_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P3_N_17_NONCONSTANT");
    kani::cover(n == 17 && descending(&bytes[1..18]), "S4P3_N_17_MAX_DESCENDING");
    kani::cover(true, "S4P3_N_17_USEFUL_RETURN");
}
