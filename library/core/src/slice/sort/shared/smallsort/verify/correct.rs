//! Correctness harnesses for full-width `u8` and `u64` arrays using verified insertion contracts.

#[cfg(kani_smallsort_controls)]
use super::super::CopyOnDrop;
#[cfg(kani_smallsort_controls)]
use super::merge::lt_u64;
use super::merge::{lt_u8, set_value_probe};
use crate::kani;

// Fallback: u64 N8..16, u8 N9..16; verified insert_tail with matching key orders.
#[cfg(kani_smallsort_controls)]
fn fallback_stub<T: kani::Arbitrary + Copy, F: FnMut(&T, &T) -> bool, const N: usize>(mut cmp: F) {
    const {
        assert!(N <= 16);
    }
    set_value_probe::<T>();
    let mut output: [T; N] = kani::any();
    let input = output;
    super::super::small_sort_fallback(&mut output, &mut cmp);
    for i in 1..N {
        assert!(!cmp(&output[i], &output[i - 1]));
    }
    assert!(
        CopyOnDrop::<T>::probe_count_unrolled(input.as_ptr(), N)
            == CopyOnDrop::<T>::probe_count_unrolled(output.as_ptr(), N)
    );
    kani::cover(true, "fallback: sortedness and probe count checked");
}

#[cfg(kani_smallsort_controls)]
macro_rules! fallback_stub_harness {
    ($name:ident, $t:ty, $cmp:ident, $n:literal) => {
        fallback_stub_harness!($name, $t, $cmp, $n, cadical);
    };
    ($name:ident, $t:ty, $cmp:ident, $n:literal, $solver:ident) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::solver($solver)]
        #[kani::unwind(34)]
        fn $name() {
            fallback_stub::<$t, _, $n>($cmp);
        }
    };
}
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n8, u64, lt_u64, 8);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n16, u64, lt_u64, 16);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n9, u8, lt_u8, 9);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n16, u8, lt_u8, 16);

#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n9, u64, lt_u64, 9);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n10, u64, lt_u64, 10);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n11, u64, lt_u64, 11);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n12, u64, lt_u64, 12);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n13, u64, lt_u64, 13);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n14, u64, lt_u64, 14);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u64_n15, u64, lt_u64, 15);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n10, u8, lt_u8, 10);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n11, u8, lt_u8, 11);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n12, u8, lt_u8, 12);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n13, u8, lt_u8, 13);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n14, u8, lt_u8, 14);
#[cfg(kani_smallsort_controls)]
fallback_stub_harness!(sorted_permutation_fallback_u8_n15, u8, lt_u8, 15);

/// u8 insertion-tail contract and suffix frame in a 17-element allocation, with tail indices
/// 1..=16.
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::solver(cadical)]
#[kani::unwind(18)]
fn contract_insert_tail_u8_prefix() {
    set_value_probe::<u8>();
    let mut input: [u8; 17] = kani::any();
    let tail: usize = kani::any_where(|t: &usize| 1 <= *t && *t < 17);
    let before = input;
    let base = input.as_mut_ptr();
    // SAFETY: valid same-allocation region. proof_for_contract supplies the
    // sorted-prefix requires; the suffix is outside the modifies region.
    unsafe {
        super::super::insert_tail(base, base.add(tail), &mut lt_u8);
    }
    for i in tail + 1..17 {
        assert!(input[i] == before[i]);
    }
    kani::cover(tail == 1, "u8 prefix: region 2 reachable");
    kani::cover(tail == 15, "u8 prefix: proper prefix region 16 reachable");
    kani::cover(tail == 16, "u8 prefix: full region 17 reachable");
    kani::cover(true, "u8 prefix: completion");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(18)]
fn reject_unsorted_prefix_insert_tail_u8_n3() {
    set_value_probe::<u8>();
    let mut input = [4u8, 0, 2];
    let base = input.as_mut_ptr();
    kani::cover(true, "insertion call with unsorted prefix is reachable");
    // SAFETY: the pointer and region are valid; only the sorted-prefix contract is violated.
    unsafe {
        super::super::insert_tail(base, base.add(2), &mut lt_u8);
    }
}

// Scratch tails in 48 elements at starts 0/6/7, lengths 5..8: general/stable N13..15 geometry
// differs from 17-element allocation prefixes.
#[cfg(kani_smallsort_controls)]
fn scratch_insert_contract<T: kani::Arbitrary + Copy + Eq, F: FnMut(&T, &T) -> bool>(mut cmp: F) {
    use super::super::SMALL_SORT_GENERAL_SCRATCH_LEN;
    set_value_probe::<T>();
    let mut scratch: [T; SMALL_SORT_GENERAL_SCRATCH_LEN] = kani::any();
    let before = scratch;
    let selector: u8 = kani::any();
    let start = match selector {
        0 => 0,
        1 => 6,
        _ => 7,
    };
    let len: usize = kani::any_where(|n: &usize| 5 <= *n && *n <= 8);
    let base = scratch.as_mut_ptr();
    // SAFETY: one initialized writable scratch allocation, start+len<=15.
    // proof_for_contract supplies exactly the callee's sorted-prefix requires.
    unsafe {
        super::super::insert_tail(base.add(start), base.add(start + len - 1), &mut cmp);
    }
    for i in 0..SMALL_SORT_GENERAL_SCRATCH_LEN {
        if i < start || i >= start + len {
            assert!(scratch[i] == before[i]);
        }
    }
    kani::cover(start == 0, "scratch insertion starts at zero");
    kani::cover(start == 6, "scratch insertion starts at six");
    kani::cover(start == 7, "scratch insertion starts at seven");
    kani::cover(len == 5, "scratch region length five");
    kani::cover(len == 8, "scratch region length eight");
    kani::cover(true, "scratch insertion: contract and frame checked");
}

#[cfg(kani_smallsort_controls)]
macro_rules! scratch_contract_harness {
    ($name:ident, $t:ty, $cmp:ident) => {
        scratch_contract_harness!($name, $t, $cmp, cadical);
    };
    ($name:ident, $t:ty, $cmp:ident, $solver:ident) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::solver($solver)]
        #[kani::unwind(50)]
        fn $name() {
            scratch_insert_contract::<$t, _>($cmp);
        }
    };
}
#[cfg(kani_smallsort_controls)]
scratch_contract_harness!(contract_insert_tail_u64_scratch, u64, lt_u64, kissat);
#[cfg(kani_smallsort_controls)]
scratch_contract_harness!(contract_insert_tail_u8_scratch, u8, lt_u8);

// Stable and general routes for `u8` and `u64` use full-width values at lengths 13 through 15.
// The sort4 step remains real; verified contracts are used for insertion and the final merge.
#[cfg(kani_smallsort_controls)]
fn general_stable_stub<
    T: kani::Arbitrary + Copy + crate::slice::sort::shared::FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut cmp: F,
) {
    use super::super::{SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl};
    use crate::mem::MaybeUninit;
    const {
        assert!(13 <= N && N <= 15);
    }
    set_value_probe::<T>();
    let mut output: [T; N] = kani::any();
    let input = output;
    let stable: bool = kani::any();
    if stable {
        let mut scratch = [MaybeUninit::<T>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
        <T as StableSmallSortTypeImpl>::small_sort(&mut output, &mut scratch, &mut cmp);
    } else {
        super::super::small_sort_general(&mut output, &mut cmp);
    }
    for i in 1..N {
        assert!(!cmp(&output[i], &output[i - 1]));
    }
    assert!(
        CopyOnDrop::<T>::probe_count_unrolled(input.as_ptr(), N)
            == CopyOnDrop::<T>::probe_count_unrolled(output.as_ptr(), N)
    );
    kani::cover(stable, "general/stable: stable Freeze route checked");
    kani::cover(!stable, "general/stable: direct general route checked");
}

#[cfg(kani_smallsort_controls)]
macro_rules! general_stub_harness {
    ($name:ident, $t:ty, $cmp:ident, $n:literal, $solver:ident) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::solver($solver)]
        #[kani::unwind(50)]
        fn $name() {
            general_stable_stub::<$t, _, $n>($cmp);
        }
    };
}
#[cfg(kani_smallsort_controls)]
general_stub_harness!(sorted_permutation_general_stable_u64_n15, u64, lt_u64, 15, cadical);
#[cfg(kani_smallsort_controls)]
general_stub_harness!(sorted_permutation_general_stable_u8_n15, u8, lt_u8, 15, cadical);
#[cfg(kani_smallsort_controls)]
general_stub_harness!(sorted_permutation_general_stable_u8_n14, u8, lt_u8, 14, cadical);

// CORR14: fixed u8 N14 routes, with the same input/probe domain and oracle as combined.
// General and non-const stable partition the old symbolic bool; their return covers unite.
// Const/aggregate preserve T/F/N and input/probe domains, but aggregate changes backing geometry.
// These callers remain conditional on insert_tail/merge premises for the actual caller domains.
#[cfg(kani_smallsort_controls)]
fn corr14_scratch_view<T>(
    holder: &mut crate::mem::MaybeUninit<[T; 48]>,
) -> &mut [crate::mem::MaybeUninit<T>] {
    // SAFETY: the pointer keeps the provenance of the exclusively borrowed holder.
    // Arrays and MaybeUninit preserve element size/alignment; the extent is exactly 48 elements.
    // Only MaybeUninit<T> references are formed, without reading uninitialized T or assume_init.
    // The result's lifetime is tied to holder, excluding access to holder throughout this borrow.
    unsafe {
        crate::slice::from_raw_parts_mut(
            holder.as_mut_ptr().cast::<crate::mem::MaybeUninit<T>>(),
            48,
        )
    }
}

#[cfg(kani_smallsort_controls)]
fn corr14_check_u8_n14<F: FnMut(&u8, &u8) -> bool>(
    input: &[u8; 14],
    output: &[u8; 14],
    cmp: &mut F,
) {
    for i in 1..14 {
        assert!(!cmp(&output[i], &output[i - 1]));
    }
    assert!(
        CopyOnDrop::<u8>::probe_count_unrolled(input.as_ptr(), 14)
            == CopyOnDrop::<u8>::probe_count_unrolled(output.as_ptr(), 14)
    );
}

#[cfg(kani_smallsort_controls)]
fn corr14_general_stub_u8_n14() {
    set_value_probe::<u8>();
    let mut output: [u8; 14] = kani::any();
    let input = output;
    let mut cmp = lt_u8;
    super::super::small_sort_general(&mut output, &mut cmp);
    corr14_check_u8_n14(&input, &output, &mut cmp);
    kani::cover(true, "CORR14: general returns with properties checked");
}

#[cfg(kani_smallsort_controls)]
fn corr14_stable_nonconst_stub_u8_n14() {
    set_value_probe::<u8>();
    let mut output: [u8; 14] = kani::any();
    let input = output;
    let mut cmp = lt_u8;
    use super::super::StableSmallSortTypeImpl;
    use crate::mem::MaybeUninit;
    let mut scratch = [MaybeUninit::<u8>::uninit(); 48];
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut output, &mut scratch, &mut cmp);
    corr14_check_u8_n14(&input, &output, &mut cmp);
    kani::cover(true, "CORR14: stable_nonconst returns with properties checked");
}

#[cfg(kani_smallsort_controls)]
fn corr14_stable_const_stub_u8_n14() {
    set_value_probe::<u8>();
    let mut output: [u8; 14] = kani::any();
    let input = output;
    let mut cmp = lt_u8;
    use super::super::StableSmallSortTypeImpl;
    use crate::mem::MaybeUninit;
    let mut scratch = [const { MaybeUninit::<u8>::uninit() }; 48];
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut output, &mut scratch, &mut cmp);
    corr14_check_u8_n14(&input, &output, &mut cmp);
    kani::cover(true, "CORR14: stable_const returns with properties checked");
}

#[cfg(kani_smallsort_controls)]
fn corr14_stable_aggregate_stub_u8_n14() {
    set_value_probe::<u8>();
    let mut output: [u8; 14] = kani::any();
    let input = output;
    let mut cmp = lt_u8;
    use super::super::StableSmallSortTypeImpl;
    use crate::mem::MaybeUninit;
    let mut holder = MaybeUninit::<[u8; 48]>::uninit();
    let scratch = corr14_scratch_view(&mut holder);
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut output, scratch, &mut cmp);
    corr14_check_u8_n14(&input, &output, &mut cmp);
    kani::cover(true, "CORR14: stable_aggregate returns with properties checked");
}

#[cfg(kani_smallsort_controls)]
macro_rules! corr14_stub_harness {
    ($name:ident, $body:ident) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::solver(cadical)]
        #[kani::unwind(50)]
        fn $name() {
            $body();
        }
    };
}
#[cfg(kani_smallsort_controls)]
corr14_stub_harness!(sorted_permutation_general_u8_n14, corr14_general_stub_u8_n14);
#[cfg(kani_smallsort_controls)]
corr14_stub_harness!(sorted_permutation_stable_nonconst_u8_n14, corr14_stable_nonconst_stub_u8_n14);
#[cfg(kani_smallsort_controls)]
corr14_stub_harness!(sorted_permutation_stable_const_u8_n14, corr14_stable_const_stub_u8_n14);
#[cfg(kani_smallsort_controls)]
corr14_stub_harness!(
    sorted_permutation_stable_aggregate_u8_n14,
    corr14_stable_aggregate_stub_u8_n14
);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::solver(cadical)]
#[kani::unwind(50)]
fn stable_aggregate_value_corruption_control_u8_n14() {
    set_value_probe::<u8>();
    let mut output: [u8; 14] = kani::any();
    let input = output;
    let mut cmp = lt_u8;
    use super::super::StableSmallSortTypeImpl;
    use crate::mem::MaybeUninit;
    let mut holder = MaybeUninit::<[u8; 48]>::uninit();
    let scratch = corr14_scratch_view(&mut holder);
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut output, scratch, &mut cmp);
    kani::cover(true, "CORR14: aggregate stable sort returns before payload corruption");
    // lt_u8 compares x >> 1, so this payload mutation preserves sortedness.
    output[0] ^= 1;
    corr14_check_u8_n14(&input, &output, &mut cmp);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::solver(cadical)]
#[kani::unwind(50)]
fn stable_aggregate_allocation_bounds_control_u8() {
    let mut holder = crate::mem::MaybeUninit::<[u8; 48]>::uninit();
    let scratch = corr14_scratch_view(&mut holder);
    let outside = scratch.as_mut_ptr().cast::<u8>().wrapping_add(48);
    kani::cover(true, "CORR14: aggregate bounds control reaches raw write");
    // Deliberately invalid: one past the entire allocation, without safe indexing or a T read.
    unsafe { crate::ptr::write(outside, 0) };
}
