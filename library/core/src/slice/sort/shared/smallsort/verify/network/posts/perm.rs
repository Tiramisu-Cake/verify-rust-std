//! Opt-in permutation oracles for the u64 N8 actual entry of `posts::partposts_count_u64_n8`:
//! the probe is chosen among the input positions (index probe) or every input position is
//! checked (quadratic), instead of an independent arbitrary `u64` probe. Inputs stay full width.
//! Since the multiplicities of all distinct input values sum to 8 = len(output), equal counts
//! for every value taken from the input mean the output is a multiset permutation of the input.
//! `kani::assert` keeps each literal in the property description.

use crate::kani;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;

/// Control witnesses: the low 32 bits agree, only the high bits order and distinguish them.
const P: u64 = 1 << 40;
const Q: u64 = 1 << 41;

/// `count(pre, pre[i]) == count(v, pre[i])` for every input position `i`.
fn quadratic_counts_preserved(pre: &[u64], v: &[u64]) -> bool {
    let mut i = 0;
    while i < pre.len() {
        if super::super::count_matching_values(pre, &pre[i])
            != super::super::count_matching_values(v, &pre[i])
        {
            return false;
        }
        i += 1;
    }
    true
}

/// Shared body of the index-probe roots: full input, probe read from the saved copy at an
/// arbitrary position before the entry, actual entry, count of that value preserved.
fn index_probe_entry_u64_n8() -> ([u64; 8], [u64; 8]) {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let j: usize = kani::any_where(|j: &usize| *j < 8);
    let probe = pre[j];
    let mut cmp = super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::super::count_matching_values(&pre, &probe)
            == super::super::count_matching_values(&v, &probe),
        "permprobe: index count preserved",
    );
    (v, pre)
}

#[kani::proof]
#[kani::unwind(25)]
fn perm_index_u64_n8() {
    let (v, pre) = index_probe_entry_u64_n8();
    kani::cover(
        !super::super::prefix_unchanged(&v, &pre, 0),
        "permprobe index: sort moves elements",
    );
    kani::cover(true, "permprobe index: check reached");
}

#[kani::proof]
#[kani::unwind(25)]
fn perm_quadratic_u64_n8() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let mut cmp = super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(quadratic_counts_preserved(&pre, &v), "permprobe: quadratic counts preserved");
    kani::cover(
        !super::super::prefix_unchanged(&v, &pre, 0),
        "permprobe quadratic: sort moves elements",
    );
    kani::cover(true, "permprobe quadratic: check reached");
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn perm_index_kissat_u64_n8() {
    let (v, pre) = index_probe_entry_u64_n8();
    kani::cover(
        !super::super::prefix_unchanged(&v, &pre, 0),
        "permprobe index: sort moves elements",
    );
    kani::cover(true, "permprobe index: check reached");
}

#[kani::proof]
#[kani::unwind(25)]
fn perm_index_negative_u64_n8() {
    let mut v: [u64; 8] = [P; 8];
    let pre = v;
    let j: usize = kani::any_where(|j: &usize| *j < 8);
    let probe = pre[j];
    let mut cmp = super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::super::count_matching_values(&pre, &probe)
            == super::super::count_matching_values(&v, &probe),
        "permprobe index control: initial count",
    );
    kani::cover(true, "permprobe index control: returned before corruption");
    v[7] = Q;
    kani::assert(
        super::super::is_sorted_by(&v, &mut cmp),
        "permprobe index control: sortedness after overwrite",
    );
    kani::cover(true, "permprobe index control: check reached");
    kani::assert(
        super::super::count_matching_values(&pre, &probe)
            == super::super::count_matching_values(&v, &probe),
        "permprobe negative: index count",
    );
}

#[kani::proof]
#[kani::unwind(25)]
fn perm_quadratic_negative_u64_n8() {
    let mut v: [u64; 8] = [P; 8];
    let pre = v;
    let mut cmp = super::super::strict_less::<u64>;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        quadratic_counts_preserved(&pre, &v),
        "permprobe quadratic control: initial counts",
    );
    kani::cover(true, "permprobe quadratic control: returned before corruption");
    v[7] = Q;
    kani::assert(
        super::super::is_sorted_by(&v, &mut cmp),
        "permprobe quadratic control: sortedness after overwrite",
    );
    kani::cover(true, "permprobe quadratic control: check reached");
    kani::assert(quadratic_counts_preserved(&pre, &v), "permprobe negative: quadratic count");
}

#[cfg(kani_smallsort_controls)]
mod solver;
