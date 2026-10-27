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

/// Lane smoke for the request field `controls`: compiled only under `--cfg kani_smallsort_controls`.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn control_cfg_only() {
    let x: u8 = kani::any();
    assert!(x != x);
}
