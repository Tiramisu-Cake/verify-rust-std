//! Length-parametric forwarding contracts, checked only on N0..3, offset 1 in backing N+2.
//! These opt-in proofs execute real trait entries, with no summaries or comparator substitution.
//! N0 checks frame/no-op; N1 order is trivial but singleton preservation is checked by count.
//! Neither these fixtures nor len <= 3 establish every backing/offset allowed by the contracts.

use super::{
    Cell, MaybeUninit, Model, NonCopyU8, StableSmallSortTypeImpl, UnstableSmallSortFreezeTypeImpl,
    UnstableSmallSortTypeImpl, byte_less, can_dereference, can_write, canonical, cell_less,
    noncopy_less, same_allocation,
};
use crate::{kani, ptr, slice};

fn region<T>(v: *mut T, len: usize) -> bool {
    !v.is_null()
        && v.is_aligned()
        && can_dereference(ptr::slice_from_raw_parts(v, len))
        && can_write(ptr::slice_from_raw_parts_mut(v, len))
}

// Conservative no-alias domain: the entire borrowed scratch is a separate allocation.
fn separate_scratch<T>(v: *mut T, scratch: &[MaybeUninit<T>]) -> bool {
    scratch.is_empty() || !same_allocation(v.cast_const(), scratch.as_ptr().cast::<T>())
}

fn sorted<T: Model>(v: &[T]) -> bool {
    let mut i = 1;
    while i < v.len() {
        if (v[i - 1].model() >> 1) > (v[i].model() >> 1) {
            return false;
        }
        i += 1;
    }
    true
}

fn count<T: Model>(v: &[T], probe: u8) -> usize {
    let mut result = 0;
    let mut i = 0;
    while i < v.len() {
        result += (v[i].model() == probe) as usize;
        i += 1;
    }
    result
}

fn region_sorted<T: Model>(v: *const T, len: usize) -> bool {
    // SAFETY: wrapper requires provide a nonnull/aligned initialized region, including at N0.
    sorted(unsafe { slice::from_raw_parts(v, len) })
}

fn region_count<T: Model>(v: *const T, len: usize, probe: u8) -> usize {
    // SAFETY: wrapper requires provide a readable initialized span; no read is made at N0.
    count(unsafe { slice::from_raw_parts(v, len) }, probe)
}

// A body guard is necessary for plain calls under --no-assert-contracts, too.
fn canonical_guard(ok: bool) -> bool {
    kani::assert(ok, "wone canonical comparator required");
    ok
}

#[kani::requires(len <= 3)]
#[kani::requires(region(v, len) && separate_scratch(v, scratch))]
#[kani::requires(canonical(cmp, cell_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, len))]
#[kani::ensures(|_| region_sorted(v, len))]
#[kani::ensures(|_| old(region_count(v, len, probe)) == region_count(v, len, probe))]
unsafe fn stable_cell_len(
    v: *mut Cell<u8>,
    len: usize,
    scratch: &mut [MaybeUninit<Cell<u8>>],
    cmp: fn(&Cell<u8>, &Cell<u8>) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, cell_less)) {
        return;
    }
    // SAFETY: requires establish len initialized writable elements and separate scratch.
    let v = unsafe { slice::from_raw_parts_mut(v, len) };
    let mut is_less = cmp;
    <Cell<u8> as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

#[kani::requires(len <= 3)]
#[kani::requires(region(v, len))]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, len))]
#[kani::ensures(|_| region_sorted(v, len))]
#[kani::ensures(|_| old(region_count(v, len, probe)) == region_count(v, len, probe))]
unsafe fn unstable_byte_len(v: *mut u8, len: usize, cmp: fn(&u8, &u8) -> bool, probe: u8) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: requires establish len initialized writable elements.
    let v = unsafe { slice::from_raw_parts_mut(v, len) };
    let mut is_less = cmp;
    <u8 as UnstableSmallSortTypeImpl>::small_sort(v, &mut is_less);
}

#[kani::requires(len <= 3)]
#[kani::requires(region(v, len))]
#[kani::requires(canonical(cmp, noncopy_less))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(v, len))]
#[kani::ensures(|_| region_sorted(v, len))]
#[kani::ensures(|_| old(region_count(v, len, probe)) == region_count(v, len, probe))]
unsafe fn freeze_noncopy_len(
    v: *mut NonCopyU8,
    len: usize,
    cmp: fn(&NonCopyU8, &NonCopyU8) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, noncopy_less)) {
        return;
    }
    // SAFETY: requires establish len initialized writable elements; general owns local scratch48.
    let v = unsafe { slice::from_raw_parts_mut(v, len) };
    let mut is_less = cmp;
    <NonCopyU8 as UnstableSmallSortFreezeTypeImpl>::small_sort(v, &mut is_less);
}

// Freeze Stable entry uses general and writes caller scratch. N0/N1 return before its size check;
// N2/N3 require at least 18/19 slots or the real body aborts. PFC below uses scratch48 only.
#[kani::requires(len <= 3)]
#[kani::requires(region(v, len) && separate_scratch(v, scratch))]
#[kani::requires(len < 2 || scratch.len() >= len + 16)]
#[kani::requires(canonical(cmp, byte_less))]
#[kani::modifies(
    ptr::slice_from_raw_parts_mut(v, len),
    ptr::slice_from_raw_parts_mut(scratch.as_ptr().cast_mut(), scratch.len())
)]
#[kani::ensures(|_| region_sorted(v, len))]
#[kani::ensures(|_| old(region_count(v, len, probe)) == region_count(v, len, probe))]
unsafe fn stable_byte_len(
    v: *mut u8,
    len: usize,
    scratch: &mut [MaybeUninit<u8>],
    cmp: fn(&u8, &u8) -> bool,
    probe: u8,
) {
    if !canonical_guard(canonical(cmp, byte_less)) {
        return;
    }
    // SAFETY: requires establish len initialized writable elements and separate adequate scratch.
    let v = unsafe { slice::from_raw_parts_mut(v, len) };
    let mut is_less = cmp;
    <u8 as StableSmallSortTypeImpl>::small_sort(v, scratch, &mut is_less);
}

fn input_frame<T: Model>(v: &[T], left: u8, right: u8) {
    kani::assert(
        v[0].model() == left && v[v.len() - 1].model() == right,
        "wone input sentinels unchanged",
    );
}

// Each match arm owns an exact N+2 backing, not an exact N allocation. The active span starts
// at offset 1, including a nonnull/aligned interior pointer at N0. No input/probe values are cut.
macro_rules! with_backing {
    ($len:expr, $values:expr, $make:expr, |$v:ident| $body:block) => {{
        let [left, a, b, c, right] = $values;
        match $len {
            0 => {
                let mut $v = [($make)(left), ($make)(right)];
                $body
                input_frame(&$v, left, right);
            }
            1 => {
                let mut $v = [($make)(left), ($make)(a), ($make)(right)];
                $body
                input_frame(&$v, left, right);
            }
            2 => {
                let mut $v = [($make)(left), ($make)(a), ($make)(b), ($make)(right)];
                $body
                input_frame(&$v, left, right);
            }
            _ => {
                let mut $v =
                    [($make)(left), ($make)(a), ($make)(b), ($make)(c), ($make)(right)];
                $body
                input_frame(&$v, left, right);
            }
        }
    }};
}

// Called only after the match has rejoined in the uncontracted harness, never in a PFC target.
// Each length/order combination has a reachable cover, without impossible N0/N1 order covers.
fn input_covers(len: usize, a: u8, b: u8, c: u8, probe: u8) {
    kani::cover(len == 0, "wone returns at len 0");
    kani::cover(len == 1, "wone returns at len 1");
    kani::cover(len == 2, "wone returns at len 2");
    kani::cover(len == 3, "wone returns at len 3");
    kani::cover(len == 2 && (a >> 1) > (b >> 1), "wone N2 reversed keys return");
    kani::cover(len == 2 && (a >> 1) < (b >> 1), "wone N2 increasing keys return");
    kani::cover(len == 2 && a != b && (a >> 1) == (b >> 1), "wone N2 tied distinct values");
    kani::cover(len == 2 && a == b, "wone N2 duplicate full values");
    kani::cover(
        len == 3 && (a >> 1) > (b >> 1) && (b >> 1) > (c >> 1),
        "wone N3 reversed keys return",
    );
    kani::cover(
        len == 3 && (a >> 1) < (b >> 1) && (b >> 1) < (c >> 1),
        "wone N3 increasing keys return",
    );
    kani::cover(
        len == 3 && a != b && (a >> 1) == (b >> 1) && (b >> 1) == (c >> 1),
        "wone N3 tied distinct values",
    );
    kani::cover(len == 3 && a == b && b == c, "wone N3 duplicate full values");
    kani::cover(len >= 1 && probe == a, "wone independent probe hits input");
    kani::cover(len == 1 && probe != a, "wone independent probe misses singleton");
    kani::cover(len == 2 && probe != a && probe != b, "wone independent probe misses pair");
    kani::cover(
        len == 3 && probe != a && probe != b && probe != c,
        "wone independent probe misses triple",
    );
}

#[kani::proof_for_contract(stable_cell_len)]
#[kani::unwind(16)]
fn stable_cell_n0_to3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let len: usize = kani::any_where(|n: &usize| *n <= 3);
    let mut scratch = [MaybeUninit::new(Cell::new(kani::any())), MaybeUninit::uninit()];
    let scratch_len: usize = kani::any_where(|n: &usize| *n <= 2);
    // SAFETY: slot 0 is initialized; slot 1 is never read.
    let scratch_before = unsafe { scratch[0].assume_init_ref() }.get();
    with_backing!(len, [left, a, b, c, right], Cell::new, |v| {
        // SAFETY: initialized offset1/lenN in backing N+2, separate scratch, canonical pointer.
        unsafe {
            stable_cell_len(
                v.as_mut_ptr().wrapping_add(1),
                len,
                &mut scratch[..scratch_len],
                cell_less,
                probe,
            )
        };
    });
    // SAFETY: Cell fallback does not write scratch; only input is in the target write-set.
    let scratch_after = unsafe { scratch[0].assume_init_ref() }.get();
    kani::assert(scratch_before == scratch_after, "wone stable Cell scratch frame");
    kani::cover(scratch_len == 0, "wone stable Cell empty scratch returns");
    kani::cover(scratch_len == 2, "wone stable Cell unread uninit scratch tail returns");
    input_covers(len, a, b, c, probe);
}

#[kani::proof_for_contract(unstable_byte_len)]
#[kani::unwind(16)]
fn unstable_byte_n0_to3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let len: usize = kani::any_where(|n: &usize| *n <= 3);
    with_backing!(len, [left, a, b, c, right], |x| x, |v| {
        // SAFETY: initialized offset1/lenN in backing N+2, canonical pointer.
        unsafe { unstable_byte_len(v.as_mut_ptr().wrapping_add(1), len, byte_less, probe) };
    });
    input_covers(len, a, b, c, probe);
}

#[kani::proof_for_contract(freeze_noncopy_len)]
#[kani::unwind(16)]
fn freeze_noncopy_n0_to3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let len: usize = kani::any_where(|n: &usize| *n <= 3);
    with_backing!(len, [left, a, b, c, right], NonCopyU8, |v| {
        // SAFETY: initialized offset1/lenN in backing N+2, canonical pointer.
        unsafe { freeze_noncopy_len(v.as_mut_ptr().wrapping_add(1), len, noncopy_less, probe) };
    });
    input_covers(len, a, b, c, probe);
}

#[kani::proof_for_contract(stable_byte_len)]
#[kani::unwind(16)]
fn stable_byte_n0_to3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let len: usize = kani::any_where(|n: &usize| *n <= 3);
    let mut scratch = [MaybeUninit::uninit(); 48];
    with_backing!(len, [left, a, b, c, right], |x| x, |v| {
        // SAFETY: initialized offset1/lenN, separate scratch48, canonical pointer.
        unsafe {
            stable_byte_len(v.as_mut_ptr().wrapping_add(1), len, &mut scratch, byte_less, probe)
        };
    });
    // Scratch may change: frame is on input sentinels only, with scratch in the write-set.
    input_covers(len, a, b, c, probe);
}

// Plain control: the body guard must reject a wrong callback even without contract assertions.
#[kani::proof]
#[kani::unwind(16)]
fn rejects_always_true() {
    let mut v: [u8; 3] = kani::any();
    let probe: u8 = kani::any();
    let mut scratch = [MaybeUninit::uninit(); 48];
    kani::cover(true, "wone invalid Stable u8 N3 comparator reaches guard");
    // SAFETY: valid initialized N3/separate scratch; only canonical identity is rejected.
    unsafe { stable_byte_len(v.as_mut_ptr(), 3, &mut scratch, super::always_true::<u8>, probe) };
}

// The same generalized full-value count used by all four contracts detects a payload flip.
// Only this control mutates the result, after a plain call of the real Stable u8 N3 entry.
#[kani::proof]
#[kani::unwind(16)]
fn rejects_payload_corruption() {
    let mut v: [u8; 3] = kani::any();
    let probe: u8 = kani::any();
    let before = count(&v, probe);
    let mut scratch = [MaybeUninit::uninit(); 48];
    // SAFETY: initialized N3, separate scratch48, canonical pointer.
    unsafe { stable_byte_len(v.as_mut_ptr(), 3, &mut scratch, byte_less, probe) };
    kani::assert(sorted(&v), "wone control real body sorts keys");
    kani::assert(before == count(&v, probe), "wone control real body keeps full values");
    kani::cover(true, "wone payload corruption reached after real Stable u8 N3 return");
    v[0] ^= 1;
    kani::assert(sorted(&v), "wone corrupted payload keeps key order");
    kani::assert(before == count(&v, probe), "wone full-value checker rejects payload corruption");
}

// Fixed-N3 diagnostic: separate uncontracted covers, without unreachable N0/N1/N2 goals.
fn input_covers_n3(a: u8, b: u8, c: u8, probe: u8) {
    kani::cover(true, "wonediag N3 returns");
    kani::cover((a >> 1) > (b >> 1) && (b >> 1) > (c >> 1), "wonediag N3 reversed keys return");
    kani::cover((a >> 1) < (b >> 1) && (b >> 1) < (c >> 1), "wonediag N3 increasing keys return");
    kani::cover(
        a != b && (a >> 1) == (b >> 1) && (b >> 1) == (c >> 1),
        "wonediag N3 tied distinct values",
    );
    kani::cover(a == b && b == c, "wonediag N3 duplicate full values");
    kani::cover(probe == a, "wonediag N3 independent probe hits input");
    kani::cover(
        probe != a && probe != b && probe != c,
        "wonediag N3 independent probe misses input",
    );
}

#[kani::proof_for_contract(unstable_byte_len)]
#[kani::unwind(16)]
fn unstable_byte_n3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, c, right];
    // SAFETY: initialized offset1/len3 in backing5, canonical pointer.
    unsafe { unstable_byte_len(v.as_mut_ptr().wrapping_add(1), 3, byte_less, probe) };
    input_frame(&v, left, right);
    input_covers_n3(a, b, c, probe);
}

#[kani::proof_for_contract(freeze_noncopy_len)]
#[kani::unwind(16)]
fn freeze_noncopy_n3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [NonCopyU8(left), NonCopyU8(a), NonCopyU8(b), NonCopyU8(c), NonCopyU8(right)];
    // SAFETY: initialized offset1/len3 in backing5, canonical pointer; internal scratch48.
    unsafe { freeze_noncopy_len(v.as_mut_ptr().wrapping_add(1), 3, noncopy_less, probe) };
    input_frame(&v, left, right);
    input_covers_n3(a, b, c, probe);
}

#[kani::proof_for_contract(stable_byte_len)]
#[kani::unwind(16)]
fn stable_byte_n3() {
    let [left, a, b, c, right]: [u8; 5] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, c, right];
    let mut scratch = [MaybeUninit::uninit(); 48];
    // SAFETY: initialized offset1/len3 in backing5, separate full scratch48, canonical pointer.
    unsafe { stable_byte_len(v.as_mut_ptr().wrapping_add(1), 3, &mut scratch, byte_less, probe) };
    // Scratch may change under the unchanged whole-slice modifies; input sentinels must not.
    input_frame(&v, left, right);
    input_covers_n3(a, b, c, probe);
}

// Fixed-N2 proofs: separate uncontracted covers, without unreachable N0/N1/N3 goals.
fn input_covers_n2(a: u8, b: u8, probe: u8) {
    kani::cover(true, "wonetwo N2 returns");
    kani::cover((a >> 1) > (b >> 1), "wonetwo N2 reversed keys return");
    kani::cover((a >> 1) < (b >> 1), "wonetwo N2 increasing keys return");
    kani::cover(a != b && (a >> 1) == (b >> 1), "wonetwo N2 tied distinct values");
    kani::cover(a == b, "wonetwo N2 duplicate full values");
    kani::cover(probe == a, "wonetwo N2 independent probe hits input");
    kani::cover(probe != a && probe != b, "wonetwo N2 independent probe misses input");
}

#[kani::proof_for_contract(unstable_byte_len)]
#[kani::unwind(16)]
fn unstable_byte_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, right];
    // SAFETY: initialized offset1/len2 in backing4, canonical pointer.
    unsafe { unstable_byte_len(v.as_mut_ptr().wrapping_add(1), 2, byte_less, probe) };
    input_frame(&v, left, right);
    input_covers_n2(a, b, probe);
}

#[kani::proof_for_contract(freeze_noncopy_len)]
#[kani::unwind(16)]
fn freeze_noncopy_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [NonCopyU8(left), NonCopyU8(a), NonCopyU8(b), NonCopyU8(right)];
    // SAFETY: initialized offset1/len2 in backing4, canonical pointer; internal scratch48.
    unsafe { freeze_noncopy_len(v.as_mut_ptr().wrapping_add(1), 2, noncopy_less, probe) };
    input_frame(&v, left, right);
    input_covers_n2(a, b, probe);
}

#[kani::proof_for_contract(stable_byte_len)]
#[kani::unwind(16)]
fn stable_byte_n2() {
    let [left, a, b, right]: [u8; 4] = kani::any();
    let probe: u8 = kani::any();
    let mut v = [left, a, b, right];
    let mut scratch = [MaybeUninit::uninit(); 48];
    // SAFETY: initialized offset1/len2 in backing4, separate full scratch48, canonical pointer.
    unsafe { stable_byte_len(v.as_mut_ptr().wrapping_add(1), 2, &mut scratch, byte_less, probe) };
    // Scratch may change under the unchanged whole-slice modifies; input sentinels must not.
    input_frame(&v, left, right);
    input_covers_n2(a, b, probe);
}
