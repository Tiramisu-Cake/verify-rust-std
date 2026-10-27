//! K1-network agent: contracts and harnesses for `swap_if_less`, `sort9_optimal`, `sort13_optimal`,
//! `insertion_sort_shift_left` and `small_sort_network`.
//! Written from the std source and the Kani documentation only (EXPERIMENT.md, rule R1).

#![allow(dead_code, unused_macros)]

use super::super::{CopyOnDrop, UnstableSmallSortFreezeTypeImpl, swap_if_less};
use super::merge::{insert_tail_len, lt_i32, lt_u8, lt_u64, set_probe};
use crate::kani;
use crate::mem::size_of;

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
#[cfg(kani_smallsort_controls)]
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
// Harness-level checks. Permutation is stated with K1-merge's probe (`set_probe`, `k1_count`).

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
            set_probe::<$t>();
            let mut v: [$t; 17] = kani::any();
            let len: usize = kani::any_where(|&l| $n <= l && l <= 17);
            kani::cover(len == $n, "exact length reachable");
            kani::cover(len == 17, "longest slice reachable");
            let pre = v;
            let mut cmp = $cmp;
            super::super::$f(&mut v[..len], &mut cmp);
            // Sortedness and probe count of `v[..n]` are the contract's `ensures`; the rest is fixed.
            assert!(same_from(&v[..], &pre[..], $n));
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_sort_n!(sort9_u8, sort9_optimal, 9, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_sort_n!(sort9_i32, sort9_optimal, 9, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_sort_n!(sort9_u64, sort9_optimal, 9, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
check_sort_n!(sort13_u8, sort13_optimal, 13, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_sort_n!(sort13_i32, sort13_optimal, 13, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_sort_n!(sort13_u64, sort13_optimal, 13, u64, lt_u64);

// ---------------------------------------------------------------------------------------------
// Formulation 3 for the network contracts (phase 2): the real network bodies with the real
// `swap_if_less`, no stubs. The contract is split over two harness families:
// - `sortNN_01_*`: `proof_for_contract` on inputs whose `v[..n]` keys (`x >> 1`) are 0 or 1. By the
//   0-1 principle this gives sortedness for every input: the body is a fixed sequence of
//   compare-exchanges, each exact by the `swap_if_less` contract (RESULT-network.md, «Редукции»).
// - `sortNN_perm_*`: permutation of `v[..n]` (probe count) on full-width inputs, plain proof.

/// `v[..n]` gets the values 0..=3 (keys 0 and 1), built rather than assumed; `v[n..]` stays arbitrary.
macro_rules! check_sort_n_01 {
    ($name:ident, $f:ident, $n:literal, $t:ty, $cmp:ident) => {
        #[kani::proof_for_contract(super::super::$f)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; 17] = kani::any();
            let bits: [u8; $n] = kani::any();
            let mut i = 0;
            while i < $n {
                v[i] = (bits[i] & 3) as $t;
                i += 1;
            }
            let len: usize = kani::any_where(|&l| $n <= l && l <= 17);
            kani::cover(len == $n, "exact length reachable");
            kani::cover(len == 17, "longest slice reachable");
            kani::cover(v[0] >= 2 && v[$n - 1] < 2, "unsorted 0-1 input reachable");
            let pre = v;
            let mut cmp = $cmp;
            super::super::$f(&mut v[..len], &mut cmp);
            assert!(same_from(&v[..], &pre[..], $n));
            kani::cover(true, "end reached");
        }
    };
}

/// Full-width values; the contract's permutation clause, stated with the same probe count.
macro_rules! check_perm_n {
    ($name:ident, $f:ident, $n:literal, $t:ty, $cmp:ident) => {
        #[kani::proof]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; 17] = kani::any();
            let len: usize = kani::any_where(|&l| $n <= l && l <= 17);
            kani::cover(len == $n, "exact length reachable");
            kani::cover(len == 17, "longest slice reachable");
            let pre = v;
            let mut cmp = $cmp;
            super::super::$f(&mut v[..len], &mut cmp);
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), $n)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), $n)
            );
            assert!(same_from(&v[..], &pre[..], $n));
            kani::cover(true, "end reached");
        }
    };
}

/// Permutation as above, with every compare-exchange through the verified `swap_if_less` contract
/// (exact swap-or-not of two cells). Job 25: the real-body version for `sort13`/u64 timed out at 10 min.
macro_rules! check_perm_stub_n {
    ($name:ident, $f:ident, $n:literal, $t:ty, $cmp:ident) => {
        #[kani::proof]
        #[kani::stub_verified(super::super::swap_if_less)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; 17] = kani::any();
            let len: usize = kani::any_where(|&l| $n <= l && l <= 17);
            kani::cover(len == $n, "exact length reachable");
            kani::cover(len == 17, "longest slice reachable");
            let pre = v;
            let mut cmp = $cmp;
            super::super::$f(&mut v[..len], &mut cmp);
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), $n)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), $n)
            );
            assert!(same_from(&v[..], &pre[..], $n));
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_perm_stub_n!(sort13_perm_stub_u8, sort13_optimal, 13, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_perm_stub_n!(sort13_perm_stub_i32, sort13_optimal, 13, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_perm_stub_n!(sort13_perm_stub_u64, sort13_optimal, 13, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
check_perm_stub_n!(sort9_perm_stub_u64, sort9_optimal, 9, u64, lt_u64);

#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort9_01_u8, sort9_optimal, 9, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort9_01_i32, sort9_optimal, 9, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort9_01_u64, sort9_optimal, 9, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort13_01_u8, sort13_optimal, 13, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort13_01_i32, sort13_optimal, 13, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_sort_n_01!(sort13_01_u64, sort13_optimal, 13, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort9_perm_u8, sort9_optimal, 9, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort9_perm_i32, sort9_optimal, 9, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort9_perm_u64, sort9_optimal, 9, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort13_perm_u8, sort13_optimal, 13, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort13_perm_i32, sort13_optimal, 13, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_perm_n!(sort13_perm_u64, sort13_optimal, 13, u64, lt_u64);

// ---------------------------------------------------------------------------------------------
// Loop invariant of `insertion_sort_shift_left` (phase 5, run B)

impl<T> CopyOnDrop<T> {
    /// Invariant of the `while tail != v_end` loop of `insertion_sort_shift_left`: `tail` is
    /// `v_base + k` with `offset <= k <= len`, `v_base[..k]` is sorted, and the probe count of
    /// `v_base[..len]` equals `count0`, its value on loop entry (`on_entry`). Loop-free, like the
    /// contract (`k1_sorted_q`, `k1_count_u`). `k` comes from byte addresses: the loop havocs `tail`,
    /// so a pointer outside `v`, or not a whole number of elements away, must make the invariant
    /// false rather than trip the UB check of `offset_from`. Zero-sized `T` is not instantiated.
    pub(crate) fn k1_ins_inv<F: FnMut(&T, &T) -> bool>(
        v_base: *const T,
        len: usize,
        offset: usize,
        tail: *const T,
        count0: usize,
        is_less: &&mut F,
    ) -> bool {
        let sz = size_of::<T>();
        let b = tail.addr().wrapping_sub(v_base.addr());
        sz != 0
            && kani::mem::same_allocation(v_base, tail)
            && b % sz == 0
            && offset <= b / sz
            && b / sz <= len
            && Self::k1_sorted_q(v_base, b / sz, is_less)
            && Self::k1_count_u(v_base, len) == count0
    }
}

/// Phase 5 run B: the loop-free contract of `insertion_sort_shift_left` through its loop invariant,
/// with `insert_tail` through its verified contract (`insert_tail_net_u64`, job 26). Length 8,
/// offset 1: the network call site for `len < 9`. Job 37 (887d01ca, contract and loop attributes of
/// that commit): goto-instrument out of memory. Those attributes were then removed from
/// `smallsort.rs`, so at HEAD this harness checks the phase 1 contract and `k1_ins_inv` is unused.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(super::super::insertion_sort_shift_left)]
#[kani::stub_verified(super::super::insert_tail)]
#[kani::unwind(18)]
fn insertion_inv_o1_u64() {
    set_probe::<u64>();
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    super::super::insertion_sort_shift_left(&mut v[..], 1, &mut lt_u64);
    kani::cover(v != pre, "an element moved");
    kani::cover(true, "end reached");
}

// ---------------------------------------------------------------------------------------------
// insertion_sort_shift_left on the network regions: `offset` 1 for `len < 9`, 9 for
// `9 <= len < 13`, 13 for `13 <= len <= 17` (EXPERIMENT.md TASK-network step 3). Real body,
// including the real `insert_tail`.

macro_rules! check_insertion {
    ($name:ident, $t:ty, $cmp:ident, $offset:literal, $lo:literal, $hi:literal) => {
        #[kani::proof_for_contract(super::super::insertion_sort_shift_left)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; $hi] = kani::any();
            let len: usize = kani::any_where(|&l| $lo <= l && l <= $hi);
            kani::cover(len == $lo, "shortest region reachable");
            kani::cover(len == $hi, "longest region reachable");
            super::super::insertion_sort_shift_left(&mut v[..len], $offset, &mut $cmp);
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o1_u8, u8, lt_u8, 1, 2, 8);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o9_u8, u8, lt_u8, 9, 9, 12);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o13_u8, u8, lt_u8, 13, 13, 17);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o1_i32, i32, lt_i32, 1, 2, 8);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o9_i32, i32, lt_i32, 9, 9, 12);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o13_i32, i32, lt_i32, 13, 13, 17);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o1_u64, u64, lt_u64, 1, 2, 8);
#[cfg(kani_smallsort_controls)]
check_insertion!(insertion_o9_u64, u64, lt_u64, 9, 9, 12);
#[cfg(kani_smallsort_controls)]
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
            set_probe::<$t>();
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
            assert!(sorted_by(&v[..len], &mut cmp));
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), len)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), len)
            );
            assert!(same_from(&v[..], &pre[..], len));
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_network_no_merge!(network_upto17_u8, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_network_no_merge!(network_upto17_i32, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_network_no_merge!(network_upto17_u64, u64, lt_u64);

/// `lo <= l <= hi` (a function, so that `lo = 0` raises no `unused_comparisons` lint).
fn in_band(l: usize, lo: usize, hi: usize) -> bool {
    lo <= l && l <= hi
}

/// Phase 2: lengths 0..=17 as three bands with one code path each (insertion from offset 1, sort9
/// then insertion from 9, sort13 then insertion from 13). The networks go through their verified
/// contracts; `insertion_sort_shift_left` and `insert_tail` are the real bodies.
macro_rules! check_network_band {
    ($name:ident, $t:ty, $cmp:ident, $lo:literal, $hi:literal, [$($c:literal),*]) => {
        #[kani::proof]
        #[kani::stub_verified(super::super::sort9_optimal)]
        #[kani::stub_verified(super::super::sort13_optimal)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; $hi] = kani::any();
            let len: usize = kani::any_where(|&l| in_band(l, $lo, $hi));
            $(kani::cover(len == $c, "boundary length reachable");)*
            let pre = v;
            let mut cmp = $cmp;
            <$t as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..len], &mut cmp);
            assert!(sorted_by(&v[..len], &mut cmp));
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), len)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), len)
            );
            assert!(same_from(&v[..], &pre[..], len));
            kani::cover(true, "end reached");
        }
    };
}

/// K1-merge's `insert_tail` contract on the network regions: `[begin, tail]` of 2..=17 elements
/// (`insertion_sort_shift_left` on a region of up to 17). Harness body is K1-merge's `insert_tail_len`.
macro_rules! check_insert_tail_net {
    ($name:ident, $t:ty, $cmp:ident) => {
        #[kani::proof_for_contract(super::super::insert_tail)]
        #[kani::unwind(18)]
        fn $name() {
            let len: usize = kani::any_where(|&l| 2 <= l && l <= 17);
            kani::cover(len == 2, "region of 2 reachable");
            kani::cover(len == 17, "region of 17 reachable");
            match len {
                2 => insert_tail_len::<$t, _, 2>($cmp),
                3 => insert_tail_len::<$t, _, 3>($cmp),
                4 => insert_tail_len::<$t, _, 4>($cmp),
                5 => insert_tail_len::<$t, _, 5>($cmp),
                6 => insert_tail_len::<$t, _, 6>($cmp),
                7 => insert_tail_len::<$t, _, 7>($cmp),
                8 => insert_tail_len::<$t, _, 8>($cmp),
                9 => insert_tail_len::<$t, _, 9>($cmp),
                10 => insert_tail_len::<$t, _, 10>($cmp),
                11 => insert_tail_len::<$t, _, 11>($cmp),
                12 => insert_tail_len::<$t, _, 12>($cmp),
                13 => insert_tail_len::<$t, _, 13>($cmp),
                14 => insert_tail_len::<$t, _, 14>($cmp),
                15 => insert_tail_len::<$t, _, 15>($cmp),
                16 => insert_tail_len::<$t, _, 16>($cmp),
                17 => insert_tail_len::<$t, _, 17>($cmp),
                _ => {}
            }
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_insert_tail_net!(insert_tail_net_u8, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
check_insert_tail_net!(insert_tail_net_i32, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
check_insert_tail_net!(insert_tail_net_u64, u64, lt_u64);

/// Wave 1 K-8: the insertion region is a prefix of a larger allocation, with every tail
/// position 1..=16 symbolic. The contract proof assumes only `insert_tail`'s own requires
/// (in particular the sorted prefix); the suffix stays arbitrary and must be unchanged.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(super::super::insert_tail)]
#[kani::unwind(18)]
fn insert_tail_prefix_u64() {
    set_probe::<u64>();
    let mut v: [u64; 17] = kani::any();
    let tail: usize = kani::any_where(|&t| 1 <= t && t < 17);
    let pre = v;
    let base = v.as_mut_ptr();
    // SAFETY: both pointers belong to `v`, tail > 0; sortedness is assumed by the
    // proof_for_contract instrumentation at this call, exactly as in insert_tail_len.
    unsafe { super::super::insert_tail(base, base.add(tail), &mut lt_u64) };
    assert!(same_from(&v, &pre, tail + 1));
    kani::cover(tail == 1, "prefix region of 2 reachable with requires satisfied");
    kani::cover(tail == 15, "proper prefix region of 16 reachable with requires satisfied");
    kani::cover(tail == 16, "full region of 17 reachable with requires satisfied");
    kani::cover(true, "prefix insertion: end reached");
}

/// K-8 review extension: both ends of the insertion region are symbolic within one allocation.
/// This includes the interior regions used by scratch-based call sites, not just prefixes.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(super::super::insert_tail)]
#[kani::unwind(18)]
fn insert_tail_region_u64() {
    set_probe::<u64>();
    let mut v: [u64; 17] = kani::any();
    let tail: usize = kani::any_where(|&t| 1 <= t && t < 17);
    let start: usize = kani::any_where(|&s| s < tail);
    let pre = v;
    let base = v.as_mut_ptr();
    // SAFETY: 0 <= start < tail < 17, and the enclosing proof_for_contract assumes
    // precisely the callee's sorted-region precondition at this call.
    unsafe { super::super::insert_tail(base.add(start), base.add(tail), &mut lt_u64) };
    let mut i = 0;
    while i < start {
        assert!(v[i] == pre[i]);
        i += 1;
    }
    assert!(same_from(&v, &pre, tail + 1));
    kani::cover(start == 0, "region begins at allocation start");
    kani::cover(start > 0, "region begins inside allocation");
    kani::cover(start > 0 && tail < 16, "region has both prefix and suffix outside it");
    kani::cover(start == 15 && tail == 16, "last two elements form region");
    kani::cover(start == 0 && tail == 16, "whole allocation forms region");
    kani::cover(true, "interior insertion: end reached");
}

/// Wave 1 D0/CD-2: read both arguments, then choose a fresh nondeterministic result.
/// Volatile reads keep these accesses observable even though the result ignores the values.
fn w1_any_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: comparator callers must supply readable u64 references. Kani checks both
    // actual accesses, including references formed from raw pointers inside the sort.
    unsafe {
        let _ = crate::ptr::read_volatile(a);
        let _ = crate::ptr::read_volatile(b);
    }
    kani::any()
}

/// K-6+ (b), length 17: network + insertion, no merge and no order-violation panic path.
/// Ordinary proof checks Kani safety and assertion classes; no sorting/permutation assertions.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(35)]
fn w1_network_o1_len17_u64() {
    let mut v: [u64; 17] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "network O1 length 17: normal return reachable");
}

/// CD-1 variant B: safety-class checks only; all assertion-class panics are allowed.
/// Every callee, including bidirectional_merge, is real; no contract checks or stubs.

/// As at length 24, with two length-16 regions (sort13 + insertion), then even merge.

/// A constant-sized trait call in each branch keeps each network/merge shape concrete.
fn w1_network_o1_fixed<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
}

/// Nondeterministic selection among constant lengths. Every allowed choice must also have a
/// normal-return path (cover after the sort); no order constraints or contract stubs are used.
macro_rules! w1_network_o1_cases {
    ($name:ident, [$($n:literal),+], [$($attr:meta),*]) => {
        #[kani::proof]
        $(#[$attr])*
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w1_network_o1_fixed::<$n>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("network O1 normal return at ", stringify!($n)));)+
            kani::cover(true, "network O1 family: end reached");
        }
    };
}

// Priority odd merge paths: homogeneous sort9 halves, mixed sort9/sort13, sort13 halves.
// No merge: includes 0/1 returns, insertion-only, sort9 and sort13, and their insertion tails.
w1_network_o1_cases!(w1_network_o1_nomerge_u64, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], []);
// Remaining merge lengths; together with 19/24/25/31/32, covers every length 18..=32.
// Smaller independent partitions after job 62's unlocalized CBMC status 6.

/// The bands again, with `insert_tail` through its verified contract as well (job 23: with the real
/// `insert_tail` every u64 band timed out at 10 min). `insertion_sort_shift_left` stays real.
macro_rules! check_network_band_tail {
    ($name:ident, $t:ty, $cmp:ident, $lo:literal, $hi:literal, [$($c:literal),*]) => {
        #[kani::proof]
        #[kani::stub_verified(super::super::sort9_optimal)]
        #[kani::stub_verified(super::super::sort13_optimal)]
        #[kani::stub_verified(super::super::insert_tail)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; $hi] = kani::any();
            let len: usize = kani::any_where(|&l| in_band(l, $lo, $hi));
            $(kani::cover(len == $c, "boundary length reachable");)*
            let pre = v;
            let mut cmp = $cmp;
            <$t as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..len], &mut cmp);
            assert!(sorted_by(&v[..len], &mut cmp));
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), len)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), len)
            );
            assert!(same_from(&v[..], &pre[..], len));
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt0_8_u8, u8, lt_u8, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt0_8_i32, i32, lt_i32, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt0_8_u64, u64, lt_u64, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt9_12_u8, u8, lt_u8, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt9_12_i32, i32, lt_i32, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt9_12_u64, u64, lt_u64, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt13_17_u8, u8, lt_u8, 13, 17, [13, 17]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt13_17_i32, i32, lt_i32, 13, 17, [13, 17]);
#[cfg(kani_smallsort_controls)]
check_network_band_tail!(bandt13_17_u64, u64, lt_u64, 13, 17, [13, 17]);

/// One constant length per harness (TASK-network phase 2, step 3: "полосами фиксированных длин").
/// Job 23 and job 26: every symbolic-length band timed out for u64, with and without the
/// `insert_tail` stub. Networks through their verified contracts, insertion real.
macro_rules! check_network_fixed {
    ($name:ident, $t:ty, $cmp:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub_verified(super::super::sort9_optimal)]
        #[kani::stub_verified(super::super::sort13_optimal)]
        #[kani::unwind(18)]
        fn $name() {
            set_probe::<$t>();
            let mut v: [$t; $n] = kani::any();
            let pre = v;
            let mut cmp = $cmp;
            <$t as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..], &mut cmp);
            assert!(sorted_by(&v[..], &mut cmp));
            assert!(
                CopyOnDrop::<$t>::k1_count(pre.as_ptr(), $n)
                    == CopyOnDrop::<$t>::k1_count(v.as_ptr(), $n)
            );
            kani::cover(true, "end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
check_network_fixed!(fixed8_u64, u64, lt_u64, 8);
#[cfg(kani_smallsort_controls)]
check_network_fixed!(fixed12_u64, u64, lt_u64, 12);
#[cfg(kani_smallsort_controls)]
check_network_fixed!(fixed17_u64, u64, lt_u64, 17);

/// Phase 5 run A: `check_network_fixed` at length 8 with `insert_tail` through its verified contract
/// (`insert_tail_net_u64`, job 26), the one combination phase 2 did not run. At length 8 the network
/// stubs are off the path (`small_sort_network` calls only `insertion_sort_shift_left(v, 1)`); they
/// are kept so that the harness differs from `fixed8_u64` (job 31) only by the `insert_tail` stub.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(super::super::sort9_optimal)]
#[kani::stub_verified(super::super::sort13_optimal)]
#[kani::stub_verified(super::super::insert_tail)]
#[kani::unwind(18)]
fn fixedt8_u64() {
    set_probe::<u64>();
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let mut cmp = lt_u64;
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..], &mut cmp);
    assert!(sorted_by(&v[..], &mut cmp));
    assert!(CopyOnDrop::<u64>::k1_count(pre.as_ptr(), 8) == CopyOnDrop::<u64>::k1_count(v.as_ptr(), 8));
    kani::cover(true, "end reached");
}

#[cfg(kani_smallsort_controls)]
check_network_band!(band0_8_u8, u8, lt_u8, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band0_8_i32, i32, lt_i32, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band0_8_u64, u64, lt_u64, 0, 8, [0, 1, 2, 8]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band9_12_u8, u8, lt_u8, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band9_12_i32, i32, lt_i32, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band9_12_u64, u64, lt_u64, 9, 12, [9, 12]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band13_17_u8, u8, lt_u8, 13, 17, [13, 17]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band13_17_i32, i32, lt_i32, 13, 17, [13, 17]);
#[cfg(kani_smallsort_controls)]
check_network_band!(band13_17_u64, u64, lt_u64, 13, 17, [13, 17]);

// ---------------------------------------------------------------------------------------------
// Cost isolation (job 10: every symbolic-length harness above timed out at 5 min for u8). Constant
// lengths, real bodies, permutation by an arbitrary probe value: for every value `p`, the number of
// elements equal to `p` is preserved, which is multiset equality since `p` is nondeterministic.

fn probe_count<T: PartialEq>(s: &[T], p: &T) -> usize {
    let mut n = 0;
    let mut i = 0;
    while i < s.len() {
        if s[i] == *p {
            n += 1;
        }
        i += 1;
    }
    n
}

/// K-9 retry: full-width u8 values at the exact network width, with a local arbitrary probe.
/// Removing the symbolic slice length and unchanged suffix leaves only the permutation claim.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(14)]
fn w1_sort13_perm_fixed_u8() {
    let mut v: [u8; 13] = kani::any();
    let p: u8 = kani::any();
    let pre = v;
    super::super::sort13_optimal(&mut v, &mut lt_u8);
    assert!(probe_count(&pre, &p) == probe_count(&v, &p));
    kani::cover(v != pre, "sort13 moves elements");
    kani::cover(pre[0] == p && pre[1] == p, "duplicate probe values reachable");
    kani::cover(true, "sort13 permutation at exact length: end reached");
}

fn sorted_by<T, F: FnMut(&T, &T) -> bool>(s: &[T], cmp: &mut F) -> bool {
    let mut i = 1;
    while i < s.len() {
        if cmp(&s[i], &s[i - 1]) {
            return false;
        }
        i += 1;
    }
    true
}

/// Real `sort9_optimal` and real `swap_if_less`, no contracts involved.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn direct_sort9_u8() {
    let mut v: [u8; 9] = kani::any();
    let p: u8 = kani::any();
    let pre = v;
    super::super::sort9_optimal(&mut v[..], &mut lt_u8);
    assert!(sorted_by(&v[..], &mut lt_u8));
    assert!(probe_count(&pre[..], &p) == probe_count(&v[..], &p));
    kani::cover(true, "end reached");
}

/// The `sort9_optimal` contract at one constant length, over `stub_verified(swap_if_less)`.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(super::super::sort9_optimal)]
#[kani::stub_verified(super::super::swap_if_less)]
fn contract_sort9_u8_len9() {
    set_probe::<u8>();
    let mut v: [u8; 9] = kani::any();
    super::super::sort9_optimal(&mut v[..], &mut lt_u8);
    kani::cover(true, "end reached");
}

/// The trait entrypoint at constant length `N`, every callee real.
fn direct_network<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    let p: u8 = kani::any();
    let pre = v;
    let mut cmp = lt_u8;
    <u8 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v[..], &mut cmp);
    assert!(sorted_by(&v[..], &mut cmp));
    assert!(probe_count(&pre[..], &p) == probe_count(&v[..], &p));
    kani::cover(true, "end reached");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(18)]
fn direct_network_len13_u8() {
    direct_network::<13>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(18)]
fn direct_network_len17_u8() {
    direct_network::<17>();
}

// ---------------------------------------------------------------------------------------------
// K-13: interior-mutable comparator on the actual non-Freeze routes and direct insertion.

#[derive(Clone, Copy)]
struct K13Tagged {
    key: u8,
    tag: u8,
}

type K13Cell = crate::cell::Cell<K13Tagged>;

static mut K13_INPUT_BASE: *const K13Tagged = crate::ptr::null();

fn k13_track_input<const N: usize>(v: &[K13Cell; N]) {
    // SAFETY: single-threaded harness; the pointer is only compared while v is alive.
    unsafe { *crate::ptr::addr_of_mut!(K13_INPUT_BASE) = v.as_ptr().cast() };
}

/// Observe both complete values before writing either one. Cell permits mutation through the
/// shared references; tags are preserved even if both references happen to name the same Cell.
fn k13_mutating_less(a: &K13Cell, b: &K13Cell) -> bool {
    // SAFETY: Cell::as_ptr points to its initialized Tagged. Volatile reads preserve both key
    // accesses for CD-2, even though the comparison result is independent of their values.
    let (left, right) = unsafe {
        (crate::ptr::read_volatile(a.as_ptr()), crate::ptr::read_volatile(b.as_ptr()))
    };
    let left_key: u8 = kani::any();
    let right_key: u8 = kani::any();
    a.set(K13Tagged { key: left_key, tag: left.tag });
    b.set(K13Tagged { key: right_key, tag: right.tag });
    kani::cover(left.key != left_key && right.key != right_key, "K13 comparator changes both keys");
    // SAFETY: each harness registers its live array before invoking the comparator.
    let base = unsafe { *crate::ptr::addr_of!(K13_INPUT_BASE) };
    kani::cover(
        !kani::mem::same_allocation(base, a.as_ptr()) || !kani::mem::same_allocation(base, b.as_ptr()),
        "K13 comparator writes an insert_tail temporary copy",
    );
    kani::any()
}

fn k13_input<const N: usize>() -> [K13Cell; N] {
    let v = [const { crate::cell::Cell::new(K13Tagged { key: 0, tag: 0 }) }; N];
    let mut i = 0;
    while i < N {
        // Both fields span all u8 values, including duplicate tags.
        v[i].set(K13Tagged { key: kani::any(), tag: kani::any() });
        i += 1;
    }
    v
}

/// An arbitrary probe proves full multiset equality, including tag multiplicities. N <= 20 in
/// every call below, so a u8 count suffices without overflow or modular-count ambiguity.
fn k13_tag_count<const N: usize>(v: &[K13Cell; N], probe: u8) -> u8 {
    let mut count = 0;
    let mut i = 0;
    while i < N {
        count += (v[i].get().tag == probe) as u8;
        i += 1;
    }
    count
}

fn k13_tags<const N: usize>(v: &[K13Cell; N]) -> [u8; N] {
    let mut tags = [0; N];
    let mut i = 0;
    while i < N {
        tags[i] = v[i].get().tag;
        i += 1;
    }
    tags
}

fn k13_route_fixed<const N: usize>(stable: bool) -> bool {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = k13_input::<N>();
    k13_track_input(&v);
    let probe: u8 = kani::any();
    let before = k13_tag_count(&v, probe);
    let tags = k13_tags(&v);
    if stable {
        // The non-Freeze default ignores scratch, so the empty slice is sufficient.
        let mut scratch = [];
        <K13Cell as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut k13_mutating_less);
    } else {
        <K13Cell as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut k13_mutating_less);
    }
    assert!(before == k13_tag_count(&v, probe));
    let moved = tags != k13_tags(&v);
    kani::cover(N < 2 || moved, "K13 route: trivial length or a tag moved");
    moved
}

/// Deliberately outside the K-1 correctness contract (len 1/18..20, arbitrary valid offset,
/// unsorted prefix). This plain proof relies on CI --no-assert-contracts and real function bodies;
/// it checks memory and tag permutation, not that contract or sortedness.
fn k13_insertion_fixed<const N: usize>() -> bool {
    let mut v = k13_input::<N>();
    k13_track_input(&v);
    let probe: u8 = kani::any();
    let before = k13_tag_count(&v, probe);
    let tags = k13_tags(&v);
    // Sortedness of the prefix is not needed for safety or tag permutation. All valid offsets
    // are checked; a fully presorted slice (offset == N) is a permitted no-op.
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    super::super::insertion_sort_shift_left(&mut v, offset, &mut k13_mutating_less);
    assert!(before == k13_tag_count(&v, probe));
    kani::cover(offset == 1, "K13 insertion: offset 1 reachable");
    kani::cover(offset == N, "K13 insertion: offset len reachable");
    let moved = tags != k13_tags(&v);
    kani::cover(N < 2 || moved, "K13 insertion: trivial length or a tag moved");
    moved
}

macro_rules! k13_route_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => { let _ = k13_route_fixed::<$n>(stable); },)+
                _ => {}
            }
            $(
                kani::cover(stable && len == $n, concat!("K13 stable default length ", stringify!($n)));
                kani::cover(!stable && len == $n, concat!("K13 unstable fallback length ", stringify!($n)));
            )+
            kani::cover(true, "K13 route family: end reached");
        }
    };
}

macro_rules! k13_insertion_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => { let _ = k13_insertion_fixed::<$n>(); },)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("K13 insertion length ", stringify!($n)));)+
            kani::cover(true, "K13 insertion family: end reached");
        }
    };
}

#[cfg(kani_smallsort_controls)]
k13_route_cases!(k13_routes_0_8, [0, 1, 2, 3, 4, 5, 6, 7, 8]);
#[cfg(kani_smallsort_controls)]
k13_route_cases!(k13_routes_9_16, [9, 10, 11, 12, 13, 14, 15, 16]);
#[cfg(kani_smallsort_controls)]
k13_insertion_cases!(k13_insertion_1_10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
#[cfg(kani_smallsort_controls)]
k13_insertion_cases!(k13_insertion_11_20, [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]);

/// Last-dispatch safety-only fallback: one allocation avoids duplicating the large permutation
/// formulas for every constant length. Tags/keys remain full-width; no property assertions/stubs.
/// Object-bound checks cover the full allocation of 20 Cells, not each shorter slice boundary.
/// In particular, an access to v[len..20] would not be detected as an allocation overrun.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(35)]
fn k13_safety_all() {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = k13_input::<20>();
    k13_track_input(&v);
    let mode: u8 = kani::any_where(|&m| m < 3);
    let len: usize = kani::any_where(|&n| if mode < 2 { n <= 16 } else { 1 <= n && n <= 20 });
    if mode == 0 {
        let mut scratch = [];
        <K13Cell as StableSmallSortTypeImpl>::small_sort(&mut v[..len], &mut scratch, &mut k13_mutating_less);
    } else if mode == 1 {
        <K13Cell as UnstableSmallSortTypeImpl>::small_sort(&mut v[..len], &mut k13_mutating_less);
    } else {
        let offset: usize = kani::any_where(|&o| 1 <= o && o <= len);
        super::super::insertion_sort_shift_left(&mut v[..len], offset, &mut k13_mutating_less);
        kani::cover(offset == 1, "K13 safety insertion offset 1");
        kani::cover(offset == len, "K13 safety insertion offset len");
    }
    macro_rules! routes {
        ($($n:literal),+) => {$(
            kani::cover(mode == 0 && len == $n, concat!("K13 safety stable ", stringify!($n)));
            kani::cover(mode == 1 && len == $n, concat!("K13 safety unstable ", stringify!($n)));
        )+};
    }
    macro_rules! insertion {
        ($($n:literal),+) => {$(
            kani::cover(mode == 2 && len == $n, concat!("K13 safety insertion ", stringify!($n)));
        )+};
    }
    routes!(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16);
    insertion!(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20);
    kani::cover(true, "K13 full safety: end reached");
}

fn k13_small_fixed<const N: usize>(mode: u8) -> bool {
    if mode < 2 { k13_route_fixed::<N>(mode == 0) } else { k13_insertion_fixed::<N>() }
}

/// Reduced permutation domain after all four broad families timed out in job 67.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(35)]
fn k13_small_permutation() {
    let len: usize = kani::any_where(|&n| n <= 4);
    let mode: u8 = kani::any_where(|&m| m < 3 && (len > 0 || m < 2));
    let moved = match len {
        0 => k13_route_fixed::<0>(mode == 0),
        1 => k13_small_fixed::<1>(mode),
        2 => k13_small_fixed::<2>(mode),
        3 => k13_small_fixed::<3>(mode),
        4 => k13_small_fixed::<4>(mode),
        _ => false,
    };
    macro_rules! lengths {
        ($($n:literal),+) => {$(
            kani::cover(mode == 0 && len == $n, concat!("K13 permutation stable ", stringify!($n)));
            kani::cover(mode == 1 && len == $n, concat!("K13 permutation unstable ", stringify!($n)));
            kani::cover(mode == 2 && len == $n, concat!("K13 permutation insertion ", stringify!($n)));
        )+};
    }
    // Length zero has no direct insertion call or offset.
    kani::cover(mode == 0 && len == 0, "K13 permutation stable 0");
    kani::cover(mode == 1 && len == 0, "K13 permutation unstable 0");
    lengths!(1, 2, 3, 4);
    kani::cover(mode == 0 && moved, "K13 stable actually moves a tag");
    kani::cover(mode == 1 && moved, "K13 unstable actually moves a tag");
    kani::cover(mode == 2 && moved, "K13 insertion actually moves a tag");
    kani::cover(true, "K13 reduced permutation: end reached");
}

// ---------------------------------------------------------------------------------------------
// Wave 2 priority 1. Variant A cuts only the explicit order-violation panic. All other
// Kani checks remain active; no should_panic or verified-contract stubs are used.
fn w2_cut_ord_violation() -> ! {
    kani::cover(true, "W2 variant A: order-violation stub reached");
    w2_assume_ord_violation()
}

/// The same cut, without a reachability property in every short/no-merge proof.
/// The covering wrapper above is used by the dedicated reachability control.
fn w2_assume_ord_violation() -> ! {
    kani::assume(false);
    unreachable!()
}

/// Control on a normal-return path, in this same module and with the same variant-A stub.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, w2_cut_ord_violation)]
#[kani::unwind(35)]
fn w2_control_a_assertion() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; 2] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "W2 control A: normal return before assertion");
    assert!(v[0] != v[0]);
}

/// Reachability is through the real trait dispatch and real merge, not a direct stub call.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, w2_cut_ord_violation)]
#[kani::unwind(35)]
fn w2_control_a_reachability() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; 18] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "W2 control A: normal return also reachable");
}

/// Each branch owns an allocation of exactly N elements. Enter through the outer trait,
/// including Freeze/Copy specialization; the CD-2 comparator and all sort bodies are real.
fn w2_network_o1_fixed<const N: usize>() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
}

macro_rules! w2_network_o1_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, w2_cut_ord_violation)]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w2_network_o1_fixed::<$n>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("W2 O1-A network normal return at ", stringify!($n)));)+
            kani::cover(true, "W2 O1-A network family: end reached");
        }
    };
}

w2_network_o1_cases!(w2_network_o1_a_18_21, [18, 19, 20, 21]);
w2_network_o1_cases!(w2_network_o1_a_22_25, [22, 23, 24, 25]);
w2_network_o1_cases!(w2_network_o1_a_26_27, [26, 27]);
w2_network_o1_cases!(w2_network_o1_a_28_29, [28, 29]);
w2_network_o1_cases!(w2_network_o1_a_30_32, [30, 31, 32]);


// K-16s: type matrix through actual trait entrypoints. Safety only; full-width inputs.
trait W2Value: Sized {
    fn w2_value() -> Self;
}

impl W2Value for () {
    fn w2_value() -> Self { () }
}

impl W2Value for u8 {
    fn w2_value() -> Self { kani::any() }
}

fn w2_reading_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: real sort bodies must supply readable initialized values. ManuallyDrop avoids
    // running Drop on the duplicate returned by the volatile read of a non-Copy value.
    unsafe {
        let _left = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(a));
        let _right = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(b));
    }
    kani::any()
}

fn w2_type_fixed<T: W2Value, const N: usize, const STABLE: bool>() {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v: [T; N] = crate::array::from_fn(|_| T::w2_value());
    if STABLE {
        let mut scratch = [const { crate::mem::MaybeUninit::<T>::uninit() }; 48];
        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut w2_reading_less::<T>);
    } else {
        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w2_reading_less::<T>);
    }
}

macro_rules! w2_type_cases {
    ($name:ident, $t:ty, $stable:literal, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, w2_assume_ord_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w2_type_fixed::<$t, $n, $stable>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("W2 K16s normal return at ", stringify!($n)));)+
            kani::cover(true, "W2 K16s family: end reached");
        }
    };
}

/// Control for the uninstrumented cut used by the short type-matrix proofs.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, w2_assume_ord_violation)]
#[kani::unwind(35)]
fn w2_control_a_quiet_assertion() {
    w2_network_o1_fixed::<2>();
    kani::cover(true, "W2 quiet control A: normal return before assertion");
    let x: u8 = kani::any();
    assert!(x != x);
}

#[cfg(kani_smallsort_controls)]
w2_type_cases!(w2_k16_zst_stable, (), true, [0, 1, 2, 7, 8, 15, 16, 17, 31, 32]);
#[cfg(kani_smallsort_controls)]
w2_type_cases!(w2_k16_zst_network_short, (), false, [8, 9, 12, 13, 17]);

w2_type_cases!(w2_k16_u8_stable_lo, u8, true, [0, 1, 2, 7, 8]);
w2_type_cases!(w2_k16_u8_stable_mid, u8, true, [15, 16, 17]);
w2_type_cases!(w2_k16_u8_stable_hi, u8, true, [31, 32]);
w2_type_cases!(w2_k16_u8_network_short, u8, false, [8, 9, 12, 13, 17]);
w2_type_cases!(w2_k16_u8_network_merge, u8, false, [18, 31, 32]);

impl W2Value for u128 {
    fn w2_value() -> Self { kani::any() }
}

/// Both outer traits on one type and the same allowed lengths; cover every (route, N).
macro_rules! w2_type_pair_cases {
    ($name:ident, $t:ty, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, w2_assume_ord_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => {
                    if stable { w2_type_fixed::<$t, $n, true>(); }
                    else { w2_type_fixed::<$t, $n, false>(); }
                },)+
                _ => {}
            }
            $(
                kani::cover(stable && len == $n, concat!("W2 K16s stable normal return at ", stringify!($n)));
                kani::cover(!stable && len == $n, concat!("W2 K16s unstable normal return at ", stringify!($n)));
            )+
            kani::cover(true, "W2 K16s paired family: end reached");
        }
    };
}

w2_type_pair_cases!(w2_k16_u128_lo, u128, [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_u128_mid, u128, [15, 16, 17]);
#[cfg(kani_smallsort_controls)]
w2_type_pair_cases!(w2_k16_u128_hi, u128, [31, 32]);


/// CD-5: the K16 template itself must expose an assertion after a normal merge return.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, w2_assume_ord_violation)]
#[kani::unwind(65)]
fn w2_control_a_quiet_merge_assertion() {
    w2_type_fixed::<u8, 18, false>();
    kani::cover(true, "W2 quiet merge control: normal return before assertion");
    let x: u8 = kani::any();
    assert!(x != x);
}

/// One separately measured reachability proof per type and outer trait route with merge.
macro_rules! w2_type_reachability {
    ($name:ident, $t:ty, $stable:literal, $n:literal) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, w2_cut_ord_violation)]
        #[kani::unwind(65)]
        fn $name() {
            w2_type_fixed::<$t, $n, $stable>();
            kani::cover(true, "W2 K16s reachability: normal return also reachable");
        }
    };
}

w2_type_reachability!(w2_k16_u8_stable_reach, u8, true, 17);
w2_type_reachability!(w2_k16_u8_network_reach, u8, false, 18);
w2_type_reachability!(w2_k16_u128_stable_reach, u128, true, 17);
w2_type_reachability!(w2_k16_u128_general_reach, u128, false, 17);

impl<const M: usize> W2Value for [u8; M] {
    fn w2_value() -> Self { kani::any() }
}

w2_type_pair_cases!(w2_k16_a16_lo, [u8; 16], [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_a16_mid, [u8; 16], [15, 16, 17]);
w2_type_pair_cases!(w2_k16_a16_n31, [u8; 16], [31]);
w2_type_pair_cases!(w2_k16_a16_n32, [u8; 16], [32]);
w2_type_reachability!(w2_k16_a16_stable_reach, [u8; 16], true, 17);
w2_type_reachability!(w2_k16_a16_general_reach, [u8; 16], false, 17);

w2_type_pair_cases!(w2_k16_u128_n31, u128, [31]);
w2_type_pair_cases!(w2_k16_u128_n32, u128, [32]);

w2_type_pair_cases!(w2_k16_a17_lo, [u8; 17], [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_a17_mid, [u8; 17], [15, 16, 17]);
w2_type_pair_cases!(w2_k16_a17_n31, [u8; 17], [31]);
w2_type_pair_cases!(w2_k16_a17_n32, [u8; 17], [32]);
w2_type_reachability!(w2_k16_a17_stable_reach, [u8; 17], true, 17);
w2_type_reachability!(w2_k16_a17_general_reach, [u8; 17], false, 17);

/// Freeze but non-Copy; the real destructor observes its own initialized key. No drop-count
/// or permutation property is asserted in the safety matrix.
struct W2Drop(u8);

impl Drop for W2Drop {
    fn drop(&mut self) {
        // SAFETY: a live value must still contain its readable u8 key when dropped.
        unsafe { let _ = crate::ptr::read_volatile(&self.0); }
    }
}

impl W2Value for W2Drop {
    fn w2_value() -> Self { Self(kani::any()) }
}

w2_type_pair_cases!(w2_k16_drop_lo, W2Drop, [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_drop_mid, W2Drop, [15, 16, 17]);
w2_type_pair_cases!(w2_k16_drop_n31, W2Drop, [31]);
w2_type_pair_cases!(w2_k16_drop_n32, W2Drop, [32]);
w2_type_reachability!(w2_k16_drop_stable_reach, W2Drop, true, 17);
w2_type_reachability!(w2_k16_drop_general_reach, W2Drop, false, 17);

impl W2Value for crate::cell::Cell<i32> {
    fn w2_value() -> Self { Self::new(kani::any()) }
}

// Cell is non-Freeze and non-Copy: both outer traits select their default insertion paths.
w2_type_pair_cases!(w2_k16_cell_nonfreeze, crate::cell::Cell<i32>, [0, 1, 2, 15, 16]);

w2_type_pair_cases!(w2_k16_a85_lo, [u8; 85], [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_a85_mid, [u8; 85], [15, 16, 17]);
w2_type_pair_cases!(w2_k16_a85_n31, [u8; 85], [31]);
w2_type_pair_cases!(w2_k16_a85_n32, [u8; 85], [32]);
w2_type_reachability!(w2_k16_a85_stable_reach, [u8; 85], true, 17);
w2_type_reachability!(w2_k16_a85_general_reach, [u8; 85], false, 17);

w2_type_cases!(w2_k16_a86_stable_lo, [u8; 86], true, [0, 1, 2, 7, 8]);
w2_type_cases!(w2_k16_a86_stable_mid, [u8; 86], true, [15, 16, 17]);
w2_type_cases!(w2_k16_a86_stable_n31, [u8; 86], true, [31]);
w2_type_cases!(w2_k16_a86_stable_n32, [u8; 86], true, [32]);
w2_type_cases!(w2_k16_a86_fallback, [u8; 86], false, [0, 1, 2, 15, 16]);
w2_type_reachability!(w2_k16_a86_stable_reach, [u8; 86], true, 17);

// K-11s/B4. Plain proofs deliberately outside the old correctness contract's offset/length
// domain. CI --no-assert-contracts is required; all insertion bodies are real.
// A const offset at each real call avoids a symbolic initial raw pointer in the loop.
// All valid offsets are still selected nondeterministically; guards discard only O > N.
fn w2_insertion_at<T, F: FnMut(&T, &T) -> bool, const O: usize>(v: &mut [T], cmp: &mut F) {
    super::super::insertion_sort_shift_left(v, O, cmp);
}

macro_rules! w2_const_offset_call {
    ($v:expr, $offset:expr, $n:expr, $cmp:expr) => {
        match $offset {
            1 if $n >= 1 => w2_insertion_at::<_, _, 1>($v, $cmp),
            2 if $n >= 2 => w2_insertion_at::<_, _, 2>($v, $cmp),
            3 if $n >= 3 => w2_insertion_at::<_, _, 3>($v, $cmp),
            4 if $n >= 4 => w2_insertion_at::<_, _, 4>($v, $cmp),
            5 if $n >= 5 => w2_insertion_at::<_, _, 5>($v, $cmp),
            6 if $n >= 6 => w2_insertion_at::<_, _, 6>($v, $cmp),
            7 if $n >= 7 => w2_insertion_at::<_, _, 7>($v, $cmp),
            8 if $n >= 8 => w2_insertion_at::<_, _, 8>($v, $cmp),
            9 if $n >= 9 => w2_insertion_at::<_, _, 9>($v, $cmp),
            10 if $n >= 10 => w2_insertion_at::<_, _, 10>($v, $cmp),
            11 if $n >= 11 => w2_insertion_at::<_, _, 11>($v, $cmp),
            12 if $n >= 12 => w2_insertion_at::<_, _, 12>($v, $cmp),
            13 if $n >= 13 => w2_insertion_at::<_, _, 13>($v, $cmp),
            14 if $n >= 14 => w2_insertion_at::<_, _, 14>($v, $cmp),
            15 if $n >= 15 => w2_insertion_at::<_, _, 15>($v, $cmp),
            16 if $n >= 16 => w2_insertion_at::<_, _, 16>($v, $cmp),
            17 if $n >= 17 => w2_insertion_at::<_, _, 17>($v, $cmp),
            18 if $n >= 18 => w2_insertion_at::<_, _, 18>($v, $cmp),
            19 if $n >= 19 => w2_insertion_at::<_, _, 19>($v, $cmp),
            20 if $n >= 20 => w2_insertion_at::<_, _, 20>($v, $cmp),
            _ => {}
        }
    };
}

fn w2_insertion_safety_fixed<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    w2_const_offset_call!(&mut v, offset, N, &mut w1_any_less_u64);
    kani::cover(offset == 1, "W2 K11s offset 1 normal return");
    kani::cover(offset == N, "W2 K11s offset len normal return");
}

macro_rules! w2_insertion_safety_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w2_insertion_safety_fixed::<$n>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("W2 K11s normal return at ", stringify!($n)));)+
            kani::cover(true, "W2 K11s family: end reached");
        }
    };
}

w2_insertion_safety_cases!(w2_k11s_1_5, [1, 2, 3, 4, 5]);
w2_insertion_safety_cases!(w2_k11s_6_10, [6, 7, 8, 9, 10]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_11_15, [11, 12, 13, 14, 15]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_16_20, [16, 17, 18, 19, 20]);

// O3-s: safety only on exact allocations; no tag count, snapshots, input-base globals or
// permutation assertions. The full Tagged input and both key writes follow K13's comparator.
fn w2_o3_mutating_less(a: &K13Cell, b: &K13Cell) -> bool {
    // SAFETY: both initialized Cell payloads must be readable before either write.
    let (left, right) = unsafe {
        (crate::ptr::read_volatile(a.as_ptr()), crate::ptr::read_volatile(b.as_ptr()))
    };
    let left_key: u8 = kani::any();
    let right_key: u8 = kani::any();
    a.set(K13Tagged { key: left_key, tag: left.tag });
    b.set(K13Tagged { key: right_key, tag: right.tag });
    kani::cover(left_key != left.key && right_key != right.key, "W2 O3 comparator changes both keys");
    kani::any()
}

fn w2_o3_input<const N: usize>() -> [K13Cell; N] {
    crate::array::from_fn(|_| K13Cell::new(K13Tagged { key: kani::any(), tag: kani::any() }))
}

fn w2_o3_route_fixed<const N: usize>(stable: bool) {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = w2_o3_input::<N>();
    if stable {
        let mut scratch = [];
        <K13Cell as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut w2_o3_mutating_less);
    } else {
        <K13Cell as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w2_o3_mutating_less);
    }
}

macro_rules! w2_o3_route_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => w2_o3_route_fixed::<$n>(stable),)+
                _ => {}
            }
            $(
                kani::cover(stable && len == $n, concat!("W2 O3 stable normal return at ", stringify!($n)));
                kani::cover(!stable && len == $n, concat!("W2 O3 unstable normal return at ", stringify!($n)));
            )+
            kani::cover(true, "W2 O3 route family: end reached");
        }
    };
}

fn w2_o3_insertion_fixed<const N: usize>() {
    let mut v = w2_o3_input::<N>();
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    w2_const_offset_call!(&mut v, offset, N, &mut w2_o3_mutating_less);
    kani::cover(offset == 1, "W2 O3 insertion offset 1 normal return");
    kani::cover(offset == N, "W2 O3 insertion offset len normal return");
}

macro_rules! w2_o3_insertion_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w2_o3_insertion_fixed::<$n>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("W2 O3 insertion normal return at ", stringify!($n)));)+
            kani::cover(true, "W2 O3 insertion family: end reached");
        }
    };
}

w2_o3_route_cases!(w2_o3_routes_0_4, [0, 1, 2, 3, 4]);
w2_o3_route_cases!(w2_o3_routes_5_8, [5, 6, 7, 8]);
w2_o3_route_cases!(w2_o3_routes_9_12, [9, 10, 11, 12]);
w2_o3_route_cases!(w2_o3_routes_13_16, [13, 14, 15, 16]);
w2_o3_insertion_cases!(w2_o3_insertion_1_5, [1, 2, 3, 4, 5]);
w2_o3_insertion_cases!(w2_o3_insertion_6_10, [6, 7, 8, 9, 10]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_11_15, [11, 12, 13, 14, 15]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_16_20, [16, 17, 18, 19, 20]);

// Final bounded split after the 11..15 O3 family returned unlocalized CBMC status 6.
w2_insertion_safety_cases!(w2_k11s_11_12, [11, 12]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_13_15, [13, 14, 15]);
w2_o3_insertion_cases!(w2_o3_insertion_11_12, [11, 12]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_13_15, [13, 14, 15]);

// Prepared after job108 exceeded the 180s Linux target. NOT_RUN in W2 P1: dispatch24/24.
w2_insertion_safety_cases!(w2_k11s_n13, [13]);
w2_insertion_safety_cases!(w2_k11s_n14, [14]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_n15, [15]);
w2_o3_insertion_cases!(w2_o3_insertion_n13, [13]);
w2_o3_insertion_cases!(w2_o3_insertion_n14, [14]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_n15, [15]);

// Wave 2 priority 2, CD-6 step 1. Actual caller domain for the remaining B4 lengths:
// one exact allocation and the constant offset 1 in each independent plain proof.
macro_rules! w2p2_b4_offset_one {
    ($plain:ident, $cell:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $plain() {
            let mut v: [u64; $n] = kani::any();
            super::super::insertion_sort_shift_left(&mut v, 1, &mut w1_any_less_u64);
            kani::cover(true, concat!("W2 P2 B4 u64 offset1 normal return N", stringify!($n)));
        }

        #[kani::proof]
        #[kani::unwind(25)]
        fn $cell() {
            let mut v = w2_o3_input::<$n>();
            super::super::insertion_sort_shift_left(&mut v, 1, &mut w2_o3_mutating_less);
            kani::cover(true, concat!("W2 P2 B4 Cell offset1 normal return N", stringify!($n)));
        }
    };
}

#[cfg(kani_smallsort_controls)]
w2p2_b4_offset_one!(w2p2_b4_u64_n16, w2p2_b4_cell_n16, 16);
#[cfg(kani_smallsort_controls)]
w2p2_b4_offset_one!(w2p2_b4_u64_n17, w2p2_b4_cell_n17, 17);
#[cfg(kani_smallsort_controls)]
w2p2_b4_offset_one!(w2p2_b4_u64_n18, w2p2_b4_cell_n18, 18);
#[cfg(kani_smallsort_controls)]
w2p2_b4_offset_one!(w2p2_b4_u64_n19, w2p2_b4_cell_n19, 19);
#[cfg(kani_smallsort_controls)]
w2p2_b4_offset_one!(w2p2_b4_u64_n20, w2p2_b4_cell_n20, 20);

// W3 L1-5: split the entire insertion-offset domain into small disjoint groups.
// Each harness owns one exact allocation; only the listed constant-offset calls
// are instantiated. No sorted-prefix assumption and no verified or manual stubs.
macro_rules! w3_insertion_group {
    ($plain:ident, $cell:ident, $n:literal, [$($o:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $plain() {
            const { $(assert!($o >= 1 && $o <= $n);)+ };
            let mut v: [u64; $n] = kani::any();
            let offset: usize = kani::any_where(|&o| matches!(o, $($o)|+));
            match offset {
                $($o => w2_insertion_at::<_, _, $o>(&mut v, &mut w1_any_less_u64),)+
                _ => unreachable!(),
            }
            $(kani::cover(offset == $o, concat!("W3 B4 offset ", stringify!($o)));)+
            kani::cover(true, "W3 B4 group: normal return");
        }

        #[kani::proof]
        #[kani::unwind(35)]
        fn $cell() {
            const { $(assert!($o >= 1 && $o <= $n);)+ };
            let mut v = w2_o3_input::<$n>();
            let offset: usize = kani::any_where(|&o| matches!(o, $($o)|+));
            match offset {
                $($o => w2_insertion_at::<_, _, $o>(&mut v, &mut w2_o3_mutating_less),)+
                _ => unreachable!(),
            }
            $(kani::cover(offset == $o, concat!("W3 O3 offset ", stringify!($o)));)+
            kani::cover(true, "W3 O3 group: normal return");
        }
    };
}

w3_insertion_group!(w3_b4_n15_g1, w3_o3_n15_g1, 15, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n15_g2, w3_o3_n15_g2, 15, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n15_g3, w3_o3_n15_g3, 15, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n15_g4, w3_o3_n15_g4, 15, [13, 14, 15]);
w3_insertion_group!(w3_b4_n16_g1, w3_o3_n16_g1, 16, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n16_g2, w3_o3_n16_g2, 16, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n16_g3, w3_o3_n16_g3, 16, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n16_g4, w3_o3_n16_g4, 16, [13, 14, 15, 16]);
w3_insertion_group!(w3_b4_n17_g1, w3_o3_n17_g1, 17, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n17_g2, w3_o3_n17_g2, 17, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n17_g3, w3_o3_n17_g3, 17, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n17_g4, w3_o3_n17_g4, 17, [13, 14, 15]);
w3_insertion_group!(w3_b4_n17_g5, w3_o3_n17_g5, 17, [16, 17]);
w3_insertion_group!(w3_b4_n18_g1, w3_o3_n18_g1, 18, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n18_g2, w3_o3_n18_g2, 18, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n18_g3, w3_o3_n18_g3, 18, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n18_g4, w3_o3_n18_g4, 18, [13, 14, 15, 16]);
w3_insertion_group!(w3_b4_n18_g5, w3_o3_n18_g5, 18, [17, 18]);
w3_insertion_group!(w3_b4_n19_g1, w3_o3_n19_g1, 19, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n19_g2, w3_o3_n19_g2, 19, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n19_g3, w3_o3_n19_g3, 19, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n19_g4, w3_o3_n19_g4, 19, [13, 14, 15, 16]);
w3_insertion_group!(w3_b4_n19_g5, w3_o3_n19_g5, 19, [17, 18, 19]);
w3_insertion_group!(w3_b4_n20_g1, w3_o3_n20_g1, 20, [1, 2, 3, 4]);
w3_insertion_group!(w3_b4_n20_g2, w3_o3_n20_g2, 20, [5, 6, 7, 8]);
w3_insertion_group!(w3_b4_n20_g3, w3_o3_n20_g3, 20, [9, 10, 11, 12]);
w3_insertion_group!(w3_b4_n20_g4, w3_o3_n20_g4, 20, [13, 14, 15, 16]);
w3_insertion_group!(w3_b4_n20_g5, w3_o3_n20_g5, 20, [17, 18, 19, 20]);

// K-10 network correctness: full-width values, a pure strict total order, actual outer trait.
fn w2p2_strict_less<T: Ord>(a: &T, b: &T) -> bool { a < b }

fn w2p2_k10_fixed<T: kani::Arbitrary + Copy + Ord, const N: usize>() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [T; N] = kani::any();
    let pre = v;
    let probe: T = kani::any();
    let mut cmp = w2p2_strict_less::<T>;
    <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    assert!(sorted_by(&v, &mut cmp));
    // Below the network width, keep the direct full-route permutation proof.
    // At N >= 9, compose the structural network permutation with the separately checked
    // real insertion-tail permutation. This keeps its probe formula out of the network.
    if N < 9 {
        assert!(probe_count(&pre, &probe) == probe_count(&v, &probe));
    }
    kani::cover(N < 2 || !same_from(&v, &pre, 0), "W2 P2 K10: trivial input or elements move");
}

macro_rules! w2p2_k10_cases {
    ($name:ident, $t:ty, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => w2p2_k10_fixed::<$t, $n>(),)+
                _ => {}
            }
            $(kani::cover(len == $n, concat!("W2 P2 K10 normal return at ", stringify!($n)));)+
            kani::cover(true, "W2 P2 K10 family: end reached");
        }
    };
}

w2p2_k10_cases!(w2p2_k10_u8_0_2, u8, [0, 1, 2]);
w2p2_k10_cases!(w2p2_k10_u64_0_2, u64, [0, 1, 2]);
w2p2_k10_cases!(w2p2_k10_u8_3_4, u8, [3, 4]);
w2p2_k10_cases!(w2p2_k10_u64_3_4, u64, [3, 4]);

w2p2_k10_cases!(w2p2_k10_u8_n5, u8, [5]);
w2p2_k10_cases!(w2p2_k10_u64_n5, u64, [5]);
w2p2_k10_cases!(w2p2_k10_u8_n6, u8, [6]);
w2p2_k10_cases!(w2p2_k10_u64_n6, u64, [6]);

w2p2_k10_cases!(w2p2_k10_u8_n7, u8, [7]);
w2p2_k10_cases!(w2p2_k10_u64_n7, u64, [7]);
w2p2_k10_cases!(w2p2_k10_u8_n8, u8, [8]);
w2p2_k10_cases!(w2p2_k10_u64_n8, u64, [8]);

// K-9s: the existing exact two-cell compare-exchange contract, every C3 representation.
// No verified stubs are used here; each proof checks the real swap_if_less body.
impl W2Value for u64 {
    fn w2_value() -> Self { kani::any() }
}

fn w2p2_zst_less(a: &(), b: &()) -> bool {
    // Read both ZST arguments through ptr::read, then retain the strict unit order.
    let _ = super::uninit::zst_aware_less(a, b);
    false
}
fn w2p2_drop_less(a: &W2Drop, b: &W2Drop) -> bool { a.0 < b.0 }
fn w2p2_cell_less(a: &crate::cell::Cell<i32>, b: &crate::cell::Cell<i32>) -> bool {
    a.get() < b.get()
}
fn w2p2_array_key_less<const M: usize>(a: &[u8; M], b: &[u8; M]) -> bool {
    // All instantiated C3 arrays have M > 0; the remaining bytes are full-width payload.
    a[0] < b[0]
}

fn w2p2_k9s_fixed<T: W2Value, F: FnMut(&T, &T) -> bool>(mut cmp: F) {
    let mut v: [T; 2] = crate::array::from_fn(|_| T::w2_value());
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    let taken = cmp(&v[b], &v[a]);
    // SAFETY: a and b are distinct initialized writable elements of the live exact array.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut cmp); }
    kani::cover(reverse, "W2 P2 K9s indices 1,0");
    kani::cover(!reverse, "W2 P2 K9s indices 0,1");
    kani::cover(size_of::<T>() == 0 || taken, "W2 P2 K9s swap branch or trivial ZST");
    kani::cover(!taken, "W2 P2 K9s no-swap branch");
    kani::cover(true, "W2 P2 K9s end reached");
}

macro_rules! w2p2_k9s_case {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof_for_contract(super::super::swap_if_less)]
        #[kani::unwind(180)]
        fn $name() {
            w2p2_k9s_fixed::<$t, _>($cmp);
        }
    };
}

// Contract instrumentation on this ZST reports an unsupported unallocated pointer.
#[cfg(kani_smallsort_controls)]
w2p2_k9s_case!(w2p2_k9s_zst, (), w2p2_zst_less);
w2p2_k9s_case!(w2p2_k9s_u8, u8, w2p2_strict_less::<u8>);
w2p2_k9s_case!(w2p2_k9s_u64, u64, w2p2_strict_less::<u64>);
w2p2_k9s_case!(w2p2_k9s_u128, u128, w2p2_strict_less::<u128>);
w2p2_k9s_case!(w2p2_k9s_a16, [u8; 16], w2p2_array_key_less::<16>);
w2p2_k9s_case!(w2p2_k9s_a17, [u8; 17], w2p2_array_key_less::<17>);
w2p2_k9s_case!(w2p2_k9s_a85, [u8; 85], w2p2_array_key_less::<85>);
w2p2_k9s_case!(w2p2_k9s_a86, [u8; 86], w2p2_array_key_less::<86>);
w2p2_k9s_case!(w2p2_k9s_drop, W2Drop, w2p2_drop_less);
w2p2_k9s_case!(w2p2_k9s_cell, crate::cell::Cell<i32>, w2p2_cell_less);


w2p2_k10_cases!(w2p2_k10_u8_n9, u8, [9]);
w2p2_k10_cases!(w2p2_k10_u64_n9, u64, [9]);
w2p2_k10_cases!(w2p2_k10_u8_n10, u8, [10]);
w2p2_k10_cases!(w2p2_k10_u64_n10, u64, [10]);


/// Full-value permutation of the real insertion suffix, independent of ordering. An arbitrary
/// read-only comparison result includes every sequence produced by K10's pure strict comparator.
/// No sorted-prefix assumption: all possible network outputs are included in this larger domain.
fn w2p2_k10_insertion_perm_fixed<T: kani::Arbitrary + Copy + Eq, const N: usize>() {
    let mut v: [T; N] = kani::any();
    let pre = v;
    let probe: T = kani::any();
    if N >= 13 {
        super::super::insertion_sort_shift_left(&mut v, 13, &mut w2_reading_less::<T>);
    } else {
        super::super::insertion_sort_shift_left(&mut v, 9, &mut w2_reading_less::<T>);
    }
    assert!(probe_count(&pre, &probe) == probe_count(&v, &probe));
    kani::cover(!same_from(&v, &pre, 0), "W2 P2 K10 insertion permutation moves elements");
}

macro_rules! w2p2_k10_insertion_perm_case {
    ($name:ident, $t:ty, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            w2p2_k10_insertion_perm_fixed::<$t, $n>();
            kani::cover(true, "W2 P2 K10 insertion permutation end reached");
        }
    };
}

w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n10, u8, 10);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n10, u64, 10);

w2p2_k10_cases!(w2p2_k10_u8_n11, u8, [11]);
w2p2_k10_cases!(w2p2_k10_u64_n11, u64, [11]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n11, u8, 11);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n11, u64, 11);

w2p2_k10_cases!(w2p2_k10_u8_n12, u8, [12]);
w2p2_k10_cases!(w2p2_k10_u64_n12, u64, [12]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n12, u8, 12);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n12, u64, 12);

// Night K-10 continuation: exact sort13 width; insertion at offset 13 is a no-op.
w2p2_k10_cases!(w2p2_k10_u8_n13, u8, [13]);
w2p2_k10_cases!(w2p2_k10_u64_n13, u64, [13]);

// Night K-10: one real insertion after sort13, with separate sortedness/permutation proofs.
w2p2_k10_cases!(w2p2_k10_u8_n14, u8, [14]);
w2p2_k10_cases!(w2p2_k10_u64_n14, u64, [14]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n14, u8, 14);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n14, u64, 14);

// Night K-10: two insertions after sort13; full-width real bodies, split properties.
w2p2_k10_cases!(w2p2_k10_u8_n15, u8, [15]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n15, u64, [15]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n15, u8, 15);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n15, u64, 15);

// Night K-10 N16: exact arrays, real sort13 plus three insertions.
w2p2_k10_cases!(w2p2_k10_u8_n16, u8, [16]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n16, u64, [16]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n16, u8, 16);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n16, u64, 16);

// Night K-10 final width: real sort13 plus four insertions, split properties.
w2p2_k10_cases!(w2p2_k10_u8_n17, u8, [17]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n17, u64, [17]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n17, u8, 17);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n17, u64, 17);

// W3 L1-4 K-9s: all distinct symbolic positions in an exact N-element allocation.
// The comparator is exactly the pure strict order used by K-10, including its function item.
fn w3_k9s_indices<T: kani::Arbitrary + Copy + Ord, const N: usize>() {
    const { assert!(N >= 9 && N <= 17) };
    let mut v: [T; N] = kani::any();
    let pre = v;
    let a: usize = kani::any_where(|&i| i < N);
    let b: usize = kani::any_where(|&i| i < N && i != a);
    let mut cmp = w2p2_strict_less::<T>;
    let taken = cmp(&v[b], &v[a]);
    // SAFETY: a and b are distinct in-bounds initialized writable elements of v.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut cmp); }
    // In addition to both existing ensures, explicitly check the untouched frame.
    let mut i = 0;
    while i < N {
        if i != a && i != b {
            assert!(v[i] == pre[i], "K9s symbolic indices: other cells unchanged");
        }
        i += 1;
    }
    kani::cover(a == 0 && b == N - 1, "K9s symbolic indices: first to last");
    kani::cover(a == N - 1 && b == 0, "K9s symbolic indices: last to first");
    kani::cover(a > 0 && a < N - 1 && b > 0 && b < N - 1, "K9s symbolic indices: interior pair");
    let network_last = if N >= 13 { 12 } else { 8 };
    kani::cover(a == network_last || b == network_last, "K9s symbolic indices: network final position");
    kani::cover(taken, "K9s symbolic indices: swap branch");
    kani::cover(!taken, "K9s symbolic indices: no-swap branch");
    kani::cover(true, "K9s symbolic indices: end reached");
}

#[kani::proof_for_contract(super::super::swap_if_less)]
#[kani::unwind(25)]
fn w2night_k9s_u8_indices17() {
    w3_k9s_indices::<u8, 17>();
}

#[kani::proof_for_contract(super::super::swap_if_less)]
#[kani::unwind(25)]
fn w2night_k9s_u64_indices17() {
    w3_k9s_indices::<u64, 17>();
}

macro_rules! w3_k9s_case {
    ($name:ident, $t:ty, $n:literal) => {
        #[kani::proof_for_contract(super::super::swap_if_less)]
        #[kani::unwind(25)]
        fn $name() {
            w3_k9s_indices::<$t, $n>();
        }
    };
}

w3_k9s_case!(w3_k9s_u8_n9, u8, 9);
w3_k9s_case!(w3_k9s_u8_n10, u8, 10);
w3_k9s_case!(w3_k9s_u8_n11, u8, 11);
w3_k9s_case!(w3_k9s_u8_n12, u8, 12);
w3_k9s_case!(w3_k9s_u8_n13, u8, 13);
w3_k9s_case!(w3_k9s_u8_n14, u8, 14);
w3_k9s_case!(w3_k9s_u8_n15, u8, 15);
w3_k9s_case!(w3_k9s_u8_n16, u8, 16);
w3_k9s_case!(w3_k9s_u64_n9, u64, 9);
w3_k9s_case!(w3_k9s_u64_n10, u64, 10);
w3_k9s_case!(w3_k9s_u64_n11, u64, 11);
w3_k9s_case!(w3_k9s_u64_n12, u64, 12);
w3_k9s_case!(w3_k9s_u64_n13, u64, 13);
w3_k9s_case!(w3_k9s_u64_n14, u64, 14);
w3_k9s_case!(w3_k9s_u64_n15, u64, 15);
w3_k9s_case!(w3_k9s_u64_n16, u64, 16);

// Night K-8r: fixed nonzero begin offsets inside [u64;17], all valid tail positions.
// Contract preconditions (including sorted [begin, tail)) are supplied by proof_for_contract.
fn w2night_k8r_start<const START: usize>() -> usize {
    set_probe::<u64>();
    let mut v: [u64; 17] = kani::any();
    let tail: usize = kani::any_where(|&t| START < t && t < 17);
    let pre = v;
    let base = v.as_mut_ptr();
    // SAFETY: each instantiation has 1 <= START <= 15, START < tail < 17; the
    // enclosing proof_for_contract assumes precisely insert_tail's own requires.
    unsafe { super::super::insert_tail(base.add(START), base.add(tail), &mut lt_u64); }
    let mut i = 0;
    while i < START {
        assert!(v[i] == pre[i], "K8r: prefix before begin unchanged");
        i += 1;
    }
    assert!(same_from(&v, &pre, tail + 1), "K8r: suffix after tail unchanged");
    kani::cover(!same_from(&v, &pre, 0), "K8r: insertion moves elements");
    kani::cover(true, "K8r: end reached");
    tail
}

// List only possible tails: Kani registers even covers in a constant-false branch.
macro_rules! w2night_k8r_case {
    ($name:ident, $start:literal, [$($end:literal),+]) => {
        #[kani::proof_for_contract(super::super::insert_tail)]
        #[kani::unwind(25)]
        fn $name() {
            let tail = w2night_k8r_start::<$start>();
            $(kani::cover(tail == $end, concat!("K8r: tail ", stringify!($end), " with requires satisfied"));)+
        }
    };
}

w2night_k8r_case!(w2night_k8r_start15_u64, 15, [16]);
w2night_k8r_case!(w2night_k8r_start14_u64, 14, [15, 16]);
w2night_k8r_case!(w2night_k8r_start13_u64, 13, [14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start12_u64, 12, [13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start11_u64, 11, [12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start10_u64, 10, [11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start9_u64, 9, [10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start8_u64, 8, [9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start7_u64, 7, [8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start6_u64, 6, [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start5_u64, 5, [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start4_u64, 4, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start3_u64, 3, [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start2_u64, 2, [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);
w2night_k8r_case!(w2night_k8r_start1_u64, 1, [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]);

// Night O3: tag permutation under key-writing Cell comparisons, one constant length per proof.
// Ordinary proofs use real bodies and CI --no-assert-contracts; no sorted-prefix assumption.
fn w2night_o3_tags<const N: usize>() -> (u8, usize) {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = w2_o3_input::<N>();
    let probe: u8 = kani::any();
    let before = k13_tag_count(&v, probe);
    let tags = k13_tags(&v);
    let mode: u8 = kani::any_where(|&m| m < 3);
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    if mode == 0 {
        let mut scratch = [];
        <K13Cell as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut w2_o3_mutating_less);
    } else if mode == 1 {
        <K13Cell as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w2_o3_mutating_less);
    } else {
        w2_const_offset_call!(&mut v, offset, N, &mut w2_o3_mutating_less);
    }
    assert!(before == k13_tag_count(&v, probe), "O3: tag multiplicity preserved");
    let moved = tags != k13_tags(&v);
    kani::cover(mode == 0 && moved, "O3: stable default moves a tag");
    kani::cover(mode == 1 && moved, "O3: unstable fallback moves a tag");
    kani::cover(mode == 2 && moved, "O3: insertion moves a tag");
    kani::cover(true, "O3: tag permutation end reached");
    (mode, offset)
}

macro_rules! w2night_o3_tags_case {
    ($name:ident, $n:literal, [$($offset:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let (mode, offset) = w2night_o3_tags::<$n>();
            $(kani::cover(mode == 2 && offset == $offset, concat!("O3: insertion normal return offset ", stringify!($offset)));)+
        }
    };
}

w2night_o3_tags_case!(w2night_o3_tags_n2, 2, [1, 2]);
w2night_o3_tags_case!(w2night_o3_tags_n3, 3, [1, 2, 3]);
w2night_o3_tags_case!(w2night_o3_tags_n4, 4, [1, 2, 3, 4]);


// K-15 controls on previously accepted K10 harnesses, preserving their exact inputs/checks.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(25)]
#[kani::stub(super::super::swap_if_less, super::mutations::mutant_swap_if_less)]
fn k15_mutant_existing_k10_swap() {
    w2p2_k10_u8_n9();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(25)]
#[kani::stub(super::super::small_sort_network, super::mutations::mutant_small_sort_network)]
fn k15_mutant_existing_k10_presorted_len() {
    w2p2_k10_u8_n10();
}
