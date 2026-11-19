//! S4 full-byte length blocks: finite normal-return candidates, no proof credit.
//! All 34 logical bytes are independent; initialized V34, base1, no summaries.
use super::super::{small_sort_fallback, small_sort_network};
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

// Checker-only count corruption: sorted [0,0] is not a permutation of [0,1].
#[kani::proof]
#[kani::unwind(36)]
fn s4p_cell_count_corrupt() {
    kani::assert(enabled::<Cell<u8>, KeyLess<Cell<u8>>>(), "S4_NEG_CELL_ACTIVE");
    let v = [const { Cell::new(0u8) }; 34];
    v[2].set(1);
    let before = snapshot::<Cell<u8>, KeyLess<Cell<u8>>>(&v[1..3]);
    v[2].set(0);
    kani::assert(post::<Cell<u8>, KeyLess<Cell<u8>>>(before, &v[1..3]), "S4_NEG_CELL_COUNT");
}

#[kani::proof]
#[kani::unwind(36)]
fn s4p_fallback_b01_n00_02_fullbyte() {
    kani::assert(enabled::<Cell<u8>, KeyLess<Cell<u8>>>(), "S4P_F_00_02_ACTIVE_CONCRETE_MODEL");
    let bytes: [u8; 34] = kani::any();
    let mut v = [const { Cell::new(0u8) }; 34];
    for i in 0..34 { v[i].set(bytes[i]); }
    let n: usize = kani::any();
    kani::assume(0 <= n && n <= 2);
    let before = snapshot::<Cell<u8>, KeyLess<Cell<u8>>>(&v[1..1 + n]);
    small_sort_fallback(&mut v[1..1 + n], &mut KeyLess::<Cell<u8>>::new());
    kani::assert(post::<Cell<u8>, KeyLess<Cell<u8>>>(before, &v[1..1 + n]), "S4P_F_00_02_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i].get() == bytes[i], "S4P_F_00_02_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary].get() == bytes[canary], "S4P_F_00_02_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 0, "S4P_F_00_02_N00");
    kani::cover(n == 1, "S4P_F_00_02_N01");
    kani::cover(n == 2, "S4P_F_00_02_N02");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P_F_00_02_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P_F_00_02_DUPLICATE");
    kani::cover(n >= 2 && v[1].get() < v[n].get(), "S4P_F_00_02_NONCONSTANT");
    kani::cover(n == 2 && descending(&bytes[1..3]), "S4P_F_00_02_MAX_DESCENDING");
    kani::cover(true, "S4P_F_00_02_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn s4p_fallback_b01_n03_04_fullbyte() {
    kani::assert(enabled::<Cell<u8>, KeyLess<Cell<u8>>>(), "S4P_F_03_04_ACTIVE_CONCRETE_MODEL");
    let bytes: [u8; 34] = kani::any();
    let mut v = [const { Cell::new(0u8) }; 34];
    for i in 0..34 { v[i].set(bytes[i]); }
    let n: usize = kani::any();
    kani::assume(3 <= n && n <= 4);
    let before = snapshot::<Cell<u8>, KeyLess<Cell<u8>>>(&v[1..1 + n]);
    small_sort_fallback(&mut v[1..1 + n], &mut KeyLess::<Cell<u8>>::new());
    kani::assert(post::<Cell<u8>, KeyLess<Cell<u8>>>(before, &v[1..1 + n]), "S4P_F_03_04_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i].get() == bytes[i], "S4P_F_03_04_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary].get() == bytes[canary], "S4P_F_03_04_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 3, "S4P_F_03_04_N03");
    kani::cover(n == 4, "S4P_F_03_04_N04");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P_F_03_04_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P_F_03_04_DUPLICATE");
    kani::cover(n >= 2 && v[1].get() < v[n].get(), "S4P_F_03_04_NONCONSTANT");
    kani::cover(n == 4 && descending(&bytes[1..5]), "S4P_F_03_04_MAX_DESCENDING");
    kani::cover(true, "S4P_F_03_04_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn s4p_network_b01_n00_02_fullbyte() {
    kani::assert(active_u8(), "S4P_N_00_02_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = kani::any();
    kani::assume(0 <= n && n <= 2);
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..1 + n]);
    small_sort_network(&mut v[1..1 + n], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..1 + n]), "S4P_N_00_02_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P_N_00_02_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P_N_00_02_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 0, "S4P_N_00_02_N00");
    kani::cover(n == 1, "S4P_N_00_02_N01");
    kani::cover(n == 2, "S4P_N_00_02_N02");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P_N_00_02_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P_N_00_02_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P_N_00_02_NONCONSTANT");
    kani::cover(n == 2 && descending(&bytes[1..3]), "S4P_N_00_02_MAX_DESCENDING");
    kani::cover(true, "S4P_N_00_02_USEFUL_RETURN");
}

#[kani::proof]
#[kani::unwind(36)]
fn s4p_network_b01_n03_04_fullbyte() {
    kani::assert(active_u8(), "S4P_N_03_04_ACTIVE_CONCRETE_MODEL");
    let mut v: [u8; 34] = kani::any();
    let bytes = v;
    let n: usize = kani::any();
    kani::assume(3 <= n && n <= 4);
    let before = snapshot::<u8, KeyLess<u8>>(&v[1..1 + n]);
    small_sort_network(&mut v[1..1 + n], &mut KeyLess::<u8>::new());
    kani::assert(post::<u8, KeyLess<u8>>(before, &v[1..1 + n]), "S4P_N_03_04_SORTED_FULL_VALUE_COUNT");
    for i in 0..34 {
        kani::assert((1 <= i && i < 1 + n) || v[i] == bytes[i], "S4P_N_03_04_FULL_OUTSIDE_FRAME");
    }
    let canary: usize = kani::any();
    kani::assume(canary < 34 && (canary < 1 || canary >= 1 + n));
    kani::assert(v[canary] == bytes[canary], "S4P_N_03_04_ARBITRARY_OUTSIDE_CANARY");
    kani::cover(n == 3, "S4P_N_03_04_N03");
    kani::cover(n == 4, "S4P_N_03_04_N04");
    kani::cover(n >= 2 && bytes[1] > bytes[n], "S4P_N_03_04_UNSORTED");
    kani::cover(n >= 2 && bytes[1] == bytes[n], "S4P_N_03_04_DUPLICATE");
    kani::cover(n >= 2 && v[1] < v[n], "S4P_N_03_04_NONCONSTANT");
    kani::cover(n == 4 && descending(&bytes[1..5]), "S4P_N_03_04_MAX_DESCENDING");
    kani::cover(true, "S4P_N_03_04_USEFUL_RETURN");
}
