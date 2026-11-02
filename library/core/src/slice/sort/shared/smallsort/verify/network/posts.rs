//! Opt-in split of `network_correctness_u64_n8`: sortedness and the full-value probe count as
//! separate direct roots over the same input, comparator and actual entry; one control each.
//! `kani::assert` keeps each literal in the property description.

use crate::kani;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;

/// Control witnesses: the low 32 bits agree, only the high bits order and distinguish them.
const P: u64 = 1 << 40;
const Q: u64 = 1 << 41;

#[kani::proof]
#[kani::unwind(25)]
fn partposts_sorted_u64_n8() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let _probe: u64 = kani::any();
    let mut cmp = super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(super::is_sorted_by(&v, &mut cmp), "partposts: sortedness");
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "partposts sorted: sort moves elements");
    kani::cover(v.len() == 8, "partposts sorted: sort returns normally at length 8");
    kani::cover(true, "partposts sorted: check reached the end");
}

#[kani::proof]
#[kani::unwind(25)]
fn partposts_count_u64_n8() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp = super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts: full-value count preserved",
    );
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "partposts count: sort moves elements");
    kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8");
    kani::cover(true, "partposts count: check reached the end");
}

#[kani::proof]
#[kani::unwind(25)]
fn partposts_order_negative_u64_n8() {
    let mut v: [u64; 8] = [P, P, P, P, P, P, P, Q];
    let pre = v;
    let probe: u64 = P;
    let mut cmp = super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(super::is_sorted_by(&v, &mut cmp), "partposts order control: initial sortedness");
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts order control: initial count",
    );
    kani::cover(true, "partposts order control: returned before corruption");
    let first = v[0];
    v[0] = v[7];
    v[7] = first;
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts order control: count after swap",
    );
    kani::cover(true, "partposts order control: order check reached");
    kani::assert(super::is_sorted_by(&v, &mut cmp), "partposts negative: sortedness");
}

#[kani::proof]
#[kani::unwind(25)]
fn partposts_count_negative_u64_n8() {
    let mut v: [u64; 8] = [P; 8];
    let pre = v;
    let probe: u64 = P;
    let mut cmp = super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(super::is_sorted_by(&v, &mut cmp), "partposts count control: initial sortedness");
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts count control: initial count",
    );
    kani::cover(true, "partposts count control: returned before corruption");
    v[7] = Q;
    kani::assert(
        super::is_sorted_by(&v, &mut cmp),
        "partposts count control: sortedness after overwrite",
    );
    kani::cover(true, "partposts count control: count check reached");
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts negative: full-value count preserved",
    );
}
