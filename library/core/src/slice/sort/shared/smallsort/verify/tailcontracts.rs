//! Bounded real insert_tail safety/modifies contracts on an initialized allocation.
//! The arbitrary reading comparator has no ordering law or sorted-prefix premise.
//! No explicit suffix frame is added; the real modifies contract remains checked.
//! No universal callback, uninit, value-validity, permission or panic-unwinding theorem.

use super::super::insert_tail;
use crate::kani;

fn read_arguments<T: Copy>(a: &T, b: &T) -> (T, T) {
    // SAFETY: the real helper supplies initialized readable references; T is Copy.
    unsafe { (crate::ptr::read_volatile(a), crate::ptr::read_volatile(b)) }
}

fn comparison_covers(answer: bool) {
    kani::cover(answer, "comparator true");
    kani::cover(!answer, "comparator false");
}

fn arbitrary_less<T: Copy>(a: &T, b: &T) -> bool {
    let _values = read_arguments(a, b);
    let answer: bool = kani::any();
    comparison_covers(answer);
    answer
}

fn exercise<T, F, const N: usize, const LO: usize, const HI: usize>(mut cmp: F)
where
    T: kani::Arbitrary + Copy + PartialEq,
    F: FnMut(&T, &T) -> bool,
{
    const { assert!(0 < LO && LO < HI && HI < N) };
    let mut v: [T; N] = kani::any();
    let tail: usize = kani::any();
    kani::assume(LO <= tail && tail <= HI);
    let begin = v.as_mut_ptr();
    // SAFETY: start 0 < LO <= tail <= HI < N; the inclusive region is initialized,
    // writable, aligned and in one allocation. No sortedness premise is required.
    unsafe { insert_tail(begin, begin.add(tail), &mut cmp) };
    kani::cover(tail == LO, "insert_tail lowest tail returns");
    kani::cover(tail == HI, "insert_tail highest tail returns");
    kani::cover(true, "insert_tail returns");
}

/// T = u64; F = arbitrary_less::<u64>; initialized allocation [u64; 17], start 0.
/// Symbolic tail 1..=7; arbitrary values, no sortedness premise; unwind 32, default solver.
/// No explicit suffix frame; real safety/modifies contract checked.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn insert_tail_safety_u64_backing17_tail1_to7() {
    exercise::<u64, _, 17, 1, 7>(arbitrary_less::<u64>);
}

/// T = u64; F = arbitrary_less::<u64>; initialized allocation [u64; 17], start 0.
/// Symbolic tail 8..=15; arbitrary values, no sortedness premise; unwind 32, default solver.
/// No explicit suffix frame; real safety/modifies contract checked.
#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(32)]
fn insert_tail_safety_u64_backing17_tail8_to15() {
    exercise::<u64, _, 17, 8, 15>(arbitrary_less::<u64>);
}
