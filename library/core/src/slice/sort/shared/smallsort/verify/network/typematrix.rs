//! TYPEMATRIX: dispatch safety for three more element layouts, opt-in only. `(u8, u32)` has
//! size 8 with padding (unstable: `small_sort_network`), `u128` alignment 16 and `[u8; 9]` the
//! first size where `has_efficient_in_place_swap` is false (both unstable: `small_sort_general`);
//! stable always takes `small_sort_general_with_scratch`. Safety and normal return only: no
//! sortedness or permutation is asserted, and padding bytes are neither zeroed nor read.
//!
//! The two macros copy the parent's `dispatch_safety_cases!` and `dispatch_pair_safety_cases!`
//! with the stub paths one module deeper as the only change; they run the parent's
//! `dispatch_safety_fixed` (scratch 48, `volatile_reading_less`).

use super::{ArbitraryValue, dispatch_safety_fixed};
use crate::kani;

// `repr(Rust)` layout is not a language guarantee: these hold for this toolchain on the targets
// the K-1 lanes use, and the route table of the harnesses below depends on them.
const _: () = {
    use super::super::super::{
        MAX_STACK_ARRAY_SIZE, SMALL_SORT_GENERAL_SCRATCH_LEN, SMALL_SORT_NETWORK_SCRATCH_LEN,
        has_efficient_in_place_swap,
    };
    use crate::mem::{align_of, size_of};
    if cfg!(any(target_arch = "x86_64", target_arch = "aarch64")) {
        assert!(size_of::<(u8, u32)>() == 8 && align_of::<(u8, u32)>() == 4);
        assert!(size_of::<u128>() == 16 && align_of::<u128>() == 16);
        assert!(size_of::<[u8; 9]>() == 9 && align_of::<[u8; 9]>() == 1);
        // Unstable routes: network for `(u8, u32)`, general for `u128` and `[u8; 9]`.
        assert!(has_efficient_in_place_swap::<(u8, u32)>());
        assert!(size_of::<(u8, u32)>() * SMALL_SORT_NETWORK_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
        assert!(!has_efficient_in_place_swap::<u128>());
        assert!(size_of::<u128>() * SMALL_SORT_GENERAL_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
        assert!(!has_efficient_in_place_swap::<[u8; 9]>());
        assert!(size_of::<[u8; 9]>() * SMALL_SORT_GENERAL_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
    }
};

impl ArbitraryValue for (u8, u32) {
    fn arbitrary_value() -> Self {
        (kani::any(), kani::any())
    }
}

impl ArbitraryValue for u128 {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}

macro_rules! dispatch_safety_cases {
    ($name:ident, $t:ty, $stable:literal, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::super::panic_on_ord_violation, super::assume_order_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            match len {
                $($n => dispatch_safety_fixed::<$t, $n, $stable>(),)+
                _ => {}
            }
            $(kani::cover(
                len == $n,
                concat!("dispatch route returns normally at ", stringify!($n))
            );)+
            kani::cover(true, "dispatch safety family reached the end");
        }
    };
}

/// Selects stable or unstable dispatch for each listed fixed array length and covers both routes.
macro_rules! dispatch_pair_safety_cases {
    ($name:ident, $t:ty, [$($n:literal),+]) => {
        #[kani::proof]
        #[kani::stub(super::super::super::panic_on_ord_violation, super::assume_order_violation)]
        #[kani::unwind(65)]
        fn $name() {
            let len: usize = kani::any_where(|&l| matches!(l, $($n)|+));
            let stable: bool = kani::any();
            match len {
                $($n => {
                    if stable { dispatch_safety_fixed::<$t, $n, true>(); }
                    else { dispatch_safety_fixed::<$t, $n, false>(); }
                },)+
                _ => {}
            }
            $(
                kani::cover(
                    stable && len == $n,
                    concat!("stable route normal return at ", stringify!($n))
                );
                kani::cover(
                    !stable && len == $n,
                    concat!("unstable route normal return at ", stringify!($n))
                );
            )+
            kani::cover(true, "dispatch family reached the end");
        }
    };
}

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_u8u32_n0_1_2_7_8,
    (u8, u32),
    [0, 1, 2, 7, 8]
);
dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_u8u32_n15_16_17,
    (u8, u32),
    [15, 16, 17]
);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u8u32_n31_32, (u8, u32), [31, 32]);

dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u128_n0_1_2_7_8, u128, [0, 1, 2, 7, 8]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u128_n15_16_17, u128, [15, 16, 17]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u128_n31_32, u128, [31, 32]);

dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes9_n0_1_2_7_8,
    [u8; 9],
    [0, 1, 2, 7, 8]
);
dispatch_pair_safety_cases!(
    dispatch_safety_stable_unstable_bytes9_n15_16_17,
    [u8; 9],
    [15, 16, 17]
);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_bytes9_n31_32, [u8; 9], [31, 32]);

// Network route of `(u8, u32)`: sort9 (9, 12), sort13 (13) and the first merge length (18).
dispatch_safety_cases!(
    dispatch_safety_unstable_u8u32_n9_12_13_18,
    (u8, u32),
    false,
    [9, 12, 13, 18]
);

// TYPESPLIT: the three `_n31_32` pair roots above split by route × length; each cell is one
// single-route root (stable: `small_sort_general_with_scratch`; unstable: network or general).
dispatch_safety_cases!(dispatch_safety_stable_u8u32_n31, (u8, u32), true, [31]);
dispatch_safety_cases!(dispatch_safety_stable_u8u32_n32, (u8, u32), true, [32]);
dispatch_safety_cases!(dispatch_safety_unstable_u8u32_n31, (u8, u32), false, [31]);
dispatch_safety_cases!(dispatch_safety_unstable_u8u32_n32, (u8, u32), false, [32]);

dispatch_safety_cases!(dispatch_safety_stable_u128_n31, u128, true, [31]);
dispatch_safety_cases!(dispatch_safety_stable_u128_n32, u128, true, [32]);
dispatch_safety_cases!(dispatch_safety_unstable_u128_n31, u128, false, [31]);
dispatch_safety_cases!(dispatch_safety_unstable_u128_n32, u128, false, [32]);

dispatch_safety_cases!(dispatch_safety_stable_bytes9_n31, [u8; 9], true, [31]);
dispatch_safety_cases!(dispatch_safety_stable_bytes9_n32, [u8; 9], true, [32]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes9_n31, [u8; 9], false, [31]);
dispatch_safety_cases!(dispatch_safety_unstable_bytes9_n32, [u8; 9], false, [32]);

// TYPEUXVI: `u16` (size 2, align 2). Only the element width is new: unstable takes
// `small_sort_network` like `(u8, u32)`, stable `small_sort_general_with_scratch`. The same seven
// shapes as `(u8, u32)`: two pair roots, the network lengths, and N31/N32 one route per root.
const _: () = {
    use super::super::super::{
        MAX_STACK_ARRAY_SIZE, SMALL_SORT_NETWORK_SCRATCH_LEN, has_efficient_in_place_swap,
    };
    use crate::mem::{align_of, size_of};
    if cfg!(any(target_arch = "x86_64", target_arch = "aarch64")) {
        assert!(size_of::<u16>() == 2 && align_of::<u16>() == 2);
        assert!(has_efficient_in_place_swap::<u16>());
        assert!(size_of::<u16>() * SMALL_SORT_NETWORK_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
    }
};

impl ArbitraryValue for u16 {
    fn arbitrary_value() -> Self {
        kani::any()
    }
}

dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u16_n0_1_2_7_8, u16, [0, 1, 2, 7, 8]);
dispatch_pair_safety_cases!(dispatch_safety_stable_unstable_u16_n15_16_17, u16, [15, 16, 17]);
dispatch_safety_cases!(dispatch_safety_unstable_u16_n9_12_13_18, u16, false, [9, 12, 13, 18]);
dispatch_safety_cases!(dispatch_safety_stable_u16_n31, u16, true, [31]);
dispatch_safety_cases!(dispatch_safety_stable_u16_n32, u16, true, [32]);
dispatch_safety_cases!(dispatch_safety_unstable_u16_n31, u16, false, [31]);
dispatch_safety_cases!(dispatch_safety_unstable_u16_n32, u16, false, [32]);
