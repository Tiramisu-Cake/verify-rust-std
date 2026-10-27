//! Lane smoke test for the K-1 experiment, not a proof obligation: `ok` must succeed with every cover
//! satisfied, `control_must_fail` must fail with a located check. Together they show that the lane
//! builds the pinned Kani, runs exactly the requested harnesses and reports both outcomes.

use super::super::has_efficient_in_place_swap;
use crate::kani;

#[kani::proof]
fn ok() {
    assert!(has_efficient_in_place_swap::<u64>());
    assert!(!has_efficient_in_place_swap::<[u8; 9]>());
    let x: u8 = kani::any();
    kani::cover(x == 0, "smoke: x == 0 is reachable");
    kani::cover(x == 255, "smoke: x == 255 is reachable");
}

#[kani::proof]
fn control_must_fail() {
    // Deliberately false for a 9-byte element.
    assert!(has_efficient_in_place_swap::<[u8; 9]>());
}

// Coordinator diagnostic (2026-10-27): for a zero-sized T, `small_sort_network` at len >= 18 never
// leaves its region loop (`v_base.add(len_div_2) == v_base`). Public sorts return before the trait
// for ZSTs, so this is latent. len 17 (no merge) is the terminating control.
#[kani::proof]
#[kani::unwind(40)]
fn zst_network_len18_loops() {
    let mut v = [(); 18];
    <() as super::super::UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut |_: &(), _: &()| false);
    kani::cover(true, "zst network len 18 returned");
}

#[kani::proof]
#[kani::unwind(40)]
fn zst_network_len17_returns() {
    let mut v = [(); 17];
    <() as super::super::UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut |_: &(), _: &()| false);
    kani::cover(true, "zst network len 17 returned");
}
