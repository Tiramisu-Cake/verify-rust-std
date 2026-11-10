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

// G2 roots use an explicit fn pointer so model specialization is enabled.
use super::trait_model::{PairModel, U64Cmp, canonical_less_u64};

fn strong_input_covers(input_descending: bool, input_equal: bool) {
    kani::cover(input_descending, "strong descending input returns");
    kani::cover(!input_descending, "strong non-descending input returns");
    kani::cover(input_equal, "strong equal input returns");
    kani::cover(true, "strong trait small_sort returns");
}

#[kani::proof_for_contract(<u64 as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn stable_ensures_u64_len2() {
    let mut v: [u64; 2] = kani::any();
    let input_descending = v[1] < v[0];
    let input_equal = v[0] == v[1];
    let mut scratch = [MaybeUninit::<u64>::uninit(); 18];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());
    kani::assert(enabled, "strong model enabled before call");
    kani::cover(enabled, "strong model enabled before call");
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    strong_input_covers(input_descending, input_equal);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn unstable_ensures_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let input_descending = v[1] < v[0];
    let input_equal = v[0] == v[1];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());
    kani::assert(enabled, "strong model enabled before call");
    kani::cover(enabled, "strong model enabled before call");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
    strong_input_covers(input_descending, input_equal);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn freeze_ensures_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let input_descending = v[1] < v[0];
    let input_equal = v[0] == v[1];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());
    kani::assert(enabled, "strong model enabled before call");
    kani::cover(enabled, "strong model enabled before call");
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
    strong_input_covers(input_descending, input_equal);
}

#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn verified_forwarding_ensures_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let pre = (v[0], v[1]);
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());
    kani::assert(enabled, "strong model enabled before call");
    kani::cover(enabled, "strong model enabled before call");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(v[0] <= v[1], "strong forwarded output is sorted");
    kani::assert(
        (v[0] == pre.0 && v[1] == pre.1) || (v[0] == pre.1 && v[1] == pre.0),
        "strong forwarded output preserves full pair",
    );
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
}

#[kani::proof]
#[kani::unwind(32)]
fn rejects_high_bit_corruption_u64_pair() {
    let mut v: [u64; 2] = kani::any();
    let pre = (v[0], v[1]);
    kani::assert(
        <() as PairModel<u64, U64Cmp>>::pair_permutation(v.as_ptr(), v.len(), pre),
        "unchanged full pair passes checker",
    );
    v[0] ^= 1u64 << 63;
    kani::assert(
        <() as PairModel<u64, U64Cmp>>::pair_permutation(v.as_ptr(), v.len(), pre),
        "high-bit corruption preserves full pair",
    );
}

fn reverse_less(a: &u64, b: &u64) -> bool {
    a > b
}

#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn rejects_reverse_pointer_sorted_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let mut cmp: U64Cmp = reverse_less;
    let enabled = <() as PairModel<u64, U64Cmp>>::enabled(&cmp, v.len());
    kani::assert(!enabled, "reverse pointer disables strong model");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(v[0] <= v[1], "reverse pointer output is sorted");
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
}
