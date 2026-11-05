//! Bounded allocation-aware helper contracts and paired consumers.
//! Every root fixes its element and comparator function-item type and allocation geometry.
//! Diagnostic labels describe each operation. Arbitrary comparator answers impose no order.
//! No universal callback, sortedness, unwinding, uninit or value-validity theorem is claimed.

use super::super::{UnstableSmallSortTypeImpl, bidirectional_merge, sort8_stable, swap_if_less};
use crate::mem::{ManuallyDrop, MaybeUninit};
use crate::{kani, ptr};

fn arbitrary_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: the real helper supplies readable initialized references. ManuallyDrop
    // prevents dropping the temporary volatile copies of the Copy scalar elements.
    unsafe {
        let _a = ManuallyDrop::new(ptr::read_volatile(a));
        let _b = ManuallyDrop::new(ptr::read_volatile(b));
    }
    let answer: bool = kani::any();
    kani::cover(answer, "comparator true");
    kani::cover(!answer, "comparator false");
    answer
}

fn exercise_swap<T: kani::Arbitrary + Copy + PartialEq>() {
    let mut backing: [T; 32] = kani::any();
    let before = backing;
    let start: usize = kani::any();
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(start < 32);
    kani::assume(a < 32 - start && b < 32 - start);
    // SAFETY: both possibly equal relative positions are initialized writable elements
    // in this allocation, including when the base is an interior pointer.
    unsafe { swap_if_less(backing.as_mut_ptr().add(start), a, b, &mut arbitrary_less::<T>) };
    for i in 0..32 {
        kani::assert(
            i == start + a || i == start + b || backing[i] == before[i],
            "swap allocation frame",
        );
    }
    kani::cover(a == b, "swap equal positions return");
    kani::cover(a < b, "swap increasing positions return");
    kani::cover(a > b, "swap decreasing positions return");
    kani::cover(start == 0, "swap allocation base returns");
    kani::cover(start == 16, "swap second half base returns");
    kani::cover(start + b == 31, "swap last element returns");
    kani::cover(true, "swap returns");
}

fn cut_order_violation() -> ! {
    kani::cover(true, "network order violation reachable");
    kani::assume(false);
    unreachable!()
}

fn tail_less_u64(a: &u64, b: &u64) -> bool {
    // SAFETY: the helper must provide readable, initialized scalar references.
    unsafe {
        ptr::read_volatile(a);
        ptr::read_volatile(b);
    }
    let answer: bool = kani::any();
    tail_comparison_covers(answer);
    answer
}

fn tail_comparison_covers(answer: bool) {
    kani::cover(answer, "comparator true");
    kani::cover(!answer, "comparator false");
}

fn cut_merge_order_violation() -> ! {
    kani::cover(true, "merge order violation reachable");
    kani::assume(false);
    unreachable!()
}

/// T = u8; F = arbitrary_less::<u8>; initialized allocation [u8; 32].
/// Base start is any 0..32; a,b are any positions < 32-start, including equality.
/// Checks the frame outside start+a/start+b; unwind 50; default solver.
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(50)]
fn swap_safety_u8_backing32() {
    exercise_swap::<u8>();
}

/// T = u64; F = arbitrary_less::<u64>; initialized allocation [u64; 32].
/// Base start is any 0..32; a,b are any positions < 32-start, including equality.
/// Checks the frame outside start+a/start+b; unwind 50; default solver.
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(50)]
fn swap_safety_u64_backing32() {
    exercise_swap::<u64>();
}

/// T = u8; F = arbitrary_less::<u8>; initialized allocation [u8; 32], start 0, len 32.
/// Real unstable network uses half starts 0/16 and insertion offset 13 on each len16 half.
/// Verified swap stub matches the paired allocation32 PFC; insertion/merge are real.
/// Order-violation panic is cut; unwind 50; default solver.
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation)]
#[kani::unwind(50)]
fn unstable_network_safety_u8_n32_stubbed() {
    let mut backing: [u8; 32] = kani::any();
    kani::cover(backing.len() == 32, "network maximum length entered");
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut backing, &mut arbitrary_less::<u8>);
    kani::cover(true, "network maximum length returns");
}

/// T = u64; F = tail_less_u64; allocation [MaybeUninit<u64>; 48], source start 32, len 8.
/// Only source [32..40] is initialized with arbitrary values; destination [0..8] is uninit.
/// Checks the source frame; order-violation panic is cut; unwind 34; default solver.
#[kani::proof_for_contract(bidirectional_merge)]
#[kani::stub(super::super::panic_on_ord_violation, cut_merge_order_violation)]
#[kani::unwind(34)]
fn merge_safety_u64_len8_scratch48_src32_dst0() {
    let values: [u64; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    for i in 0..8 {
        scratch[32 + i].write(values[i]);
    }
    kani::cover(values.len() == 8, "merge length8 entered");
    // SAFETY: initialized source [32..40] and uninitialized destination [0..8] are
    // disjoint regions of this one aligned, writable allocation of 48 elements.
    unsafe {
        let base = scratch.as_mut_ptr().cast::<u64>();
        let source = crate::slice::from_raw_parts(base.add(32), 8);
        bidirectional_merge(source, base, &mut tail_less_u64);
    }
    for i in 0..8 {
        // SAFETY: the initialized source must be framed by the merge.
        let after = unsafe { scratch[32 + i].assume_init() };
        kani::assert(after == values[i], "merge source frame");
    }
    kani::cover(true, "merge length8 returns");
}

/// T = u64; F = tail_less_u64; initialized input [u64; 32], start 0, input len 8.
/// Scratch [MaybeUninit<u64>; 48] starts uninit; destination start 0, scratch source start 32.
/// Real sort4 initializes [32..40] before the matching verified len8 merge stub.
/// Checks all 32 input elements framed; no output initialization assumed; unwind 34.
/// Default solver; input values and comparator answers are arbitrary.
#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(34)]
fn sort8_safety_u64_scratch48_src32_dst0_merge_stubbed() {
    let mut backing: [u64; 32] = kani::any();
    let before = backing;
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    kani::cover(scratch.len() == 48, "sort8 scratch48 entered");
    // SAFETY: the real sort4 calls initialize scratch[32..40] before the verified
    // merge stub writes the disjoint destination [0..8]. Input has eight readable elements.
    unsafe {
        let base = scratch.as_mut_ptr().cast::<u64>();
        sort8_stable(backing.as_mut_ptr(), base, base.add(32), &mut tail_less_u64);
    }
    for i in 0..32 {
        kani::assert(backing[i] == before[i], "sort8 source allocation frame");
    }
    // A safety/modifies-only stub gives no initialization postcondition for destination.
    kani::cover(true, "sort8 merge consumer returns");
}
