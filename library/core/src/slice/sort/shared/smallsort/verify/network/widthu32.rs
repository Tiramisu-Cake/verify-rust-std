//! Width point for the u64 N8 permutation oracle: the arbitrary-probe body of
//! `posts::perm::solver::perm_arbitrary_kissat_u64_n8` (PERMSOLVER) with `u32` as the element and
//! probe type, over the actual unstable entry and the strict-less function item.
//! Only the type changes in the copied body; the module path is one level shallower. Two covers
//! record that the probe both occurs and does not occur in the input. The control overwrites
//! `v[0]` with `v[1]` after the sort, losing a value.
//! `kani::assert` keeps each literal in the property description.

use crate::kani;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;

#[kani::proof]
#[kani::unwind(25)]
fn widthu32_perm_n8_default() {
    let mut v: [u32; 8] = kani::any();
    let pre = v;
    let probe: u32 = kani::any();
    let mut cmp = super::strict_less::<u32>;
    <u32 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts: full-value count preserved",
    );
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "partposts count: sort moves elements");
    kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8");
    kani::cover(true, "partposts count: check reached the end");
    kani::cover(super::count_matching_values(&pre, &probe) > 0, "widthu32: probe occurs in input");
    kani::cover(
        super::count_matching_values(&pre, &probe) == 0,
        "widthu32: probe absent from input",
    );
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn widthu32_perm_n8_kissat() {
    let mut v: [u32; 8] = kani::any();
    let pre = v;
    let probe: u32 = kani::any();
    let mut cmp = super::strict_less::<u32>;
    <u32 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "partposts: full-value count preserved",
    );
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "partposts count: sort moves elements");
    kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8");
    kani::cover(true, "partposts count: check reached the end");
    kani::cover(super::count_matching_values(&pre, &probe) > 0, "widthu32: probe occurs in input");
    kani::cover(
        super::count_matching_values(&pre, &probe) == 0,
        "widthu32: probe absent from input",
    );
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn widthu32_perm_n8_value_loss_control() {
    let mut v: [u32; 8] = kani::any();
    let pre = v;
    let probe: u32 = kani::any();
    let mut cmp = super::strict_less::<u32>;
    <u32 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    v[0] = v[1];
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "widthu32 negative: full-value count after value loss",
    );
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "partposts count: sort moves elements");
    kani::cover(v.len() == 8, "partposts count: sort returns normally at length 8");
    kani::cover(true, "partposts count: check reached the end");
    kani::cover(super::count_matching_values(&pre, &probe) > 0, "widthu32: probe occurs in input");
    kani::cover(
        super::count_matching_values(&pre, &probe) == 0,
        "widthu32: probe absent from input",
    );
}
