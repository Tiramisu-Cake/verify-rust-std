//! K1-merge agent: contracts and harnesses for `merge_up`/`merge_down`/`bidirectional_merge`,
//! `sort4_stable`, `sort8_stable`, `insert_tail` and `small_sort_general_with_scratch`.
//! Written from the std source and the Kani documentation only (EXPERIMENT.md, rule R1).
//!
//! Specification helpers. The contract attributes in `smallsort.rs` cannot name this private module,
//! so the helpers are inherent associated functions of `smallsort::CopyOnDrop<T>`, which the parent
//! module can name: `CopyOnDrop::<T>::k1_sorted(..)` and so on.
//!
//! Permutation ("same multiset of full element values") is stated with a probe value: a global
//! byte buffer that a harness sets to an arbitrary value before it calls anything. Every contract
//! says that the number of elements bytewise equal to the probe is preserved. Proof harnesses pick
//! the probe nondeterministically, so a passing proof covers every probe value, which is exactly
//! multiset equality. Under `stub_verified` the same probe is in effect for every stub and for the
//! final assertion of the top harness, so the composition is sound. Bytewise equality is full value
//! equality for the element types of K-1 (integers and `[u8; N]`, no padding). The count is a
//! `usize`, so `old()` never has to clone a `T` (EXPERIMENT.md §7, risk "old() и T: Clone").
//!
//! Sortedness is stated with the comparator itself. Contract clauses are `Fn` closures while
//! `is_less` is `&mut F` with `F: FnMut`, so the helpers call it through a shared reference to the
//! `&mut F` argument; this is sound for the harness comparators below, which are stateless
//! function items. `is_less` being a strict weak order is not expressible for a generic `F`; every
//! proof is instantiated with these concrete strict orders, and stubs are used only with the same
//! `(T, F)` instantiations.

#![allow(dead_code)]

use super::super::{CopyOnDrop, bidirectional_merge, insert_tail};
use crate::intrinsics::compare_bytes;
use crate::kani;
use crate::mem::{MaybeUninit, size_of};
use crate::ptr;
use crate::slice::sort::shared::FreezeMarker;

// ---------------------------------------------------------------------------------------------
// Probe for permutation counting.

const PROBE_BYTES: usize = 128;

#[repr(C, align(16))]
struct Probe([u8; PROBE_BYTES]);

static mut K1_PROBE: Probe = Probe([0; PROBE_BYTES]);

/// Sets the probe to an arbitrary value. Every harness calls this once, before anything else.
pub(crate) fn set_probe<T>() {
    assert!(size_of::<T>() <= PROBE_BYTES);
    let bytes: [u8; PROBE_BYTES] = kani::any();
    // SAFETY: single-threaded harness; no reference to the static is alive.
    unsafe { *ptr::addr_of_mut!(K1_PROBE) = Probe(bytes) };
}

/// `*p` is bytewise equal to the probe. `p` must be valid for reads of one initialized `T`.
#[inline(always)]
unsafe fn is_probe<T>(p: *const T) -> bool {
    // SAFETY: `p` is readable for `size_of::<T>()` bytes, the probe buffer is larger.
    unsafe {
        compare_bytes(p as *const u8, ptr::addr_of!(K1_PROBE) as *const u8, size_of::<T>()) == 0
    }
}

#[inline(always)]
fn call_less<T, F: FnMut(&T, &T) -> bool>(is_less: &&mut F, a: *const T, b: *const T) -> bool {
    let f = is_less as *const &mut F as *mut &mut F;
    // SAFETY: spec-only call of a stateless comparator; `a` and `b` are valid (callers' contract).
    unsafe { (*f)(&*a, &*b) }
}

impl<T> CopyOnDrop<T> {
    /// Number of elements of `base[..len]` equal to the probe.
    pub(crate) fn k1_count(base: *const T, len: usize) -> usize {
        let mut c = 0;
        let mut i = 0;
        while i < len {
            // SAFETY: callers pass a readable, initialized region of `len` elements.
            if unsafe { is_probe(base.add(i)) } {
                c += 1;
            }
            i += 1;
        }
        c
    }

    /// `base[..len]` is sorted: no element is less than its predecessor.
    pub(crate) fn k1_sorted<F: FnMut(&T, &T) -> bool>(
        base: *const T,
        len: usize,
        is_less: &&mut F,
    ) -> bool {
        let mut i = 1;
        while i < len {
            // SAFETY: callers pass a readable, initialized region of `len` elements.
            if call_less(is_less, unsafe { base.add(i) }, unsafe { base.add(i - 1) }) {
                return false;
            }
            i += 1;
        }
        true
    }

    /// `a[..n]` and `b[..m]` do not overlap.
    pub(crate) fn k1_disjoint(a: *const T, n: usize, b: *const T, m: usize) -> bool {
        !kani::mem::same_allocation(a, b) || {
            // SAFETY: same allocation was checked just above.
            let d = unsafe { b.offset_from(a) };
            d >= n as isize || -d >= m as isize
        }
    }

    // insert_tail

    /// Number of elements in `[begin, tail]`. Only meaningful under `k1_tail_region_ok`.
    pub(crate) fn k1_tail_len(begin: *const T, tail: *const T) -> usize {
        // SAFETY: under the requires, both pointers are in one allocation.
        (unsafe { tail.offset_from(begin) }) as usize + 1
    }

    /// `begin < tail`, both in one allocation, `[begin, tail]` valid for reads and writes.
    pub(crate) fn k1_tail_region_ok(begin: *mut T, tail: *mut T) -> bool {
        kani::mem::same_allocation(begin as *const T, tail as *const T)
            && (unsafe { tail.offset_from(begin) }) >= 1
            && kani::mem::can_write(ptr::slice_from_raw_parts_mut(
                begin,
                Self::k1_tail_len(begin, tail),
            ))
    }

    /// Requires of `insert_tail`: the region is valid and `[begin, tail)` is sorted. One clause,
    /// so that the pointer difference is taken only after the region check.
    pub(crate) fn k1_tail_pre<F: FnMut(&T, &T) -> bool>(
        begin: *mut T,
        tail: *mut T,
        is_less: &&mut F,
    ) -> bool {
        Self::k1_tail_region_ok(begin, tail)
            && Self::k1_sorted(begin, Self::k1_tail_len(begin, tail) - 1, is_less)
    }

    // bidirectional_merge

    /// `dst` is valid for `v.len()` writes and does not overlap `v`.
    pub(crate) fn k1_merge_dst_ok(v: &[T], dst: *mut T) -> bool {
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(dst, v.len()))
            && Self::k1_disjoint(v.as_ptr(), v.len(), dst as *const T, v.len())
    }

    /// `v[..len / 2]` and `v[len / 2..]` are sorted.
    pub(crate) fn k1_merge_halves_sorted<F: FnMut(&T, &T) -> bool>(
        v: &[T],
        is_less: &&mut F,
    ) -> bool {
        let len = v.len();
        let half = len / 2;
        Self::k1_sorted(v.as_ptr(), half, is_less)
            && Self::k1_sorted(v.as_ptr().wrapping_add(half), len - half, is_less)
    }
}

// ---------------------------------------------------------------------------------------------
// Comparators: strict orders by key, so that elements with equal keys but different full values
// exist and the permutation property is not implied by sortedness.

pub(crate) fn lt_i32(a: &i32, b: &i32) -> bool {
    (*a >> 1) < (*b >> 1)
}

pub(crate) fn lt_u64(a: &u64, b: &u64) -> bool {
    (*a >> 1) < (*b >> 1)
}

pub(crate) fn lt_b16(a: &[u8; 16], b: &[u8; 16]) -> bool {
    a[0] < b[0]
}

pub(crate) fn lt_b85(a: &[u8; 85], b: &[u8; 85]) -> bool {
    a[0] < b[0]
}

// ---------------------------------------------------------------------------------------------
// Harness bodies, one per concrete length so that every loop has a constant bound.

macro_rules! by_len {
    ($len:expr, $f:ident::<$t:ty>($cmp:expr), [$($n:literal)*]) => {
        match $len {
            $( $n => $f::<$t, _, $n>($cmp), )*
            _ => {}
        }
    };
}

fn bm_len<T: kani::Arbitrary + FreezeMarker, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut is_less: F,
) {
    set_probe::<T>();
    let v: [T; N] = kani::any();
    let mut dst = MaybeUninit::<[T; N]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut T, &mut is_less) };
    kani::cover(true, "bidirectional_merge: a length is reachable with requires satisfied");
}

fn insert_tail_len<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool, const N: usize>(mut is_less: F) {
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { insert_tail(base, base.add(N - 1), &mut is_less) };
    kani::cover(true, "insert_tail: a length is reachable with requires satisfied");
}

// ---------------------------------------------------------------------------------------------
// Phase 1 probe (diagnostic): old() and permutation, small lengths, plus the R11 control.

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
fn bm_u64_upto8() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 8);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 8, "len 8");
    by_len!(len, bm_len::<u64>(lt_u64), [2 3 4 5 6 7 8]);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
fn bm_u64_upto32() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 32);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 32, "len 32");
    by_len!(len, bm_len::<u64>(lt_u64),
        [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32]);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
fn insert_tail_u64_upto8() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 8);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 8, "len 8");
    by_len!(len, insert_tail_len::<u64>(lt_u64), [2 3 4 5 6 7 8]);
}

/// R11 control: the caller violates the "halves sorted" requires of a `stub_verified` callee.
/// Expected FAILED on the requires check `k1_merge_halves_sorted`.
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
fn r11_control_bm_requires() {
    set_probe::<u64>();
    // Keys (x >> 1) are [3, 0 | 1, 2]: the left half is not sorted.
    let v: [u64; 4] = [6, 0, 2, 4];
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    let mut is_less = lt_u64;
    // SAFETY: dst is a separate local of 4 elements; only the sortedness requires is violated.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut is_less) };
    kani::cover(true, "r11 control: call site reached");
}
