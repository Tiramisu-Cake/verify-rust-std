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

/// K-8 review extension: both ends of the insertion region are symbolic within one allocation.
/// This includes the interior regions used by scratch-based call sites, not just prefixes.
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
#[kani::proof]
#[kani::unwind(35)]
fn w1_network_o1_len17_u64() {
    let mut v: [u64; 17] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "network O1 length 17: normal return reachable");
}

/// CD-1 variant B: safety-class checks only; all assertion-class panics are allowed.
/// Every callee, including bidirectional_merge, is real; no contract checks or stubs.
#[kani::proof]
#[kani::should_panic]
#[kani::unwind(35)]
fn w1_network_o1_len24_u64() {
    let mut v: [u64; 24] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "network O1 length 24: normal return reachable");
}

/// As at length 24, with two length-16 regions (sort13 + insertion), then even merge.
#[kani::proof]
#[kani::should_panic]
#[kani::unwind(35)]
fn w1_network_o1_len32_u64() {
    let mut v: [u64; 32] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut w1_any_less_u64);
    kani::cover(true, "network O1 length 32: normal return reachable");
}

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
w1_network_o1_cases!(w1_network_o1_odd_u64, [19, 25, 31], [kani::should_panic]);
// No merge: includes 0/1 returns, insertion-only, sort9 and sort13, and their insertion tails.
w1_network_o1_cases!(w1_network_o1_nomerge_u64, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17], []);
// Remaining merge lengths; together with 19/24/25/31/32, covers every length 18..=32.
w1_network_o1_cases!(w1_network_o1_othermerge_u64, [18, 20, 21, 22, 23, 26, 27, 28, 29, 30], [kani::should_panic]);
// Smaller independent partitions after job 62's unlocalized CBMC status 6.
w1_network_o1_cases!(w1_network_o1_othermerge_lo_u64, [18, 20, 21, 22, 23], [kani::should_panic]);
w1_network_o1_cases!(w1_network_o1_othermerge_hi_u64, [26, 27, 28, 29, 30], [kani::should_panic]);

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

/// K-9 retry: full-width u8 values at the exact network width, with a local arbitrary probe.
/// Removing the symbolic slice length and unchanged suffix leaves only the permutation claim.
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

k13_route_cases!(k13_routes_0_8, [0, 1, 2, 3, 4, 5, 6, 7, 8]);
k13_route_cases!(k13_routes_9_16, [9, 10, 11, 12, 13, 14, 15, 16]);
k13_insertion_cases!(k13_insertion_1_10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);
k13_insertion_cases!(k13_insertion_11_20, [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]);

/// Last-dispatch safety-only fallback: one allocation avoids duplicating the large permutation
/// formulas for every constant length. Tags/keys remain full-width; no property assertions/stubs.
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
