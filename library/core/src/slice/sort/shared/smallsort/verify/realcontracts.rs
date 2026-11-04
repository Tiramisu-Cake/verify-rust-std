//! Opt-in safety contracts on the real helpers; no verified stubs in positive proofs.
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
