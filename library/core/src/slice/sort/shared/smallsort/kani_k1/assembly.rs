//! Stage B CI witnesses and K-15 paired mutation controls.
//! Positive/negative pairs execute the same check helper; only the named body is replaced.

use super::super::{
    StableSmallSortTypeImpl, bidirectional_merge, insert_tail, merge_up, small_sort_network,
    swap_if_less,
};
use crate::kani;
use crate::mem::MaybeUninit;
use crate::ptr;

fn strict_less(a: &u8, b: &u8) -> bool {
    // SAFETY: both arguments must be initialized and readable before comparison.
    unsafe { ptr::read_volatile(a) < ptr::read_volatile(b) }
}

fn cut_ord_violation() -> ! {
    // Variant A: cut only the explicit order-violation panic; cover normal returns below.
    kani::assume(false);
    unreachable!()
}

fn check_swap() {
    let mut v: [u8; 2] = kani::any();
    let before = v;
    // SAFETY: two distinct initialized elements in one array.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut strict_less) };
    assert!(v[0] <= v[1]);
    assert!((v == before) || (v == [before[1], before[0]]));
    kani::cover(true, "K15 swap: sorted permutation returned");
}

fn check_insert() {
    let mut v: [u8; 2] = kani::any();
    let before = v;
    // SAFETY: one-element sorted prefix, initialized tail, both in the same array.
    unsafe { insert_tail(v.as_mut_ptr(), v.as_mut_ptr().add(1), &mut strict_less) };
    assert!(v[0] <= v[1]);
    assert!((v == before) || (v == [before[1], before[0]]));
    kani::cover(true, "K15 insert: sorted permutation returned");
}

fn check_merge_up() {
    let src: [u8; 2] = kani::any();
    let left = src.as_ptr();
    // SAFETY: second element in src.
    let right = unsafe { left.add(1) };
    let mut dst = MaybeUninit::<u8>::uninit();
    let out = dst.as_mut_ptr();
    // SAFETY: two initialized input elements, separate one-element destination.
    let (next_left, next_right, next_dst) = unsafe { merge_up(left, right, out, &mut strict_less) };
    let take_left = src[0] <= src[1];
    // SAFETY: these expected pointers are at most one-past the source/destination arrays.
    let advancement_ok = unsafe {
        next_left == left.add(take_left as usize)
            && next_right == right.add((!take_left) as usize)
            && next_dst == out.add(1)
    };
    assert!(advancement_ok);
    // SAFETY: merge_up wrote exactly one element.
    let value = unsafe { dst.assume_init() };
    assert!(value == if take_left { src[0] } else { src[1] });
    kani::cover(take_left, "K15 merge_up: left consumed");
    kani::cover(!take_left, "K15 merge_up: right consumed");
}

fn count(v: &[u8; 4], probe: u8) -> usize {
    (v[0] == probe) as usize + (v[1] == probe) as usize
        + (v[2] == probe) as usize + (v[3] == probe) as usize
}

fn check_merge_consumption() {
    let src: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut dst = MaybeUninit::<[u8; 4]>::uninit();
    // SAFETY: separate initialized source and writable destination, len >= 2, u8 is Freeze.
    // No sortedness is assumed: this is the real-body safety/permutation claim for arbitrary
    // comparators, under the organizers' --no-assert-contracts, as in W2 variant A.
    unsafe {
        bidirectional_merge(&src, dst.as_mut_ptr().cast(), &mut |a, b| {
            let _left = ptr::read_volatile(a);
            let _right = ptr::read_volatile(b);
            kani::any()
        });
    }
    // SAFETY: both merge directions wrote two output elements on normal return.
    let result = unsafe { dst.assume_init() };
    assert!(count(&src, probe) == count(&result, probe));
    kani::cover(true, "K15 merge: normal return preserves arbitrary full-value probe count");
}

fn check_presorted_len() {
    // Deterministic regression: the network sorts its first 9 values, then insertion must
    // consume index 9. Reporting presorted_len=10 silently skips this zero.
    let mut v = [1u8, 1, 1, 1, 1, 1, 1, 1, 1, 0];
    small_sort_network(&mut v, &mut strict_less);
    assert!(v[0] == 0 && v[9] == 1);
    kani::cover(true, "K15 presorted_len: tenth element inserted");
}

macro_rules! paired_case {
    ($positive:ident, $negative:ident, $check:ident, $original:path, $mutant:path) => {
        #[kani::proof]
        #[kani::unwind(17)]
        #[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
        fn $positive() {
            $check();
        }

        #[cfg(kani_smallsort_controls)]
        #[kani::proof]
        #[kani::unwind(17)]
        #[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
        #[kani::stub($original, $mutant)]
        fn $negative() {
            $check();
        }
    };
}

paired_case!(k15_swap, k15_mutant_swap, check_swap,
    super::super::swap_if_less, super::mutations::mutant_swap_if_less);
paired_case!(k15_insert, k15_mutant_insert, check_insert,
    super::super::insert_tail, super::mutations::mutant_insert_tail);
paired_case!(k15_merge_up, k15_mutant_merge_up, check_merge_up,
    super::super::merge_up, super::mutations::mutant_merge_up);
paired_case!(k15_merge_consumption, k15_mutant_merge_consumption, check_merge_consumption,
    super::super::bidirectional_merge, super::mutations::mutant_bidirectional_merge);
paired_case!(k15_presorted_len, k15_mutant_presorted_len, check_presorted_len,
    super::super::small_sort_network, super::mutations::mutant_small_sort_network);

macro_rules! zst_ci_case {
    ($name:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(65)]
        #[kani::stub(super::super::panic_on_ord_violation, cut_ord_violation)]
        fn $name() {
            let mut v = [(); $n];
            let mut scratch = [MaybeUninit::<()>::uninit(); 48];
            <() as StableSmallSortTypeImpl>::small_sort(
                &mut v, &mut scratch, &mut super::uninit::zst_aware_less::<()>,
            );
            kani::cover(true, concat!("CI ZST stable normal return N=", stringify!($n)));
        }
    };
}

zst_ci_case!(ci_zst_stable_1, 1);
zst_ci_case!(ci_zst_stable_2, 2);
zst_ci_case!(ci_zst_stable_7, 7);
zst_ci_case!(ci_zst_stable_8, 8);
zst_ci_case!(ci_zst_stable_16, 16);
zst_ci_case!(ci_zst_stable_17, 17);
zst_ci_case!(ci_zst_stable_31, 31);
zst_ci_case!(ci_zst_stable_32, 32);
