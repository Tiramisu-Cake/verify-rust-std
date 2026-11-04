//! Opt-in real-helper contract PFCs and paired real-entry consumers with/without swap stubs.
//! Each PFC uses one T/F instantiation. Stateless comparators read both arguments and return
//! an arbitrary decision on every call, including when both swap positions are equal.
//! Bounded domains do not establish a frame for stateful or externally mutating callbacks.
//! ENSURES adds a separate canonical u64 comparator model and ordered insertion composition.

use super::super::{
    bidirectional_merge, insert_tail, insertion_sort_shift_left, sort4_stable, swap_if_less,
};
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
// REALCONTRACTSTWO adds matching backing9/backing13 PFCs below; composition credit requires
// both the matching PFC and consumer to pass, and remains limited to these T/F/backing domains.
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

// REALCONTRACTSTWO G1: cover the actual network consumers' allocation sizes with the same
// u8/function-item comparator and arbitrary (including equal) positions throughout backing N.
fn exercise_swap_u8_backing<const N: usize>() {
    let mut v: [u8; N] = kani::any();
    let before = v;
    let a: usize = kani::any();
    let b: usize = kani::any();
    kani::assume(a < N && b < N);
    // SAFETY: both positions are initialized writable elements of this allocation.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut arbitrary_less::<u8>) };
    for i in 0..N {
        kani::assert(i == a || i == b || v[i] == before[i], "realcontractstwo swap frame");
    }
    kani::cover(a == b, "realcontractstwo equal swap positions return");
    kani::cover(a < b, "realcontractstwo increasing swap positions return");
    kani::cover(a > b, "realcontractstwo decreasing swap positions return");
    kani::cover(true, "realcontractstwo swap returns");
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
    // SAFETY: begin < tail, and the inclusive region is initialized, readable/writable,
    // aligned and within this one allocation. No sorted-prefix premise is needed for safety.
    unsafe { insert_tail(begin, begin.add(tail), &mut arbitrary_less::<u64>) };
    for i in 0..5 {
        kani::assert(i <= tail || v[i] == before[i], "realcontractstwo insert_tail frame");
    }
    kani::cover(tail == 1, "realcontractstwo insert_tail offset1 returns");
    kani::cover(tail == 2, "realcontractstwo insert_tail offset2 returns");
    kani::cover(tail == 3, "realcontractstwo insert_tail offset3 returns");
    kani::cover(tail == 4, "realcontractstwo insert_tail offset4 returns");
    kani::cover(true, "realcontractstwo insert_tail returns");
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn rejects_insert_tail_equal_begin_u64() {
    let mut v: [u64; 5] = kani::any();
    let begin = v.as_mut_ptr();
    kani::cover(true, "realcontractstwo invalid insert_tail consumer reached");
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
        kani::assert(src[i] == before[i], "realcontractstwo sort4 source frame");
    }
    // SAFETY: the real body writes all four output slots on every normal-return path.
    // This read exercises the output; the lane does not enable uninit/value-validity checks.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: each returned output element is initialized and readable.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontractstwo sort4 returns");
}

// G2 compares every source byte with scalar equality, avoiding array PartialEq's memcmp.
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
            kani::assert(src[i][byte] == before[i][byte], "realcontractstwo sort4 byte source frame");
        }
    }
    // SAFETY: the real body writes all four output values before returning normally.
    // Uninit/value-validity checks remain disabled in this diagnostic lane.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: each output is initialized on normal return.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontractstwo sort4 bytes16 returns");
}

fn cut_merge_order_violation() -> ! {
    // Match the ordinary safety family: reach the explicit order-violation boundary,
    // then cut the abort path. This does not check panic unwinding.
    kani::cover(true, "realcontractstwo merge order violation reachable");
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
        kani::assert(src[i] == before[i], "realcontractstwo merge source frame");
    }
    // SAFETY: every output slot is written on normal return; inconsistent comparator
    // paths reach the explicit panic boundary and are cut by the safety stub.
    let result = unsafe { dst.assume_init() };
    for value in &result {
        // SAFETY: initialized output on normal return.
        let _value = unsafe { crate::ptr::read_volatile(value) };
    }
    kani::cover(true, "realcontractstwo merge returns");
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

#[kani::proof]
#[kani::stub_verified(bidirectional_merge)]
#[kani::unwind(16)]
fn rejects_merge_overlapping_dst_u64() {
    let mut backing: [u64; 4] = kani::any();
    let base = backing.as_mut_ptr();
    // SAFETY: source is the first two initialized values of this allocation.
    let src = unsafe { crate::slice::from_raw_parts(base as *const u64, 2) };
    kani::cover(true, "realcontractstwo overlapping merge consumer reached");
    // Deliberate contract violation: dst[0..2] covers backing[1..3], so it is writable
    // and in bounds but overlaps source[0..2] at backing[1]. Only disjointness fails.
    unsafe { bidirectional_merge(src, base.add(1), &mut arbitrary_less::<u64>) };
}

// ENSURES G1: one concrete comparator type shared by the PFC and real-entry consumers.
// Only this model has ordering/count summaries; arbitrary_less keeps the safety-only default.
use super::super::{InsertTailComparatorModel, InsertTailU64Less};

fn ensures_sorted(v: &[u64]) -> bool {
    for i in 1..v.len() {
        if v[i] < v[i - 1] {
            return false;
        }
    }
    true
}

fn ensures_count(v: &[u64], probe: u64) -> usize {
    let mut count = 0;
    for value in v {
        if *value == probe {
            count += 1;
        }
    }
    count
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail1_to4_backing5() {
    let mut v: [u64; 5] = kani::any();
    let before = v;
    let tail: usize = kani::any();
    kani::assume(1 <= tail && tail <= 4);
    let probe: u64 = kani::any();
    let mut cmp = InsertTailU64Less { probe };
    let prefix_sorted = ensures_sorted(&before[..tail]);
    kani::assert(
        <InsertTailU64Less as InsertTailComparatorModel<u64>>::has_model(&cmp),
        "ensures canonical comparator model selected",
    );
    let begin = v.as_mut_ptr();
    // SAFETY: tail is 1..4 in an initialized writable u64 backing5 allocation.
    // No sortedness assumption: the order ensures is checked as an implication.
    unsafe { insert_tail(begin, begin.add(tail), &mut cmp) };
    kani::assert(
        !prefix_sorted || ensures_sorted(&v[..=tail]),
        "ensures insert_tail sorted prefix extended",
    );
    kani::assert(
        ensures_count(&before[..=tail], probe) == ensures_count(&v[..=tail], probe),
        "ensures insert_tail full-value probe count",
    );
    for i in 0..5 {
        kani::assert(i <= tail || v[i] == before[i], "ensures insert_tail suffix frame");
    }
    kani::cover(tail == 1, "ensures insert_tail tail1 returns");
    kani::cover(tail == 2, "ensures insert_tail tail2 returns");
    kani::cover(tail == 3, "ensures insert_tail tail3 returns");
    kani::cover(tail == 4, "ensures insert_tail tail4 returns");
    kani::cover(prefix_sorted, "ensures insert_tail sorted premise reachable");
    kani::cover(!prefix_sorted, "ensures insert_tail unsorted premise reachable");
    kani::cover(before[tail] < before[tail - 1], "ensures insert_tail moves reachable");
    kani::cover(before[tail] >= before[tail - 1], "ensures insert_tail early return reachable");
    kani::cover(ensures_count(&before[..=tail], probe) > 0, "ensures probe present reachable");
    kani::cover(true, "ensures insert_tail returns");
}

fn exercise_ensures_insertion_n5(corrupt: bool) {
    let mut v: [u64; 5] = kani::any();
    let before = v;
    let probe: u64 = kani::any();
    let mut cmp = InsertTailU64Less { probe };
    // The real insertion loop calls insert_tail four times on this same backing5,
    // at tails 1, 2, 3 and 4; (T, F, backing, tail) all match the PFC above.
    insertion_sort_shift_left(&mut v, 1, &mut cmp);
    kani::cover(true, "ensures insertion n5 stubbed entry returns");
    if corrupt {
        // Deliberate post-stub consumer mutation. This preserves the original call domain
        // and forces an inversion independently of the arbitrary input and probe.
        v[0] = u64::MAX;
        v[1] = 0;
    }
    kani::assert(ensures_sorted(&v), "ensures consumer n5 sortedness");
    kani::assert(
        ensures_count(&before, probe) == ensures_count(&v, probe),
        "ensures consumer n5 full-value permutation probe",
    );
    kani::cover(ensures_count(&before, probe) > 0, "ensures consumer probe present reachable");
    kani::cover(v[0] < v[4], "ensures consumer nonconstant result reachable");
    kani::cover(true, "ensures consumer assertions reached");
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn insertion_ensures_u64_n5_stubbed() {
    exercise_ensures_insertion_n5(false);
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn rejects_insertion_ensures_u64_n5_corruption() {
    exercise_ensures_insertion_n5(true);
}

// ENSURES G2: fixed-tail PFC roots split the full consumer domain on one backing8.
// Each root runs the real helper with the same canonical F and arbitrary full-value probe.
fn exercise_insert_tail_ensures_backing8<const TAIL: usize>() {
    let mut v: [u64; 8] = kani::any();
    let before = v;
    let probe: u64 = kani::any();
    let mut cmp = InsertTailU64Less { probe };
    let prefix_sorted = ensures_sorted(&before[..TAIL]);
    kani::assert(
        <InsertTailU64Less as InsertTailComparatorModel<u64>>::has_model(&cmp),
        "ensures backing8 canonical comparator model selected",
    );
    let begin = v.as_mut_ptr();
    // SAFETY: the seven PFC roots instantiate TAIL as 1..7 in initialized u64 backing8.
    // No sorted-prefix assumption: the order ensures remains a checked implication.
    unsafe { insert_tail(begin, begin.add(TAIL), &mut cmp) };
    kani::assert(
        !prefix_sorted || ensures_sorted(&v[..=TAIL]),
        "ensures backing8 insert_tail sorted prefix extended",
    );
    kani::assert(
        ensures_count(&before[..=TAIL], probe) == ensures_count(&v[..=TAIL], probe),
        "ensures backing8 insert_tail full-value probe count",
    );
    for i in 0..8 {
        kani::assert(i <= TAIL || v[i] == before[i], "ensures backing8 insert_tail suffix frame");
    }
    kani::cover(prefix_sorted, "ensures backing8 sorted premise reachable");
    // A singleton prefix at TAIL=1 is always sorted; request the opposite only at TAIL>=2.
    if TAIL > 1 {
        kani::cover(!prefix_sorted, "ensures backing8 unsorted premise reachable");
    }
    kani::cover(before[TAIL] < before[TAIL - 1], "ensures backing8 moves reachable");
    kani::cover(before[TAIL] >= before[TAIL - 1], "ensures backing8 early return reachable");
    kani::cover(ensures_count(&before[..=TAIL], probe) > 0, "ensures backing8 probe present reachable");
    kani::cover(true, "ensures backing8 insert_tail returns");
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail1_backing8() {
    exercise_insert_tail_ensures_backing8::<1>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail2_backing8() {
    exercise_insert_tail_ensures_backing8::<2>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail3_backing8() {
    exercise_insert_tail_ensures_backing8::<3>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail4_backing8() {
    exercise_insert_tail_ensures_backing8::<4>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail5_backing8() {
    exercise_insert_tail_ensures_backing8::<5>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail6_backing8() {
    exercise_insert_tail_ensures_backing8::<6>();
}

#[kani::proof_for_contract(insert_tail)]
#[kani::unwind(16)]
fn insert_tail_ensures_u64_tail7_backing8() {
    exercise_insert_tail_ensures_backing8::<7>();
}

#[kani::proof]
#[kani::stub_verified(insert_tail)]
#[kani::unwind(16)]
fn insertion_ensures_u64_n8_stubbed() {
    let mut v: [u64; 8] = kani::any();
    let before = v;
    let probe: u64 = kani::any();
    let mut cmp = InsertTailU64Less { probe };
    // Real insertion loop, seven verified-stub calls, same backing8 and canonical F.
    // The union of the fixed-tail PFC domains above covers every actual tail 1..7.
    insertion_sort_shift_left(&mut v, 1, &mut cmp);
    kani::cover(true, "ensures insertion n8 stubbed entry returns");
    kani::assert(ensures_sorted(&v), "ensures consumer n8 sortedness");
    kani::assert(
        ensures_count(&before, probe) == ensures_count(&v, probe),
        "ensures consumer n8 full-value permutation probe",
    );
    kani::cover(ensures_count(&before, probe) > 0, "ensures consumer n8 probe present reachable");
    kani::cover(v[0] < v[7], "ensures consumer n8 nonconstant result reachable");
    kani::cover(true, "ensures consumer n8 assertions reached");
}
