//! WIDEDOMAINS G1: allocation-aware real-helper safety PFCs and one real network consumer.
//! All roots are opt-in through the parent module. Each proof fixes its T and function-item F;
//! no generic callback frame, sortedness, unwinding, uninit or value-validity proof is claimed.
//! Backing32 swap permits an interior base, including the N32 network's second half at 16.
//! Tail partitions keep allocation identity/size, begin offset and outside initialization
//! explicit. Backing48 partitions are scratch evidence, not inferred from backing32.

use super::super::{UnstableSmallSortTypeImpl, insert_tail, swap_if_less};
use crate::mem::{ManuallyDrop, MaybeUninit};
use crate::{kani, ptr};

fn arbitrary_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: the real helper must provide readable initialized references. All current T
    // are Copy scalars; ManuallyDrop prevents dropping the temporary volatile copies.
    unsafe {
        let _a = ManuallyDrop::new(ptr::read_volatile(a));
        let _b = ManuallyDrop::new(ptr::read_volatile(b));
    }
    let answer: bool = kani::any();
    kani::cover(answer, "widedomains comparator true");
    kani::cover(!answer, "widedomains comparator false");
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
    // SAFETY: both relative positions, including equal ones, are initialized writable
    // elements of this allocation. The base itself may be an interior pointer.
    unsafe { swap_if_less(backing.as_mut_ptr().add(start), a, b, &mut arbitrary_less::<T>) };
    for i in 0..32 {
        kani::assert(
            i == start + a || i == start + b || backing[i] == before[i],
            "widedomains swap allocation frame",
        );
    }
    kani::cover(a == b, "widedomains swap equal positions return");
    kani::cover(a < b, "widedomains swap increasing positions return");
    kani::cover(a > b, "widedomains swap decreasing positions return");
    kani::cover(start == 0, "widedomains swap allocation base returns");
    kani::cover(start == 16, "widedomains swap second half base returns");
    kani::cover(start + b == 31, "widedomains swap last element returns");
    kani::cover(true, "widedomains swap returns");
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(50)]
fn swap_safety_u8_backing32() {
    exercise_swap::<u8>();
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(50)]
fn swap_safety_u64_backing32() {
    exercise_swap::<u64>();
}

fn cut_order_violation() -> ! {
    kani::cover(true, "widedomains network order violation reachable");
    kani::assume(false);
    unreachable!()
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation)]
#[kani::unwind(50)]
fn unstable_network_safety_u8_n32_stubbed() {
    let mut backing: [u8; 32] = kani::any();
    kani::cover(backing.len() == 32, "widedomains network maximum length entered");
    // Actual unstable dispatch selects small_sort_network: two sort13 calls with bases 0/16,
    // real insertion at offset 13 on each length16 half, then a real length32 merge.
    // Only swap is contract-stubbed. The paired u8 PFC has identical F and backing32 geometry;
    // insertion and merge are real bodies and need no insert_tail/merge PFC composition credit.
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut backing, &mut arbitrary_less::<u8>);
    kani::cover(true, "widedomains network maximum length returns");
}

fn exercise_tail<const B: usize, const LO: usize, const HI: usize>() {
    const { assert!(1 <= LO && LO <= HI && HI < B) };
    let values: [u64; B] = kani::any();
    let initialized: [bool; B] = kani::any();
    let mut backing = [MaybeUninit::<u64>::uninit(); B];
    let start: usize = kani::any();
    let tail: usize = kani::any();
    kani::assume(LO <= tail && tail <= HI);
    kani::assume(start < B - tail);
    for i in 0..B {
        // Only the inclusive helper region must be initialized. Arbitrary outside masks
        // include fully initialized insertion allocations and partially initialized scratch.
        if (start <= i && i <= start + tail) || initialized[i] {
            backing[i].write(values[i]);
        }
    }
    // SAFETY: begin < tail and the inclusive region is initialized, aligned and exclusively
    // writable in one allocation; no sortedness premise is required by the safety contract.
    unsafe {
        let begin = backing.as_mut_ptr().cast::<u64>().add(start);
        insert_tail(begin, begin.add(tail), &mut arbitrary_less::<u64>);
    }
    for i in 0..B {
        if (i < start || i > start + tail) && initialized[i] {
            // SAFETY: this outside element was initialized above; the helper must frame it.
            let after = unsafe { backing[i].assume_init() };
            kani::assert(after == values[i], "widedomains insert_tail allocation frame");
        }
    }
    kani::cover(tail == LO, "widedomains insert_tail partition lower end returns");
    kani::cover(tail == HI, "widedomains insert_tail partition upper end returns");
    kani::cover(start == 0, "widedomains insert_tail allocation base returns");
    kani::cover(start > 0, "widedomains insert_tail interior base returns");
    kani::cover(start + tail == B - 1, "widedomains insert_tail last element returns");
    kani::cover(true, "widedomains insert_tail returns");
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing32_tail1_to4() {
    exercise_tail::<32, 1, 4>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing32_tail5_to8() {
    exercise_tail::<32, 5, 8>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing32_tail9_to12() {
    exercise_tail::<32, 9, 12>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing32_tail13_to16() {
    exercise_tail::<32, 13, 16>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing32_tail17_to19() {
    exercise_tail::<32, 17, 19>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing48_tail1_to4() {
    exercise_tail::<48, 1, 4>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(50)]
fn insert_tail_safety_u64_backing48_tail5_to8() {
    exercise_tail::<48, 5, 8>();
}
