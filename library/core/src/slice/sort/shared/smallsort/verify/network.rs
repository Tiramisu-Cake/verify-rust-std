//! Exchange contracts and bounded real-body network, insertion and dispatch checks.

#![allow(dead_code)]

use super::super::{UnstableSmallSortFreezeTypeImpl, swap_if_less};
use super::merge::{lt_i32, lt_u8, lt_u64, set_value_probe};
use crate::kani;
use crate::mem::size_of;

// Share key-order function items with merge contract proofs; equal keys may have different values.

/// Positions anywhere in a 4-element array, in either order, distinct as the contract requires.
fn exercise_swap_contract<T: kani::Arbitrary + Copy, F: FnMut(&T, &T) -> bool>(mut cmp: F) {
    let mut v: [T; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    proof_cover!(a == 0 && b == 3, "swap_if_less: a < b reachable");
    proof_cover!(a == 3 && b == 0, "swap_if_less: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut cmp) };
    proof_cover!(cmp(&old_b, &old_a), "swap_if_less: swap taken");
    proof_cover!(!cmp(&old_b, &old_a), "swap_if_less: swap not taken");
    proof_cover!(true, "swap_if_less: end reached");
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_contract_four_positions_u8() {
    exercise_swap_contract::<u8, _>(lt_u8);
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_contract_four_positions_i32() {
    exercise_swap_contract::<i32, _>(lt_i32);
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_contract_four_positions_u64() {
    exercise_swap_contract::<u64, _>(lt_u64);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(super::super::swap_if_less)]
fn control_swap_contract_precondition_u8() {
    let mut v: [u8; 2] = kani::any();
    // SAFETY: deliberately breaks the contract precondition `a_pos != b_pos`; position 1 is
    // in-bounds, so the real body would be memory safe.
    unsafe { swap_if_less(v.as_mut_ptr(), 1, 1, &mut lt_u8) };
    proof_cover!(true, "swap contract control reached the end");
}

/// `a[from..] == b[from..]` element by element (slice `==` would become a byte loop of `memcmp`).
fn prefix_unchanged<T: PartialEq>(a: &[T], b: &[T], from: usize) -> bool {
    let mut i = from;
    while i < a.len() {
        if a[i] != b[i] {
            return false;
        }
        i += 1;
    }
    a.len() == b.len()
}

fn volatile_reading_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: initialized readable references; volatile reads retain both accesses.
    unsafe {
        let _ = crate::ptr::read_volatile(a);
        let _ = crate::ptr::read_volatile(b);
    }
    kani::any()
}

// Real u64 network safety, exact N0..32 split by route; arbitrary reading comparator.
fn unstable_freeze_network_fixed<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut volatile_reading_less_u64);
}

macro_rules! unstable_freeze_network_cases {
    ($name:ident, [$($n:literal),+], [$($attr:meta),*]) => {
        #[kani::proof]
        $(#[$attr])*
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => unstable_freeze_network_fixed::<$n>(),)+
                _ => {}
            }
            $(proof_cover!(
                len == $n,
                concat!("unstable network normal return at ", stringify!($n))
            );)+
        }
    };
}

unstable_freeze_network_cases!(
    network_safety_unstable_u64_n0_to17,
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
    []
);
fn count_matching_values<T: PartialEq>(s: &[T], p: &T) -> usize {
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
fn is_sorted_by<T, F: FnMut(&T, &T) -> bool>(s: &[T], cmp: &mut F) -> bool {
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
struct TaggedKey {
    key: u8,
    tag: u8,
}

type TaggedKeyCell = crate::cell::Cell<TaggedKey>;
// N <= 20, so a u8 probe count cannot overflow.
fn count_tagged_values<const N: usize>(v: &[TaggedKeyCell; N], probe: u8) -> u8 {
    let mut count = 0;
    let mut i = 0;
    while i < N {
        count += (v[i].get().tag == probe) as u8;
        i += 1;
    }
    count
}

fn tag_sequence<const N: usize>(v: &[TaggedKeyCell; N]) -> [u8; N] {
    let mut tags = [0; N];
    let mut i = 0;
    while i < N {
        tags[i] = v[i].get().tag;
        i += 1;
    }
    tags
}
// These route checks stub only the explicit order-violation panic. The other assertions and
// memory checks remain active, and no verified contracts replace the sort bodies.
fn cut_order_violation_panic() -> ! {
    proof_cover!(true, "order-violation panic stub reached");
    assume_order_violation()
}

fn assume_order_violation() -> ! {
    kani::assume(false);
    unreachable!()
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
#[kani::unwind(35)]
fn control_order_violation_assertion() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; 2] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less_u64);
    proof_cover!(true, "order-violation control reaches normal return before assertion");
    assert!(v[0] != v[0]);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
#[kani::unwind(35)]
fn control_order_violation_reachability() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; 18] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less_u64);
    proof_cover!(true, "order-violation control reaches normal return");
}

fn unstable_dispatch_network_fixed<const N: usize>() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [u64; N] = kani::any();
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less_u64);
}

macro_rules! unstable_dispatch_network_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => unstable_dispatch_network_fixed::<$n>(),)+
                _ => {}
            }
            $(proof_cover!(
                len == $n,
                concat!("unstable network normal return at ", stringify!($n))
            );)+
        }
    };
}

unstable_dispatch_network_cases!(network_safety_unstable_u64_n18_to21, [18, 19, 20, 21]);
unstable_dispatch_network_cases!(network_safety_unstable_u64_n22_to25, [22, 23, 24, 25]);
unstable_dispatch_network_cases!(network_safety_unstable_u64_n26_to27, [26, 27]);
unstable_dispatch_network_cases!(network_safety_unstable_u64_n28_to29, [28, 29]);
unstable_dispatch_network_cases!(network_safety_unstable_u64_n30_to32, [30, 31, 32]);

// Type and length matrix through the actual stable and unstable trait entry points. Inputs use
// their full element domains; these harnesses check safety and normal return, not sortedness.
trait ArbitraryValue: Sized {
    fn arbitrary_value() -> Self;
}

impl ArbitraryValue for () {
    fn arbitrary_value() -> Self {
        ()
    }
}

impl ArbitraryValue for u8 {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}

fn volatile_reading_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: real sort bodies must supply readable initialized values. ManuallyDrop avoids
    // running Drop on the duplicate returned by the volatile read of a non-Copy value.
    unsafe {
        let _left = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(a));
        let _right = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(b));
    }
    kani::any()
}

fn dispatch_safety_fixed<T: ArbitraryValue, const N: usize, const STABLE: bool>() {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v: [T; N] = crate::array::from_fn(|_| T::arbitrary_value());
    if STABLE {
        let mut scratch = [const { crate::mem::MaybeUninit::<T>::uninit() }; 48];
        <T as StableSmallSortTypeImpl>::small_sort(
            &mut v,
            &mut scratch,
            &mut volatile_reading_less::<T>,
        );
    } else {
        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut volatile_reading_less::<T>);
    }
}

macro_rules! dispatch_safety_cases {
    ($name:ident, $t:ty, $stable:literal, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => dispatch_safety_fixed::<$t, $n, $stable>(),)+
                _ => {}
            }
            $(proof_cover!(
                len == $n,
                concat!("dispatch route returns normally at ", stringify!($n))
            );)+
        }
    };
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]
#[kani::unwind(35)]
fn control_network_normal_return_assertion() {
    unstable_dispatch_network_fixed::<2>();
    proof_cover!(true, "order-violation control reaches normal return before assertion");
    let x: u8 = kani::any();
    assert!(x != x);
}

#[cfg(kani_smallsort_controls)]
dispatch_safety_cases!(
    dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32,
    (),
    true,
    [0, 1, 2, 7, 8, 15, 16, 17, 31, 32]
);
#[cfg(kani_smallsort_controls)]
dispatch_safety_cases!(dispatch_safety_unstable_zst_n8_9_12_13_17, (), false, [8, 9, 12, 13, 17]);

dispatch_safety_cases!(dispatch_safety_stable_u8_n0_1_2_7_8, u8, true, [0, 1, 2, 7, 8]);
dispatch_safety_cases!(dispatch_safety_stable_u8_n15_16_17, u8, true, [15, 16, 17]);
dispatch_safety_cases!(dispatch_safety_stable_u8_n31_32, u8, true, [31, 32]);
dispatch_safety_cases!(dispatch_safety_unstable_u8_n8_9_12_13_17, u8, false, [8, 9, 12, 13, 17]);
dispatch_safety_cases!(dispatch_safety_unstable_u8_n18_31_32, u8, false, [18, 31, 32]);

/// Selects stable or unstable dispatch for each listed fixed array length and covers both routes.
macro_rules! dispatch_pair_safety_cases {
    ($name:ident, $t:ty, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => {
                    if stable { dispatch_safety_fixed::<$t, $n, true>(); }
                    else { dispatch_safety_fixed::<$t, $n, false>(); }
                },)+
                _ => {}
            }
            $(
                proof_cover!(
                    stable && len == $n,
                    concat!("stable route normal return at ", stringify!($n))
                );
                proof_cover!(
                    !stable && len == $n,
                    concat!("unstable route normal return at ", stringify!($n))
                );
            )+
        }
    };
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]
#[kani::unwind(65)]
fn control_order_violation_merge_assertion() {
    dispatch_safety_fixed::<u8, 18, false>();
    proof_cover!(true, "merge-route control reaches normal return before assertion");
    let x: u8 = kani::any();
    assert!(x != x);
}

macro_rules! dispatch_reachability_case {
    ($name:ident, $t:ty, $stable:literal, $n:literal) => {
        #[kani::proof]
        #[kani::stub(super::super::panic_on_ord_violation, cut_order_violation_panic)]
        #[kani::unwind(65)]
        fn $name() {
            dispatch_safety_fixed::<$t, $n, $stable>();
            proof_cover!(true, "dispatch route normal return is reachable");
        }
    };
}

dispatch_reachability_case!(dispatch_reachability_stable_u8_n17, u8, true, 17);
dispatch_reachability_case!(dispatch_reachability_general_bytes16_n17, [u8; 16], false, 17);
dispatch_reachability_case!(dispatch_reachability_network_u8_n18, u8, false, 18);

impl<const M: usize> ArbitraryValue for [u8; M] {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes16_n0_1_2_7_8,
    [u8; 16],
    [0, 1, 2, 7, 8]
);
dispatch_safety_cases!(dispatch_safety_stable_bytes16_n15, [u8; 16], true, [15]);
dispatch_safety_cases!(dispatch_safety_stable_bytes16_n16, [u8; 16], true, [16]);
dispatch_safety_cases!(dispatch_safety_stable_bytes16_n17, [u8; 16], true, [17]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes16_n15, [u8; 16], false, [15]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes16_n16, [u8; 16], false, [16]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes16_n17, [u8; 16], false, [17]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes16_n31, [u8; 16], [31]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes16_n32, [u8; 16], [32]);

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes17_n0_1_2_7_8,
    [u8; 17],
    [0, 1, 2, 7, 8]
);
dispatch_safety_cases!(dispatch_safety_stable_bytes17_n15, [u8; 17], true, [15]);
dispatch_safety_cases!(dispatch_safety_stable_bytes17_n16, [u8; 17], true, [16]);
dispatch_safety_cases!(dispatch_safety_stable_bytes17_n17, [u8; 17], true, [17]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes17_n15, [u8; 17], false, [15]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes17_n16, [u8; 17], false, [16]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes17_n17, [u8; 17], false, [17]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes17_n31, [u8; 17], [31]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes17_n32, [u8; 17], [32]);

/// Freeze but non-Copy; the real destructor observes its own initialized key. No drop-count
/// or permutation property is asserted in the safety matrix.
struct DropValue(u8);

impl Drop for DropValue {
    fn drop(&mut self) {
        // SAFETY: a live value must still contain its readable u8 key when dropped.
        unsafe {
            let _ = crate::ptr::read_volatile(&self.0);
        }
    }
}

impl ArbitraryValue for DropValue {
    fn arbitrary_value() -> Self {
        Self(kani::any())
    }
}

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_drop_u8_n0_1_2_7_8,
    DropValue,
    [0, 1, 2, 7, 8]
);
dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_drop_u8_n15_16_17,
    DropValue,
    [15, 16, 17]
);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_drop_u8_n31, DropValue, [31]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_drop_u8_n32, DropValue, [32]);

impl ArbitraryValue for crate::cell::Cell<i32> {
    fn arbitrary_value() -> Self {
        Self::new(kani::any())
    }
}

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes85_n0_1_2_7_8,
    [u8; 85],
    [0, 1, 2, 7, 8]
);
dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes85_n15_16_17,
    [u8; 85],
    [15, 16, 17]
);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes85_n31, [u8; 85], [31]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes85_n32, [u8; 85], [32]);

dispatch_safety_cases!(
    dispatch_safety_unstable_bytes86_n0_1_2_15_16,
    [u8; 86],
    false,
    [0, 1, 2, 15, 16]
);

// Exercises insertion at every valid offset in exact `[u64; N]` arrays. Each match arm makes the
// offset constant at the call site; all insertion bodies are real and no sorted prefix is assumed.
fn insertion_at<T, F: FnMut(&T, &T) -> bool, const O: usize>(v: &mut [T], cmp: &mut F) {
    super::super::insertion_sort_shift_left(v, O, cmp);
}

macro_rules! insertion_at_any_offset {
    ($v:expr, $offset:expr, $n:expr, $cmp:expr) => {
        match $offset {
            1 if $n >= 1 => insertion_at::<_, _, 1>($v, $cmp),
            2 if $n >= 2 => insertion_at::<_, _, 2>($v, $cmp),
            3 if $n >= 3 => insertion_at::<_, _, 3>($v, $cmp),
            4 if $n >= 4 => insertion_at::<_, _, 4>($v, $cmp),
            5 if $n >= 5 => insertion_at::<_, _, 5>($v, $cmp),
            6 if $n >= 6 => insertion_at::<_, _, 6>($v, $cmp),
            7 if $n >= 7 => insertion_at::<_, _, 7>($v, $cmp),
            8 if $n >= 8 => insertion_at::<_, _, 8>($v, $cmp),
            9 if $n >= 9 => insertion_at::<_, _, 9>($v, $cmp),
            10 if $n >= 10 => insertion_at::<_, _, 10>($v, $cmp),
            11 if $n >= 11 => insertion_at::<_, _, 11>($v, $cmp),
            12 if $n >= 12 => insertion_at::<_, _, 12>($v, $cmp),
            13 if $n >= 13 => insertion_at::<_, _, 13>($v, $cmp),
            14 if $n >= 14 => insertion_at::<_, _, 14>($v, $cmp),
            15 if $n >= 15 => insertion_at::<_, _, 15>($v, $cmp),
            16 if $n >= 16 => insertion_at::<_, _, 16>($v, $cmp),
            17 if $n >= 17 => insertion_at::<_, _, 17>($v, $cmp),
            18 if $n >= 18 => insertion_at::<_, _, 18>($v, $cmp),
            19 if $n >= 19 => insertion_at::<_, _, 19>($v, $cmp),
            20 if $n >= 20 => insertion_at::<_, _, 20>($v, $cmp),
            _ => {}
        }
    };
}

fn insertion_safety_fixed<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    insertion_at_any_offset!(&mut v, offset, N, &mut volatile_reading_less_u64);
    proof_cover!(offset == 1, "insertion at offset one returns normally");
    proof_cover!(offset == N, "insertion at final offset returns normally");
}

macro_rules! insertion_safety_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => insertion_safety_fixed::<$n>(),)+
                _ => {}
            }
            $(proof_cover!(
                len == $n,
                concat!("insertion returns normally at length ", stringify!($n))
            );)+
        }
    };
}

insertion_safety_cases!(insertion_safety_u64_n1_to5, [1, 2, 3, 4, 5]);
insertion_safety_cases!(insertion_safety_u64_n6_to10, [6, 7, 8, 9, 10]);
#[cfg(kani_smallsort_controls)]
insertion_safety_cases!(insertion_safety_u64_n11_to15, [11, 12, 13, 14, 15]);
#[cfg(kani_smallsort_controls)]
insertion_safety_cases!(insertion_safety_u64_n16_to20, [16, 17, 18, 19, 20]);

// Mutating comparisons overwrite both keys in tagged `Cell` values. These exact-length route and
// insertion harnesses check memory safety and normal return without assuming a sorted prefix.
fn mutating_key_order(a: &TaggedKeyCell, b: &TaggedKeyCell) -> bool {
    // SAFETY: both initialized Cell payloads must be readable before either write.
    let (left, right) =
        unsafe { (crate::ptr::read_volatile(a.as_ptr()), crate::ptr::read_volatile(b.as_ptr())) };
    let left_key: u8 = kani::any();
    let right_key: u8 = kani::any();
    a.set(TaggedKey { key: left_key, tag: left.tag });
    b.set(TaggedKey { key: right_key, tag: right.tag });
    // Keep the in-sort witness available to coverage audits without retaining its long trace
    // in every ordinary proof. The standalone witness below checks the same key mutation.
    #[cfg(kani_smallsort_controls)]
    proof_cover!(
        left_key != left.key && right_key != right.key,
        "mutating comparator changes both keys",
    );
    kani::any()
}

// The comparator still chooses both full-width keys and its result independently. This small
// witness avoids recording an entire sort execution just to exhibit one key-changing call.
#[kani::proof]
fn mutating_comparator_changes_both_keys() {
    let a = TaggedKeyCell::new(TaggedKey { key: kani::any(), tag: kani::any() });
    let b = TaggedKeyCell::new(TaggedKey { key: kani::any(), tag: kani::any() });
    let old_a = a.get();
    let old_b = b.get();
    let _ = mutating_key_order(&a, &b);
    kani::cover(
        a.get().key != old_a.key && b.get().key != old_b.key,
        "mutating comparator changes both keys",
    );
}

fn tagged_values<const N: usize>() -> [TaggedKeyCell; N] {
    crate::array::from_fn(|_| TaggedKeyCell::new(TaggedKey { key: kani::any(), tag: kani::any() }))
}

fn mutating_route_fixed<const N: usize>(stable: bool) {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = tagged_values::<N>();
    if stable {
        let mut scratch = [];
        <TaggedKeyCell as StableSmallSortTypeImpl>::small_sort(
            &mut v,
            &mut scratch,
            &mut mutating_key_order,
        );
    } else {
        <TaggedKeyCell as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut mutating_key_order);
    }
}

macro_rules! mutating_route_cases {
    ($name:ident, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(35)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => mutating_route_fixed::<$n>(stable),)+
                _ => {}
            }
            $(
                proof_cover!(
                    stable && len == $n,
                    concat!("stable mutating route returns normally at ", stringify!($n))
                );
                proof_cover!(
                    !stable && len == $n,
                    concat!("unstable mutating route returns normally at ", stringify!($n))
                );
            )+
        }
    };
}

fn mutating_insertion_fixed<const N: usize>() {
    let mut v = tagged_values::<N>();
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    insertion_at_any_offset!(&mut v, offset, N, &mut mutating_key_order);
    proof_cover!(offset == 1, "mutating insertion at offset one returns normally");
    proof_cover!(offset == N, "mutating insertion at final offset returns normally");
}

macro_rules! mutating_insertion_cases {
    ($name:ident, [$($n:literal),+]) => {
        mutating_insertion_cases!($name, [$($n),+], 35);
    };
    ($name:ident, [$($n:literal),+], $unwind:literal) => {
        #[kani::proof]
        #[kani::unwind($unwind)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => mutating_insertion_fixed::<$n>(),)+
                _ => {}
            }
            $(proof_cover!(
                len == $n,
                concat!("mutating insertion returns normally at ", stringify!($n))
            );)+
        }
    };
}

mutating_route_cases!(mutating_route_safety_cell_n0_to4, [0, 1, 2, 3, 4]);
mutating_route_cases!(mutating_route_safety_cell_n5_to8, [5, 6, 7, 8]);
mutating_route_cases!(mutating_route_safety_cell_n9_to12, [9, 10, 11, 12]);
mutating_route_cases!(mutating_route_safety_cell_n13_to16, [13, 14, 15, 16]);
mutating_insertion_cases!(mutating_insertion_safety_cell_n1_to5, [1, 2, 3, 4, 5]);
mutating_insertion_cases!(mutating_insertion_safety_cell_n6_to10, [6, 7, 8, 9, 10]);
#[cfg(kani_smallsort_controls)]
mutating_insertion_cases!(mutating_insertion_safety_cell_n11_to15, [11, 12, 13, 14, 15]);
#[cfg(kani_smallsort_controls)]
mutating_insertion_cases!(mutating_insertion_safety_cell_n16_to20, [16, 17, 18, 19, 20]);

insertion_safety_cases!(insertion_safety_u64_n11_to12, [11, 12]);
#[cfg(kani_smallsort_controls)]
insertion_safety_cases!(insertion_safety_u64_n13_to15, [13, 14, 15]);
// The two proofs partition the former length domain exactly. Unwinding assertions remain on;
// each bound exceeds its exact array length, including array initialization and insertion loops.
mutating_insertion_cases!(mutating_insertion_safety_cell_n11, [11], 13);
mutating_insertion_cases!(mutating_insertion_safety_cell_n12, [12], 14);
#[cfg(kani_smallsort_controls)]
mutating_insertion_cases!(mutating_insertion_safety_cell_n13_to15, [13, 14, 15]);

insertion_safety_cases!(insertion_safety_u64_n13, [13]);
insertion_safety_cases!(insertion_safety_u64_n14, [14]);
#[cfg(kani_smallsort_controls)]
insertion_safety_cases!(insertion_safety_u64_n15, [15]);
mutating_insertion_cases!(mutating_insertion_safety_cell_n13, [13]);
mutating_insertion_cases!(mutating_insertion_safety_cell_n14, [14]);
#[cfg(kani_smallsort_controls)]
mutating_insertion_cases!(mutating_insertion_safety_cell_n15, [15]);

// Exact-length cases check the actual offset-one insertion call for both ordinary and mutating
// Cell comparators. The array itself supplies the bounds for the real insertion body.
#[cfg(kani_smallsort_controls)]
macro_rules! insertion_offset_one_cases {
    ($plain:ident, $cell:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $plain() {
            let mut v: [u64; $n] = kani::any();
            super::super::insertion_sort_shift_left(&mut v, 1, &mut volatile_reading_less_u64);
            proof_cover!(
                true,
                concat!("u64 insertion at offset one returns normally at length ", stringify!($n)),
            );
        }

        #[kani::proof]
        #[kani::unwind(25)]
        fn $cell() {
            let mut v = tagged_values::<$n>();
            super::super::insertion_sort_shift_left(&mut v, 1, &mut mutating_key_order);
            proof_cover!(
                true,
                concat!("Cell insertion at offset one returns normally at length ", stringify!($n)),
            );
        }
    };
}

#[cfg(kani_smallsort_controls)]
insertion_offset_one_cases!(
    insertion_safety_u64_n16_offset1,
    mutating_insertion_safety_cell_n16_offset1,
    16
);
#[cfg(kani_smallsort_controls)]
insertion_offset_one_cases!(
    insertion_safety_u64_n17_offset1,
    mutating_insertion_safety_cell_n17_offset1,
    17
);
#[cfg(kani_smallsort_controls)]
insertion_offset_one_cases!(
    insertion_safety_u64_n18_offset1,
    mutating_insertion_safety_cell_n18_offset1,
    18
);
#[cfg(kani_smallsort_controls)]
insertion_offset_one_cases!(
    insertion_safety_u64_n19_offset1,
    mutating_insertion_safety_cell_n19_offset1,
    19
);
#[cfg(kani_smallsort_controls)]
insertion_offset_one_cases!(
    insertion_safety_u64_n20_offset1,
    mutating_insertion_safety_cell_n20_offset1,
    20
);

// The groups partition all valid offsets for each exact array length. Each listed offset becomes a
// constant call-site value; comparisons are unconstrained and no sorted-prefix contract is assumed.
macro_rules! insertion_offset_group_cases {
    ($plain:ident, $cell:ident, $n:literal, [$($o:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $plain() {
            const { $(assert!($o >= 1 && $o <= $n);)+ };
            let mut v: [u64; $n] = kani::any();
            let offset: usize = kani::any_where(|&o| matches!(o, $($o)|+));
            match offset {
                $($o => insertion_at::<_, _, $o>(&mut v, &mut volatile_reading_less_u64),)+
                _ => unreachable!(),
            }
            $(proof_cover!(offset == $o, concat!("insertion offset ", stringify!($o)));)+
        }

        #[kani::proof]
        #[kani::unwind(35)]
        fn $cell() {
            const { $(assert!($o >= 1 && $o <= $n);)+ };
            let mut v = tagged_values::<$n>();
            let offset: usize = kani::any_where(|&o| matches!(o, $($o)|+));
            match offset {
                $($o => insertion_at::<_, _, $o>(&mut v, &mut mutating_key_order),)+
                _ => unreachable!(),
            }
            $(proof_cover!(offset == $o, concat!("mutating insertion offset ", stringify!($o)));)+
        }
    };
}

insertion_offset_group_cases!(
    insertion_safety_u64_n15_offsets1_to4,
    mutating_insertion_safety_cell_n15_offsets1_to4,
    15,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n15_offsets5_to8,
    mutating_insertion_safety_cell_n15_offsets5_to8,
    15,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n15_offsets9_to12,
    mutating_insertion_safety_cell_n15_offsets9_to12,
    15,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n15_offsets13_to15,
    mutating_insertion_safety_cell_n15_offsets13_to15,
    15,
    [13, 14, 15]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n16_offsets1_to4,
    mutating_insertion_safety_cell_n16_offsets1_to4,
    16,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n16_offsets5_to8,
    mutating_insertion_safety_cell_n16_offsets5_to8,
    16,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n16_offsets9_to12,
    mutating_insertion_safety_cell_n16_offsets9_to12,
    16,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n16_offsets13_to16,
    mutating_insertion_safety_cell_n16_offsets13_to16,
    16,
    [13, 14, 15, 16]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n17_offsets1_to4,
    mutating_insertion_safety_cell_n17_offsets1_to4,
    17,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n17_offsets5_to8,
    mutating_insertion_safety_cell_n17_offsets5_to8,
    17,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n17_offsets9_to12,
    mutating_insertion_safety_cell_n17_offsets9_to12,
    17,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n17_offsets13_to15,
    mutating_insertion_safety_cell_n17_offsets13_to15,
    17,
    [13, 14, 15]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n17_offsets16_to17,
    mutating_insertion_safety_cell_n17_offsets16_to17,
    17,
    [16, 17]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n18_offsets1_to4,
    mutating_insertion_safety_cell_n18_offsets1_to4,
    18,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n18_offsets5_to8,
    mutating_insertion_safety_cell_n18_offsets5_to8,
    18,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n18_offsets9_to12,
    mutating_insertion_safety_cell_n18_offsets9_to12,
    18,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n18_offsets13_to16,
    mutating_insertion_safety_cell_n18_offsets13_to16,
    18,
    [13, 14, 15, 16]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n18_offsets17_to18,
    mutating_insertion_safety_cell_n18_offsets17_to18,
    18,
    [17, 18]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n19_offsets1_to4,
    mutating_insertion_safety_cell_n19_offsets1_to4,
    19,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n19_offsets5_to8,
    mutating_insertion_safety_cell_n19_offsets5_to8,
    19,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n19_offsets9_to12,
    mutating_insertion_safety_cell_n19_offsets9_to12,
    19,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n19_offsets13_to16,
    mutating_insertion_safety_cell_n19_offsets13_to16,
    19,
    [13, 14, 15, 16]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n19_offsets17_to19,
    mutating_insertion_safety_cell_n19_offsets17_to19,
    19,
    [17, 18, 19]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n20_offsets1_to4,
    mutating_insertion_safety_cell_n20_offsets1_to4,
    20,
    [1, 2, 3, 4]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n20_offsets5_to8,
    mutating_insertion_safety_cell_n20_offsets5_to8,
    20,
    [5, 6, 7, 8]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n20_offsets9_to12,
    mutating_insertion_safety_cell_n20_offsets9_to12,
    20,
    [9, 10, 11, 12]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n20_offsets13_to16,
    mutating_insertion_safety_cell_n20_offsets13_to16,
    20,
    [13, 14, 15, 16]
);
insertion_offset_group_cases!(
    insertion_safety_u64_n20_offsets17_to20,
    mutating_insertion_safety_cell_n20_offsets17_to20,
    20,
    [17, 18, 19, 20]
);

// Full-width `u8` and `u64` arrays enter through the unstable trait with a strict total order.
// The checks assert sortedness and use probe counts to establish permutation.
fn strict_less<T: Ord>(a: &T, b: &T) -> bool {
    a < b
}

fn network_correctness_fixed<T: kani::Arbitrary + Copy + Ord, const N: usize>() {
    use super::super::UnstableSmallSortTypeImpl;
    let mut v: [T; N] = kani::any();
    let pre = v;
    let probe: T = kani::any();
    let mut cmp = strict_less::<T>;
    <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    assert!(is_sorted_by(&v, &mut cmp));
    // Below the network width, keep the direct full-route permutation proof.
    // At N >= 9, compose the structural network permutation with the separately checked
    // real insertion-tail permutation. This keeps its probe formula out of the network.
    if N < 9 {
        assert!(count_matching_values(&pre, &probe) == count_matching_values(&v, &probe));
    }
    proof_cover!(N < 2 || !prefix_unchanged(&v, &pre, 0), "trivial input or sort moves elements");
}

macro_rules! network_correctness_cases {
    ($name:ident, $t:ty, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => network_correctness_fixed::<$t, $n>(),)+
                _ => {}
            }
            $(proof_cover!(len == $n, concat!("sort returns normally at length ", stringify!($n)));)+
        }
    };
}

network_correctness_cases!(network_correctness_u8_n0_to2, u8, [0, 1, 2]);
network_correctness_cases!(network_correctness_u64_n0_to2, u64, [0, 1, 2]);
network_correctness_cases!(network_correctness_u8_n3_to4, u8, [3, 4]);
network_correctness_cases!(network_correctness_u64_n3_to4, u64, [3, 4]);

network_correctness_cases!(network_correctness_u8_n5, u8, [5]);
network_correctness_cases!(network_correctness_u64_n5, u64, [5]);
network_correctness_cases!(network_correctness_u8_n6, u8, [6]);
network_correctness_cases!(network_correctness_u64_n6, u64, [6]);

network_correctness_cases!(network_correctness_u8_n7, u8, [7]);
network_correctness_cases!(network_correctness_u64_n7, u64, [7]);
network_correctness_cases!(network_correctness_u8_n8, u8, [8]);
network_correctness_cases!(network_correctness_u64_n8, u64, [8]);

// Exact two-element compare-exchange contract checks use the real body across the listed element
// representations. The contract supplies its own bounds and distinct-index preconditions.
impl ArbitraryValue for u64 {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}

#[cfg(kani_smallsort_controls)]
fn zst_less(a: &(), b: &()) -> bool {
    // Read both ZST arguments through ptr::read, then retain the strict unit order.
    let _ = super::comparators::zst_aware_less(a, b);
    false
}
fn drop_value_less(a: &DropValue, b: &DropValue) -> bool {
    a.0 < b.0
}
fn cell_value_less(a: &crate::cell::Cell<i32>, b: &crate::cell::Cell<i32>) -> bool {
    a.get() < b.get()
}
fn array_key_less<const M: usize>(a: &[u8; M], b: &[u8; M]) -> bool {
    // All instantiated arrays have M > 0; the remaining bytes are full-width payload.
    a[0] < b[0]
}

fn swap_contract_fixed<T: ArbitraryValue, F: FnMut(&T, &T) -> bool>(mut cmp: F) {
    let mut v: [T; 2] = crate::array::from_fn(|_| T::arbitrary_value());
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    let taken = cmp(&v[b], &v[a]);
    // SAFETY: a and b are distinct initialized writable elements of the live exact array.
    unsafe {
        swap_if_less(v.as_mut_ptr(), a, b, &mut cmp);
    }
    proof_cover!(reverse, "swap contract covers indices 1 and 0");
    proof_cover!(!reverse, "swap contract covers indices 0 and 1");
    proof_cover!(size_of::<T>() == 0 || taken, "swap branch or zero-sized value");
    proof_cover!(!taken, "no-swap branch");
    proof_cover!(true, "swap contract reached the end");
}

macro_rules! swap_contract_exact_array_case {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof_for_contract(super::super::swap_if_less)]
        #[kani::unwind(180)]
        fn $name() {
            swap_contract_fixed::<$t, _>($cmp);
        }
    };
}

swap_contract_exact_array_case!(swap_contract_u8_n2, u8, strict_less::<u8>);
swap_contract_exact_array_case!(swap_contract_u64_n2, u64, strict_less::<u64>);
swap_contract_exact_array_case!(swap_contract_bytes85_n2, [u8; 85], array_key_less::<85>);
swap_contract_exact_array_case!(swap_contract_drop_u8_n2, DropValue, drop_value_less);
swap_contract_exact_array_case!(swap_contract_cell_i32_n2, crate::cell::Cell<i32>, cell_value_less);
// This zero-sized-type case is control-only because contract instrumentation does not support its
// unallocated pointer representation.
#[cfg(kani_smallsort_controls)]
swap_contract_exact_array_case!(swap_contract_zero_sized_n2, (), zst_less);
swap_contract_exact_array_case!(swap_contract_bytes16_n2, [u8; 16], array_key_less::<16>);
swap_contract_exact_array_case!(swap_contract_bytes17_n2, [u8; 17], array_key_less::<17>);
swap_contract_exact_array_case!(swap_contract_bytes86_n2, [u8; 86], array_key_less::<86>);

network_correctness_cases!(network_correctness_u8_n9, u8, [9]);
network_correctness_cases!(network_correctness_u64_n9, u64, [9]);
network_correctness_cases!(network_correctness_u8_n10, u8, [10]);
network_correctness_cases!(network_correctness_u64_n10, u64, [10]);

/// Full-value permutation of the real insertion suffix, independent of ordering. An arbitrary
/// read-only comparison result includes every sequence produced by the pure strict comparator.
/// No sorted-prefix assumption: all possible network outputs are included in this larger domain.
fn insertion_permutation_fixed<T: kani::Arbitrary + Copy + Eq, const N: usize>() {
    let mut v: [T; N] = kani::any();
    let pre = v;
    let probe: T = kani::any();
    if N >= 13 {
        super::super::insertion_sort_shift_left(&mut v, 13, &mut volatile_reading_less::<T>);
    } else {
        super::super::insertion_sort_shift_left(&mut v, 9, &mut volatile_reading_less::<T>);
    }
    assert!(count_matching_values(&pre, &probe) == count_matching_values(&v, &probe));
    proof_cover!(
        !prefix_unchanged(&v, &pre, 0),
        "insertion preserves permutation and moves elements",
    );
}

macro_rules! insertion_permutation_case {
    ($name:ident, $t:ty, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            insertion_permutation_fixed::<$t, $n>();
        }
    };
}

insertion_permutation_case!(insertion_permutation_u8_n10, u8, 10);
insertion_permutation_case!(insertion_permutation_u64_n10, u64, 10);

network_correctness_cases!(network_correctness_u8_n11, u8, [11]);
network_correctness_cases!(network_correctness_u64_n11, u64, [11]);
insertion_permutation_case!(insertion_permutation_u8_n11, u8, 11);
insertion_permutation_case!(insertion_permutation_u64_n11, u64, 11);

network_correctness_cases!(network_correctness_u8_n12, u8, [12]);
network_correctness_cases!(network_correctness_u64_n12, u64, [12]);
insertion_permutation_case!(insertion_permutation_u8_n12, u8, 12);
insertion_permutation_case!(insertion_permutation_u64_n12, u64, 12);

network_correctness_cases!(network_correctness_u8_n13, u8, [13]);
network_correctness_cases!(network_correctness_u64_n13, u64, [13]);

network_correctness_cases!(network_correctness_u8_n14, u8, [14]);
network_correctness_cases!(network_correctness_u64_n14, u64, [14]);
insertion_permutation_case!(insertion_permutation_u8_n14, u8, 14);
insertion_permutation_case!(insertion_permutation_u64_n14, u64, 14);

network_correctness_cases!(network_correctness_u8_n15, u8, [15]);
#[cfg(kani_smallsort_controls)]
network_correctness_cases!(network_correctness_u64_n15, u64, [15]);
insertion_permutation_case!(insertion_permutation_u8_n15, u8, 15);
insertion_permutation_case!(insertion_permutation_u64_n15, u64, 15);

network_correctness_cases!(network_correctness_u8_n16, u8, [16]);
#[cfg(kani_smallsort_controls)]
network_correctness_cases!(network_correctness_u64_n16, u64, [16]);
#[cfg(kani_smallsort_controls)]
insertion_permutation_case!(insertion_permutation_u8_n16, u8, 16);
#[cfg(kani_smallsort_controls)]
insertion_permutation_case!(insertion_permutation_u64_n16, u64, 16);

network_correctness_cases!(network_correctness_u8_n17, u8, [17]);
#[cfg(kani_smallsort_controls)]
network_correctness_cases!(network_correctness_u64_n17, u64, [17]);
#[cfg(kani_smallsort_controls)]
insertion_permutation_case!(insertion_permutation_u8_n17, u8, 17);
#[cfg(kani_smallsort_controls)]
insertion_permutation_case!(insertion_permutation_u64_n17, u64, 17);

// Contract checks choose distinct positions in selected exact arrays of lengths 9 through 17.
// The comparator is the same strict total order used by the network correctness harnesses.
fn swap_contract_indices<T: kani::Arbitrary + Copy + Ord, const N: usize>() {
    const { assert!(N >= 9 && N <= 17) };
    let mut v: [T; N] = kani::any();
    let pre = v;
    let a: usize = kani::any_where(|&i| i < N);
    let b: usize = kani::any_where(|&i| i < N && i != a);
    let mut cmp = strict_less::<T>;
    let taken = cmp(&v[b], &v[a]);
    // SAFETY: a and b are distinct in-bounds initialized writable elements of v.
    unsafe {
        swap_if_less(v.as_mut_ptr(), a, b, &mut cmp);
    }
    let mut i = 0;
    while i < N {
        if i != a && i != b {
            assert!(v[i] == pre[i], "swap contract covers other cells unchanged");
        }
        i += 1;
    }
    proof_cover!(a == 0 && b == N - 1, "swap contract covers first to last");
    proof_cover!(a == N - 1 && b == 0, "swap contract covers last to first");
    proof_cover!(a > 0 && a < N - 1 && b > 0 && b < N - 1, "swap contract covers interior pair");
    let network_last = if N >= 13 { 12 } else { 8 };
    proof_cover!(
        a == network_last || b == network_last,
        "swap contract covers network final position",
    );
    proof_cover!(taken, "swap contract covers swap branch");
    proof_cover!(!taken, "swap contract covers no-swap branch");
    proof_cover!(true, "swap contract covers end reached");
}

#[kani::proof_for_contract(super::super::swap_if_less)]
#[kani::unwind(25)]
fn swap_contract_u8_indices_n17() {
    swap_contract_indices::<u8, 17>();
}

#[kani::proof_for_contract(super::super::swap_if_less)]
#[kani::unwind(25)]
fn swap_contract_u64_indices_n17() {
    swap_contract_indices::<u64, 17>();
}

macro_rules! swap_contract_arbitrary_indices_case {
    ($name:ident, $t:ty, $n:literal) => {
        #[kani::proof_for_contract(super::super::swap_if_less)]
        #[kani::unwind(25)]
        fn $name() {
            swap_contract_indices::<$t, $n>();
        }
    };
}

swap_contract_arbitrary_indices_case!(swap_contract_u8_n9, u8, 9);
swap_contract_arbitrary_indices_case!(swap_contract_u8_n12, u8, 12);
swap_contract_arbitrary_indices_case!(swap_contract_u8_n13, u8, 13);
swap_contract_arbitrary_indices_case!(swap_contract_u8_n16, u8, 16);
swap_contract_arbitrary_indices_case!(swap_contract_u64_n9, u64, 9);
swap_contract_arbitrary_indices_case!(swap_contract_u64_n12, u64, 12);
swap_contract_arbitrary_indices_case!(swap_contract_u64_n13, u64, 13);
swap_contract_arbitrary_indices_case!(swap_contract_u64_n16, u64, 16);

// Checks insertion into every nonempty interior region of an exact `[u64; 17]` array. The
// `proof_for_contract` harness supplies the callee's sorted-prefix precondition.
fn insert_tail_value<const START: usize>(fixed_tail: Option<usize>) -> usize {
    set_value_probe::<u64>();
    let mut v: [u64; 17] = kani::any();
    let tail: usize = match fixed_tail {
        Some(tail) => tail,
        None => kani::any_where(|&t| START < t && t < 17),
    };
    let pre = v;
    let base = v.as_mut_ptr();
    // SAFETY: each instantiation has 1 <= START <= 15, START < tail < 17; the
    // enclosing proof_for_contract assumes precisely insert_tail's own requires.
    unsafe {
        super::super::insert_tail(base.add(START), base.add(tail), &mut lt_u64);
    }
    let mut i = 0;
    while i < START {
        assert!(v[i] == pre[i], "insert-tail contract covers prefix before begin unchanged");
        i += 1;
    }
    assert!(prefix_unchanged(&v, &pre, tail + 1), "suffix after inserted tail remains unchanged");
    proof_cover!(!prefix_unchanged(&v, &pre, 0), "insertion moves elements");
    proof_cover!(true, "insert-tail contract covers end reached");
    tail
}

macro_rules! insert_tail_contract_case {
    ($name:ident, $start:literal, [$($end:literal),+]) => {
        #[kani::proof_for_contract(super::super::insert_tail)]
        #[kani::unwind(25)]
        fn $name() {
            let tail = insert_tail_value::<$start>(None);
            $(proof_cover!(
                tail == $end,
                concat!(
                    "insert-tail contract covers tail ",
                    stringify!($end),
                    " with requires satisfied"
                )
            );)+
        }
    };
}

macro_rules! insert_tail_contract_exact_case {
    ($name:ident, $start:literal, $end:literal) => {
        #[kani::proof_for_contract(super::super::insert_tail)]
        #[kani::unwind(25)]
        fn $name() {
            let tail = insert_tail_value::<$start>(Some($end));
            proof_cover!(
                tail == $end,
                concat!(
                    "insert-tail contract covers exact tail ",
                    stringify!($end),
                    " with requires satisfied"
                ),
            );
        }
    };
}

insert_tail_contract_case!(insert_tail_contract_u64_start15, 15, [16]);
insert_tail_contract_case!(insert_tail_contract_u64_start14, 14, [15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start13, 13, [14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start12, 12, [13, 14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start11, 11, [12, 13, 14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start10, 10, [11, 12, 13, 14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start9, 9, [10, 11, 12, 13, 14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start8, 8, [9, 10, 11, 12, 13, 14, 15, 16]);
insert_tail_contract_case!(insert_tail_contract_u64_start7, 7, [8, 9, 10, 11, 12, 13, 14, 15, 16]);
insert_tail_contract_case!(
    insert_tail_contract_u64_start6,
    6,
    [7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
);
insert_tail_contract_case!(
    insert_tail_contract_u64_start5,
    5,
    [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail5, 4, 5);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail6, 4, 6);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail7, 4, 7);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail8, 4, 8);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail9, 4, 9);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail10, 4, 10);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail11, 4, 11);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail12, 4, 12);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail13, 4, 13);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail14, 4, 14);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail15, 4, 15);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start4_tail16, 4, 16);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail4, 3, 4);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail5, 3, 5);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail6, 3, 6);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail7, 3, 7);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail8, 3, 8);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail9, 3, 9);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail10, 3, 10);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail11, 3, 11);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail12, 3, 12);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail13, 3, 13);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail14, 3, 14);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail15, 3, 15);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start3_tail16, 3, 16);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail3, 2, 3);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail4, 2, 4);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail5, 2, 5);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail6, 2, 6);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail7, 2, 7);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail8, 2, 8);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail9, 2, 9);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail10, 2, 10);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail11, 2, 11);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail12, 2, 12);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail13, 2, 13);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail14, 2, 14);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail15, 2, 15);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start2_tail16, 2, 16);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail2, 1, 2);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail3, 1, 3);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail4, 1, 4);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail5, 1, 5);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail6, 1, 6);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail7, 1, 7);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail8, 1, 8);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail9, 1, 9);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail10, 1, 10);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail11, 1, 11);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail12, 1, 12);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail13, 1, 13);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail14, 1, 14);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail15, 1, 15);
insert_tail_contract_exact_case!(insert_tail_contract_u64_start1_tail16, 1, 16);

// At lengths 2 through 4, checks tag multiplicities after stable, unstable, or insertion routes
// whose comparator may rewrite keys. No ordering precondition is assumed.
fn mutating_route_permutation<const N: usize>() -> (u8, usize) {
    use super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v = tagged_values::<N>();
    let probe: u8 = kani::any();
    let before = count_tagged_values(&v, probe);
    let tags = tag_sequence(&v);
    let mode: u8 = kani::any_where(|&m| m < 3);
    let offset: usize = kani::any_where(|&o| 1 <= o && o <= N);
    if mode == 0 {
        let mut scratch = [];
        <TaggedKeyCell as StableSmallSortTypeImpl>::small_sort(
            &mut v,
            &mut scratch,
            &mut mutating_key_order,
        );
    } else if mode == 1 {
        <TaggedKeyCell as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut mutating_key_order);
    } else {
        insertion_at_any_offset!(&mut v, offset, N, &mut mutating_key_order);
    }
    assert!(before == count_tagged_values(&v, probe), "tag multiplicity is preserved");
    let moved = tags != tag_sequence(&v);
    proof_cover!(mode == 0 && moved, "stable route moves a tag");
    proof_cover!(mode == 1 && moved, "unstable route moves a tag");
    proof_cover!(mode == 2 && moved, "insertion route moves a tag");
    proof_cover!(true, "tag permutation check reached the end");
    (mode, offset)
}

macro_rules! mutating_route_permutation_case {
    ($name:ident, $n:literal, [$($offset:literal),+]) => {
        #[kani::proof]
        #[kani::unwind(25)]
        fn $name() {
            let (mode, offset) = mutating_route_permutation::<$n>();
            $(proof_cover!(
                mode == 2 && offset == $offset,
                concat!("insertion route returns normally at offset ", stringify!($offset))
            );)+
        }
    };
}

mutating_route_permutation_case!(mutating_route_permutation_cell_n2, 2, [1, 2]);
mutating_route_permutation_case!(mutating_route_permutation_cell_n3, 3, [1, 2, 3]);
mutating_route_permutation_case!(mutating_route_permutation_cell_n4, 4, [1, 2, 3, 4]);

// Negative control applies the one-change network copy to the same exact input and assertions.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(25)]
#[kani::stub(super::super::small_sort_network, super::mutations::mutant_small_sort_network)]
fn control_network_mutant_presorted_u8_n10() {
    network_correctness_u8_n10();
}
