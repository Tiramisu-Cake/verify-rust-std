//! W3-L2 L2-2: full-width u8/u64 correctness with verified insertion contracts.
//! Historical L2-0/L2-1 experiments remain at 4dc9995c and are not submitted.

use super::merge::{lt_u8, lt_u64, set_probe};
use super::super::CopyOnDrop;
use crate::kani;

// L2-2: preserve the original u8/u64 domains; use insert_tail's contract
// instead of expanding every insertion. No Tagged routing reduction here.
fn fallback_stub<T: kani::Arbitrary + Copy, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut cmp: F,
) {
    const { assert!(N <= 16); }
    set_probe::<T>();
    let mut output: [T; N] = kani::any();
    let input = output;
    super::super::small_sort_fallback(&mut output, &mut cmp);
    for i in 1..N { assert!(!cmp(&output[i], &output[i - 1])); }
    assert!(CopyOnDrop::<T>::k1_count_u(input.as_ptr(), N)
        == CopyOnDrop::<T>::k1_count_u(output.as_ptr(), N));
    kani::cover(true, "fallback: sortedness and probe count checked");
}

macro_rules! fallback_stub_harness {
    ($name:ident, $t:ty, $cmp:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::solver(cadical)]
        #[kani::unwind(34)]
        fn $name() { fallback_stub::<$t, _, $n>($cmp); }
    };
}
fallback_stub_harness!(l2_fallback_u64_n8, u64, lt_u64, 8);
fallback_stub_harness!(l2_fallback_u64_n16, u64, lt_u64, 16);
fallback_stub_harness!(l2_fallback_u8_n9, u8, lt_u8, 9);
fallback_stub_harness!(l2_fallback_u8_n16, u8, lt_u8, 16);

// Instances of reviewed template 8e499dcd; first measurement 1e932304 gate=true.
fallback_stub_harness!(l2_fallback_u64_n9, u64, lt_u64, 9);
fallback_stub_harness!(l2_fallback_u64_n10, u64, lt_u64, 10);
fallback_stub_harness!(l2_fallback_u64_n11, u64, lt_u64, 11);
fallback_stub_harness!(l2_fallback_u64_n12, u64, lt_u64, 12);
fallback_stub_harness!(l2_fallback_u64_n13, u64, lt_u64, 13);
fallback_stub_harness!(l2_fallback_u64_n14, u64, lt_u64, 14);
fallback_stub_harness!(l2_fallback_u64_n15, u64, lt_u64, 15);
fallback_stub_harness!(l2_fallback_u8_n10, u8, lt_u8, 10);
fallback_stub_harness!(l2_fallback_u8_n11, u8, lt_u8, 11);
fallback_stub_harness!(l2_fallback_u8_n12, u8, lt_u8, 12);
fallback_stub_harness!(l2_fallback_u8_n13, u8, lt_u8, 13);
fallback_stub_harness!(l2_fallback_u8_n14, u8, lt_u8, 14);
fallback_stub_harness!(l2_fallback_u8_n15, u8, lt_u8, 15);

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::solver(cadical)]
#[kani::unwind(18)]
fn l2_insert_tail_prefix_u8() {
    set_probe::<u8>();
    let mut input: [u8; 17] = kani::any();
    let tail: usize = kani::any_where(|t: &usize| 1 <= *t && *t < 17);
    let before = input;
    let base = input.as_mut_ptr();
    // SAFETY: valid same-allocation region. proof_for_contract supplies the
    // sorted-prefix requires; the suffix is outside the modifies region.
    unsafe { super::super::insert_tail(base, base.add(tail), &mut lt_u8); }
    for i in tail + 1..17 { assert!(input[i] == before[i]); }
    kani::cover(tail == 1, "u8 prefix: region 2 reachable");
    kani::cover(tail == 15, "u8 prefix: proper prefix region 16 reachable");
    kani::cover(tail == 16, "u8 prefix: full region 17 reachable");
    kani::cover(true, "u8 prefix: completion");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(18)]
fn l2_r11_insert_tail() {
    set_probe::<u8>();
    let mut input = [4u8, 0, 2];
    let base = input.as_mut_ptr();
    kani::cover(true, "R11 insertion: sorted-prefix violation call reachable");
    // Deliberate requires violation: prefix keys [2,0] are unsorted;
    // pointers, allocation, initialization and region length are valid.
    unsafe { super::super::insert_tail(base, base.add(2), &mut lt_u8); }
}
