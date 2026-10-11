// Compiler binding query fixture. The trait and both impl blocks below are copied
// byte-for-byte from the pinned SmallSort source. Helper bodies and non-base
// continuations are diagnostic cuts; this fixture claims no sorting proof.
#![feature(freeze, rustc_attrs, min_specialization)]
#![allow(internal_features, dead_code, unused_variables)]
use std::cell::Cell;
use std::marker::Freeze;
use std::mem::MaybeUninit;

#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}

impl<T: Freeze> FreezeMarker for T {}

pub(crate) trait StableSmallSortTypeImpl: Sized {
    /// For which input length <= return value of this function, is it valid to call `small_sort`.
    fn small_sort_threshold() -> usize;

    /// Sorts `v` using strategies optimized for small sizes.
    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    #[inline(always)]
    default fn small_sort_threshold() -> usize {
        // Optimal number of comparisons, and good perf.
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    #[inline(always)]
    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    #[inline(always)]
    fn small_sort_threshold() -> usize {
        SMALL_SORT_GENERAL_THRESHOLD
    }

    #[inline(always)]
    fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        small_sort_general_with_scratch(v, scratch, is_less);
    }
}

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

// Diagnostic transitive-body cuts; exact production callees are not exported
// or proved by this compiler selection query.
fn insertion_sort_shift_left<T, F: FnMut(&T, &T) -> bool>(
    _v: &mut [T], _offset: usize, _is_less: &mut F,
) {}
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    _v: &mut [T], _scratch: &mut [MaybeUninit<T>], _is_less: &mut F,
) {}

// Exact quicksort base-case statements; the non-base continuation is cut.
fn binding_selected_freeze<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T], scratch: &mut [MaybeUninit<T>],
    mut limit: u32, mut left_ancestor_pivot: Option<&T>, is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }
        return; // diagnostic cut before partition and recursion
    }
}

// Concrete non-Freeze control with the identical two trait calls and operands.
fn binding_fallback_cell<F: FnMut(&Cell<u8>, &Cell<u8>) -> bool>(
    mut v: &mut [Cell<u8>], scratch: &mut [MaybeUninit<Cell<u8>>],
    mut limit: u32, mut left_ancestor_pivot: Option<&Cell<u8>>, is_less: &mut F,
) {
    type T = Cell<u8>;
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }
        return; // diagnostic cut before partition and recursion
    }
}

// Actual quicksort's generic bound shape; this cannot inherit Freeze evidence.
fn binding_unconstrained_generic<T, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T], scratch: &mut [MaybeUninit<T>],
    mut limit: u32, mut left_ancestor_pivot: Option<&T>, is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }
        return; // diagnostic cut before partition and recursion
    }
}
