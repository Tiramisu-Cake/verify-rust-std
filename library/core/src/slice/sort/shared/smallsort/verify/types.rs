//! Logical-value correctness through real trait entries; no contracts or panic paths are stubbed.

use super::super::{
    SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl, UnstableSmallSortTypeImpl,
};
use crate::cell::Cell;
use crate::kani;
use crate::mem::MaybeUninit;

trait LogicalByte {
    fn new(value: u8) -> Self;
    fn value(&self) -> u8;
}

impl LogicalByte for Cell<u8> {
    fn new(value: u8) -> Self {
        Cell::new(value)
    }

    fn value(&self) -> u8 {
        self.get()
    }
}

#[repr(transparent)]
struct DropKey(u8);

impl crate::ops::Drop for DropKey {
    fn drop(&mut self) {}
}

impl LogicalByte for DropKey {
    fn new(value: u8) -> Self {
        Self(value)
    }

    fn value(&self) -> u8 {
        self.0
    }
}

fn logical_less<T: LogicalByte>(a: &T, b: &T) -> bool {
    a.value() < b.value()
}

fn count(values: &[u8], probe: u8) -> usize {
    let mut count = 0;
    for value in values {
        count += (*value == probe) as usize;
    }
    count
}

fn check_output<const N: usize>(input: &[u8; N], output: &[u8; N], probe: u8) {
    for i in 1..N {
        assert!(output[i - 1] <= output[i], "logical output is sorted");
    }
    assert!(count(input, probe) == count(output, probe), "logical multiset is preserved");
    kani::cover(true, "logical sort returns after both assertions");
}

fn cover_nontrivial_input<const N: usize>(input: &[u8; N]) {
    kani::cover(input[0] > input[1], "logical sort returns from an unsorted input");
    kani::cover(input[0] == input[1], "logical sort returns with duplicate keys");
}

// Cell is !Freeze: both trait defaults use insertion/fallback, with threshold 16.
// DropKey is Freeze and non-Copy: stable and unstable dispatch select general, threshold 32.
fn trait_properties<T: LogicalByte, const N: usize>() -> [u8; N] {
    let input: [u8; N] = kani::any();
    let probe: u8 = kani::any();
    let mut values: [T; N] = crate::array::from_fn(|i| T::new(input[i]));
    let stable: bool = kani::any();
    if stable {
        let mut scratch = [const { MaybeUninit::<T>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
        <T as StableSmallSortTypeImpl>::small_sort(
            &mut values,
            &mut scratch,
            &mut logical_less::<T>,
        );
    } else {
        <T as UnstableSmallSortTypeImpl>::small_sort(&mut values, &mut logical_less::<T>);
    }
    let output = crate::array::from_fn(|i| values[i].value());
    check_output(&input, &output, probe);
    kani::cover(stable, "logical stable trait entry returns");
    kani::cover(!stable, "logical unstable trait entry returns");
    input
}

fn trivial_trait_properties<T: LogicalByte>() {
    let selector: u8 = kani::any();
    match selector {
        0 => {
            trait_properties::<T, 0>();
        }
        1 => {
            trait_properties::<T, 1>();
        }
        _ => cover_nontrivial_input(&trait_properties::<T, 2>()),
    }
    kani::cover(selector == 0, "logical length zero");
    kani::cover(selector == 1, "logical length one");
    kani::cover(selector == 2, "logical length two");
}

macro_rules! trait_cases {
    ($name:ident, $t:ty, [0, 1, 2]) => {
        #[kani::proof]
        #[kani::solver(cadical)]
        #[kani::unwind(50)]
        fn $name() {
            trivial_trait_properties::<$t>();
        }
    };
    ($name:ident, $t:ty, [$a:literal, $b:literal, $c:literal]) => {
        #[kani::proof]
        #[kani::solver(cadical)]
        #[kani::unwind(50)]
        fn $name() {
            let selector: u8 = kani::any();
            match selector {
                0 => cover_nontrivial_input(&trait_properties::<$t, $a>()),
                1 => cover_nontrivial_input(&trait_properties::<$t, $b>()),
                _ => cover_nontrivial_input(&trait_properties::<$t, $c>()),
            }
            kani::cover(selector == 0, concat!("logical length ", stringify!($a)));
            kani::cover(selector == 1, concat!("logical length ", stringify!($b)));
            kani::cover(selector == 2, concat!("logical length ", stringify!($c)));
        }
    };
}

trait_cases!(sorted_permutation_traits_fallback_cell_u8_n0_to2, Cell<u8>, [0, 1, 2]);
// Cell N7/8/9 timed out at 600 s; Drop N7/8/9 took 349.69 s (C3a, 2026-10-28).
// Keep these grouped experiments opt-in; neither establishes CI suitability.
#[cfg(kani_smallsort_controls)]
trait_cases!(sorted_permutation_traits_fallback_cell_u8_n7_to9, Cell<u8>, [7, 8, 9]);
trait_cases!(sorted_permutation_traits_general_drop_u8_n0_to2, DropKey, [0, 1, 2]);
#[cfg(kani_smallsort_controls)]
trait_cases!(sorted_permutation_traits_general_drop_u8_n7_to9, DropKey, [7, 8, 9]);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(50)]
fn control_sorted_permutation_traits_cell_drop_n0_to2() {
    if kani::any() {
        trivial_trait_properties::<Cell<u8>>();
    } else {
        trivial_trait_properties::<DropKey>();
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(4)]
fn reject_logical_sortedness_cell_n2() {
    // Reversing a sorted pair preserves the multiset but must fail the sortedness assertion.
    let mut values = [Cell::new(2), Cell::new(1)];
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(&mut values, &mut logical_less);
    values.swap(0, 1);
    check_output(&[2, 1], &[values[0].get(), values[1].get()], kani::any());
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(4)]
fn reject_logical_permutation_drop_n2() {
    // Overwriting by zero stays sorted but loses one occurrence of logical value one.
    let mut values = [DropKey(1), DropKey(0)];
    <DropKey as UnstableSmallSortTypeImpl>::small_sort(&mut values, &mut logical_less);
    values[1].0 = 0;
    check_output(&[1, 0], &[values[0].0, values[1].0], 1);
}
