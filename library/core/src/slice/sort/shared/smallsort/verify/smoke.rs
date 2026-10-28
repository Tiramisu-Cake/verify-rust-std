//! Smoke checks cover the in-place swap size heuristic and simple control assertions.
//! The type matrix includes scalars, arrays around the size threshold, `Cell`, Drop, and ZSTs.

use super::super::has_efficient_in_place_swap;
use crate::kani;
#[repr(transparent)]
struct SwapDrop(u8);

impl crate::ops::Drop for SwapDrop {
    fn drop(&mut self) {}
}

/// Checks the heuristic for scalar, array, `Cell`, Drop, and zero-sized element types.
#[kani::proof]
fn predicate_efficient_swap_type_matrix() {
    macro_rules! check {
        ($t:ty, $expected:literal) => {
            assert!(has_efficient_in_place_swap::<$t>() == $expected);
            kani::cover(true, concat!("efficient swap predicate for ", stringify!($t)));
        };
    }
    check!(u8, true);
    check!(u16, true);
    check!(u64, true);
    check!(u128, false);
    check!([u8; 9], false);
    check!([u8; 16], false);
    check!([u8; 17], false);
    check!([u8; 85], false);
    check!([u8; 86], false);
    check!(SwapDrop, true);
    check!(crate::cell::Cell<i32>, true);
    check!((), true);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn predicate_efficient_swap_boundaries() {
    assert!(has_efficient_in_place_swap::<u64>());
    assert!(!has_efficient_in_place_swap::<[u8; 9]>());
    let x: u8 = kani::any();
    kani::cover(x == 0, "smoke: x == 0 is reachable");
    kani::cover(x == 255, "smoke: x == 255 is reachable");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn reject_efficient_swap_bytes9() {
    // Deliberately false for a 9-byte element.
    assert!(has_efficient_in_place_swap::<[u8; 9]>());
}
