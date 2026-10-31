//! SPECFIX StageA: proof-owned checked profiles for the four contracted helpers; opt-in only.
//! A profile fixes a closed element type `P` and its audited canonical comparator `P::CMP`.
//! Specifications compute order and full-value counts from the pure model `P::model`; they never
//! call the runtime callback. The forwarder passes exactly `cmp` to the real generic helper, and
//! `specfix_canonical_comparator` rejects any other function pointer before an ordered summary.
//! Arbitrary or effectful `FnMut` comparators stay outside every profile; their safety remains
//! with the real-body harnesses. Ordinary generic annotations are unchanged in this stage.
//! `kani::assert` keeps literal property descriptions; core `assert!` reports a placeholder.

use super::{
    CopyOnDrop, VALUE_PROBE_BYTES, lt_b16, lt_u8, lt_u64, matches_value_probe, set_value_probe,
};
use crate::cell::Cell;
use crate::mem::{MaybeUninit, size_of};
use crate::slice::sort::shared::FreezeMarker;
use crate::slice::sort::shared::smallsort::{
    bidirectional_merge, insert_tail, small_sort_general, sort4_stable, swap_if_less,
};
use crate::ub_checks::{can_dereference, can_write, same_allocation};
use crate::{kani, ptr};

/// Closed verification profile. Each implementation is audited: `CMP(a, b)` is literally
/// `model_less(&model(a), &model(b))` plus volatile reads, `model` is the full logical value and
/// has no side effects, and the probe is one nondeterministic model shared by a composition.
pub(crate) trait Profile: Sized {
    type Model: Copy + PartialEq;
    const CMP: fn(&Self, &Self) -> bool;
    fn model(x: &Self) -> Self::Model;
    fn model_less(a: &Self::Model, b: &Self::Model) -> bool;
    fn probe() -> Self::Model;
    fn set_probe(m: Self::Model);
}

fn read_pair<U: Copy>(a: &U, b: &U) {
    // SAFETY: both references point to initialized values; volatile reads retain the accesses.
    unsafe {
        let _ = ptr::read_volatile(a);
        let _ = ptr::read_volatile(b);
    }
}

pub(crate) fn specfix_u8_less(a: &u8, b: &u8) -> bool {
    read_pair(a, b);
    lt_u8(a, b)
}

pub(crate) fn specfix_u64_less(a: &u64, b: &u64) -> bool {
    read_pair(a, b);
    lt_u64(a, b)
}

pub(crate) fn specfix_b16_less(a: &[u8; 16], b: &[u8; 16]) -> bool {
    read_pair(a, b);
    lt_b16(a, b)
}

pub(crate) fn specfix_cell_i32_less(a: &Cell<i32>, b: &Cell<i32>) -> bool {
    full_i32_less(&a.get(), &b.get())
}

fn full_i32_less(a: &i32, b: &i32) -> bool {
    *a < *b
}

macro_rules! copy_profile {
    ($t:ty, $probe:ident, $zero:expr, $cmp:ident, $less:ident) => {
        static mut $probe: $t = $zero;

        impl Profile for $t {
            type Model = $t;
            const CMP: fn(&$t, &$t) -> bool = $cmp;
            fn model(x: &$t) -> $t {
                *x
            }
            fn model_less(a: &$t, b: &$t) -> bool {
                $less(a, b)
            }
            fn probe() -> $t {
                // SAFETY: single-threaded harness; no reference to the static is alive.
                unsafe { *ptr::addr_of!($probe) }
            }
            fn set_probe(m: $t) {
                // SAFETY: single-threaded harness; no reference to the static is alive.
                unsafe { *ptr::addr_of_mut!($probe) = m }
            }
        }
    };
}

copy_profile!(u8, SPECFIX_PROBE_U8, 0, specfix_u8_less, lt_u8);
copy_profile!(u64, SPECFIX_PROBE_U64, 0, specfix_u64_less, lt_u64);
copy_profile!([u8; 16], SPECFIX_PROBE_B16, [0; 16], specfix_b16_less, lt_b16);

static mut SPECFIX_PROBE_CELL_I32: i32 = 0;

/// `Cell<i32>` is modelled by `get()`, its full logical value; the comparator only reads.
impl Profile for Cell<i32> {
    type Model = i32;
    const CMP: fn(&Cell<i32>, &Cell<i32>) -> bool = specfix_cell_i32_less;
    fn model(x: &Cell<i32>) -> i32 {
        x.get()
    }
    fn model_less(a: &i32, b: &i32) -> bool {
        full_i32_less(a, b)
    }
    fn probe() -> i32 {
        // SAFETY: single-threaded harness; no reference to the static is alive.
        unsafe { *ptr::addr_of!(SPECFIX_PROBE_CELL_I32) }
    }
    fn set_probe(m: i32) {
        // SAFETY: single-threaded harness; no reference to the static is alive.
        unsafe { *ptr::addr_of_mut!(SPECFIX_PROBE_CELL_I32) = m }
    }
}

/// The canonical guard: only the profile's audited function value is accepted. This is the
/// address comparison `ptr::fn_addr_eq` performs, written as a direct cast for the pinned model.
pub(crate) fn specfix_canonical_comparator<P: Profile>(cmp: fn(&P, &P) -> bool) -> bool {
    cmp as *const () == P::CMP as *const ()
}

/// No adjacent strict model inversion in `base[..len]`; loop-free for `len <= 32`.
pub(crate) fn model_sorted<P: Profile>(base: *const P, len: usize) -> bool {
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
pub(crate) fn model_count<P: Profile>(base: *const P, len: usize) -> usize {
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

pub(crate) fn swap_geometry<P>(v: *mut P, a: usize, b: usize) -> bool {
    a != b
        && same_allocation(v as *const P, v.wrapping_add(a) as *const P)
        && same_allocation(v as *const P, v.wrapping_add(b) as *const P)
        && can_dereference(v.wrapping_add(a) as *const P)
        && can_dereference(v.wrapping_add(b) as *const P)
        && can_write(v.wrapping_add(a))
        && can_write(v.wrapping_add(b))
}

pub(crate) fn pair_models<P: Profile>(v: *const P, a: usize, b: usize) -> (P::Model, P::Model) {
    // SAFETY: the requires make both positions readable initialized values.
    unsafe { (P::model(&*v.add(a)), P::model(&*v.add(b))) }
}

/// Conditional transfer by the pure pre-key comparison; the other branch keeps both values.
pub(crate) fn swap_transfer<P: Profile>(
    pre: (P::Model, P::Model),
    v: *const P,
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

pub(crate) fn swap_ordered<P: Profile>(v: *const P, a: usize, b: usize) -> bool {
    let (now_a, now_b) = pair_models::<P>(v, a, b);
    !P::model_less(&now_b, &now_a)
}

#[kani::requires(swap_geometry::<P>(v, a, b))]
#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<P>(v, a, b))]
pub(crate) unsafe fn swap_profile<P: Profile>(
    v: *mut P,
    a: usize,
    b: usize,
    cmp: fn(&P, &P) -> bool,
) {
    let mut is_less = cmp;
    // SAFETY: the requires establish swap_if_less's safety conditions; `is_less` is `P::CMP`.
    unsafe { swap_if_less(v, a, b, &mut is_less) }
}

// sort4_stable profile: readable initialized source, writable disjoint destination.

pub(crate) fn sort4_regions<P>(src: *const P, dst: *mut P) -> bool {
    size_of::<P>() > 0
        && can_dereference(ptr::slice_from_raw_parts(src, 4))
        && can_write(ptr::slice_from_raw_parts_mut(dst, 4))
        && CopyOnDrop::<P>::regions_are_disjoint(src, 4, dst as *const P, 4)
}

#[kani::requires(sort4_regions::<P>(src, dst))]
#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4))]
#[kani::ensures(|_| model_sorted::<P>(dst, 4))]
#[kani::ensures(|_| model_count::<P>(src, 4) == model_count::<P>(dst, 4))]
pub(crate) unsafe fn sort4_profile<P: Profile>(
    src: *const P,
    dst: *mut P,
    cmp: fn(&P, &P) -> bool,
) {
    let mut is_less = cmp;
    // SAFETY: the requires establish sort4_stable's read/write/disjointness conditions.
    unsafe { sort4_stable(src, dst, &mut is_less) }
}

// insert_tail profile: geometry and bounds before the distance, full region readable and
// writable before any typed read; the sorted prefix is a pure model premise.

pub(crate) fn tail_len<P>(begin: *const P, tail: *const P) -> usize {
    // SAFETY: evaluated only after `tail_region` established one allocation and both bounds.
    (unsafe { tail.offset_from(begin) }) as usize + 1
}

pub(crate) fn tail_region<P>(begin: *mut P, tail: *mut P) -> bool {
    size_of::<P>() > 0
        && same_allocation(begin as *const P, tail as *const P)
        && can_dereference(begin as *const P)
        && can_dereference(tail as *const P)
        && {
            // SAFETY: nonzero size, one allocation, both pointers in bounds (checked above).
            let d = unsafe { tail.offset_from(begin) };
            1 <= d && d < 32
        }
        && can_dereference(ptr::slice_from_raw_parts(begin as *const P, tail_len::<P>(begin, tail)))
        && can_write(ptr::slice_from_raw_parts_mut(begin, tail_len::<P>(begin, tail)))
}

#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::requires(
    tail_region::<P>(begin, tail) && model_sorted::<P>(begin, tail_len::<P>(begin, tail) - 1)
)]
#[kani::modifies(ptr::slice_from_raw_parts_mut(begin, tail_len::<P>(begin, tail)))]
#[kani::ensures(|_| model_sorted::<P>(begin, tail_len::<P>(begin, tail)))]
#[kani::ensures(|_|
    old(model_count::<P>(begin, tail_len::<P>(begin, tail)))
        == model_count::<P>(begin, tail_len::<P>(begin, tail))
)]
pub(crate) unsafe fn insert_tail_profile<P: Profile>(
    begin: *mut P,
    tail: *mut P,
    cmp: fn(&P, &P) -> bool,
) {
    let mut is_less = cmp;
    // SAFETY: the requires establish insert_tail's region and sorted-prefix conditions.
    unsafe { insert_tail(begin, tail, &mut is_less) }
}

// bidirectional_merge profile: N in 2..=32 before any half or pointer computation.

pub(crate) fn merge_regions<P>(v: &[P], dst: *mut P) -> bool {
    size_of::<P>() > 0
        && v.len() >= 2
        && v.len() <= 32
        && can_dereference(v as *const [P])
        && can_write(ptr::slice_from_raw_parts_mut(dst, v.len()))
        && CopyOnDrop::<P>::regions_are_disjoint(v.as_ptr(), v.len(), dst as *const P, v.len())
}

pub(crate) fn merge_halves_sorted<P: Profile>(v: &[P]) -> bool {
    let half = v.len() / 2;
    model_sorted::<P>(v.as_ptr(), half)
        && model_sorted::<P>(v.as_ptr().wrapping_add(half), v.len() - half)
}

#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::requires(merge_regions::<P>(v, dst) && merge_halves_sorted::<P>(v))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, v.len()))]
#[kani::ensures(|_| model_sorted::<P>(dst, v.len()))]
#[kani::ensures(|_| model_count::<P>(v.as_ptr(), v.len()) == model_count::<P>(dst, v.len()))]
pub(crate) unsafe fn merge_profile<P: Profile + FreezeMarker>(
    v: &[P],
    dst: *mut P,
    cmp: fn(&P, &P) -> bool,
) {
    let mut is_less = cmp;
    // SAFETY: the requires establish bidirectional_merge's destination and length conditions.
    unsafe { bidirectional_merge(v, dst, &mut is_less) }
}

/// Transparent stub adapter for `bidirectional_merge`: forwards the same arguments to the checked
/// profile. Only function-pointer comparators convert; the profile guard then checks the value.
pub(crate) unsafe fn merge_adapter<T, F>(v: &[T], dst: *mut T, is_less: &mut F)
where
    T: FreezeMarker + Profile,
    F: FnMut(&T, &T) -> bool + Copy + Into<fn(&T, &T) -> bool>,
{
    let cmp: fn(&T, &T) -> bool = (*is_less).into();
    // SAFETY: arguments are forwarded unchanged; the profile requires are checked at this call.
    unsafe { merge_profile::<T>(v, dst, cmp) }
}

// Profile proofs. Domains mirror the PFC names in network.rs, merge.rs and correct.rs; each
// profile instance is new evidence and does not transfer a prior PASS.

#[kani::proof_for_contract(swap_profile)]
fn swap_profile_four_positions_u8() {
    let mut v: [u8; 4] = kani::any();
    let a: usize = kani::any_where(|&a| a < 4);
    let b: usize = kani::any_where(|&b| b < 4 && b != a);
    kani::cover(a == 0 && b == 3, "specfix swap profile: a < b reachable");
    kani::cover(a == 3 && b == 0, "specfix swap profile: a > b reachable");
    let (old_a, old_b) = (v[a], v[b]);
    // SAFETY: `a` and `b` are distinct in-bounds positions of `v`; canonical comparator.
    unsafe { swap_profile::<u8>(v.as_mut_ptr(), a, b, <u8 as Profile>::CMP) };
    kani::cover(lt_u8(&old_b, &old_a), "specfix swap profile: swap taken");
    kani::cover(!lt_u8(&old_b, &old_a), "specfix swap profile: swap not taken");
    kani::cover(true, "specfix swap profile: end reached");
}

/// Exact two-element array in either index order; shared with the Drop profile in network.rs.
pub(crate) fn swap_profile_pair<P: Profile>(mut v: [P; 2]) {
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    let taken = P::model_less(&P::model(&v[b]), &P::model(&v[a]));
    // SAFETY: distinct initialized writable elements of one live array; canonical comparator.
    unsafe { swap_profile::<P>(v.as_mut_ptr(), a, b, P::CMP) };
    kani::cover(reverse, "specfix swap pair covers indices 1 and 0");
    kani::cover(!reverse, "specfix swap pair covers indices 0 and 1");
    kani::cover(taken, "specfix swap pair swap branch");
    kani::cover(!taken, "specfix swap pair no-swap branch");
    kani::cover(true, "specfix swap pair reached the end");
}

#[kani::proof_for_contract(swap_profile)]
#[kani::unwind(180)]
fn swap_profile_cell_i32_n2() {
    swap_profile_pair::<Cell<i32>>([Cell::new(kani::any()), Cell::new(kani::any())]);
}

fn sort4_profile_body<P>()
where
    P: Profile + kani::Arbitrary,
    P::Model: kani::Arbitrary,
{
    P::set_probe(kani::any());
    let v: [P; 4] = kani::any();
    let mut dst = MaybeUninit::<[P; 4]>::uninit();
    // SAFETY: two disjoint exact four-element allocations, initialized source.
    unsafe { sort4_profile::<P>(v.as_ptr(), dst.as_mut_ptr() as *mut P, P::CMP) };
    kani::cover(true, "specfix sort4 profile returns");
}

#[kani::proof_for_contract(sort4_profile)]
#[kani::unwind(34)]
fn sort4_profile_u64_n4() {
    sort4_profile_body::<u64>();
}

#[kani::proof_for_contract(sort4_profile)]
#[kani::unwind(34)]
fn sort4_profile_bytes16_n4() {
    sort4_profile_body::<[u8; 16]>();
}

/// u8 insertion profile and suffix frame in a 17-element allocation, tail indices 1..=16.
#[kani::proof_for_contract(insert_tail_profile)]
#[kani::solver(cadical)]
#[kani::unwind(18)]
fn insert_tail_profile_u8_prefix() {
    <u8 as Profile>::set_probe(kani::any());
    let mut input: [u8; 17] = kani::any();
    let tail: usize = kani::any_where(|t: &usize| 1 <= *t && *t < 17);
    let before = input;
    let base = input.as_mut_ptr();
    // SAFETY: valid same-allocation region; the profile requires supply the sorted prefix.
    unsafe { insert_tail_profile::<u8>(base, base.add(tail), <u8 as Profile>::CMP) };
    for i in tail + 1..17 {
        kani::assert(input[i] == before[i], "specfix u8 prefix: suffix unchanged");
    }
    kani::cover(tail == 1, "specfix u8 prefix: region 2 reachable");
    kani::cover(tail == 15, "specfix u8 prefix: proper prefix region 16 reachable");
    kani::cover(tail == 16, "specfix u8 prefix: full region 17 reachable");
    kani::cover(true, "specfix u8 prefix: completion");
}

/// u64 START1 insertion profile, tails 2..=8 of an exact `[u64; 17]`, prefix and suffix frame.
#[kani::proof_for_contract(insert_tail_profile)]
#[kani::unwind(25)]
fn insert_tail_profile_u64_start1_tail2_to8() {
    <u64 as Profile>::set_probe(kani::any());
    let mut v: [u64; 17] = kani::any();
    let tail: usize = kani::any_where(|&t| 2 <= t && t <= 8);
    let pre = v;
    let base = v.as_mut_ptr();
    // SAFETY: begin = 1 < tail <= 8 < 17; the profile requires supply the sorted prefix.
    unsafe { insert_tail_profile::<u64>(base.add(1), base.add(tail), <u64 as Profile>::CMP) };
    kani::assert(v[0] == pre[0], "specfix start1: prefix before begin unchanged");
    let mut moved = false;
    let mut i = 0;
    while i < 17 {
        if i > tail {
            kani::assert(v[i] == pre[i], "specfix start1: suffix after tail unchanged");
        }
        moved |= v[i] != pre[i];
        i += 1;
    }
    kani::cover(moved, "specfix start1: insertion moves elements");
    kani::cover(tail == 2, "specfix start1: tail 2 with requires satisfied");
    kani::cover(tail == 3, "specfix start1: tail 3 with requires satisfied");
    kani::cover(tail == 4, "specfix start1: tail 4 with requires satisfied");
    kani::cover(tail == 5, "specfix start1: tail 5 with requires satisfied");
    kani::cover(tail == 6, "specfix start1: tail 6 with requires satisfied");
    kani::cover(tail == 7, "specfix start1: tail 7 with requires satisfied");
    kani::cover(tail == 8, "specfix start1: tail 8 with requires satisfied");
}

#[kani::proof_for_contract(merge_profile)]
#[kani::unwind(34)]
fn merge_profile_u8_n8() {
    <u8 as Profile>::set_probe(kani::any());
    let v: [u8; 8] = kani::any();
    let mut dst = MaybeUninit::<[u8; 8]>::uninit();
    // SAFETY: initialized source, separate destination of eight elements.
    unsafe { merge_profile::<u8>(&v, dst.as_mut_ptr() as *mut u8, <u8 as Profile>::CMP) };
    kani::cover(true, "specfix merge profile returns for length 8");
}

// Positive regression: raw unordered forms of SPECDIAG 1-4, readonly/initialized admission,
// a 129-byte typed swap without the probe, and the typed/byte oracle bridge.

static SPECFIX_READONLY_U64: [u64; 4] = [6, 2, 4, 0];

fn specfix_abort_on_order_violation() -> ! {
    kani::cover(true, "specfix order violation panic path is reachable");
    kani::assume(false);
    unreachable!()
}

fn raw_sort4_true_f() {
    <u8 as Profile>::set_probe(kani::any());
    let src: [u8; 4] = kani::any();
    let mut dst = [0u8; 4];
    let mut cmp = |_: &u8, _: &u8| true;
    // SAFETY: disjoint initialized arrays; sort4 safety does not need an ordered comparator.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    let same = model_count::<u8>(src.as_ptr(), 4) == model_count::<u8>(dst.as_ptr(), 4);
    kani::assert(same, "specfix raw sort4 true F preserves full values");
    kani::cover(true, "specfix raw sort4 true F returned");
}

fn raw_insert_true_f() {
    <u8 as Profile>::set_probe(kani::any());
    let mut v: [u8; 2] = kani::any();
    let orig = v;
    let base = v.as_mut_ptr();
    let mut cmp = |_: &u8, _: &u8| true;
    // SAFETY: begin < tail in one initialized writable array; no sorted-prefix claim is used.
    unsafe { insert_tail(base, base.add(1), &mut cmp) };
    let same = model_count::<u8>(orig.as_ptr(), 2) == model_count::<u8>(v.as_ptr(), 2);
    kani::assert(same, "specfix raw insert_tail true F preserves full values");
    kani::cover(true, "specfix raw insert_tail true F returned");
}

fn raw_merge_true_f() {
    let v: [u8; 2] = kani::any();
    let mut dst = MaybeUninit::<[u8; 2]>::uninit();
    let mut cmp = |_: &u8, _: &u8| true;
    // SAFETY: initialized source, separate destination of two; normal return only is claimed.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut u8, &mut cmp) };
    kani::cover(true, "specfix raw merge true F returned");
}

fn runtime_fnmut_observer() {
    let mut v: [u8; 2] = kani::any();
    let mut calls = 0u8;
    let mut cmp = |a: &u8, b: &u8| {
        calls += 1;
        lt_u8(a, b)
    };
    // SAFETY: distinct initialized writable positions of one array.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::assert(calls == 1, "specfix runtime FnMut observer sees exactly one call");
    kani::cover(true, "specfix runtime FnMut observer returned");
}

fn readonly_and_initialized_admission() {
    let mut dst = [0u64; 4];
    let src = SPECFIX_READONLY_U64.as_ptr();
    let admitted = sort4_regions::<u64>(src, dst.as_mut_ptr());
    kani::assert(admitted, "specfix sort4 profile admits a readonly initialized source");
    let mut cmp = <u64 as Profile>::CMP;
    // SAFETY: readonly initialized static source of four, separate writable destination.
    unsafe { sort4_stable(src, dst.as_mut_ptr(), &mut cmp) };
    kani::assert(model_sorted::<u64>(dst.as_ptr(), 4), "specfix readonly source sorts");
    let mut w: [u8; 3] = kani::any();
    let base = w.as_mut_ptr();
    // SAFETY: in-bounds element pointers of `w`, used only by predicates.
    let tail = unsafe { base.add(2) };
    kani::assert(tail_region::<u8>(base, tail), "specfix insert profile admits initialized region");
    kani::cover(true, "specfix readonly and initialized admission reached");
}

fn typed_swap_t129() {
    let x: [u8; 129] = kani::any();
    let y: [u8; 129] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 129], b: &[u8; 129]| a[0] < b[0];
    let taken = y[0] < x[0];
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "specfix typed swap keeps full 129-byte values");
    kani::cover(true, "specfix typed swap 129 returned");
}

fn oracle_bridge_u64() {
    set_value_probe::<u64>();
    // SAFETY: the probe buffer is 16-aligned and holds at least eight initialized bytes.
    let p = unsafe { ptr::read_unaligned(ptr::addr_of!(VALUE_PROBE_BYTES) as *const u64) };
    <u64 as Profile>::set_probe(p);
    let x: u64 = kani::any();
    // SAFETY: `x` is an initialized readable u64 and 8 <= 128.
    let bytes = unsafe { matches_value_probe(&x as *const u64) };
    kani::assert((x == <u64 as Profile>::probe()) == bytes, "specfix typed u64 model = byte probe");
    kani::cover(bytes, "specfix oracle bridge match reachable");
    kani::cover(!bytes, "specfix oracle bridge mismatch reachable");
}

#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    specfix_abort_on_order_violation
)]
#[kani::unwind(140)]
fn specfix_positive_regression() {
    let case: u8 = kani::any_where(|c: &u8| *c < 7);
    match case {
        0 => raw_sort4_true_f(),
        1 => raw_insert_true_f(),
        2 => raw_merge_true_f(),
        3 => runtime_fnmut_observer(),
        4 => readonly_and_initialized_admission(),
        5 => typed_swap_t129(),
        _ => oracle_bridge_u64(),
    }
    kani::cover(case == 6, "specfix positive regression: last case reachable");
}

// Negative controls: each expects exactly the named check to fail.

fn specfix_always_true_u8(_: &u8, _: &u8) -> bool {
    true
}

/// Real general route at N2 (merge only) with the merge adapter and verified merge profile.
/// The canonical pointer path asserts the summary; an always-true pointer must fail the guard.
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::bidirectional_merge, merge_adapter)]
#[kani::stub_verified(merge_profile)]
#[kani::unwind(34)]
fn specfix_adapter_rejects_noncanonical_u8_n2() {
    <u8 as Profile>::set_probe(kani::any());
    let mut v: [u8; 2] = kani::any();
    let orig = v;
    let canonical: bool = kani::any();
    let always_true: fn(&u8, &u8) -> bool = specfix_always_true_u8;
    let mut cmp = if canonical { <u8 as Profile>::CMP } else { always_true };
    small_sort_general(&mut v, &mut cmp);
    let sorted = model_sorted::<u8>(v.as_ptr(), 2);
    kani::assert(sorted, "specfix adapter route output is model-sorted");
    let same = model_count::<u8>(orig.as_ptr(), 2) == model_count::<u8>(v.as_ptr(), 2);
    kani::assert(same, "specfix adapter route preserves full values");
    kani::cover(canonical, "specfix adapter canonical comparator path returns");
    kani::cover(!canonical, "specfix adapter noncanonical comparator path reached");
}

/// Real sort4 with the canonical comparator, then one payload bit flip that keeps the key.
#[kani::proof]
#[kani::unwind(6)]
fn specfix_full_value_checker_rejects_payload_change_u8() {
    <u8 as Profile>::set_probe(kani::any());
    let src: [u8; 4] = kani::any();
    let mut dst = [0u8; 4];
    let mut cmp = <u8 as Profile>::CMP;
    // SAFETY: separate initialized four-element arrays.
    unsafe { sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut cmp) };
    kani::cover(true, "specfix payload corruption reached");
    dst[1] ^= 1;
    kani::assert(model_sorted::<u8>(dst.as_ptr(), 4), "specfix corrupted payload keeps key order");
    let same = model_count::<u8>(src.as_ptr(), 4) == model_count::<u8>(dst.as_ptr(), 4);
    kani::assert(same, "specfix full-value checker detects payload corruption");
}

/// The probe helper must reject a 129-byte value before its first raw read.
#[kani::proof]
#[kani::unwind(140)]
fn specfix_probe_guard_rejects_t129() {
    let x = [0u8; 129];
    kani::cover(true, "specfix probe guard call reached");
    // SAFETY: `x` is readable for 129 bytes; the helper guard rejects before reading the probe.
    let matched = unsafe { matches_value_probe(&x as *const [u8; 129]) };
    kani::cover(!matched, "specfix probe guard returns no match");
}
