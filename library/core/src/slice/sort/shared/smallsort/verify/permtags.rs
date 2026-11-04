//! Bounded permutation checks with distinct identity tags and arbitrary comparison answers.
//!
//! Inputs contain each tag in `0..N` once, initially in ascending identity order. Every
//! comparison reads both arguments and independently chooses a fresh symbolic bool; no order
//! laws are assumed. The real trait entries run without verified-contract stubs. Only the
//! explicit order-violation panic is cut, as in the Part 1 safety family, so the assertion is
//! about normal return and says nothing about unwinding or comparator panics.
//!
//! Transfer assumption: on the same type-selected route, SmallSort only moves whole elements
//! and branches on comparison answers, positions, lengths and type properties, not payloads.
//! Fresh answers therefore include every answer sequence of any returning comparator. Distinct
//! tags track each original element even when its original payload equals another's; a fixed
//! identity order imposes no payload-order restriction. Under this source-level assumption,
//! preserving all tags implies permutation for arbitrary payloads on that route. This is not a
//! machine-checked generic refinement theorem. Comparators that mutate payloads are excluded.
//! The tag types are exactly the source types (u8, u64, Cell<u8>), without wrappers; a separate
//! root checks the dispatch predicates and thresholds. Other types require their own route and
//! whole-element-movement justification. These checks establish neither sortedness nor stability.
//!
//! With exactly N output positions, range checks and the N-bit all-ones mask imply each tag
//! occurs exactly once. A u64 mask leaves room for N=32 without a full-width shift or u128.

use super::super::{
    MAX_STACK_ARRAY_SIZE, SMALL_SORT_FALLBACK_THRESHOLD, SMALL_SORT_GENERAL_SCRATCH_LEN,
    SMALL_SORT_GENERAL_THRESHOLD, SMALL_SORT_NETWORK_SCRATCH_LEN, SMALL_SORT_NETWORK_THRESHOLD,
    StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl,
    has_efficient_in_place_swap,
};
use crate::cell::Cell;
#[cfg(kani_smallsort_controls)]
use crate::mem::MaybeUninit;
use crate::mem::size_of;
use crate::{kani, ptr};

fn arbitrary_u8_order(a: &u8, b: &u8) -> bool {
    // SAFETY: the real sort must supply initialized, readable comparator arguments.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
    kani::any()
}

#[cfg(kani_smallsort_controls)]
fn arbitrary_u64_order(a: &u64, b: &u64) -> bool {
    // SAFETY: the real sort must supply initialized, readable comparator arguments.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
    kani::any()
}

#[cfg(kani_smallsort_controls)]
fn arbitrary_cell_order(a: &Cell<u8>, b: &Cell<u8>) -> bool {
    // SAFETY: read both initialized payloads without modifying either Cell.
    unsafe {
        let _ = ptr::read_volatile(a.as_ptr());
        let _ = ptr::read_volatile(b.as_ptr());
    }
    kani::any()
}

fn abort_on_order_violation() -> ! {
    kani::cover(true, "permtags: order violation panic is reachable");
    kani::assume(false);
    unreachable!()
}

fn check_tags<const N: usize>(tags: &[u64; N]) {
    assert!(N > 0 && N <= 32);
    let mut seen = 0u64;
    for &tag in tags {
        kani::assert(tag < N as u64, "permtags: output tag is in range");
        // Keep the shift defined even on a counterexample with an out-of-range tag.
        if tag < N as u64 {
            seen |= 1u64 << tag;
        }
    }
    kani::assert(seen == (1u64 << N) - 1, "permtags: every input tag occurs exactly once");
}

fn network_output<const N: usize>() -> [u8; N] {
    let mut v = crate::array::from_fn(|i| i as u8);
    <u8 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut arbitrary_u8_order);
    v
}

fn network_body<const N: usize>() {
    let v = network_output::<N>();
    check_tags(&crate::array::from_fn::<_, N, _>(|i| v[i] as u64));
    kani::cover(true, "permtags: network returns with every tag");
}

#[cfg(kani_smallsort_controls)]
fn general_body<const N: usize>() {
    let mut v: [u64; N] = crate::array::from_fn(|i| i as u64);
    let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut arbitrary_u64_order);
    check_tags(&v);
    kani::cover(true, "permtags: general with scratch 48 returns with every tag");
}

#[cfg(kani_smallsort_controls)]
fn fallback_body<const N: usize>() {
    let mut v: [Cell<u8>; N] = crate::array::from_fn(|i| Cell::new(i as u8));
    let mut scratch = [const { MaybeUninit::<Cell<u8>>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(
        &mut v,
        &mut scratch,
        &mut arbitrary_cell_order,
    );
    check_tags(&crate::array::from_fn::<_, N, _>(|i| v[i].get() as u64));
    kani::cover(true, "permtags: stable Cell insertion returns with every tag");
}

#[kani::proof]
fn tag_types_preserve_source_routes() {
    fn require_freeze_copy<T: crate::slice::sort::shared::FreezeMarker + Copy>() {}
    require_freeze_copy::<u8>();
    require_freeze_copy::<u64>();

    // Unstable u8 takes the Freeze+Copy network specialization and its size branch.
    assert!(size_of::<u8>() == 1);
    assert!(has_efficient_in_place_swap::<u8>());
    assert!(size_of::<u8>() * SMALL_SORT_NETWORK_SCRATCH_LEN <= MAX_STACK_ARRAY_SIZE);
    assert!(<u8 as UnstableSmallSortTypeImpl>::small_sort_threshold() == 32);
    assert!(
        <u8 as UnstableSmallSortFreezeTypeImpl>::small_sort_threshold()
            == SMALL_SORT_NETWORK_THRESHOLD
    );

    // Stable Freeze u64 always selects general, independently of the swap heuristic.
    assert!(size_of::<u64>() == 8);
    assert!(SMALL_SORT_GENERAL_SCRATCH_LEN == 48);
    assert!(
        <u64 as StableSmallSortTypeImpl>::small_sort_threshold() == SMALL_SORT_GENERAL_THRESHOLD
    );
    assert!(SMALL_SORT_GENERAL_THRESHOLD == 32);

    // The Freeze specialization would return 32: 16 identifies the blanket Stable entry.
    assert!(
        <Cell<u8> as StableSmallSortTypeImpl>::small_sort_threshold()
            == SMALL_SORT_FALLBACK_THRESHOLD
    );
    assert!(SMALL_SORT_FALLBACK_THRESHOLD == 16);
    kani::cover(true, "permtags: tag and source types select the required routes");
}

macro_rules! permutation_case {
    ($name:ident, $body:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub(
            crate::slice::sort::shared::smallsort::panic_on_ord_violation,
            abort_on_order_violation
        )]
        #[kani::unwind(34)]
        fn $name() {
            $body::<$n>();
        }
    };
}

permutation_case!(network_u8_n9, network_body, 9);
permutation_case!(network_u8_n13, network_body, 13);
#[cfg(kani_smallsort_controls)]
permutation_case!(network_u8_n16, network_body, 16);
#[cfg(kani_smallsort_controls)]
permutation_case!(network_u8_n17, network_body, 17);
#[cfg(kani_smallsort_controls)]
permutation_case!(network_u8_n32, network_body, 32);
#[cfg(kani_smallsort_controls)]
permutation_case!(general_u64_n9, general_body, 9);
#[cfg(kani_smallsort_controls)]
permutation_case!(general_u64_n16, general_body, 16);
// Larger domains remain opt-in research roots.
#[cfg(kani_smallsort_controls)]
permutation_case!(general_u64_n17, general_body, 17);
#[cfg(kani_smallsort_controls)]
permutation_case!(general_u64_n32, general_body, 32);
#[cfg(kani_smallsort_controls)]
permutation_case!(fallback_cell_u8_n16, fallback_body, 16);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(34)]
fn reject_duplicate_network_u8_n9() {
    let mut v = network_output::<9>();
    kani::cover(true, "permtags: duplicate mutant reaches the corruption");
    // SAFETY: both pointers name distinct initialized elements of the same live array.
    // Deliberately lose one identity after the same real sorting call used by the positive root.
    unsafe { ptr::copy(v.as_ptr(), v.as_mut_ptr().add(1), 1) };
    check_tags(&crate::array::from_fn::<_, 9, _>(|i| v[i] as u64));
}
