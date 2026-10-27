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

// Same, with the sorting networks and the insertion step stubbed out: for a ZST they cannot change
// anything, and the region loop's pointer logic does not depend on them. Isolates the loop.
fn zst_noop_network<T, F: FnMut(&T, &T) -> bool>(_v: &mut [T], _is_less: &mut F) {}
fn zst_noop_insertion<T, F: FnMut(&T, &T) -> bool>(_v: &mut [T], _offset: usize, _is_less: &mut F) {}

#[kani::proof]
#[kani::unwind(5)]
#[kani::stub(crate::slice::sort::shared::smallsort::sort9_optimal, zst_noop_network)]
#[kani::stub(crate::slice::sort::shared::smallsort::sort13_optimal, zst_noop_network)]
#[kani::stub(crate::slice::sort::shared::smallsort::insertion_sort_shift_left, zst_noop_insertion)]
fn zst_network_len18_loop_isolated() {
    let mut v = [(); 18];
    <() as super::super::UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut |_: &(), _: &()| false);
    kani::cover(true, "zst network len 18 returned (isolated)");
}

#[kani::proof]
#[kani::unwind(5)]
#[kani::stub(crate::slice::sort::shared::smallsort::sort9_optimal, zst_noop_network)]
#[kani::stub(crate::slice::sort::shared::smallsort::sort13_optimal, zst_noop_network)]
#[kani::stub(crate::slice::sort::shared::smallsort::insertion_sort_shift_left, zst_noop_insertion)]
fn zst_network_len18_u8_control_isolated() {
    // Control: a non-ZST of the same route leaves the loop after two iterations.
    let mut v = [0u8; 18];
    <u8 as super::super::UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut |a: &u8, b: &u8| a < b);
    kani::cover(true, "u8 network len 18 returned (isolated)");
}
