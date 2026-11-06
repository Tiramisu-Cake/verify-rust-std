//! Real helper contract proofs and consumers paired on the same comparator and allocation.
//! The reading comparator chooses each answer independently, including at equal swap positions.

#[cfg(kani_smallsort_controls)]
use super::super::insertion_sort_shift_left;
use super::super::{bidirectional_merge, insert_tail, sort4_stable, swap_if_less};
use crate::kani;

fn arbitrary_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: the real helper must pass initialized readable references. The proof uses Copy
    // elements; ManuallyDrop also prevents running Drop on the temporary volatile copies.
    unsafe {
        let _a = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(a));
        let _b = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(b));
    }
    let answer: bool = kani::any();
    comparison_covers(answer);
    answer
}

// A coverage-only hook lets stubbed consumers omit unreachable callback covers while retaining
// the same arbitrary_less::<u8> function-item type as their matching ordinary PFCs.
fn comparison_covers(answer: bool) {
    kani::cover(answer, "realcontracts comparator true");
    kani::cover(!answer, "realcontracts comparator false");
}

fn omit_comparison_covers(_answer: bool) {}

fn exercise_swap<T: kani::Arbitrary + Copy + PartialEq>() {
    let mut v: [T; 4] = kani::any();
    let before = v;
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < 4 && b < 4);
    // SAFETY: both positions are initialized, aligned, readable and writable and in this allocation.
    // Equality is allowed by the real helper's safety condition.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut arbitrary_less::<T>) };
    for i in 0..4 {
        kani::assert(i == a || i == b || v[i] == before[i], "realcontracts swap frame");
    }
    kani::cover(a == b, "realcontracts equal swap positions return");
    kani::cover(a < b, "realcontracts increasing swap positions return");
    kani::cover(a > b, "realcontracts decreasing swap positions return");
    kani::cover(true, "realcontracts swap returns");
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(8)]
fn swap_safety_u8_backing4() {
    exercise_swap::<u8>();
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(8)]
fn swap_safety_u64_backing4() {
    exercise_swap::<u64>();
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(32)]
fn swap_safety_bytes17_backing4() {
    exercise_swap::<[u8; 17]>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::unwind(16)]
fn insertion_safety_u64_len1_to6() {
    let mut backing: [u64; 6] = kani::any();
    let before = backing;
    let len: usize = kani::any();
    kani::assume(1 <= len && len <= 6);
    let offset: usize = kani::any();
    kani::assume(offset != 0 && offset <= len);
    insertion_sort_shift_left(&mut backing[..len], offset, &mut arbitrary_less::<u64>);
    for i in 0..6 {
        kani::assert(i < len || backing[i] == before[i], "realcontracts insertion frame");
    }
    kani::cover(len == 1, "realcontracts insertion len1 returns");
    kani::cover(len == 2, "realcontracts insertion len2 returns");
    kani::cover(len == 3, "realcontracts insertion len3 returns");
    kani::cover(len == 4, "realcontracts insertion len4 returns");
    kani::cover(len == 5, "realcontracts insertion len5 returns");
    kani::cover(len == 6, "realcontracts insertion len6 returns");
    kani::cover(offset < len, "realcontracts insertion offset below len returns");
    kani::cover(offset == len, "realcontracts insertion final offset returns");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
fn rejects_swap_outside_backing_u8() {
    let mut v: [u8; 4] = kani::any();
    kani::cover(true, "realcontracts invalid swap consumer reached");
    // Deliberate contract violation: b == 4 is one-past-end, so it cannot be dereferenced.
    // The verified stub must reject its requires before havoc or any real-body access.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 4, &mut arbitrary_less::<u8>) };
}

// Constant lengths avoid a symbolic loop bound in the insertion proof.
#[cfg(kani_smallsort_controls)]
fn exercise_insertion_fixed<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let offset: usize = kani::any();
    kani::assume(offset != 0 && offset <= N);
    insertion_sort_shift_left(&mut v, offset, &mut arbitrary_less::<u64>);
    kani::cover(offset == 1, "realcontracts fixed insertion offset one returns");
    kani::cover(offset == N, "realcontracts fixed insertion final offset returns");
    kani::cover(offset < N, "realcontracts fixed insertion below final offset returns");
    kani::cover(true, "realcontracts fixed insertion returns");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::unwind(8)]
fn insertion_safety_u64_len2() {
    exercise_insertion_fixed::<2>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::unwind(8)]
fn insertion_safety_u64_len3() {
    exercise_insertion_fixed::<3>();
}

// These lengths finish after the network: insertion starts at the end and no merge runs.
// Real and stubbed consumers share this body and the stateless comparator. Each stubbed
// consumer needs the swap proof for its own allocation size; a four-element proof is insufficient.
fn exercise_unstable_network_u8<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    <u8 as super::super::UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut arbitrary_less::<u8>);
    kani::cover(true, "realcontracts unstable network consumer returns");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n9_real() {
    exercise_unstable_network_u8::<9>();
}

#[kani::proof]
#[kani::stub(comparison_covers, omit_comparison_covers)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n9_stubbed() {
    exercise_unstable_network_u8::<9>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n9_stubbed_with_callback_covers() {
    exercise_unstable_network_u8::<9>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n13_real() {
    exercise_unstable_network_u8::<13>();
}

#[kani::proof]
#[kani::stub(comparison_covers, omit_comparison_covers)]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n13_stubbed() {
    exercise_unstable_network_u8::<13>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n13_stubbed_with_callback_covers() {
    exercise_unstable_network_u8::<13>();
}

// Match the consumers' allocation sizes and comparator type, including coincident positions.
fn exercise_swap_u8_backing<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    let before = v;
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < N && b < N);
    // SAFETY: both positions are initialized writable elements of this allocation.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut arbitrary_less::<u8>) };
    for i in 0..N {
        kani::assert(i == a || i == b || v[i] == before[i], "realcontracts swap frame");
    }
    kani::cover(a == b, "realcontracts equal swap positions return");
    kani::cover(a < b, "realcontracts increasing swap positions return");
    kani::cover(a > b, "realcontracts decreasing swap positions return");
    kani::cover(true, "realcontracts swap returns");
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(16)]
fn swap_safety_u8_backing9() {
    exercise_swap_u8_backing::<9>();
}

#[kani::proof_for_contract(swap_if_less)]
#[kani::unwind(16)]
fn swap_safety_u8_backing13() {
    exercise_swap_u8_backing::<13>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_safety_u64_tail1_to4_backing5() {
    let mut v: [u64; 5] = kani::any();
    let before = v;
    let tail: usize = kani::any();
    kani::assume(1 <= tail && tail <= 4);
    let begin = v.as_mut_ptr();
    // SAFETY: begin < tail, and the inclusive region is initialized, readable and writable,
    // aligned and within this one allocation. No sorted-prefix premise is needed for safety.
    unsafe { insert_tail(begin, begin.add(tail), &mut arbitrary_less::<u64>) };
    for i in 0..5 {
        kani::assert(i <= tail || v[i] == before[i], "realcontracts insert_tail frame");
    }
    kani::cover(tail == 1, "realcontracts insert_tail offset1 returns");
    kani::cover(tail == 2, "realcontracts insert_tail offset2 returns");
    kani::cover(tail == 3, "realcontracts insert_tail offset3 returns");
    kani::cover(tail == 4, "realcontracts insert_tail offset4 returns");
    kani::cover(true, "realcontracts insert_tail returns");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn rejects_insert_tail_equal_begin_u64() {
    let mut v: [u64; 5] = kani::any();
    let begin = v.as_mut_ptr();
    kani::cover(true, "realcontracts invalid insert_tail consumer reached");
    // Deliberate contract violation: initialized pointers in one allocation, but tail == begin.
    // The stub must fail the begin < tail requires, before any real-body access.
    unsafe { insert_tail(begin, begin, &mut arbitrary_less::<u64>) };
}

#[kani::proof_for_contract(sort4_stable)]
#[kani::unwind(16)]
fn sort4_safety_u64() {
    let src: [u64; 4] = kani::any();
    let before = src;
    let mut dst = crate::mem::MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: four initialized source values and a distinct allocation writable for four
    // destination values. The destination need not be initialized before the call.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr().cast(), &mut arbitrary_less::<u64>) };
    for i in 0..4 {
        kani::assert(src[i] == before[i], "realcontracts sort4 source frame");
    }
    // SAFETY: the real body writes all four output slots on every normal-return path.
    // Read the output to exercise the initialized slots.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: each returned output element is initialized and readable.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontracts sort4 returns");
}

#[cfg(kani_smallsort_controls)]
// Scalar byte comparisons avoid the loop inside array PartialEq's memcmp.
#[kani::proof_for_contract(sort4_stable)]
#[kani::unwind(32)]
fn sort4_safety_bytes16() {
    let src: [[u8; 16]; 4] = kani::any();
    let before = src;
    let mut dst = crate::mem::MaybeUninit::<[[u8; 16]; 4]>::uninit();
    // SAFETY: four initialized source values, disjoint storage writable for four outputs.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr().cast(), &mut arbitrary_less::<[u8; 16]>) };
    for i in 0..4 {
        for byte in 0..16 {
            kani::assert(
                src[i][byte] == before[i][byte],
                "realcontracts sort4 byte source frame",
            );
        }
    }
    // SAFETY: the real body writes all four output values before returning normally.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: each output is initialized on normal return.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontracts sort4 bytes16 returns");
}

fn cut_merge_order_violation() -> ! {
    // Cover the explicit order-violation boundary before cutting the abort path.
    kani::cover(true, "realcontracts merge order violation reachable");
    kani::assume(false);
    unreachable!()
}

fn exercise_merge_u64<const N: usize>() {
    let src: [u64; N] = kani::any();
    let before = src;
    let mut dst = crate::mem::MaybeUninit::<[u64; N]>::uninit();
    // SAFETY: N is 2 or 4 in these PFCs; src is an initialized Freeze u64 slice,
    // and a distinct destination allocation has space for exactly N values.
    unsafe { bidirectional_merge(&src, dst.as_mut_ptr().cast(), &mut arbitrary_less::<u64>) };
    for i in 0..N {
        kani::assert(src[i] == before[i], "realcontracts merge source frame");
    }
    // SAFETY: every output slot is written on normal return; inconsistent comparator
    // paths reach the explicit panic boundary and are cut by the safety stub.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: initialized output on normal return.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontracts merge returns");
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::stub(super::super::panic_on_ord_violation, cut_merge_order_violation)]
#[kani::unwind(16)]
fn merge_safety_u64_len2() {
    exercise_merge_u64::<2>();
}

#[kani::proof_for_contract(bidirectional_merge)]
#[kani::stub(super::super::panic_on_ord_violation, cut_merge_order_violation)]
#[kani::unwind(16)]
fn merge_safety_u64_len4() {
    exercise_merge_u64::<4>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(16)]
fn rejects_merge_overlapping_dst_u64() {
    let mut backing: [u64; 4] = kani::any();
    let base = backing.as_mut_ptr();
    // SAFETY: source is the first two initialized values of this allocation.
    let src = unsafe { crate::slice::from_raw_parts(base as *const u64, 2) };
    kani::cover(true, "realcontracts overlapping merge consumer reached");
    // Deliberate contract violation: dst[0..2] covers backing[1..3], so it is writable
    // and in bounds but overlaps source[0..2] at backing[1]. Only disjointness fails.
    unsafe { bidirectional_merge(src, base.add(1), &mut arbitrary_less::<u64>) };
}

// The order is lawful; only the captured counter lies outside the helper's write set.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(swap_if_less)]
fn rejects_swap_comparator_writing_outside_frame_u8() {
    let mut v: [u8; 4] = kani::any();
    let mut comparisons = 0u8;
    let mut is_less = |a: &u8, b: &u8| {
        comparisons = comparisons.wrapping_add(1);
        *a < *b
    };
    // SAFETY: both positions are distinct initialized writable elements of this allocation.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut is_less) };
}
