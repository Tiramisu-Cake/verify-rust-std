//! Opt-in, one-factor diagnostics for the real `insert_tail` safety/modifies contract.
//! The common domain is start 0, symbolic tail 1..=7, fully initialized arbitrary values,
//! unwind 32 and an explicit suffix frame. Backing, answer policy, solver, type and frame
//! change independently from the u64/backing17/default-solver/arbitrary-answer baseline.
//! Two additional tail 8..=15 roots extend the baseline and deterministic comparator domains.
//! No sorted-prefix assumption, profile wrapper, stub, loop contract or runtime change is used.
//! Each result is bounded by its exact T/F/allocation/start/tail domain; it is not a generic
//! callback theorem. No uninitialized-memory, value-validity, permission or panic-unwinding proof.

use super::super::insert_tail;
use crate::kani;

fn read_arguments<T: Copy>(a: &T, b: &T) -> (T, T) {
    // SAFETY: the real helper must supply initialized readable references. T is Copy, so the
    // temporary volatile copies cannot run Drop. Both comparator policies make the same reads.
    unsafe { (crate::ptr::read_volatile(a), crate::ptr::read_volatile(b)) }
}

fn comparison_covers(answer: bool) {
    kani::cover(answer, "taildiag comparator true");
    kani::cover(!answer, "taildiag comparator false");
}

fn arbitrary_less<T: Copy>(a: &T, b: &T) -> bool {
    let _values = read_arguments(a, b);
    let answer: bool = kani::any();
    comparison_covers(answer);
    answer
}

fn value_less_u64(a: &u64, b: &u64) -> bool {
    let (a, b) = read_arguments(a, b);
    let answer = a < b;
    comparison_covers(answer);
    answer
}

fn exercise<T, F, const N: usize, const LO: usize, const HI: usize, const FRAME: bool>(mut cmp: F)
where
    T: kani::Arbitrary + Copy + PartialEq,
    F: FnMut(&T, &T) -> bool,
{
    const { assert!(0 < LO && LO < HI && HI < N) };
    let mut v: [T; N] = kani::any();
    let before = v;
    let tail: usize = kani::any();
    kani::assume(LO <= tail && tail <= HI);
    let begin = v.as_mut_ptr();
    // SAFETY: start 0 < LO <= tail <= HI < N. The inclusive region belongs to this one
    // initialized writable allocation. Safety requires no sortedness and no ordering law.
    unsafe { insert_tail(begin, begin.add(tail), &mut cmp) };
    if FRAME {
        for i in 0..N {
            kani::assert(i <= tail || v[i] == before[i], "taildiag suffix frame");
        }
    }
    kani::cover(tail == LO, "taildiag lowest tail returns");
    kani::cover(tail == HI, "taildiag highest tail returns");
    kani::cover(true, "taildiag returns");
}

/// Backing-size factor; initialized [u64; 8], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing8_tail1_to7() {
    exercise::<u64, _, 8, 1, 7, true>(arbitrary_less::<u64>);
}

/// Backing-size factor; initialized [u64; 12], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing12_tail1_to7() {
    exercise::<u64, _, 12, 1, 7, true>(arbitrary_less::<u64>);
}

/// Baseline; initialized [u64; 17], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing17_tail1_to7() {
    exercise::<u64, _, 17, 1, 7, true>(arbitrary_less::<u64>);
}

/// Comparator factor; initialized [u64; 17], start 0, tail 1..=7, unwind 32.
/// F = value_less_u64; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing17_tail1_to7_value_order() {
    exercise::<u64, _, 17, 1, 7, true>(value_less_u64);
}

/// Solver factor; initialized [u64; 17], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = cadical; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
#[kani::solver(cadical)]
fn u64_backing17_tail1_to7_cadical() {
    exercise::<u64, _, 17, 1, 7, true>(arbitrary_less::<u64>);
}

/// Solver factor; initialized [u64; 17], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = kissat; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
#[kani::solver(kissat)]
fn u64_backing17_tail1_to7_kissat() {
    exercise::<u64, _, 17, 1, 7, true>(arbitrary_less::<u64>);
}

/// Element-type factor; initialized [u8; 17], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u8>; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u8_backing17_tail1_to7() {
    exercise::<u8, _, 17, 1, 7, true>(arbitrary_less::<u8>);
}

/// Frame factor; initialized [u64; 17], start 0, tail 1..=7, unwind 32.
/// F = arbitrary_less::<u64>; solver = default; explicit suffix frame = false.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing17_tail1_to7_no_explicit_frame() {
    exercise::<u64, _, 17, 1, 7, false>(arbitrary_less::<u64>);
}

/// Upper-tail baseline extension; initialized [u64; 17], start 0, tail 8..=15, unwind 32.
/// F = arbitrary_less::<u64>; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing17_tail8_to15() {
    exercise::<u64, _, 17, 8, 15, true>(arbitrary_less::<u64>);
}

/// Upper-tail comparator extension; initialized [u64; 17], start 0, tail 8..=15, unwind 32.
/// F = value_less_u64; solver = default; explicit suffix frame = true.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn u64_backing17_tail8_to15_value_order() {
    exercise::<u64, _, 17, 8, 15, true>(value_less_u64);
}
