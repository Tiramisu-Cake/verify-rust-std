//! K1-network agent: contracts and harnesses for `swap_if_less`, `sort9_optimal`, `sort13_optimal`,
//! `insertion_sort_shift_left` and `small_sort_network`.
//! Written from the std source and the Kani documentation only (EXPERIMENT.md, rule R1).

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

check_sort_n!(sort9_u8, sort9_optimal, 9, u8, lt_u8);
check_sort_n!(sort9_i32, sort9_optimal, 9, i32, lt_i32);
check_sort_n!(sort9_u64, sort9_optimal, 9, u64, lt_u64);
check_sort_n!(sort13_u8, sort13_optimal, 13, u8, lt_u8);
check_sort_n!(sort13_i32, sort13_optimal, 13, i32, lt_i32);
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

check_perm_stub_n!(sort13_perm_stub_u8, sort13_optimal, 13, u8, lt_u8);
check_perm_stub_n!(sort13_perm_stub_i32, sort13_optimal, 13, i32, lt_i32);
check_perm_stub_n!(sort13_perm_stub_u64, sort13_optimal, 13, u64, lt_u64);
check_perm_stub_n!(sort9_perm_stub_u64, sort9_optimal, 9, u64, lt_u64);

check_sort_n_01!(sort9_01_u8, sort9_optimal, 9, u8, lt_u8);
check_sort_n_01!(sort9_01_i32, sort9_optimal, 9, i32, lt_i32);
check_sort_n_01!(sort9_01_u64, sort9_optimal, 9, u64, lt_u64);
check_sort_n_01!(sort13_01_u8, sort13_optimal, 13, u8, lt_u8);
check_sort_n_01!(sort13_01_i32, sort13_optimal, 13, i32, lt_i32);
check_sort_n_01!(sort13_01_u64, sort13_optimal, 13, u64, lt_u64);
check_perm_n!(sort9_perm_u8, sort9_optimal, 9, u8, lt_u8);
check_perm_n!(sort9_perm_i32, sort9_optimal, 9, i32, lt_i32);
check_perm_n!(sort9_perm_u64, sort9_optimal, 9, u64, lt_u64);
check_perm_n!(sort13_perm_u8, sort13_optimal, 13, u8, lt_u8);
check_perm_n!(sort13_perm_i32, sort13_optimal, 13, i32, lt_i32);
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

check_network_no_merge!(network_upto17_u8, u8, lt_u8);
check_network_no_merge!(network_upto17_i32, i32, lt_i32);
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

check_insert_tail_net!(insert_tail_net_u8, u8, lt_u8);
check_insert_tail_net!(insert_tail_net_i32, i32, lt_i32);
check_insert_tail_net!(insert_tail_net_u64, u64, lt_u64);

/// Wave 1 K-8: the insertion region is a prefix of a larger allocation, with every tail
/// position 1..=16 symbolic. The contract proof assumes only `insert_tail`'s own requires
/// (in particular the sorted prefix); the suffix stays arbitrary and must be unchanged.
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

check_network_band_tail!(bandt0_8_u8, u8, lt_u8, 0, 8, [0, 1, 2, 8]);
check_network_band_tail!(bandt0_8_i32, i32, lt_i32, 0, 8, [0, 1, 2, 8]);
check_network_band_tail!(bandt0_8_u64, u64, lt_u64, 0, 8, [0, 1, 2, 8]);
check_network_band_tail!(bandt9_12_u8, u8, lt_u8, 9, 12, [9, 12]);
check_network_band_tail!(bandt9_12_i32, i32, lt_i32, 9, 12, [9, 12]);
check_network_band_tail!(bandt9_12_u64, u64, lt_u64, 9, 12, [9, 12]);
check_network_band_tail!(bandt13_17_u8, u8, lt_u8, 13, 17, [13, 17]);
check_network_band_tail!(bandt13_17_i32, i32, lt_i32, 13, 17, [13, 17]);
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

check_network_fixed!(fixed8_u64, u64, lt_u64, 8);
check_network_fixed!(fixed12_u64, u64, lt_u64, 12);
check_network_fixed!(fixed17_u64, u64, lt_u64, 17);

/// Phase 5 run A: `check_network_fixed` at length 8 with `insert_tail` through its verified contract
/// (`insert_tail_net_u64`, job 26), the one combination phase 2 did not run. At length 8 the network
/// stubs are off the path (`small_sort_network` calls only `insertion_sort_shift_left(v, 1)`); they
/// are kept so that the harness differs from `fixed8_u64` (job 31) only by the `insert_tail` stub.
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

check_network_band!(band0_8_u8, u8, lt_u8, 0, 8, [0, 1, 2, 8]);
check_network_band!(band0_8_i32, i32, lt_i32, 0, 8, [0, 1, 2, 8]);
check_network_band!(band0_8_u64, u64, lt_u64, 0, 8, [0, 1, 2, 8]);
check_network_band!(band9_12_u8, u8, lt_u8, 9, 12, [9, 12]);
check_network_band!(band9_12_i32, i32, lt_i32, 9, 12, [9, 12]);
check_network_band!(band9_12_u64, u64, lt_u64, 9, 12, [9, 12]);
check_network_band!(band13_17_u8, u8, lt_u8, 13, 17, [13, 17]);
check_network_band!(band13_17_i32, i32, lt_i32, 13, 17, [13, 17]);
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

#[kani::proof]
#[kani::unwind(18)]
fn direct_network_len13_u8() {
    direct_network::<13>();
}

#[kani::proof]
#[kani::unwind(18)]
fn direct_network_len17_u8() {
    direct_network::<17>();
}
