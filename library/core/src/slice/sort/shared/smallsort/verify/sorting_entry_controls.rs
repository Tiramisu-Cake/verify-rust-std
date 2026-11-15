//! Legal companions and isolated CI-only false-ensures activation variants.
//! The variants change exactly the actual method ensures, never this fixture.

use super::super::StableSmallSortTypeImpl;
use super::sorting_model::{KeyLess, enabled, post, snapshot};
use crate::cell::Cell;
use crate::kani;
use crate::mem::MaybeUninit;

#[kani::proof_for_contract(<Cell<u8> as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(34)]
fn stable_default_activation() {
    let mut v = [Cell::new(2u8), Cell::new(1u8)];
    assert!(enabled::<Cell<u8>, KeyLess<Cell<u8>>>(), "S1_ACTUAL_DEFAULT_ENABLED");
    let before = snapshot::<Cell<u8>, KeyLess<Cell<u8>>>(&v);
    let mut scratch: [MaybeUninit<Cell<u8>>; 0] = [];
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(
        &mut v, &mut scratch, &mut KeyLess::<Cell<u8>>::new());
    assert!(post::<Cell<u8>, KeyLess<Cell<u8>>>(before, &v), "S1_DEFAULT_COMPANION_POST");
    kani::cover(true, "S1_actual_default_companion_return");
}

#[kani::proof_for_contract(<u8 as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(34)]
fn stable_freeze_activation() {
    let mut v = [2u8, 1u8];
    assert!(enabled::<u8, KeyLess<u8>>(), "S1_ACTUAL_OVERRIDE_ENABLED");
    let before = snapshot::<u8, KeyLess<u8>>(&v);
    let mut scratch: [MaybeUninit<u8>; 18] = [MaybeUninit::uninit(); 18];
    <u8 as StableSmallSortTypeImpl>::small_sort(
        &mut v, &mut scratch, &mut KeyLess::<u8>::new());
    assert!(post::<u8, KeyLess<u8>>>(before, &v), "S1_OVERRIDE_COMPANION_POST");
    kani::cover(true, "S1_actual_override_companion_return");
}
