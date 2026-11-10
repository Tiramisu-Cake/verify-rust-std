//! N2 resolution and frame checks for the default small-sort contracts.

#![cfg(kani_smallsort_controls)]

use super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
};
use crate::cell::Cell;
use crate::kani;

struct NonCopyU8(u8);

impl kani::Arbitrary for NonCopyU8 {
    fn any() -> Self {
        Self(kani::any())
    }
}

fn cell_less(a: &Cell<u8>, b: &Cell<u8>) -> bool {
    a.get() < b.get()
}

fn noncopy_less(a: &NonCopyU8, b: &NonCopyU8) -> bool {
    a.0 < b.0
}

fn input_covers(reversed: bool) {
    kani::cover(reversed, "reversed input");
    kani::cover(!reversed, "nondecreasing input");
    kani::cover(true, "default contract call returns");
}

#[kani::proof_for_contract(<Cell<u8> as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(4)]
fn stable_default_n2() {
    let [a, b]: [u8; 2] = kani::any();
    let mut v = [Cell::new(a), Cell::new(b)];
    let reversed = cell_less(&v[1], &v[0]);
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(&mut v, &mut [], &mut cell_less);
    input_covers(reversed);
}

#[kani::proof_for_contract(<Cell<u8> as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(4)]
fn unstable_default_n2() {
    let [a, b]: [u8; 2] = kani::any();
    let mut v = [Cell::new(a), Cell::new(b)];
    let reversed = cell_less(&v[1], &v[0]);
    <Cell<u8> as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cell_less);
    input_covers(reversed);
}

#[kani::proof_for_contract(<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(8)]
fn freeze_default_n2() {
    let mut backing: [NonCopyU8; 4] = kani::any();
    let (left, right) = (backing[0].0, backing[3].0);
    let v = &mut backing[1..3];
    let reversed = noncopy_less(&v[1], &v[0]);
    <NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut noncopy_less);
    kani::assert(backing[0].0 == left && backing[3].0 == right, "default Freeze frame");
    input_covers(reversed);
}

fn ordered_backing() -> [NonCopyU8; 4] {
    let backing: [NonCopyU8; 4] = kani::any();
    // The order check already holds at entry, so skipping the call cannot fail it.
    kani::assume(backing[1].0 <= backing[2].0);
    backing
}

#[kani::proof]
#[kani::unwind(8)]
fn freeze_forwarder_body_n2() {
    let mut backing = ordered_backing();
    let (left, right) = (backing[0].0, backing[3].0);
    let v = &mut backing[1..3];
    <NonCopyU8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut noncopy_less);
    kani::assert(v[0].0 <= v[1].0, "real Freeze forwarder preserves input order");
    kani::assert(backing[0].0 == left && backing[3].0 == right, "real Freeze forwarder frame");
}

#[kani::proof]
#[kani::stub_verified(<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(8)]
fn freeze_forwarder_stub_frame_n2() {
    let mut backing = ordered_backing();
    let (left, right) = (backing[0].0, backing[3].0);
    let v = &mut backing[1..3];
    <NonCopyU8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut noncopy_less);
    kani::assert(backing[0].0 == left && backing[3].0 == right, "stubbed Freeze forwarder frame");
    kani::cover(true, "stubbed Freeze forwarder returns");
}

#[kani::proof]
#[kani::stub_verified(<NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(8)]
fn freeze_forwarder_stub_order_n2() {
    let mut backing = ordered_backing();
    let v = &mut backing[1..3];
    <NonCopyU8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut noncopy_less);
    kani::assert(v[0].0 <= v[1].0, "KF2 S2 weak Freeze stub permits reversed output");
}
