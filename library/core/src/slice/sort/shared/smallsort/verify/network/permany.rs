//! Opt-in permutation check of the u64 N8 actual unstable entry under an arbitrary read-only
//! comparator: every call returns a fresh `kani::any()` and reads neither argument. For u64 at
//! N8 `small_sort_network` takes `no_merge` (len < 18) with a region below 9, so only
//! `insertion_sort_shift_left(region, 1, ..)` runs; `bidirectional_merge` and its
//! `panic_on_ord_violation` guard are off the path, so the count must hold for any answers.
//! The shared body is the arbitrary-probe count of `posts::partposts_count_u64_n8` (PERMSOLVER)
//! with `strict_less` replaced by `any_less`, plus probe-hit/miss covers.
//! `kani::assert` keeps the literal in the property description.

use crate::kani;
use crate::slice::sort::shared::smallsort::UnstableSmallSortTypeImpl;

/// Arbitrary answer independent of both arguments; reads no memory.
fn any_less(_a: &u64, _b: &u64) -> bool {
    let r: bool = kani::any();
    kani::cover(r, "permany: comparator returned true");
    kani::cover(!r, "permany: comparator returned false");
    r
}

/// Full input, independent arbitrary probe, actual entry with `any_less`, full-value count of the
/// probe preserved. `CORRUPT` (control only) sets `v[0] = v[1]` after the entry.
fn permany_count_u64_n8<const CORRUPT: bool>() {
    let mut v: [u64; 8] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let mut cmp = any_less;
    <u64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut cmp);
    if CORRUPT {
        v[0] = v[1];
    }
    kani::assert(
        super::count_matching_values(&pre, &probe) == super::count_matching_values(&v, &probe),
        "permany: full-value count preserved",
    );
    kani::cover(super::count_matching_values(&pre, &probe) > 0, "permany: probe hits the input");
    kani::cover(super::count_matching_values(&pre, &probe) == 0, "permany: probe misses the input");
    kani::cover(!super::prefix_unchanged(&v, &pre, 0), "permany count: sort moves elements");
    kani::cover(v.len() == 8, "permany count: sort returns normally at length 8");
    kani::cover(true, "permany count: check reached the end");
}

#[kani::proof]
#[kani::unwind(25)]
fn permany_u64_n8_default() {
    permany_count_u64_n8::<false>();
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn permany_u64_n8_kissat() {
    permany_count_u64_n8::<false>();
}

#[kani::proof]
#[kani::unwind(25)]
#[kani::solver(kissat)]
fn permany_u64_n8_value_loss_control() {
    permany_count_u64_n8::<true>();
}
