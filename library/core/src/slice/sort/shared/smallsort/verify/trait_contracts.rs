//! Two-element calibration of trait contracts and their slice write sets.
//! Comparators write nowhere else; these contracts do not promise sortedness.

use super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
};
use crate::kani;
use crate::mem::MaybeUninit;

fn trait_less_u64(a: &u64, b: &u64) -> bool {
    a < b
}

fn trait_input_covers(input_descending: bool) {
    kani::cover(input_descending, "descending input returns");
    kani::cover(!input_descending, "non-descending input returns");
    kani::cover(true, "trait small_sort returns");
}

#[kani::proof_for_contract(<u64 as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn stable_safety_u64_len2() {
    let mut v: [u64; 2] = kani::any();
    let input_descending = v[1] < v[0];
    let mut scratch = [MaybeUninit::<u64>::uninit(); 18];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut trait_less_u64);
    trait_input_covers(input_descending);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn unstable_safety_u64_len2() {
    let mut v: [u64; 2] = kani::any();
    let input_descending = v[1] < v[0];
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut trait_less_u64);
    trait_input_covers(input_descending);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn freeze_safety_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let input_descending = v[1] < v[0];
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut trait_less_u64);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
    trait_input_covers(input_descending);
}

#[kani::proof]
#[kani::unwind(32)]
fn real_forwarding_sorts_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut trait_less_u64);
    kani::assert(v[0] <= v[1], "forwarded output is sorted");
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
}

#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn verified_forwarding_frame_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut trait_less_u64);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
}

#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn rejects_verified_forwarding_sorted_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut trait_less_u64);
    kani::assert(v[0] <= v[1], "forwarded output is sorted");
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
}
