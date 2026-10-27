//! Lane smoke tests and the L1-2 size-heuristic proof. `ok` must succeed with every cover
//! satisfied, `control_must_fail` must fail with a located check. Together they show that the lane
//! builds the pinned Kani, runs exactly the requested harnesses and reports both outcomes.

use super::super::has_efficient_in_place_swap;
use crate::kani;

#[repr(transparent)]
struct W3SwapDrop(u8);

impl crate::ops::Drop for W3SwapDrop {
    fn drop(&mut self) {}
}

/// L1-2: the size heuristic on the C3 type matrix, including a zero-sized type.
#[kani::proof]
fn w3_efficient_swap_c3() {
    macro_rules! check {
        ($t:ty, $expected:literal) => {
            assert!(has_efficient_in_place_swap::<$t>() == $expected);
            kani::cover(true, concat!("L1-2: ", stringify!($t)));
        };
    }
    check!(u8, true);
    check!(u64, true);
    check!(u128, false);
    check!([u8; 16], false);
    check!([u8; 17], false);
    check!([u8; 85], false);
    check!([u8; 86], false);
    check!(W3SwapDrop, true);
    check!(crate::cell::Cell<i32>, true);
    check!((), true);
}

#[kani::proof]
fn ok() {
    assert!(has_efficient_in_place_swap::<u64>());
    assert!(!has_efficient_in_place_swap::<[u8; 9]>());
    let x: u8 = kani::any();
    kani::cover(x == 0, "smoke: x == 0 is reachable");
    kani::cover(x == 255, "smoke: x == 255 is reachable");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn control_must_fail() {
    // Deliberately false for a 9-byte element.
    assert!(has_efficient_in_place_swap::<[u8; 9]>());
}
