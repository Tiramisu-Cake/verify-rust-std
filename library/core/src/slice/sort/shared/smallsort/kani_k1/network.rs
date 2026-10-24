//! K1-network agent: contracts and harnesses for `swap_if_less`, `sort9_optimal`, `sort13_optimal`,
//! `insertion_sort_shift_left` and `small_sort_network`.
//! Written from the std source and the Kani documentation only (EXPERIMENT.md, rule R1).

use super::super::{UnstableSmallSortFreezeTypeImpl, swap_if_less};
use super::merge::{lt_i32, lt_u8, lt_u64};
use crate::kani;

// Comparators: K1-merge's `lt_u8`/`lt_i32`/`lt_u64`, strict orders by the key `x >> 1`, so equal keys
// with different full values exist and permutation is not implied by sortedness. Function items
// shared with K1-merge's proofs, so that every `stub_verified` use (here and of
// `bidirectional_merge`) has the same `(T, F)` as the `proof_for_contract` that verifies it.

// ---------------------------------------------------------------------------------------------
// swap_if_less

/// Positions anywhere in a 4-element array, in either order, distinct as the contract requires.
fn check_swap_if_less<T: kani::Arbitrary + Copy, F: FnMut(&T, &T) -> bool>(mut cmp: F) {
    let mut v: [T; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    kani::cover(a == 0 && b == 3, "swap_if_less: a < b reachable");
    kani::cover(a == 3 && b == 0, "swap_if_less: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut cmp) };
    kani::cover(cmp(&old_b, &old_a), "swap_if_less: swap taken");
    kani::cover(!cmp(&old_b, &old_a), "swap_if_less: swap not taken");
    kani::cover(true, "swap_if_less: end reached");
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_u8() {
    check_swap_if_less::<u8, _>(lt_u8);
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_i32() {
    check_swap_if_less::<i32, _>(lt_i32);
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_u64() {
    check_swap_if_less::<u64, _>(lt_u64);
}

/// R11 control: under `stub_verified`, a call that breaks `requires(a_pos != b_pos)` must be
/// reported as a failed precondition. Nothing else in this call can fail: the positions are
/// in-bounds and the postcondition is satisfiable.
#[kani::proof]
#[kani::stub_verified(super::super::swap_if_less)]
fn r11_control_swap_if_less_requires() {
    let mut v: [u8; 2] = kani::any();
    // SAFETY: deliberately breaks the contract precondition `a_pos != b_pos`; position 1 is
    // in-bounds, so the real body would be memory safe.
    unsafe { swap_if_less(v.as_mut_ptr(), 1, 1, &mut lt_u8) };
    kani::cover(true, "r11 control: end reached");
}

// ---------------------------------------------------------------------------------------------
// Harness-level checks: sortedness by `lt` and permutation by full-value equality.

fn count<T: PartialEq>(s: &[T], x: &T) -> usize {
    let mut n = 0;
    let mut i = 0;
    while i < s.len() {
        if s[i] == *x {
            n += 1;
        }
        i += 1;
    }
    n
}

fn sorted_permutation<T: PartialEq, F: FnMut(&T, &T) -> bool>(
    pre: &[T],
    cur: &[T],
    cmp: &mut F,
) -> bool {
    let mut ok = pre.len() == cur.len();
    let mut i = 0;
    while ok && i < pre.len() {
        ok = count(pre, &pre[i]) == count(cur, &pre[i]) && (i == 0 || !cmp(&cur[i], &cur[i - 1]));
        i += 1;
    }
    ok
}

/// `a[from..] == b[from..]` element by element (slice `==` would become a byte loop of `memcmp`).
fn same_from<T: PartialEq>(a: &[T], b: &[T], from: usize) -> bool {
    let mut i = from;
    while i < a.len() {
        if a[i] != b[i] {
            return false;
        }
        i += 1;
    }
    a.len() == b.len()
}

// ---------------------------------------------------------------------------------------------
// sort9_optimal, sort13_optimal: the real network bodies over `stub_verified(swap_if_less)`.

/// Every slice length the contract admits (`n..=17`), so "only `v[..n]` changes" is exercised.
macro_rules! check_sort_n {
    ($name:ident, $f:ident, $n:literal, $t:ty, $cmp:ident) => {
        #[kani::proof_for_contract(super::super::$f)]
        #[kani::stub_verified(super::super::swap_if_less)]
        #[kani::unwind(18)]
        fn $name() {
            let mut v: [$t; 17] = kani::any();
            let len: usize = kani::any_where(|&l| $n <= l && l <= 17);
            kani::cover(len == $n, "exact length reachable");
            kani::cover(len == 17, "longest slice reachable");
            let pre = v;
            let mut cmp = $cmp;
            super::super::$f(&mut v[..len], &mut cmp);
            assert!(sorted_permutation(&pre[..$n], &v[..$n], &mut cmp));
            assert!(same_from(&v, &pre, $n));
            kani::cover(true, "end reached");
        }
    };
}

check_sort_n!(sort9_u8, sort9_optimal, 9, u8, lt_u8);
check_sort_n!(sort9_i32, sort9_optimal, 9, i32, lt_i32);
check_sort_n!(sort9_u64, sort9_optimal, 9, u64, lt_u64);
check_sort_n!(sort13_u8, sort13_optimal, 13, u8, lt_u8);
check_sort_n!(sort13_i32, sort13_optimal, 13, i32, lt_i32);
check_sort_n!(sort13_u64, sort13_optimal, 13, u64, lt_u64);

// ---------------------------------------------------------------------------------------------
// insertion_sort_shift_left on the network regions: `offset` 1 for `len < 9`, 9 for
// `9 <= len < 13`, 13 for `13 <= len <= 17` (EXPERIMENT.md TASK-network step 3). Real body,
// including the real `insert_tail`.

macro_rules! check_insertion {
    ($name:ident, $t:ty, $cmp:ident, $offset:literal, $lo:literal, $hi:literal) => {
        #[kani::proof_for_contract(super::super::insertion_sort_shift_left)]
        #[kani::unwind(18)]
        fn $name() {
            let mut v: [$t; $hi] = kani::any();
            let len: usize = kani::any_where(|&l| $lo <= l && l <= $hi);
            kani::cover(len == $lo, "shortest region reachable");
            kani::cover(len == $hi, "longest region reachable");
            super::super::insertion_sort_shift_left(&mut v[..len], $offset, &mut $cmp);
            kani::cover(true, "end reached");
        }
    };
}

check_insertion!(insertion_o1_u8, u8, lt_u8, 1, 2, 8);
check_insertion!(insertion_o9_u8, u8, lt_u8, 9, 9, 12);
check_insertion!(insertion_o13_u8, u8, lt_u8, 13, 13, 17);
check_insertion!(insertion_o1_i32, i32, lt_i32, 1, 2, 8);
check_insertion!(insertion_o9_i32, i32, lt_i32, 9, 9, 12);
check_insertion!(insertion_o13_i32, i32, lt_i32, 13, 13, 17);
check_insertion!(insertion_o1_u64, u64, lt_u64, 1, 2, 8);
check_insertion!(insertion_o9_u64, u64, lt_u64, 9, 9, 12);
check_insertion!(insertion_o13_u64, u64, lt_u64, 13, 13, 17);

// ---------------------------------------------------------------------------------------------
// Top level, lengths 0..=17 (no merge): the real trait entrypoint and `small_sort_network` body
// over the verified contracts of the networks and of the insertion sort.

macro_rules! check_network_no_merge {
    ($name:ident, $t:ty, $cmp:ident) => {
        #[kani::proof]
        #[kani::stub_verified(super::super::sort9_optimal)]
        #[kani::stub_verified(super::super::sort13_optimal)]
        #[kani::stub_verified(super::super::insertion_sort_shift_left)]
        #[kani::unwind(18)]
        fn $name() {
            let mut v: [$t; 17] = kani::any();
            let len: usize = kani::any_where(|&l| l <= 17);
            kani::cover(len == 0, "len 0 reachable");
            kani::cover(len == 1, "len 1 reachable");
            kani::cover(len == 2, "len 2 reachable");
            kani::cover(len == 9, "len 9 (sort9) reachable");
            kani::cover(len == 13, "len 13 (sort13) reachable");
            kani::cover(len == 17, "len 17 (last without merge) reachable");
            let pre = v;
            let mut cmp = $cmp;
            <$t as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..len], &mut cmp);
            assert!(sorted_permutation(&pre[..len], &v[..len], &mut cmp));
            assert!(same_from(&v, &pre, len));
            kani::cover(true, "end reached");
        }
    };
}

check_network_no_merge!(network_upto17_u8, u8, lt_u8);
check_network_no_merge!(network_upto17_i32, i32, lt_i32);
check_network_no_merge!(network_upto17_u64, u64, lt_u64);
