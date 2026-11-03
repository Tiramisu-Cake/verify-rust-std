//! ZSTPROBE: localizes the pointer-check failures of the stable unit-ZST dispatch root
//! `dispatch_safety_stable_zst_n0_1_2_7_8_15_16_17_31_32`. Opt-in only. Root 1 copies that root
//! and its `dispatch_safety_fixed` with `zst_aware_less` as the only change; root 2 runs the
//! original body at N2 only; roots 3 and 4 are minimal volatile unit reads.

use super::super::comparators::zst_aware_less;
use super::ArbitraryValue;
use crate::{kani, ptr};

fn dispatch_safety_fixed<T: ArbitraryValue, const N: usize, const STABLE: bool>() {
    use super::super::super::{StableSmallSortTypeImpl, UnstableSmallSortTypeImpl};
    let mut v: [T; N] = crate::array::from_fn(|_| T::arbitrary_value());
    if STABLE {
        let mut scratch = [const { crate::mem::MaybeUninit::<T>::uninit() }; 48];
        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut zst_aware_less::<T>);
    } else {
        <T as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut zst_aware_less::<T>);
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

dispatch_safety_cases!(
    zst_stable_dispatch_aware_n0_1_2_7_8_15_16_17_31_32,
    (),
    true,
    [0, 1, 2, 7, 8, 15, 16, 17, 31, 32]
);

// UNSTABLEZST: `dispatch_safety_unstable_zst_n8_9_12_13_17` with `zst_aware_less` as the only
// change, as one family and per length.
dispatch_safety_cases!(zst_unstable_dispatch_aware_n8_9_12_13_17, (), false, [8, 9, 12, 13, 17]);
dispatch_safety_cases!(zst_unstable_dispatch_aware_n8, (), false, [8]);
dispatch_safety_cases!(zst_unstable_dispatch_aware_n9, (), false, [9]);
dispatch_safety_cases!(zst_unstable_dispatch_aware_n12, (), false, [12]);
dispatch_safety_cases!(zst_unstable_dispatch_aware_n13, (), false, [13]);
dispatch_safety_cases!(zst_unstable_dispatch_aware_n17, (), false, [17]);

// The original root restricted to N2: the unchanged `volatile_reading_less` body.
#[kani::proof]
#[kani::stub(super::super::super::panic_on_ord_violation, super::assume_order_violation)]
#[kani::unwind(65)]
fn zst_stable_dispatch_volatile_n2() {
    let len: usize = kani::any_where(|&l| matches!(l, 2));
    match len {
        2 => super::dispatch_safety_fixed::<(), 2, true>(),
        _ => {}
    }
    kani::cover(len == 2, "dispatch route returns normally at 2");
    kani::cover(true, "dispatch safety family reached the end");
}

#[kani::proof]
fn zst_read_volatile_dangling() {
    let p = ptr::NonNull::<()>::dangling().as_ptr();
    // SAFETY: `p` is non-null and aligned; a unit read accesses no bytes.
    let _unit: () = unsafe { ptr::read_volatile(p) };
    kani::cover(true, "volatile unit read through dangling pointer returns");
}

#[kani::proof]
fn zst_read_volatile_local() {
    let x = ();
    // SAFETY: `&x` refers to a live local; a unit read accesses no bytes.
    let _unit: () = unsafe { ptr::read_volatile(&x) };
    kani::cover(true, "volatile unit read through local reference returns");
}
