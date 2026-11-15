//! Ordered profiles for the real swap, sort4, tail-insertion, and merge helpers.
//! Each tag fixes an element type, a static comparator, and a pure full-value model.
//! Specifications use that model without calling the comparator. Wrappers accept no callback;
//! each real helper receives the direct closure `|a, b| P::cmp(a, b)`. The helpers' frame
//! contracts alone do not promise an order. Equal keys may have different full values.
//!
//! `kani::assert` preserves literal descriptions here; core `assert!` reports a shared
//! placeholder on the pinned Kani.

use super::{lt_u8, lt_u64, regions_are_disjoint};
use crate::mem::MaybeUninit;
use crate::mem::size_of;
use crate::slice::sort::shared::FreezeMarker;
use crate::slice::sort::shared::smallsort::{
    bidirectional_merge, insert_tail, sort4_stable, swap_if_less,
};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

/// Closed verification profile. Each implementation is audited: `cmp(a, b)` computes
/// `model_less(&model(a), &model(b))`, at most with additional volatile reads of both arguments;
/// `model` is the full logical value and has no side effects; the probe is one model value shared
/// by a composition. This is not a blanket lawful-order or purity claim about any other `FnMut`.
pub(crate) trait Profile {
    type Elem;
    type Model: Copy + PartialEq;
    fn cmp(a: &Self::Elem, b: &Self::Elem) -> bool;
    fn model(x: &Self::Elem) -> Self::Model;
    fn model_less(a: &Self::Model, b: &Self::Model) -> bool;
    fn probe() -> Self::Model;
    fn set_probe(m: Self::Model);
}

/// Tag whose model is the whole value; `$less` is the pure order and `$cmp` is `$less`, possibly
/// with volatile reads. Callers import `Profile`.
macro_rules! identity_profile {
    ($(#[$doc:meta])* $tag:ident, $t:ty, $probe:ident, $zero:expr, $cmp:expr, $less:expr) => {
        $(#[$doc])*
        pub(crate) struct $tag;

        static mut $probe: $t = $zero;

        impl Profile for $tag {
            type Elem = $t;
            type Model = $t;
            fn cmp(a: &$t, b: &$t) -> bool {
                $cmp(a, b)
            }
            fn model(x: &$t) -> $t {
                *x
            }
            fn model_less(a: &$t, b: &$t) -> bool {
                $less(a, b)
            }
            fn probe() -> $t {
                // SAFETY: single-threaded harness; no reference to the static is alive.
                unsafe { *$crate::ptr::addr_of!($probe) }
            }
            fn set_probe(m: $t) {
                // SAFETY: single-threaded harness; no reference to the static is alive.
                unsafe { *$crate::ptr::addr_of_mut!($probe) = m }
            }
        }
    };
}
pub(crate) use identity_profile;

/// The sort4 fixture order: both arguments are read volatile, then `lt_u64`.
pub(crate) fn sort4_read_lt_u64(a: &u64, b: &u64) -> bool {
    super::read_sort4_arguments(a, b);
    lt_u64(a, b)
}

/// The sort4 fixture order on 16-byte arrays: volatile reads, then `lt_b16` (first byte).
pub(crate) fn sort4_read_lt_b16(a: &[u8; 16], b: &[u8; 16]) -> bool {
    super::read_sort4_arguments(a, b);
    super::lt_b16(a, b)
}

identity_profile!(
    /// `u8` with `lt_u8`, key `x >> 1`.
    LtU8,
    u8,
    PROFILE_PROBE_LT_U8,
    0,
    lt_u8,
    lt_u8
);
identity_profile!(
    /// `i32` with `lt_i32`, key `x >> 1`.
    LtI32,
    i32,
    PROFILE_PROBE_LT_I32,
    0,
    super::lt_i32,
    super::lt_i32
);
identity_profile!(
    /// `u64` with `lt_u64`, key `x >> 1`.
    LtU64,
    u64,
    PROFILE_PROBE_LT_U64,
    0,
    lt_u64,
    lt_u64
);
identity_profile!(
    /// `u64` with the reading sort4 fixture over `lt_u64`.
    Sort4ReadU64,
    u64,
    PROFILE_PROBE_SORT4_U64,
    0,
    sort4_read_lt_u64,
    lt_u64
);
identity_profile!(
    /// `[u8; 16]` with the reading sort4 fixture over `lt_b16`.
    Sort4ReadB16,
    [u8; 16],
    PROFILE_PROBE_SORT4_B16,
    [0; 16],
    sort4_read_lt_b16,
    super::lt_b16
);

/// No adjacent strict model inversion in `base[..len]`; loop-free for `len <= 32`.
pub(crate) fn model_sorted<P: Profile>(base: *const P::Elem, len: usize) -> bool {
    let mut ok = true;
    macro_rules! step {
        ($($i:literal)*) => {$(
            // SAFETY: `$i < len`; callers pass a readable initialized region of `len` elements.
            if $i < len
                && unsafe {
                    P::model_less(&P::model(&*base.add($i)), &P::model(&*base.add($i - 1)))
                }
            {
                ok = false;
            }
        )*};
    }
    step!(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
    ok
}

/// Number of full models equal to the shared probe in `base[..len]`; loop-free for `len <= 32`.
pub(crate) fn model_count<P: Profile>(base: *const P::Elem, len: usize) -> usize {
    let mut c = 0;
    let probe = P::probe();
    macro_rules! step {
        ($($i:literal)*) => {$(
            // SAFETY: `$i < len`; callers pass a readable initialized region of `len` elements.
            if $i < len && unsafe { P::model(&*base.add($i)) } == probe {
                c += 1;
            }
        )*};
    }
    step!(
        0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
    );
    c
}

// swap_if_less profile: one comparator decision, made from pure pre-state models.

pub(crate) fn swap_geometry<T>(v: *mut T, a: usize, b: usize) -> bool {
    a != b
        && same_allocation(v as *const T, v.wrapping_add(a) as *const T)
        && same_allocation(v as *const T, v.wrapping_add(b) as *const T)
        && can_dereference(v.wrapping_add(a) as *const T)
        && can_dereference(v.wrapping_add(b) as *const T)
        && can_write(v.wrapping_add(a))
        && can_write(v.wrapping_add(b))
}

pub(crate) fn pair_models<P: Profile>(
    v: *const P::Elem,
    a: usize,
    b: usize,
) -> (P::Model, P::Model) {
    // SAFETY: fixture values are initialized; the requires check both positions' geometry.
    unsafe { (P::model(&*v.add(a)), P::model(&*v.add(b))) }
}

/// Conditional transfer by the pure pre-key comparison; the other branch keeps both values.
pub(crate) fn swap_transfer<P: Profile>(
    pre: (P::Model, P::Model),
    v: *const P::Elem,
    a: usize,
    b: usize,
) -> bool {
    let (now_a, now_b) = pair_models::<P>(v, a, b);
    if P::model_less(&pre.1, &pre.0) {
        now_a == pre.1 && now_b == pre.0
    } else {
        now_a == pre.0 && now_b == pre.1
    }
}

pub(crate) fn swap_ordered<P: Profile>(v: *const P::Elem, a: usize, b: usize) -> bool {
    let (now_a, now_b) = pair_models::<P>(v, a, b);
    !P::model_less(&now_b, &now_a)
}

#[kani::requires(swap_geometry::<P::Elem>(v, a, b))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<P>(v, a, b))]
pub(crate) unsafe fn swap_profile<P: Profile>(
    v: *mut P::Elem,
    a: usize,
    b: usize,
) {
    let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);
    // SAFETY: initialized exclusive fixture storage; requires check geometry; the profile fixes the comparator.
    unsafe { swap_if_less(v, a, b, &mut is_less) }
}

// sort4_stable profile: source and destination geometry; fixtures initialize the source.

pub(crate) fn sort4_regions<T>(src: *const T, dst: *mut T) -> bool {
    size_of::<T>() > 0
        && can_dereference(ptr::slice_from_raw_parts(src, 4))
        && can_write(ptr::slice_from_raw_parts_mut(dst, 4))
        && regions_are_disjoint::<T>(src, 4, dst as *const T, 4)
}

#[kani::requires(sort4_regions::<P::Elem>(src, dst))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4))]
#[kani::ensures(|_| model_sorted::<P>(dst, 4))]
#[kani::ensures(|_| model_count::<P>(src, 4) == model_count::<P>(dst, 4))]
pub(crate) unsafe fn sort4_profile<P: Profile>(
    src: *const P::Elem,
    dst: *mut P::Elem,
) {
    let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);
    // SAFETY: fixtures initialize src and own dst; requires check both spans and disjointness.
    unsafe { sort4_stable(src, dst, &mut is_less) }
}

// insert_tail profile: full-span geometry and bounds before the distance or typed reads;
// fixtures initialize the elements; the sorted prefix is a pure model premise.

pub(crate) fn tail_len<T>(begin: *const T, tail: *const T) -> usize {
    // SAFETY: evaluated only after `tail_region` established one allocation and both bounds.
    (unsafe { tail.offset_from(begin) }) as usize + 1
}

pub(crate) fn tail_region<T>(begin: *mut T, tail: *mut T) -> bool {
    size_of::<T>() > 0
        && same_allocation(begin as *const T, tail as *const T)
        && can_dereference(begin as *const T)
        && can_dereference(tail as *const T)
        && {
            // SAFETY: nonzero size, one allocation, both pointers in bounds (checked above).
            let d = unsafe { tail.offset_from(begin) };
            1 <= d && d < 32
        }
        && can_dereference(ptr::slice_from_raw_parts(begin as *const T, tail_len::<T>(begin, tail)))
        && can_write(ptr::slice_from_raw_parts_mut(begin, tail_len::<T>(begin, tail)))
}

#[kani::requires(
    tail_region::<P::Elem>(begin, tail)
        && model_sorted::<P>(begin, tail_len::<P::Elem>(begin, tail) - 1)
)]
#[kani::modifies(ptr::slice_from_raw_parts_mut(begin, tail_len::<P::Elem>(begin, tail)))]
#[kani::ensures(|_| model_sorted::<P>(begin, tail_len::<P::Elem>(begin, tail)))]
#[kani::ensures(|_|
    old(model_count::<P>(begin, tail_len::<P::Elem>(begin, tail)))
        == model_count::<P>(begin, tail_len::<P::Elem>(begin, tail))
)]
pub(crate) unsafe fn insert_tail_profile<P: Profile>(
    begin: *mut P::Elem,
    tail: *mut P::Elem,
) {
    let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);
    // SAFETY: initialized exclusive fixture storage; requires check geometry and sorted prefix.
    unsafe { insert_tail(begin, tail, &mut is_less) }
}

// bidirectional_merge profile: N in 2..=32 before any half or pointer computation.

pub(crate) fn merge_regions<T>(v: &[T], dst: *mut T) -> bool {
    size_of::<T>() > 0
        && v.len() >= 2
        && v.len() <= 32
        && can_dereference(v as *const [T])
        && can_write(ptr::slice_from_raw_parts_mut(dst, v.len()))
        && regions_are_disjoint::<T>(v.as_ptr(), v.len(), dst as *const T, v.len())
}

pub(crate) fn merge_halves_sorted<P: Profile>(v: &[P::Elem]) -> bool {
    let half = v.len() / 2;
    model_sorted::<P>(v.as_ptr(), half)
        && model_sorted::<P>(v.as_ptr().wrapping_add(half), v.len() - half)
}

#[kani::requires(merge_regions::<P::Elem>(v, dst) && merge_halves_sorted::<P>(v))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, v.len()))]
#[kani::ensures(|_| model_sorted::<P>(dst, v.len()))]
#[kani::ensures(|_| model_count::<P>(v.as_ptr(), v.len()) == model_count::<P>(dst, v.len()))]
pub(crate) unsafe fn merge_profile<P: Profile>(
    v: &[P::Elem],
    dst: *mut P::Elem,
) where
    P::Elem: FreezeMarker,
{
    let mut is_less = |a: &P::Elem, b: &P::Elem| P::cmp(a, b);
    // SAFETY: fixtures initialize v and own dst; requires check destination geometry and lengths.
    unsafe { bidirectional_merge(v, dst, &mut is_less) }
}

// Matched summary consumers: the wrapper itself owns the closure expression, so a leaf and
// its consumer instantiate the same P/Elem/closure even when the wrapper is replaced. These
// roots require new qualification; no result for the former fn-pointer signature is reused.
#[kani::proof]
#[kani::stub_verified(swap_profile)]
#[kani::unwind(6)]
fn profile_swap_consumer_u8_backing4() {
    let mut v: [u8; 4] = kani::any();
    let before = v;
    let a: usize = kani::any_where(|a: &usize| *a < 4);
    let b: usize = kani::any_where(|b: &usize| *b < 4 && *b != a);
    let pre = pair_models::<LtU8>(v.as_ptr(), a, b);
    // SAFETY: distinct initialized writable positions in the matching backing4 geometry.
    unsafe { swap_profile::<LtU8>(v.as_mut_ptr(), a, b) };
    kani::assert(swap_transfer::<LtU8>(pre, v.as_ptr(), a, b), "static swap transfer");
    kani::assert(swap_ordered::<LtU8>(v.as_ptr(), a, b), "static swap ordered");
    for i in 0..4 {
        kani::assert(i == a || i == b || v[i] == before[i], "static swap consumer frame");
    }
    kani::cover(true, "static swap consumer returns");
}

fn sort4_consumer<P: Profile>()
where
    P::Elem: kani::Arbitrary,
    P::Model: kani::Arbitrary,
{
    P::set_probe(kani::any());
    let src: [P::Elem; 4] = kani::any();
    let before = model_count::<P>(src.as_ptr(), 4);
    let mut dst = MaybeUninit::<[P::Elem; 4]>::uninit();
    let out = dst.as_mut_ptr().cast::<P::Elem>();
    // SAFETY: separate exact arrays, initialized source; matching sort4 leaf geometry.
    unsafe { sort4_profile::<P>(src.as_ptr(), out) };
    kani::assert(model_sorted::<P>(out, 4), "static sort4 consumer ordered");
    kani::assert(before == model_count::<P>(out, 4), "static sort4 consumer full values");
    kani::assert(before == model_count::<P>(src.as_ptr(), 4), "static sort4 source probe count");
    kani::cover(true, "static sort4 consumer returns");
}

#[kani::proof]
#[kani::stub_verified(sort4_profile)]
#[kani::unwind(34)]
fn profile_sort4_consumer_u64() {
    sort4_consumer::<Sort4ReadU64>();
}

#[kani::proof]
#[kani::stub_verified(sort4_profile)]
#[kani::unwind(34)]
fn profile_sort4_consumer_b16() {
    sort4_consumer::<Sort4ReadB16>();
}

#[kani::proof]
#[kani::stub_verified(insert_tail_profile)]
#[kani::unwind(18)]
fn profile_insert_consumer_u8_backing17() {
    LtU8::set_probe(kani::any());
    let mut v: [u8; 17] = kani::any();
    let tail: usize = kani::any_where(|tail: &usize| 1 <= *tail && *tail < 17);
    let before = v;
    kani::assume(model_sorted::<LtU8>(v.as_ptr(), tail));
    let count = model_count::<LtU8>(v.as_ptr(), tail + 1);
    // SAFETY: matching backing17, begin at zero and symbolic tail; sorted prefix above.
    unsafe { insert_tail_profile::<LtU8>(v.as_mut_ptr(), v.as_mut_ptr().add(tail)) };
    kani::assert(model_sorted::<LtU8>(v.as_ptr(), tail + 1), "static insert consumer ordered");
    kani::assert(
        count == model_count::<LtU8>(v.as_ptr(), tail + 1),
        "static insert consumer full values",
    );
    for i in tail + 1..17 {
        kani::assert(v[i] == before[i], "static insert consumer frame");
    }
    kani::cover(tail == 1, "static insert consumer minimum tail");
    kani::cover(tail == 16, "static insert consumer maximum tail");
    kani::cover(true, "static insert consumer returns");
}

#[kani::proof]
#[kani::stub_verified(merge_profile)]
#[kani::unwind(34)]
fn profile_merge_consumer_u8_len4() {
    LtU8::set_probe(kani::any());
    let src: [u8; 4] = kani::any();
    let before = src;
    kani::assume(merge_halves_sorted::<LtU8>(&src));
    let count = model_count::<LtU8>(src.as_ptr(), 4);
    let mut dst = MaybeUninit::<[u8; 4]>::uninit();
    let out = dst.as_mut_ptr().cast::<u8>();
    // SAFETY: separate exact arrays and sorted halves, matching the len2-to4 leaf's len4 arm.
    unsafe { merge_profile::<LtU8>(&src, out) };
    kani::assert(model_sorted::<LtU8>(out, 4), "static merge consumer ordered");
    kani::assert(count == model_count::<LtU8>(out, 4), "static merge consumer full values");
    kani::assert(src == before, "static merge source frame");
    kani::cover(true, "static merge consumer returns");
}

/// Real sort4 with the static profile comparator, then one payload bit flip that keeps the key.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn profile_full_value_checker_rejects_payload_change_u8() {
    LtU8::set_probe(kani::any());
    let src: [u8; 4] = kani::any();
    let mut dst = [0u8; 4];
    let mut cmp = |a: &u8, b: &u8| LtU8::cmp(a, b);
    // SAFETY: separate initialized four-element arrays.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "payload corruption reached");
    dst[1] ^= 1;
    let keys = model_sorted::<LtU8>(dst.as_ptr(), 4);
    kani::assert(keys, "corrupted payload keeps key order");
    let same = model_count::<LtU8>(src.as_ptr(), 4) == model_count::<LtU8>(dst.as_ptr(), 4);
    kani::assert(same, "full-value checker detects payload corruption");
}

// Historical wrong-F root names are retained for inventory continuity. The new API has no
// comparator argument, so a wrong function value cannot be supplied. These controls instead
// execute real wrappers with deliberately unaudited test-only profiles; no verified stub may
// admit these profiles. Each checks the same pure model postcondition as its legal companion.

#[cfg(kani_smallsort_controls)]
fn always_true_u8(_: &u8, _: &u8) -> bool {
    true
}

#[cfg(kani_smallsort_controls)]
fn always_true_u64(_: &u64, _: &u64) -> bool {
    true
}

#[cfg(kani_smallsort_controls)]
fn reverse_u8(a: &u8, b: &u8) -> bool {
    lt_u8(b, a)
}

#[cfg(kani_smallsort_controls)]
identity_profile!(BadCmpU8, u8, BAD_CMP_U8_PROBE, 0, always_true_u8, lt_u8);
#[cfg(kani_smallsort_controls)]
identity_profile!(BadCmpU64, u64, BAD_CMP_U64_PROBE, 0, always_true_u64, lt_u64);
#[cfg(kani_smallsort_controls)]
identity_profile!(BadRelationU8, u8, BAD_RELATION_U8_PROBE, 0, lt_u8, reverse_u8);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn profile_wrong_f_swap_rejected_u8() {
    let mut v = [0u8, 2];
    let pre = pair_models::<BadCmpU8>(v.as_ptr(), 0, 1);
    kani::cover(true, "wrong-F swap call reached");
    // SAFETY: distinct initialized positions; deliberately bad comparator/model relation only.
    unsafe { swap_profile::<BadCmpU8>(v.as_mut_ptr(), 0, 1) };
    kani::assert(
        swap_transfer::<BadCmpU8>(pre, v.as_ptr(), 0, 1),
        "bad-profile swap transfer rejected",
    );
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
fn profile_wrong_f_sort4_rejected_u64() {
    let src = [0u64, 2, 4, 6];
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    kani::cover(true, "wrong-F sort4 call reached");
    // SAFETY: initialized source, separate four-element destination; bad relation only.
    unsafe { sort4_profile::<BadCmpU64>(src.as_ptr(), dst.as_mut_ptr().cast()) };
    kani::assert(
        model_sorted::<BadCmpU64>(dst.as_ptr().cast(), 4),
        "bad-profile sort4 order rejected",
    );
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn profile_wrong_f_insert_rejected_u8() {
    // Keys [0, 2, 1] have a model-sorted prefix.
    let mut v = [0u8, 4, 2];
    let base = v.as_mut_ptr();
    kani::cover(true, "wrong-F insert call reached");
    // SAFETY: one initialized writable array, begin < tail; bad relation only.
    unsafe { insert_tail_profile::<BadCmpU8>(base, base.add(2)) };
    kani::assert(model_sorted::<BadCmpU8>(base, 3), "bad-profile insert order rejected");
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn profile_wrong_f_merge_rejected_u8() {
    // Singleton halves satisfy even the bad (reversed) model order. The comparator itself is
    // lawful: merge returns normally, so an order-violation abort cannot hide this negative.
    let v = [0u8, 2];
    let mut dst = MaybeUninit::<[u8; 2]>::uninit();
    kani::cover(true, "wrong-F merge call reached");
    // SAFETY: initialized source, separate destination of two; wrong model relation only.
    unsafe { merge_profile::<BadRelationU8>(&v, dst.as_mut_ptr().cast()) };
    kani::assert(
        model_sorted::<BadRelationU8>(dst.as_ptr().cast(), 2),
        "bad-relation merge order rejected",
    );
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
fn profile_bad_relation_rejected_u8() {
    let (a, b) = (0u8, 2u8);
    kani::cover(true, "bad relation reached");
    kani::assert(
        BadRelationU8::cmp(&a, &b)
            == BadRelationU8::model_less(&BadRelationU8::model(&a), &BadRelationU8::model(&b)),
        "bad comparator-model relation rejected",
    );
}
