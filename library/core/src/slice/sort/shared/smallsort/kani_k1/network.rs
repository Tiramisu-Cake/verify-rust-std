//! K1-network agent: contracts and harnesses for `swap_if_less`, `sort9_optimal`, `sort13_optimal`,
//! `insertion_sort_shift_left` and `small_sort_network`.
//! Written from the std source and the Kani documentation only (EXPERIMENT.md, rule R1).

use super::super::swap_if_less;
use crate::kani;

/// The comparator of every harness here: a strict order on the full value. A named function, so
/// that a contract proved with it and a `stub_verified` use of it share one `F`.
fn lt<T: Ord>(a: &T, b: &T) -> bool {
    a < b
}

// ---------------------------------------------------------------------------------------------
// swap_if_less

/// Positions anywhere in a 4-element array, in either order, distinct as the contract requires.
fn check_swap_if_less<T: kani::Arbitrary + Ord + Copy>() {
    let mut v: [T; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    kani::cover(a == 0 && b == 3, "swap_if_less: a < b reachable");
    kani::cover(a == 3 && b == 0, "swap_if_less: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut lt::<T>) };
    kani::cover(old_b < old_a, "swap_if_less: swap taken");
    kani::cover(!(old_b < old_a), "swap_if_less: swap not taken");
    kani::cover(true, "swap_if_less: end reached");
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_u8() {
    check_swap_if_less::<u8>();
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_i32() {
    check_swap_if_less::<i32>();
}

#[kani::proof_for_contract(super::super::swap_if_less)]
fn swap_if_less_u64() {
    check_swap_if_less::<u64>();
}

/// R11 control: under `stub_verified`, a call that breaks `requires(a_pos != b_pos)` must be
/// reported as a failed precondition. Nothing else in this call can fail: the positions are
/// in-bounds and the postcondition is satisfiable.
#[kani::proof]
#[kani::stub_verified(super::super::swap_if_less)]
fn r11_control_swap_if_less_requires() {
    let mut v: [u8; 2] = kani::any();
    // SAFETY: deliberately breaks the contract precondition `a_pos != b_pos`; position 1 is
    // in-bounds, so the real body would be memory safe.
    unsafe { swap_if_less(v.as_mut_ptr(), 1, 1, &mut lt::<u8>) };
    kani::cover(true, "r11 control: end reached");
}
