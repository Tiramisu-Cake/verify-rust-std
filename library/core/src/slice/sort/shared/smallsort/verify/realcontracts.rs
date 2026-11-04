//! Opt-in real-helper contract PFCs and paired real-entry consumers with/without swap stubs.
//! Each PFC uses one T/F instantiation. Stateless comparators read both arguments and return
//! an arbitrary decision on every call, including when both swap positions are equal.
//! Bounded domains do not establish a frame for stateful or externally mutating callbacks.

use super::super::{insertion_sort_shift_left, swap_if_less};
use crate::kani;

fn arbitrary_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: the real helper must pass initialized readable references. The proof uses Copy
    // elements; ManuallyDrop also prevents running Drop on the temporary volatile copies.
    unsafe {
        let _a = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(a));
        let _b = crate::mem::ManuallyDrop::new(crate::ptr::read_volatile(b));
    }
    let answer: bool = kani::any();
    kani::cover(answer, "realcontracts comparator true");
    kani::cover(!answer, "realcontracts comparator false");
    answer
}

fn exercise_swap<T: kani::Arbitrary + Copy + PartialEq>() {
    let mut v: [T; 4] = kani::any();
    let before = v;
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < 4 && b < 4);
    // SAFETY: both positions are initialized, aligned, readable/writable and in this allocation.
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

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
fn rejects_swap_outside_backing_u8() {
    let mut v: [u8; 4] = kani::any();
    kani::cover(true, "realcontracts invalid swap consumer reached");
    // Deliberate contract violation: b == 4 is one-past-end, so it cannot be dereferenced.
    // The verified stub must reject its requires before havoc or any real-body access.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 4, &mut arbitrary_less::<u8>) };
}

// G2 isolates exact lengths after the symbolic len1..6 insertion PFC timed out in G1.
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

#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::unwind(8)]
fn insertion_safety_u64_len2() {
    exercise_insertion_fixed::<2>();
}

#[kani::proof_for_contract(insertion_sort_shift_left)]
#[kani::unwind(8)]
fn insertion_safety_u64_len3() {
    exercise_insertion_fixed::<3>();
}

// u8 selects the Copy/Freeze efficient-swap network through the actual Unstable trait entry.
// At N9/N13 the network calls sort9_optimal/sort13_optimal, then insertion at offset == N
// (no insertion iterations), and returns without merge. All swap positions are in backing N.
// Both consumers in each pair call this identical body with the same stateless F as the u8 PFC.
// The verified-stub version checks call-site requires and assumes the swap frame; G1's PFC
// backing4 is bounded evidence, not an independent universal proof for backing9/backing13.
fn exercise_unstable_network_u8<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    <u8 as super::super::UnstableSmallSortTypeImpl>::small_sort(
        &mut v,
        &mut arbitrary_less::<u8>,
    );
    kani::cover(true, "realcontracts unstable network consumer returns");
}

#[kani::proof]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n9_real() {
    exercise_unstable_network_u8::<9>();
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n9_stubbed() {
    exercise_unstable_network_u8::<9>();
}

#[kani::proof]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n13_real() {
    exercise_unstable_network_u8::<13>();
}

#[kani::proof]
#[kani::stub_verified(swap_if_less)]
#[kani::unwind(16)]
fn unstable_network_safety_u8_n13_stubbed() {
    exercise_unstable_network_u8::<13>();
}
