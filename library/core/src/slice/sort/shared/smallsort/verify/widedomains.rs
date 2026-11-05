//! WIDEDOMAINS G1: allocation-aware real-helper safety PFCs and one real network consumer.
//! All roots are opt-in through the parent module. Each proof fixes its T and function-item F;
//! no generic callback frame, sortedness, unwinding, uninit or value-validity proof is claimed.
//! Backing32 swap permits an interior base, including the N32 network's second half at 16.
//! Tail partitions keep allocation identity/size, begin offset and outside initialization
//! explicit. Backing48 partitions are scratch evidence, not inferred from backing32.

use super::super::{
    UnstableSmallSortTypeImpl, bidirectional_merge, insert_tail, insertion_sort_shift_left,
    sort8_stable, swap_if_less,
};
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

// G2 fixes the consumer's initialized backing32 and starts 0/16. These are new restricted
// domains, not proofs of G1's arbitrary-start/initialization-mask domains that timed out.
// Keep G1's comparator and roots unchanged. This separate function item has a coverage-only
// hook so insertion PFCs can omit callback covers cut by their verified insert_tail stubs.
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
    kani::cover(answer, "widedomains G2 comparator true");
    kani::cover(!answer, "widedomains G2 comparator false");
}

fn omit_tail_comparison_covers(_answer: bool) {}

fn exercise_initialized_tail<const LO: usize, const HI: usize>() -> (usize, usize) {
    const { assert!(1 <= LO && LO <= HI && HI <= 19) };
    let mut backing: [u64; 32] = kani::any();
    let before = backing;
    let start = if kani::any() { 16 } else { 0 };
    let tail: usize = kani::any();
    kani::assume(LO <= tail && tail <= HI);
    kani::assume(start + tail < 32);
    // SAFETY: the inclusive region lies in initialized, exclusively writable backing32.
    unsafe {
        let begin = backing.as_mut_ptr().add(start);
        insert_tail(begin, begin.add(tail), &mut tail_less_u64);
    }
    for i in 0..32 {
        kani::assert(
            (start <= i && i <= start + tail) || backing[i] == before[i],
            "widedomains G2 insert_tail frame",
        );
    }
    kani::cover(tail == LO, "widedomains G2 tail partition lower end returns");
    kani::cover(tail == HI, "widedomains G2 tail partition upper end returns");
    kani::cover(start == 0, "widedomains G2 tail first region returns");
    kani::cover(start == 16, "widedomains G2 tail second region returns");
    kani::cover(true, "widedomains G2 tail returns");
    (start, tail)
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(34)]
fn insert_tail_initialized_u64_backing32_tail1_to4() {
    exercise_initialized_tail::<1, 4>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(34)]
fn insert_tail_initialized_u64_backing32_tail5_to9() {
    exercise_initialized_tail::<5, 9>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(34)]
fn insert_tail_initialized_u64_backing32_tail10_to14() {
    exercise_initialized_tail::<10, 14>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(34)]
fn insert_tail_initialized_u64_backing32_tail15_to19() {
    let (start, tail) = exercise_initialized_tail::<15, 19>();
    kani::cover(start + tail == 31, "widedomains G2 tail last element returns");
}

fn exercise_stubbed_insertion<const LO: usize, const HI: usize>() -> usize {
    const { assert!(1 <= LO && LO <= HI && HI <= 20) };
    let mut backing: [u64; 32] = kani::any();
    let before = backing;
    let start = if HI <= 16 && kani::any() { 16 } else { 0 };
    let len: usize = kani::any();
    let offset: usize = kani::any();
    kani::assume(LO <= len && len <= HI);
    kani::assume(1 <= offset && offset <= len);
    insertion_sort_shift_left(&mut backing[start..start + len], offset, &mut tail_less_u64);
    for i in 0..32 {
        kani::assert(
            (start <= i && i < start + len) || backing[i] == before[i],
            "widedomains G2 insertion allocation frame",
        );
    }
    kani::cover(len == LO, "widedomains G2 insertion lower length returns");
    kani::cover(len == HI, "widedomains G2 insertion upper length returns");
    kani::cover(start == 0, "widedomains G2 insertion first region returns");
    kani::cover(offset == 1, "widedomains G2 insertion first offset returns");
    kani::cover(offset == len, "widedomains G2 insertion final offset returns");
    kani::cover(offset < len, "widedomains G2 insertion nonempty loop returns");
    kani::cover(true, "widedomains G2 insertion returns");
    start
}

#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::stub_verified(insert_tail)]
#[kani::stub(tail_comparison_covers, omit_tail_comparison_covers)]
#[kani::unwind(34)]
fn insertion_stubbed_u64_backing32_len1_to16() {
    let start = exercise_stubbed_insertion::<1, 16>();
    kani::cover(start == 16, "widedomains G2 insertion second region returns");
}

#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::stub_verified(insert_tail)]
#[kani::stub(tail_comparison_covers, omit_tail_comparison_covers)]
#[kani::unwind(34)]
fn insertion_stubbed_u64_backing32_len17_to20() {
    exercise_stubbed_insertion::<17, 20>();
}

// The G2 network uses tail_less_u64, so its swap stubs need this matching F-item PFC.
// G1's swap PFCs use arbitrary_less::<u64> and cannot supply that composition credit.
#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(34)]
fn swap_safety_u64_backing32_tail_comparator() {
    let mut backing: [u64; 32] = kani::any();
    let before = backing;
    let start: usize = kani::any();
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(start < 32);
    kani::assume(a < 32 - start && b < 32 - start);
    // SAFETY: both possibly equal positions are initialized writable allocation elements.
    unsafe { swap_if_less(backing.as_mut_ptr().add(start), a, b, &mut tail_less_u64) };
    for i in 0..32 {
        kani::assert(
            i == start + a || i == start + b || backing[i] == before[i],
            "widedomains G2 swap allocation frame",
        );
    }
    kani::cover(a == b, "widedomains G2 swap equal positions return");
    kani::cover(a < b, "widedomains G2 swap increasing positions return");
    kani::cover(a > b, "widedomains G2 swap decreasing positions return");
    kani::cover(start == 0, "widedomains G2 swap allocation base returns");
    kani::cover(start == 16, "widedomains G2 swap second half base returns");
    kani::cover(start + b == 31, "widedomains G2 swap last element returns");
    kani::cover(true, "widedomains G2 swap returns");
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::stub_verified(insertion_sort_shift_left)]
#[kani::stub(super::super::panic_on_ord_violation, cut_order_violation)]
#[kani::unwind(34)]
fn unstable_network_safety_u64_n32_swap_insertion_stubbed() {
    let mut backing: [u64; 32] = kani::any();
    kani::cover(backing.len() == 32, "widedomains G2 network maximum length entered");
    // Actual N32 network: swap at bases 0/16, insertion on length16 halves at offset13,
    // then a real merge32. Composition requires the matching G2 swap and insertion PFCs;
    // the latter requires all matching insert_tail partitions. The real merge calls F.
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut backing, &mut tail_less_u64);
    kani::cover(true, "widedomains G2 network maximum length returns");
}

fn cut_merge_order_violation() -> ! {
    kani::cover(true, "widedomains G2 merge order violation reachable");
    kani::assume(false);
    unreachable!()
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::stub(super::super::panic_on_ord_violation, cut_merge_order_violation)]
#[kani::unwind(34)]
fn merge_safety_u64_len8_scratch48_src32_dst0() {
    let values: [u64; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    for i in 0..8 {
        scratch[32 + i].write(values[i]);
    }
    kani::cover(values.len() == 8, "widedomains G2 merge length8 entered");
    // Exact first sort8_stable geometry inside small_sort_general N32: initialized source
    // scratch[32..40], disjoint uninitialized destination scratch[0..8], same allocation48.
    unsafe {
        let base = scratch.as_mut_ptr().cast::<u64>();
        let source = crate::slice::from_raw_parts(base.add(32), 8);
        bidirectional_merge(source, base, &mut tail_less_u64);
    }
    for i in 0..8 {
        // SAFETY: source elements were initialized and must be framed by the merge.
        let after = unsafe { scratch[32 + i].assume_init() };
        kani::assert(after == values[i], "widedomains G2 merge source frame");
    }
    kani::cover(true, "widedomains G2 merge length8 returns");
}

#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(34)]
fn sort8_safety_u64_scratch48_src32_dst0_merge_stubbed() {
    let mut backing: [u64; 32] = kani::any();
    let before = backing;
    let mut scratch = [MaybeUninit::<u64>::uninit(); 48];
    kani::cover(scratch.len() == 48, "widedomains G2 sort8 scratch48 entered");
    // Execute the real sort8 body, matching the first general N32 call. Real sort4 calls
    // initialize exactly scratch[32..40] before the verified merge stub writes [0..8].
    unsafe {
        let base = scratch.as_mut_ptr().cast::<u64>();
        sort8_stable(backing.as_mut_ptr(), base, base.add(32), &mut tail_less_u64);
    }
    for i in 0..32 {
        kani::assert(backing[i] == before[i], "widedomains G2 sort8 source allocation frame");
    }
    // A safety/modifies-only stub gives no initialization or sortedness postcondition;
    // do not read the destination as initialized output after this stubbed merge.
    kani::cover(true, "widedomains G2 sort8 merge consumer returns");
}
