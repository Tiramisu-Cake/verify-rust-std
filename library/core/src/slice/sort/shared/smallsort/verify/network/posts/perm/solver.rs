//! Opt-in kissat variants of the two remaining u64 N8 permutation oracles: the independent
//! arbitrary `u64` probe of `posts::partposts_count_u64_n8` and the quadratic check of
//! `perm::perm_quadratic_u64_n8`, over the same full-width input, comparator and actual entry.
//! The positive bodies copy their originals; only the solver attribute differs.
//! `kani::assert` keeps each literal in the property description.

use crate::kani;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;

/// Control witnesses: the low 32 bits agree, only the high bits order and distinguish them.
const P: u64 = 1 << 40;
const Q: u64 = 1 << 41;

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn perm_arbitrary_kissat_u64_n8() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp = super::super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::super::super::count_matching_values(&pre, &probe)
            == super::super::super::count_matching_values(&v, &probe),
        "partposts: full-value count preserved",
    );
    kani::cover(
        !super::super::super::prefix_unchanged(&v, &pre, 0),
        "partposts count: sort moves elements",
    );
    kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8");
    kani::cover(true, "partposts count: check reached the end");
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn perm_quadratic_kissat_u64_n8() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let mut cmp = super::super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::quadratic_counts_preserved(&pre, &v),
        "permprobe: quadratic counts preserved",
    );
    kani::cover(
        !super::super::super::prefix_unchanged(&v, &pre, 0),
        "permprobe quadratic: sort moves elements",
    );
    kani::cover(true, "permprobe quadratic: check reached");
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn perm_arbitrary_kissat_negative_u64_n8() {
    let mut v: [u64; 8] = [P; 8];
    let pre = v;
    let probe: u64 = P;
    let mut cmp = super::super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::super::super::is_sorted_by(&v, &mut cmp),
        "permsolver arbitrary control: initial sortedness",
    );
    kani::assert(
        super::super::super::count_matching_values(&pre, &probe)
            == super::super::super::count_matching_values(&v, &probe),
        "permsolver arbitrary control: initial count",
    );
    kani::cover(true, "permsolver arbitrary control: returned before corruption");
    v[7] = Q;
    kani::assert(
        super::super::super::is_sorted_by(&v, &mut cmp),
        "permsolver arbitrary control: sortedness after overwrite",
    );
    kani::cover(true, "permsolver arbitrary control: check reached");
    kani::assert(
        super::super::super::count_matching_values(&pre, &probe)
            == super::super::super::count_matching_values(&v, &probe),
        "permsolver negative: arbitrary count",
    );
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn perm_quadratic_kissat_negative_u64_n8() {
    let mut v: [u64; 8] = [P; 8];
    let pre = v;
    let mut cmp = super::super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::quadratic_counts_preserved(&pre, &v),
        "permsolver quadratic control: initial counts",
    );
    kani::cover(true, "permsolver quadratic control: returned before corruption");
    v[7] = Q;
    kani::assert(
        super::super::super::is_sorted_by(&v, &mut cmp),
        "permsolver quadratic control: sortedness after overwrite",
    );
    kani::cover(true, "permsolver quadratic control: check reached");
    kani::assert(
        super::quadratic_counts_preserved(&pre, &v),
        "permsolver negative: quadratic count",
    );
}
