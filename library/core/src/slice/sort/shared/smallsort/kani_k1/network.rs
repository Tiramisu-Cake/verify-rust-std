//! Harnesses for compare-exchange, sorting networks, insertion, and the outer small-sort routes.
//! The families below check contract behavior, memory safety, normal returns, and selected
//! sortedness and permutation properties over their stated element types and fixed lengths.

#![allow(dead_code, unused_macros)]

use crate::kani;
use crate::mem::size_of;
use super::merge::{insert_tail_len, lt_i32, lt_u8, lt_u64, set_probe};
use super::super::{CopyOnDrop, UnstableSmallSortFreezeTypeImpl, swap_if_less};

// These comparators order by `x >> 1`, allowing distinct full values to share a key. Sortedness
// therefore does not imply permutation. The shared function items match the `(T, F)` instances
// used to verify contracts for `swap_if_less` and `bidirectional_merge`.

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

/// Checks that the verified contract rejects equal positions in a two-element array. Both indices
/// remain in bounds, isolating the distinct-position precondition.
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
// Harness-level checks use the shared arbitrary probe (`set_probe`, `k1_count`).

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

/// Reads both `u64` arguments, then returns a fresh nondeterministic result. Volatile reads keep
/// the element accesses observable while leaving comparator outcomes unconstrained.
fn w1_any_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: comparator callers must supply readable u64 references. Kani checks both
    // actual accesses, including references formed from raw pointers inside the sort.
    unsafe {
        let _ = crate::ptr::read_volatile(a);
        let _ = crate::ptr::read_volatile(b);
    }
    kani::any()
}

/// Runs the actual freeze-specialized route on an exact `[u64; N]` array with unconstrained
/// comparisons. These harnesses target memory safety and normal return, not ordering.
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

// Exact lengths 0..=17 cover the no-merge routes: empty/singleton, insertion-only,
// sort9/sort13 and their insertion tails.
w1_network_o1_cases!(
    w1_network_o1_nomerge_u64,
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    []
);
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
#[derive(Clone, Copy)]
struct K13Tagged {
    key: u8,
    tag: u8,
}

type K13Cell = crate::cell::Cell<K13Tagged>;
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
// ---------------------------------------------------------------------------------------------
// These route checks stub only the explicit order-violation panic. The other assertions and
// memory checks remain active, and no verified contracts replace the sort bodies.
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

/// Control showing that an assertion is reported after a normal return with the same panic stub.
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

/// Checks that the real trait dispatch and merge can return normally at length 18.
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

/// Each instantiation owns an exact `[u64; N]` array and enters through the unstable trait route.
/// Comparisons are unconstrained after readable accesses, and all sorting bodies remain real.
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
            $(kani::cover(
                len == $n,
                concat!("W2 O1-A network normal return at ", stringify!($n))
            );)+
            kani::cover(true, "W2 O1-A network family: end reached");
        }
    };
}

w2_network_o1_cases!(w2_network_o1_a_18_21, [18, 19, 20, 21]);
w2_network_o1_cases!(w2_network_o1_a_22_25, [22, 23, 24, 25]);
w2_network_o1_cases!(w2_network_o1_a_26_27, [26, 27]);
w2_network_o1_cases!(w2_network_o1_a_28_29, [28, 29]);
w2_network_o1_cases!(w2_network_o1_a_30_32, [30, 31, 32]);

// Type and length matrix through the actual stable and unstable trait entry points. Inputs use
// their full element domains; these harnesses check safety and normal return, not sortedness.
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

/// Confirms an assertion remains visible after a normal return through the short route.
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

/// Selects stable or unstable dispatch for each listed fixed array length and covers both routes.
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
                kani::cover(
                    stable && len == $n,
                    concat!("W2 K16s stable normal return at ", stringify!($n))
                );
                kani::cover(
                    !stable && len == $n,
                    concat!("W2 K16s unstable normal return at ", stringify!($n))
                );
            )+
            kani::cover(true, "W2 K16s paired family: end reached");
        }
    };
}

w2_type_pair_cases!(w2_k16_u128_lo, u128, [0, 1, 2, 7, 8]);
w2_type_pair_cases!(w2_k16_u128_mid, u128, [15, 16, 17]);
#[cfg(kani_smallsort_controls)]
w2_type_pair_cases!(w2_k16_u128_hi, u128, [31, 32]);

/// Confirms an assertion remains visible after a normal return through a merge route.
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

/// Checks normal-return reachability for one type, trait route, and merge length.
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

// `Cell<i32>` is non-Freeze and non-Copy, so both trait entry points exercise default paths.
w2_type_pair_cases!(w2_k16_cell_nonfreeze, crate::cell::Cell<i32>, [0, 1, 2, 15, 16]);

impl W2Value for i32 {
    fn w2_value() -> Self { kani::any() }
}

// `i32` is Freeze and Copy; check both trait entry points at the same lengths as the Cell cases.
w2_type_pair_cases!(w3_k16_i32_freeze, i32, [0, 1, 2, 15, 16]);

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

// Exercises insertion at every valid offset in exact `[u64; N]` arrays. Each match arm makes the
// offset constant at the call site; all insertion bodies are real and no sorted prefix is assumed.
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

// Mutating comparisons overwrite both keys in tagged `Cell` values. These exact-length route and
// insertion harnesses check memory safety and normal return without assuming a sorted prefix.
fn w2_o3_mutating_less(a: &K13Cell, b: &K13Cell) -> bool {
    // SAFETY: both initialized Cell payloads must be readable before either write.
    let (left, right) = unsafe {
        (crate::ptr::read_volatile(a.as_ptr()), crate::ptr::read_volatile(b.as_ptr()))
    };
    let left_key: u8 = kani::any();
    let right_key: u8 = kani::any();
    a.set(K13Tagged { key: left_key, tag: left.tag });
    b.set(K13Tagged { key: right_key, tag: right.tag });
    kani::cover(
        left_key != left.key && right_key != right.key,
        "W2 O3 comparator changes both keys"
    );
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
        <K13Cell as StableSmallSortTypeImpl>::small_sort(
            &mut v,
            &mut scratch,
            &mut w2_o3_mutating_less,
        );
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
                kani::cover(
                    stable && len == $n,
                    concat!("W2 O3 stable normal return at ", stringify!($n))
                );
                kani::cover(
                    !stable && len == $n,
                    concat!("W2 O3 unstable normal return at ", stringify!($n))
                );
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
            $(kani::cover(
                len == $n,
                concat!("W2 O3 insertion normal return at ", stringify!($n))
            );)+
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

// Separate lengths into smaller groups so each symbolic offset is checked with a fixed allocation.
w2_insertion_safety_cases!(w2_k11s_11_12, [11, 12]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_13_15, [13, 14, 15]);
w2_o3_insertion_cases!(w2_o3_insertion_11_12, [11, 12]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_13_15, [13, 14, 15]);

// Exact single-length instances retain coverage for the larger insertion cases.
w2_insertion_safety_cases!(w2_k11s_n13, [13]);
w2_insertion_safety_cases!(w2_k11s_n14, [14]);
#[cfg(kani_smallsort_controls)]
w2_insertion_safety_cases!(w2_k11s_n15, [15]);
w2_o3_insertion_cases!(w2_o3_insertion_n13, [13]);
w2_o3_insertion_cases!(w2_o3_insertion_n14, [14]);
#[cfg(kani_smallsort_controls)]
w2_o3_insertion_cases!(w2_o3_insertion_n15, [15]);

// Exact-length cases check the actual offset-one insertion call for both ordinary and mutating
// Cell comparators. The array itself supplies the bounds for the real insertion body.
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

// The groups partition all valid offsets for each exact array length. Each listed offset becomes a
// constant call-site value; comparisons are unconstrained and no sorted-prefix contract is assumed.
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

// Full-width `u8`, `u64`, or `u128` arrays enter through the unstable trait with a strict total
// order. The checks assert sortedness and use probe counts to establish permutation.
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

// Exact two-element compare-exchange contract checks use the real body across the listed element
// representations. The contract supplies its own bounds and distinct-index preconditions.
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

// This zero-sized-type case is control-only because contract instrumentation does not support its
// unallocated pointer representation.
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
/// read-only comparison result includes every sequence produced by the pure strict comparator.
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

// Exact sort13-width arrays check the sort route where insertion begins at the array end.
w2p2_k10_cases!(w2p2_k10_u8_n13, u8, [13]);
w2p2_k10_cases!(w2p2_k10_u64_n13, u64, [13]);

// Length-14 arrays check one real insertion after sort13, with sortedness and permutation checked
// by separate harnesses.
w2p2_k10_cases!(w2p2_k10_u8_n14, u8, [14]);
w2p2_k10_cases!(w2p2_k10_u64_n14, u64, [14]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n14, u8, 14);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n14, u64, 14);

// Length-15 arrays check two real insertions after sort13 using full-width values.
w2p2_k10_cases!(w2p2_k10_u8_n15, u8, [15]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n15, u64, [15]);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n15, u8, 15);
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n15, u64, 15);

// Length-16 arrays check sort13 followed by three real insertions.
w2p2_k10_cases!(w2p2_k10_u8_n16, u8, [16]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n16, u64, [16]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n16, u8, 16);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n16, u64, 16);

// Length-17 arrays check sort13 followed by four real insertions.
w2p2_k10_cases!(w2p2_k10_u8_n17, u8, [17]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_cases!(w2p2_k10_u64_n17, u64, [17]);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u8_n17, u8, 17);
#[cfg(kani_smallsort_controls)]
w2p2_k10_insertion_perm_case!(w2p2_k10_perm_u64_n17, u64, 17);

// Contract checks choose any two distinct positions in exact arrays of lengths 9 through 17.
// The comparator is the same strict total order used by the network correctness harnesses.
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
    kani::cover(
        a == network_last || b == network_last,
        "K9s symbolic indices: network final position"
    );
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

// Checks insertion into every nonempty interior region of an exact `[u64; 17]` array. The
// `proof_for_contract` harness supplies the callee's sorted-prefix precondition.
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

// Enumerate possible tail positions so each contract-backed interior region has a cover.
macro_rules! w2night_k8r_case {
    ($name:ident, $start:literal, [$($end:literal),+]) => {
        #[kani::proof_for_contract(super::super::insert_tail)]
        #[kani::unwind(25)]
        fn $name() {
            let tail = w2night_k8r_start::<$start>();
            $(kani::cover(
                tail == $end,
                concat!("K8r: tail ", stringify!($end), " with requires satisfied")
            );)+
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

// At lengths 2 through 4, checks tag multiplicities after stable, unstable, or insertion routes
// whose comparator may rewrite keys. No ordering precondition is assumed.
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
        <K13Cell as StableSmallSortTypeImpl>::small_sort(
            &mut v,
            &mut scratch,
            &mut w2_o3_mutating_less,
        );
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
            $(kani::cover(
                mode == 2 && offset == $offset,
                concat!("O3: insertion normal return offset ", stringify!($offset))
            );)+
        }
    };
}

w2night_o3_tags_case!(w2night_o3_tags_n2, 2, [1, 2]);
w2night_o3_tags_case!(w2night_o3_tags_n3, 3, [1, 2, 3]);
w2night_o3_tags_case!(w2night_o3_tags_n4, 4, [1, 2, 3, 4]);

// Negative control applies the one-change network copy to the same exact input and assertions.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(25)]
#[kani::stub(super::super::small_sort_network, super::mutations::mutant_small_sort_network)]
fn k15_mutant_existing_k10_presorted_len() {
    w2p2_k10_u8_n10();
}
