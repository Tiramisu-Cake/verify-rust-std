//! S1: six real implementation contracts, symbolic N0..3, no summaries or panic stubs.
//! Fixed initialized backing and separate MU scratch qualify only this fixture geometry.

use super::super::{
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
    has_efficient_in_place_swap,
};
use super::sorting_model::{KeyLess, NonCopyByte, enabled, post, snapshot};
use crate::cell::Cell;
use crate::kani;
use crate::mem::{MaybeUninit, size_of};

fn byte(x: u8) -> u8 { x }

macro_rules! invoke {
    (stable_empty, $ty:ty, $trait:ident, $v:expr, $n:expr, $less:expr) => {{
        let mut scratch: [MaybeUninit<$ty>; 0] = [];
        <$ty as $trait>::small_sort($v, &mut scratch, $less);
    }};
    (stable_general, $ty:ty, $trait:ident, $v:expr, $n:expr, $less:expr) => {{
        // One flat, separate allocation; MU payload never read by the fixture.
        let mut scratch: [MaybeUninit<$ty>; 19] = [const { MaybeUninit::uninit() }; 19];
        let scratch_len = if $n < 2 { 0 } else { $n + 16 };
        kani::assert(scratch_len <= scratch.len(), "S1_SCRATCH_PREFIX_VALID");
        <$ty as $trait>::small_sort($v, &mut scratch[..scratch_len], $less);
    }};
    (unstable, $ty:ty, $trait:ident, $v:expr, $n:expr, $less:expr) => {
        <$ty as $trait>::small_sort($v, $less)
    };
}

macro_rules! smoke {
    ($name:ident, $ty:ty, $new:path, $trait:ident, $threshold:literal, $route:ident) => {
        #[kani::proof_for_contract(<$ty as $trait>::small_sort)]
        #[kani::unwind(34)]
        fn $name() {
            let input: [u8; 3] = kani::any();
            let n: usize = kani::any();
            kani::assume(n <= 3);
            let mut backing = [$new(0xa5), $new(input[0]), $new(input[1]),
                $new(input[2]), $new(0x5a)];
            assert!(enabled::<$ty, KeyLess<$ty>>(), "S1_ENTRY_MODEL_ENABLED");
            assert!(<$ty as $trait>::small_sort_threshold() == $threshold,
                "S1_EXACT_TRAIT_THRESHOLD");
            assert!(size_of::<$ty>() == 1 && size_of::<KeyLess<$ty>>() == 0,
                "S1_ENTRY_TYPE_LAYOUT");
            let left = snapshot::<$ty, KeyLess<$ty>>(&backing[..1]);
            let right = snapshot::<$ty, KeyLess<$ty>>(&backing[n + 1..n + 2]);
            let before = snapshot::<$ty, KeyLess<$ty>>(&backing[1..n + 1]);
            let mut less = KeyLess::<$ty>::new();
            invoke!($route, $ty, $trait, &mut backing[1..n + 1], n, &mut less);
            assert!(post::<$ty, KeyLess<$ty>>(before, &backing[1..n + 1]),
                "S1_ENTRY_POST_INDEPENDENT_CALLER");
            assert!(post::<$ty, KeyLess<$ty>>(left, &backing[..1]), "S1_LEFT_CANARY");
            assert!(post::<$ty, KeyLess<$ty>>(right, &backing[n + 1..n + 2]),
                "S1_RIGHT_CANARY");
            if n == 1 {
                let expected = [$new(input[0])];
                assert!(post::<$ty, KeyLess<$ty>>(
                    snapshot::<$ty, KeyLess<$ty>>(&expected), &backing[1..2]),
                    "S1_N1_VALUE_UNCHANGED");
            }
            if n == 0 {
                assert!(post::<$ty, KeyLess<$ty>>(before, &[]), "S1_N0_EMPTY_UNCHANGED");
            }
            kani::cover(n == 0, "S1_entry_N0_return");
            kani::cover(n == 1, "S1_entry_N1_return");
            kani::cover(n == 2, "S1_entry_N2_return");
            kani::cover(n == 3, "S1_entry_N3_return");
            kani::cover(n == 2 && input[0] > input[1], "S1_entry_N2_reversed_return");
            kani::cover(n == 2 && input[0] == input[1], "S1_entry_N2_duplicate_return");
            kani::cover(n == 2 && input[0] < input[1], "S1_entry_N2_ascending_return");
            kani::cover(n == 3 && input[0] > input[1] && input[1] > input[2],
                "S1_entry_N3_reversed_return");
            kani::cover(n == 3 && (input[0] == input[1] || input[1] == input[2]
                || input[0] == input[2]), "S1_entry_N3_duplicate_return");
            kani::cover(n == 3 && input[0] < input[1] && input[1] < input[2],
                "S1_entry_N3_ascending_return");
            kani::cover(true, "S1_entry_useful_return");
        }
    };
}

smoke!(stable_default_cell, Cell<u8>, Cell::new, StableSmallSortTypeImpl, 16, stable_empty);
smoke!(stable_freeze_u8, u8, byte, StableSmallSortTypeImpl, 32, stable_general);
smoke!(unstable_default_cell, Cell<u8>, Cell::new, UnstableSmallSortTypeImpl, 16, unstable);
smoke!(unstable_freeze_u8, u8, byte, UnstableSmallSortTypeImpl, 32, unstable);
smoke!(freeze_default_noncopy, NonCopyByte, NonCopyByte::new,
    UnstableSmallSortFreezeTypeImpl, 32, unstable);
smoke!(freeze_copy_u8, u8, byte, UnstableSmallSortFreezeTypeImpl, 32, unstable);

// This source predicate is also asserted by the ordinary bridge root. For the
// Copy u8 body, size1 and efficient swap select network, with early insertion N<9.
const _: () = assert!(has_efficient_in_place_swap::<u8>());
