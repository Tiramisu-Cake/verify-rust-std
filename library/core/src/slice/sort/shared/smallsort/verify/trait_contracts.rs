//! Bounded trait sort contracts for canonical u64 ordering and full-value multiplicities.
//! Ordinary roots match the enabled entries at lengths two and three. Controls are opt-in.

use super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
};
use super::trait_model::{SortEntry, SortModel, U64Cmp, canonical_less_u64};
use crate::kani;
use crate::mem::MaybeUninit;

fn sort_input_covers(ascending: bool, descending: bool, duplicate: bool) {
    kani::cover(ascending, "ascending input returns");
    kani::cover(descending, "descending input returns");
    kani::cover(duplicate, "duplicate input returns");
    kani::cover(true, "trait small_sort returns");
}

#[kani::proof_for_contract(<u64 as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn stable_sorts_permutation_u64_len2() {
    let mut v: [u64; 2] = kani::any();
    let ascending = v[0] < v[1];
    let descending = v[1] < v[0];
    let duplicate = v[0] == v[1];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Stable, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    let mut scratch = [MaybeUninit::<u64>::uninit(); 18];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof_for_contract(<u64 as StableSmallSortTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn stable_sorts_permutation_u64_len3() {
    let mut v: [u64; 3] = kani::any();
    let ascending = v[0] < v[1] && v[1] < v[2];
    let descending = v[1] < v[0] && v[2] < v[1];
    let duplicate = v[0] == v[1] || v[0] == v[2] || v[1] == v[2];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Stable, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    let mut scratch = [MaybeUninit::<u64>::uninit(); 19];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn freeze_sorts_permutation_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let ascending = v[0] < v[1];
    let descending = v[1] < v[0];
    let duplicate = v[0] == v[1];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn freeze_sorts_permutation_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let ascending = v[0] < v[1] && v[1] < v[2];
    let descending = v[1] < v[0] && v[2] < v[1];
    let duplicate = v[0] == v[1] || v[0] == v[2] || v[1] == v[2];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn unstable_sorts_permutation_u64_backing4() {
    let mut backing: [u64; 4] = kani::any();
    let outside = [backing[0], backing[3]];
    let v = &mut backing[1..3];
    let ascending = v[0] < v[1];
    let descending = v[1] < v[0];
    let duplicate = v[0] == v[1];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Unstable, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[3] == outside[1], "outside slice unchanged");
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof_for_contract(<u64 as UnstableSmallSortTypeImpl>::small_sort)]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn unstable_sorts_permutation_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let ascending = v[0] < v[1] && v[1] < v[2];
    let descending = v[1] < v[0] && v[2] < v[1];
    let duplicate = v[0] == v[1] || v[0] == v[2] || v[1] == v[2];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Unstable, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
    sort_input_covers(ascending, descending, duplicate);
}

#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn verified_forwarding_sorts_permutation_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let pre = [v[0], v[1], v[2]];
    let ascending = v[0] < v[1] && v[1] < v[2];
    let descending = v[1] < v[0] && v[2] < v[1];
    let duplicate = v[0] == v[1] || v[0] == v[2] || v[1] == v[2];
    let mut cmp: U64Cmp = canonical_less_u64;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Unstable, &cmp, v.len())
        && <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(enabled, "sort model enabled before call");
    kani::cover(enabled, "sort model enabled before call");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(v[0] <= v[1] && v[1] <= v[2], "forwarded output is sorted");
    let post = [v[0], v[1], v[2]];
    let mut i = 0;
    while i < 3 {
        let mut pre_count = 0;
        let mut post_count = 0;
        let mut j = 0;
        while j < 3 {
            pre_count += usize::from(pre[j] == pre[i]);
            post_count += usize::from(post[j] == pre[i]);
            j += 1;
        }
        kani::assert(pre_count == post_count, "forwarded output preserves full multiplicities");
        i += 1;
    }
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
    sort_input_covers(ascending, descending, duplicate);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(32)]
fn rejects_high_bit_corruption_u64_len3() {
    let mut v: [u64; 3] = kani::any();
    // Establish a sorted fixture without restricting any full u64 input value.
    if v[0] > v[1] {
        v.swap(0, 1);
    }
    if v[1] > v[2] {
        v.swap(1, 2);
    }
    if v[0] > v[1] {
        v.swap(0, 1);
    }
    let pre = <() as SortModel<u64, U64Cmp>>::snapshot(v.as_ptr(), v.len());
    kani::assert(
        <() as SortModel<u64, U64Cmp>>::sort_postcondition(pre, v.as_ptr(), v.len()),
        "unchanged sorted snapshot passes checker",
    );
    v[0] ^= 1u64 << 63;
    kani::assert(
        <() as SortModel<u64, U64Cmp>>::sort_postcondition(pre, v.as_ptr(), v.len()),
        "high-bit corruption preserves sorted full values",
    );
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(32)]
fn rejects_changed_multiplicities_u64_len3() {
    let a: u64 = kani::any();
    let b: u64 = kani::any();
    kani::assume(a < b);
    let pre_values = [a, a, b];
    let pre = <() as SortModel<u64, U64Cmp>>::snapshot(pre_values.as_ptr(), 3);
    let post = [a, b, b];
    kani::assert(
        <() as SortModel<u64, U64Cmp>>::sort_postcondition(pre, post.as_ptr(), 3),
        "same set preserves full multiplicities",
    );
}

#[cfg(kani_smallsort_controls)]
fn reverse_less(a: &u64, b: &u64) -> bool {
    a > b
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn rejects_reverse_pointer_sorted_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let mut cmp: U64Cmp = reverse_less;
    let enabled = <() as SortModel<u64, U64Cmp>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(!enabled, "reverse pointer disables sort model");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(v[0] <= v[1] && v[1] <= v[2], "reverse pointer output is sorted");
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
}

#[cfg(kani_smallsort_controls)]
fn trait_less_u64(a: &u64, b: &u64) -> bool {
    a < b
}

#[cfg(kani_smallsort_controls)]
fn trait_input_covers(input_descending: bool) {
    kani::cover(input_descending, "descending input returns");
    kani::cover(!input_descending, "non-descending input returns");
    kani::cover(true, "trait small_sort returns");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn rejects_function_item_sorted_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let mut cmp = trait_less_u64;
    let enabled = <() as SortModel<u64, _>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(!enabled, "function item disables sort model");
    <u64 as UnstableSmallSortTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(v[0] <= v[1] && v[1] <= v[2], "function item output is sorted");
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(<u64 as UnstableSmallSortFreezeTypeImpl>::small_sort)]
#[kani::unwind(32)]
fn freeze_frame_function_item_u64_backing5() {
    let mut backing: [u64; 5] = kani::any();
    let outside = [backing[0], backing[4]];
    let v = &mut backing[1..4];
    let input_descending = v[1] < v[0];
    let mut cmp = trait_less_u64;
    let enabled = <() as SortModel<u64, _>>::enabled(SortEntry::Freeze, &cmp, v.len());
    kani::assert(!enabled, "function item disables sort model");
    <u64 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut cmp);
    kani::assert(backing[0] == outside[0] && backing[4] == outside[1], "outside slice unchanged");
    trait_input_covers(input_descending);
}
