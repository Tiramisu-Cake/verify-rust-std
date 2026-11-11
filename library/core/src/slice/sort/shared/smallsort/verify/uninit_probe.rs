//! KANI3300 U0 diagnostics for the opt-in uninitialized-memory checks.

#![cfg(kani_smallsort_controls)]

use super::super::{
    bidirectional_merge, insert_tail, small_sort_general_with_scratch, swap_if_less,
};
use super::merge::lt_u8;
use super::merge::profiles::{
    LtU8, Profile, pair_models, swap_geometry, swap_ordered, swap_profile, swap_transfer,
};
use crate::mem::MaybeUninit;
use crate::{kani, ptr};

/// Uninit-check calibration: both rows read through this function; only the construction of
/// `slot` differs.
fn pincheck_read_slot(slot: MaybeUninit<u8>) -> u8 {
    // SAFETY: intentionally unchecked; the uninitialized calibration row violates it on purpose.
    unsafe { slot.assume_init() }
}

/// Calibration, failing half: reads a `MaybeUninit<u8>` that was never written.
#[kani::proof]
fn pincheck_calibration_uninit_read_u8() {
    let slot = MaybeUninit::<u8>::uninit();
    kani::cover(true, "pincheck calibration uninit: read reached");
    let value = pincheck_read_slot(slot);
    kani::cover(value == 0, "pincheck calibration uninit: read value zero");
    kani::cover(value != 0, "pincheck calibration uninit: read value nonzero");
}

/// Calibration, passing half: the same read of a `MaybeUninit<u8>` written with an arbitrary byte.
#[kani::proof]
fn pincheck_calibration_init_read_u8() {
    let x: u8 = kani::any();
    let slot = MaybeUninit::<u8>::new(x);
    kani::cover(true, "pincheck calibration init: read reached");
    let value = pincheck_read_slot(slot);
    kani::assert(value == x, "pincheck calibration init: read returns the written byte");
    kani::cover(value == 0, "pincheck calibration init: read value zero");
    kani::cover(value != 0, "pincheck calibration init: read value nonzero");
}

/// SPECDIAG row 17: a volatile read of an uninitialized `MaybeUninit<u8>` through `as_ptr`.
#[kani::proof]
fn raw_uninit_read_sensitivity() {
    let slot = MaybeUninit::<u8>::uninit();
    kani::cover(true, "specdiag raw uninitialized before volatile read");
    // SAFETY: intentionally violated, with dependent observations retaining the actual read.
    let value = unsafe { ptr::read_volatile(slot.as_ptr()) };
    kani::cover(value == 0, "specdiag raw uninitialized read value zero");
    kani::cover(value != 0, "specdiag raw uninitialized read value nonzero");
}

/// Positions anywhere in a 4-element array, in either order, distinct as the profile requires.
fn exercise_swap_contract<P: Profile>()
where
    P::Elem: kani::Arbitrary + Copy,
{
    let mut v: [P::Elem; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    kani::cover(a == 0 && b == 3, "swap_if_less: a < b reachable");
    kani::cover(a == 3 && b == 0, "swap_if_less: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`; canonical comparator.
    unsafe { swap_profile::<P>(v.as_mut_ptr(), a, b, P::CMP) };
    kani::cover((P::CMP)(&old_b, &old_a), "swap_if_less: swap taken");
    kani::cover(!(P::CMP)(&old_b, &old_a), "swap_if_less: swap not taken");
    kani::cover(true, "swap_if_less: end reached");
}

#[kani::proof_for_contract(super::merge::profiles::swap_profile)]
fn swap_contract_four_positions_u8() {
    exercise_swap_contract::<LtU8>();
}

fn strict_less(a: &u8, b: &u8) -> bool {
    // SAFETY: both arguments must be initialized and readable before comparison.
    unsafe { ptr::read_volatile(a) < ptr::read_volatile(b) }
}

fn cut_ord_violation() -> ! {
    // The panic stub cuts only the explicit order-violation path; normal returns are covered below.
    kani::assume(false);
    unreachable!()
}

fn check_insert(call: impl FnOnce(&mut [u8; 2])) {
    let mut v: [u8; 2] = kani::any();
    let before = v;
    call(&mut v);
    assert!(v[0] <= v[1]);
    assert!((v == before) || (v == [before[1], before[0]]));
    kani::cover(true, "insertion returns a sorted permutation");
}

fn count(v: &[u8; 4], probe: u8) -> usize {
    (v[0] == probe) as usize
        + (v[1] == probe) as usize
        + (v[2] == probe) as usize
        + (v[3] == probe) as usize
}

fn arbitrary_less(a: &u8, b: &u8) -> bool {
    // SAFETY: both comparator arguments must be initialized and readable.
    unsafe {
        let _left = ptr::read_volatile(a);
        let _right = ptr::read_volatile(b);
    }
    kani::any()
}

fn check_merge_consumption(call: impl FnOnce(&[u8; 4], *mut u8)) {
    let src: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut dst = MaybeUninit::<[u8; 4]>::uninit();
    call(&src, dst.as_mut_ptr().cast());
    // SAFETY: both merge directions wrote two output elements on normal return.
    let result = unsafe { dst.assume_init() };
    assert!(count(&src, probe) == count(&result, probe));
    kani::cover(true, "merge preserves the probe count on normal return");
}

#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn sorted_permutation_insert_tail_u8_n2() {
    // SAFETY: sorted one-element prefix and initialized tail in the same array.
    check_insert(|v: &mut [u8; 2]| unsafe {
        insert_tail(v.as_mut_ptr(), v.as_mut_ptr().add(1), &mut strict_less)
    });
}

#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn permutation_merge_u8_n4() {
    // SAFETY: helper supplies four initialized inputs and a separate four-element destination.
    check_merge_consumption(|v: &[u8; 4], d| unsafe {
        bidirectional_merge(v, d, &mut arbitrary_less)
    });
}

// The canonical comparator is fixed by the body, so there is no function pointer to validate.
#[kani::requires(swap_geometry::<u8>(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<LtU8>(old(pair_models::<LtU8>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<LtU8>(v, a, b))]
unsafe fn swap_profile_function_item(v: *mut u8, a: usize, b: usize) {
    // SAFETY: fixture values are initialized and the requires check the pointer geometry.
    unsafe { swap_if_less(v, a, b, &mut lt_u8) };
}

#[kani::proof_for_contract(swap_profile_function_item)]
fn swap_contract_four_positions_u8_function_item() {
    let mut v: [u8; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    kani::cover(a == 0 && b == 3, "swap_if_less: a < b reachable");
    kani::cover(a == 3 && b == 0, "swap_if_less: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`.
    unsafe { swap_profile_function_item(v.as_mut_ptr(), a, b) };
    kani::cover(lt_u8(&old_b, &old_a), "swap_if_less: swap taken");
    kani::cover(!lt_u8(&old_b, &old_a), "swap_if_less: swap not taken");
    kani::cover(true, "swap_if_less: end reached");
}

#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn small_sort_general_with_scratch_u8_n4() {
    let before: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = before;
    let mut scratch = [MaybeUninit::<u8>::uninit(); 4 + 16];
    small_sort_general_with_scratch(&mut v, &mut scratch, &mut strict_less);
    kani::assert(v[0] <= v[1] && v[1] <= v[2] && v[2] <= v[3], "scratch sort returns sorted bytes");
    kani::assert(
        count(&v, probe) == count(&before, probe),
        "scratch sort preserves the probe count",
    );
    kani::cover(true, "scratch sort returns normally");
}

/// U9: the real N4 scratch path initializes slots 0..4 but never writes slot 4.
#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn small_sort_general_scratch_unwritten_slot_u8_n4() {
    let mut v: [u8; 4] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); 20];
    small_sort_general_with_scratch(&mut v, &mut scratch, &mut strict_less);
    kani::cover(true, "U9 scratch: normal return reached");

    // SAFETY: the N4 path copies and extends both two-byte halves in scratch[0..4].
    let written = unsafe { scratch[3].assume_init_read() };
    kani::cover(written == 0, "U9 scratch[3]: written byte zero");
    kani::cover(written != 0, "U9 scratch[3]: written byte nonzero");

    kani::cover(true, "U9 scratch[4]: unwritten read reached");
    // SAFETY: intentionally violated; slot 4 remains unwritten after the real sort.
    let unwritten = unsafe { scratch[4].assume_init_read() };
    kani::cover(unwritten == 0, "U9 scratch[4]: unwritten byte zero");
    kani::cover(unwritten != 0, "U9 scratch[4]: unwritten byte nonzero");
}

/// U9a: observe only the written slot after the same real N4 scratch sort as U9.
#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn small_sort_general_scratch_written_slot_u8_n4() {
    let mut v: [u8; 4] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); 20];
    small_sort_general_with_scratch(&mut v, &mut scratch, &mut strict_less);
    kani::cover(true, "U9a scratch: normal return reached");

    // SAFETY: the N4 path copies and extends both two-byte halves in scratch[0..4].
    let written = unsafe { scratch[3].assume_init_read() };
    kani::cover(written == 0, "U9a scratch[3]: written byte zero");
    kani::cover(written != 0, "U9a scratch[3]: written byte nonzero");
}

/// U9b: observe only the unwritten slot after the same real N4 scratch sort as U9.
#[kani::proof]
#[kani::unwind(17)]
#[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
fn small_sort_general_scratch_unwritten_slot_only_u8_n4() {
    let mut v: [u8; 4] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); 20];
    small_sort_general_with_scratch(&mut v, &mut scratch, &mut strict_less);
    kani::cover(true, "U9b scratch: normal return reached");

    kani::cover(true, "U9b scratch[4]: unwritten read reached");
    // SAFETY: intentionally violated; slot 4 remains unwritten after the real sort.
    let unwritten = unsafe { scratch[4].assume_init_read() };
    kani::cover(unwritten == 0, "U9b scratch[4]: unwritten byte zero");
    kani::cover(unwritten != 0, "U9b scratch[4]: unwritten byte nonzero");
}
