//! Contracts and bounded harnesses for merge, stable primitives, insertion tails and general sort.
//!
//! Specification helpers are inherent functions of `CopyOnDrop<T>` so the contract attributes in
//! the parent module can name them. An arbitrary global byte probe counts full element values for
//! integers and byte arrays without padding; preserving its multiplicity for every probe gives
//! multiset equality. A caller and its verified stubs share the same probe. Tagged Drop values
//! instead use fieldwise tag counts because their representations can contain padding.
//!
//! Sortedness helpers call the comparator through the contract's shared reference to `&mut F`.
//! Ordered harnesses instantiate stateless strict orders and use the same `(T, F)` in callees and
//! callers. This does not establish an ordering contract for arbitrary `FnMut` implementations.
//! Separate real-body harnesses allow arbitrary comparison results and check normal-return safety.

#![allow(dead_code)]

use crate::kani;
use crate::mem::{MaybeUninit, size_of};
use crate::ptr;
use crate::slice::sort::shared::FreezeMarker;
use super::super::{
    CopyOnDrop, SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl,
    UnstableSmallSortFreezeTypeImpl, UnstableSmallSortTypeImpl, bidirectional_merge, insert_tail,
    sort4_stable, sort8_stable,
};

// ---------------------------------------------------------------------------------------------
// Probe for permutation counting.

const PROBE_BYTES: usize = 128;

/// Largest region the loop-free helpers `k1_count_u`/`k1_sorted_u` handle.
const K1_UNROLL: usize = 32;

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
/// Loop-free: up to 16 guarded 8-byte words (`size_of::<T>() <= PROBE_BYTES`, checked in
/// `set_probe`) and a 4/2/1-byte tail. Avoiding nested specification loops limits instrumentation
/// size before constant propagation.
#[inline(always)]
unsafe fn is_probe<T>(p: *const T) -> bool {
    let a = p as *const u8;
    let n = size_of::<T>();
    let w = n / 8;
    let mut eq = true;
    // SAFETY: `p` is readable for `n` bytes and the probe buffer is larger than `n`; every read
    // below is guarded to lie in `0..n`.
    unsafe {
        let b = ptr::addr_of!(K1_PROBE) as *const u8;
        macro_rules! words {
            ($($j:literal)*) => {$(
                if $j < w {
                    let x = ptr::read_unaligned(a.add(8 * $j) as *const u64);
                    let y = ptr::read_unaligned(b.add(8 * $j) as *const u64);
                    eq &= x == y;
                }
            )*};
        }
        words!(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15);
        let mut i = 8 * w;
        if n - i >= 4 {
            eq &= ptr::read_unaligned(a.add(i) as *const u32)
                == ptr::read_unaligned(b.add(i) as *const u32);
            i += 4;
        }
        if n - i >= 2 {
            eq &= ptr::read_unaligned(a.add(i) as *const u16)
                == ptr::read_unaligned(b.add(i) as *const u16);
            i += 2;
        }
        if n - i >= 1 {
            eq &= *a.add(i) == *b.add(i);
        }
    }
    eq
}

/// Type-specialized probe test, so that a probe count
/// over 32 elements is 32 single tests instead of 32 x 19 guarded word compares. Integers: one
/// compare; `[u8; 16]`: two words; `[u8; 85]`: ten words and a 4/1-byte tail. Default: `is_probe`.
/// `p` must be valid for reads of one initialized element.
pub(crate) trait K1Probe: Sized {
    unsafe fn k1_probe(p: *const Self) -> bool;
}

impl<T> K1Probe for T {
    #[inline(always)]
    default unsafe fn k1_probe(p: *const T) -> bool {
        // SAFETY: forwarded from the caller.
        unsafe { is_probe(p) }
    }
}

macro_rules! k1_probe_int {
    ($($t:ty)*) => {$(
        impl K1Probe for $t {
            #[inline(always)]
            unsafe fn k1_probe(p: *const $t) -> bool {
                // SAFETY: `p` is an aligned readable element (caller); the probe buffer is
                // 16-aligned and larger than the integer. Plain loads, no `read_unaligned`: its
                // library body and UB checks would be inlined with the specification.
                unsafe { *p == *(ptr::addr_of!(K1_PROBE) as *const $t) }
            }
        }
    )*};
}
k1_probe_int!(u8 i8 u16 i16 u32 i32 u64 i64);

/// The `W`-sized word at byte offset `at` of the element at `a` equals the same word of the probe.
#[inline(always)]
unsafe fn k1_probe_word<W: PartialEq + Copy>(a: *const u8, at: usize) -> bool {
    // SAFETY: callers keep `at + size_of::<W>()` within the element and the probe buffer.
    unsafe {
        let b = ptr::addr_of!(K1_PROBE) as *const u8;
        ptr::read_unaligned(a.add(at) as *const W) == ptr::read_unaligned(b.add(at) as *const W)
    }
}

impl K1Probe for [u8; 16] {
    #[inline(always)]
    unsafe fn k1_probe(p: *const [u8; 16]) -> bool {
        let a = p as *const u8;
        // SAFETY: words 0..2 lie within the 16-byte element.
        unsafe { k1_probe_word::<u64>(a, 0) && k1_probe_word::<u64>(a, 8) }
    }
}

impl K1Probe for [u8; 85] {
    #[inline(always)]
    unsafe fn k1_probe(p: *const [u8; 85]) -> bool {
        let a = p as *const u8;
        // SAFETY: ten 8-byte words, a 4-byte and a 1-byte tail cover bytes 0..85 of the element.
        unsafe {
            k1_probe_word::<u64>(a, 0)
                && k1_probe_word::<u64>(a, 8)
                && k1_probe_word::<u64>(a, 16)
                && k1_probe_word::<u64>(a, 24)
                && k1_probe_word::<u64>(a, 32)
                && k1_probe_word::<u64>(a, 40)
                && k1_probe_word::<u64>(a, 48)
                && k1_probe_word::<u64>(a, 56)
                && k1_probe_word::<u64>(a, 64)
                && k1_probe_word::<u64>(a, 72)
                && k1_probe_word::<u32>(a, 80)
                && k1_probe_word::<u8>(a, 84)
        }
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

    /// `k1_count` without a loop, for `len <= K1_UNROLL` (callers check the bound).
    /// Explicit guarded tests bound specification instrumentation to the small-sort threshold.
    pub(crate) fn k1_count_u(base: *const T, len: usize) -> usize {
        let mut c = 0;
        macro_rules! step {
            ($($i:literal)*) => {$(
                // SAFETY: `$i < len`, callers pass a readable region of `len` elements.
                if $i < len && unsafe { is_probe(base.add($i)) } {
                    c += 1;
                }
            )*};
        }
        step!(
            0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        );
        c
    }

    /// `k1_sorted` without a loop, for `len <= K1_UNROLL` (callers check the bound).
    pub(crate) fn k1_sorted_u<F: FnMut(&T, &T) -> bool>(
        base: *const T,
        len: usize,
        is_less: &&mut F,
    ) -> bool {
        let mut ok = true;
        macro_rules! step {
            ($($i:literal)*) => {$(
                // SAFETY: `$i < len`, callers pass a readable region of `len` elements.
                if $i < len
                    && call_less(is_less, unsafe { base.add($i) }, unsafe { base.add($i - 1) })
                {
                    ok = false;
                }
            )*};
        }
        step!(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
        ok
    }

    /// `k1_sorted` as one quantifier over the constant range `1..K1_UNROLL` (the SAT backend of the
    /// configured backend requires constant bounds), guarded by `i < len`. For `len <= K1_UNROLL`.
    /// Retained as an alternative specification; the active merge contract uses `k1_sorted_u`.
    pub(crate) fn k1_sorted_q<F: FnMut(&T, &T) -> bool>(
        base: *const T,
        len: usize,
        is_less: &&mut F,
    ) -> bool {
        crate::forall!(|i in (1, K1_UNROLL)| i >= len
            || !call_less(is_less, base.wrapping_add(i), base.wrapping_add(i - 1)))
    }

    /// Light probe count of `base[..len]`, `len <= K1_UNROLL`: 32 guarded `K1Probe` tests.
    pub(crate) fn k1_count_l(base: *const T, len: usize) -> usize {
        let mut c = 0;
        macro_rules! step {
            ($($i:literal)*) => {$(
                // SAFETY: `$i < len`, callers pass a readable region of `len` elements.
                if $i < len && unsafe { <T as K1Probe>::k1_probe(base.wrapping_add($i)) } {
                    c += 1;
                }
            )*};
        }
        step!(
            0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        );
        c
    }

    /// Permutation by the light probe count: `a[..len]` and `b[..len]` hold equally many probes.
    /// For `len <= K1_UNROLL`.
    pub(crate) fn k1_perm_l(a: *const T, b: *const T, len: usize) -> bool {
        Self::k1_count_l(a, len) == Self::k1_count_l(b, len)
    }

    /// Alternative quantified sortedness of two halves, bounded to 32 elements.
    pub(crate) fn k1_merge_halves_sorted_q<F: FnMut(&T, &T) -> bool>(
        v: &[T],
        is_less: &&mut F,
    ) -> bool {
        let len = v.len();
        let half = len / 2;
        len <= K1_UNROLL
            && Self::k1_sorted_q(v.as_ptr(), half, is_less)
            && Self::k1_sorted_q(v.as_ptr().wrapping_add(half), len - half, is_less)
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
        // SAFETY: same-allocation is checked before the pointer difference; the instantiated
        // element types are nonzero-sized. The write predicate checks the resulting region.
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

    /// `p[..n]` is valid for reads and writes. Every caller of the sort primitives passes writable
    /// memory as the source too (it comes from `&mut [T]`), so writability is required for reads.
    pub(crate) fn k1_region_ok(p: *const T, n: usize) -> bool {
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(p as *mut T, n))
    }

    // sort4_stable / sort8_stable

    pub(crate) fn k1_sort4_pre(v_base: *const T, dst: *mut T) -> bool {
        Self::k1_region_ok(v_base, 4)
            && Self::k1_region_ok(dst, 4)
            && Self::k1_disjoint(v_base, 4, dst, 4)
    }

    pub(crate) fn k1_sort8_pre(v_base: *mut T, dst: *mut T, scratch_base: *mut T) -> bool {
        Self::k1_region_ok(v_base, 8)
            && Self::k1_region_ok(dst, 8)
            && Self::k1_region_ok(scratch_base, 8)
            && Self::k1_disjoint(v_base, 8, dst, 8)
            && Self::k1_disjoint(v_base, 8, scratch_base, 8)
            && Self::k1_disjoint(dst, 8, scratch_base, 8)
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
        len <= K1_UNROLL
            && Self::k1_sorted_u(v.as_ptr(), half, is_less)
            && Self::k1_sorted_u(v.as_ptr().wrapping_add(half), len - half, is_less)
    }
}

// ---------------------------------------------------------------------------------------------
// Comparators: strict orders by key, so that elements with equal keys but different full values
// exist and the permutation property is not implied by sortedness.

/// Network key order; the low bit remains part of the full-value permutation property.
pub(crate) fn lt_u8(a: &u8, b: &u8) -> bool {
    (*a >> 1) < (*b >> 1)
}

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

pub(crate) fn bm_len<T: kani::Arbitrary + FreezeMarker, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut is_less: F,
) {
    set_probe::<T>();
    let v: [T; N] = kani::any();
    let mut dst = MaybeUninit::<[T; N]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut T, &mut is_less) };
    kani::cover(true, "bidirectional_merge: a length is reachable with requires satisfied");
}

pub(crate) fn insert_tail_len<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut is_less: F,
) {
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { insert_tail(base, base.add(N - 1), &mut is_less) };
    kani::cover(true, "insert_tail: a length is reachable with requires satisfied");
}

/// Negative precondition control: u64 length 4 violates the verified merge's sorted-halves clause.
/// Expected FAILED on the requires check `k1_merge_halves_sorted`.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
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
// ---------------------------------------------------------------------------------------------
// Contract proofs on the whole domain reachable from small_sort_general (len <= 32, scratch 48),
// for every (T, F) instantiation that the top harnesses below stub.

fn sort4_body<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool>(mut is_less: F) {
    set_probe::<T>();
    let v: [T; 4] = kani::any();
    let mut dst = MaybeUninit::<[T; 4]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { sort4_stable(v.as_ptr(), dst.as_mut_ptr() as *mut T, &mut is_less) };
    kani::cover(true, "sort4_stable: reachable with requires satisfied");
}

fn sort8_body<T: kani::Arbitrary + FreezeMarker, F: FnMut(&T, &T) -> bool>(mut is_less: F) {
    set_probe::<T>();
    let mut v: [T; 8] = kani::any();
    let mut dst = MaybeUninit::<[T; 8]>::uninit();
    let mut scratch = MaybeUninit::<[T; 8]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe {
        sort8_stable(
            v.as_mut_ptr(),
            dst.as_mut_ptr() as *mut T,
            scratch.as_mut_ptr() as *mut T,
            &mut is_less,
        )
    };
    kani::cover(true, "sort8_stable: reachable with requires satisfied");
}

/// sort4_stable for all four general element types (direct, no stubs).
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_all() {
    let t: u8 = kani::any_where(|t: &u8| *t < 4);
    kani::cover(t == 3, "type selector: last type reachable");
    match t {
        0 => sort4_body::<i32, _>(lt_i32),
        1 => sort4_body::<u64, _>(lt_u64),
        2 => sort4_body::<[u8; 16], _>(lt_b16),
        _ => sort4_body::<[u8; 85], _>(lt_b85),
    }
}

/// sort8_stable for the three types with size <= 16 (direct, no stubs).
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort8_stable)]
#[kani::unwind(34)]
fn sort8_all() {
    let t: u8 = kani::any_where(|t: &u8| *t < 3);
    kani::cover(t == 2, "type selector: last type reachable");
    match t {
        0 => sort8_body::<i32, _>(lt_i32),
        1 => sort8_body::<u64, _>(lt_u64),
        _ => sort8_body::<[u8; 16], _>(lt_b16),
    }
}

// Direct four-element contract instances for i32 and byte arrays of widths 16 and 85.

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_i32() {
    sort4_body::<i32, _>(lt_i32);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_b16() {
    sort4_body::<[u8; 16], _>(lt_b16);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_b85() {
    sort4_body::<[u8; 85], _>(lt_b85);
}

// The four-element contract promises sortedness unconditionally, so its
// proof uses a strict comparator. The separate ordinary proof permits arbitrary
// comparison results and checks safety and full-value permutation of the real body.
fn w3_sort4_read_args<T: Copy>(a: &T, b: &T) {
    // SAFETY: both references must point to initialized readable elements.
    // Volatile accesses retain every byte read even when the result is arbitrary.
    unsafe {
        ptr::read_volatile(a);
        ptr::read_volatile(b);
    }
}

fn w3_sort4_arbitrary<T: kani::Arbitrary + Copy>() {
    set_probe::<T>();
    let v: [T; 4] = kani::any();
    let mut dst = MaybeUninit::<[T; 4]>::uninit();
    let mut cmp = |a: &T, b: &T| {
        w3_sort4_read_args(a, b);
        kani::any()
    };
    // SAFETY: two disjoint exact four-element allocations, initialized source;
    // sort4_stable's SAFETY precondition does not require an ordered comparator.
    unsafe { sort4_stable(v.as_ptr(), dst.as_mut_ptr() as *mut T, &mut cmp) };
    assert!(
        CopyOnDrop::<T>::k1_count(v.as_ptr(), 4)
            == CopyOnDrop::<T>::k1_count(dst.as_ptr() as *const T, 4)
    );
    kani::cover(true, "W3 L1-3: arbitrary comparator normal return and permutation");
}

macro_rules! w3_sort4_cases {
    ($contract:ident, $arbitrary:ident, $t:ty, $ordered:ident) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
        #[kani::unwind(34)]
        fn $contract() {
            sort4_body::<$t, _>(|a, b| {
                w3_sort4_read_args(a, b);
                $ordered(a, b)
            });
        }

        #[kani::proof]
        #[kani::unwind(34)]
        fn $arbitrary() {
            w3_sort4_arbitrary::<$t>();
        }
    };
}

w3_sort4_cases!(w3_sort4_contract_u64, w3_sort4_arbitrary_u64, u64, lt_u64);
w3_sort4_cases!(w3_sort4_contract_b16, w3_sort4_arbitrary_b16, [u8; 16], lt_b16);
#[cfg(kani_smallsort_controls)]
w3_sort4_cases!(w3_sort4_contract_b85, w3_sort4_arbitrary_b85, [u8; 85], lt_b85);

// Eight-element stable sort contract composed from matching sort4 and merge contracts.
macro_rules! sort8_harness {
    ($name:ident, $t:ty, $cmp:expr) => {
        /// sort8_stable with its two callees replaced by their verified contracts.
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort8_stable)]
        #[kani::unwind(34)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::sort4_stable)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        fn $name() {
            sort8_body::<$t, _>($cmp);
        }
    };
}

#[cfg(kani_smallsort_controls)]
sort8_harness!(sort8_i32, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
sort8_harness!(sort8_u64, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
sort8_harness!(sort8_b16, [u8; 16], lt_b16);

/// insert_tail on regions of 2..=16 elements (general inserts up to index 15 of a half).
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(34)]
fn insert_tail_int() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 16);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 16, "len 16");
    if kani::any() {
        by_len!(len, insert_tail_len::<i32>(lt_i32), [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]);
    } else {
        by_len!(len, insert_tail_len::<u64>(lt_u64), [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]);
    }
}

/// Byte-array widths 16/85, exact regions 2..=16, ordered prefix supplied by the tail contract.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(34)]
fn insert_tail_bytes() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 16);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 16, "len 16");
    if kani::any() {
        by_len!(len, insert_tail_len::<[u8; 16]>(lt_b16), [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]);
    } else {
        by_len!(len, insert_tail_len::<[u8; 85]>(lt_b85), [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]);
    }
}

// Type-specific merge contracts over exact lengths 2..=32 and disjoint destination arrays.
macro_rules! bm_harness {
    ($name:ident, $t:ty, $cmp:expr) => {
        /// bidirectional_merge on 2..=32 elements.
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 32);
            kani::cover(len == 2, "len 2");
            kani::cover(len == 32, "len 32");
            by_len!(len, bm_len::<$t>($cmp), [
                2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32
            ]);
        }
    };
}

#[cfg(kani_smallsort_controls)]
bm_harness!(bm_u8, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
bm_harness!(bm_i32, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
bm_harness!(bm_u64, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
bm_harness!(bm_b16, [u8; 16], lt_b16);
#[cfg(kani_smallsort_controls)]
bm_harness!(bm_b85, [u8; 85], lt_b85);

// ---------------------------------------------------------------------------------------------
// Top harnesses: real trait entrypoints, every length 0..=32, callees replaced by their verified
// contracts. Checks: enabled Kani safety properties, sortedness and full-value permutation.
// Uninitialized-memory and aliasing-model limitations are disclosed in the PR description.

fn check_sorted_perm<T, F: FnMut(&T, &T) -> bool>(orig: &[T], out: &[T], is_less: &mut F) {
    let mut i = 1;
    while i < out.len() {
        assert!(!is_less(&out[i], &out[i - 1]), "K-1 general: output is sorted");
        i += 1;
    }
    assert!(
        CopyOnDrop::<T>::k1_count(orig.as_ptr(), orig.len())
            == CopyOnDrop::<T>::k1_count(out.as_ptr(), out.len()),
        "K-1 general: output is a permutation of the input"
    );
    kani::cover(true, "K-1 general: end of a length reached");
}

fn general_stable_len<
    T: kani::Arbitrary + Copy + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut is_less: F,
) {
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    let mut scratch = [MaybeUninit::<T>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut is_less);
    check_sorted_perm(&orig, &v, &mut is_less);
}

fn general_unstable_len<
    T: kani::Arbitrary + Copy + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut is_less: F,
) {
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    <T as UnstableSmallSortFreezeTypeImpl>::small_sort(&mut v, &mut is_less);
    check_sorted_perm(&orig, &v, &mut is_less);
}

macro_rules! general_covers {
    ($len:expr) => {
        kani::cover($len == 0, "len 0");
        kani::cover($len == 1, "len 1");
        kani::cover($len == 2, "len 2");
        kani::cover($len == 7, "len 7: last length without presort");
        kani::cover($len == 8, "len 8: presort by 4");
        kani::cover($len == 15, "len 15: last length with presort by 4");
        kani::cover($len == 16, "len 16: presort by 8 when size_of::<T>() <= 16");
        kani::cover($len == 32, "len 32");
    };
}

macro_rules! general_harness {
    ($name:ident, $body:ident, $t:ty, $cmp:expr) => {
        #[kani::proof]
        #[kani::unwind(34)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::sort4_stable)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::sort8_stable)]
        fn $name() {
            let len: usize = kani::any_where(|l: &usize| *l <= 32);
            general_covers!(len);
            by_len!(len, $body::<$t>($cmp), [
                0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28
                29 30 31 32
            ]);
        }
    };
}

#[cfg(kani_smallsort_controls)]
general_harness!(general_i32, general_stable_len, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
general_harness!(general_u64, general_stable_len, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
general_harness!(general_b16, general_unstable_len, [u8; 16], lt_b16);
#[cfg(kani_smallsort_controls)]
general_harness!(general_b85, general_unstable_len, [u8; 85], lt_b85);

/// One band of lengths `[$($n)*]` of a top harness. The family of bands of one type covers every
/// length 0..=32. Explicit covers in `[$($c)*]` witness the selected routing boundaries.
/// Contract stubs assume the matching type, comparator and allocation prerequisites.
macro_rules! general_band {
    ($name:ident, $body:ident, $t:ty, $cmp:expr, [$($n:literal)*], covers [$($c:literal)*]) => {
        #[kani::proof]
        #[kani::unwind(34)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::insert_tail)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::sort4_stable)]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::sort8_stable)]
        fn $name() {
            let len: usize = kani::any_where(|l: &usize| $(*l == $n)||*);
            $( kani::cover(len == $c, concat!("len ", stringify!($c))); )*
            by_len!(len, $body::<$t>($cmp), [$($n)*]);
        }
    };
}

// Single-length probe of the composition cost (diagnostic).
#[cfg(kani_smallsort_controls)]
general_band!(general_u64_len32, general_stable_len, u64, lt_u64, [32], covers [32]);

// ---------------------------------------------------------------------------------------------
// Real-body safety harnesses use no verified-contract stubs. The manual panic boundary cuts
// order-violation panic paths under abort semantics; it makes no claim about unwinding.

fn w1_arbitrary_less(a: &u64, b: &u64) -> bool {
    // SAFETY: callers pass initialized references; volatile reads keep both accesses observable
    // even though the result is arbitrary. Forming a reference alone need not exercise a read.
    unsafe {
        ptr::read_volatile(a);
        ptr::read_volatile(b);
    }
    kani::any()
}

fn w1_abort_ord_violation() -> ! {
    kani::cover(true, "wave1: panic_on_ord_violation is reachable");
    kani::assume(false);
    unreachable!()
}

/// Four-element u64 negative control: check real-merge permutation, then fail on normal return.
/// Arbitrary comparisons read both arguments; only the order-violation panic path is cut.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, w1_abort_ord_violation)]
#[kani::unwind(6)]
fn w1_control_a_must_fail() {
    let v: [u64; 4] = kani::any();
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source, separate destination for four writes, len >= 2.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut w1_arbitrary_less);
        let out = dst.assume_init();
        kani::cover(true, "wave1 A mutant: normal return reached");
        for value in v {
            let before = v.iter().filter(|x| **x == value).count();
            let after = out.iter().filter(|x| **x == value).count();
            assert!(before == after, "wave1 A permutation");
        }
    }
    assert!(v[0] != v[0]);
}

/// Four-element u64 positive control with normal-return and panic-boundary reachability.
/// Exact multiset equality is checked only on normal returns, with the real merge body.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, w1_abort_ord_violation)]
#[kani::unwind(6)]
fn w1_control_a_panic_reachable() {
    let v: [u64; 4] = kani::any();
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source, separate destination for four writes, len >= 2.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut w1_arbitrary_less);
        let out = dst.assume_init();
        for value in v {
            let before = v.iter().filter(|x| **x == value).count();
            let after = out.iter().filter(|x| **x == value).count();
            assert!(before == after, "wave1 A permutation");
        }
    }
    kani::cover(true, "wave1 A: normal return and permutation checked");
}

// Real merge safety on exact u64 arrays of 2..=32 elements with arbitrary comparisons.
// No sortedness premise is imposed; normal-return covers check that the panic cut is nonvacuous.
fn w1_merge_safety<const N: usize>() {
    const { assert!(N >= 2 && N <= 32) };
    let v: [u64; N] = kani::any();
    let mut dst = MaybeUninit::<[u64; N]>::uninit();
    // SAFETY: each harness uses N >= 2; v is initialized, dst is separate and
    // valid for N writes. Safety does not require ordered halves or comparator.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut w1_arbitrary_less);
    }
    kani::cover(true, "wave1 merge O1: normal return reachable");
}

// u64 selects the network through the unstable trait. A transparent non-Copy wrapper also
// exercises the general trait route; stable Freeze sorting selects general directly for u64.
#[repr(transparent)]
struct W1GeneralU64(u64);

fn w1_general_arbitrary_less(a: &W1GeneralU64, b: &W1GeneralU64) -> bool {
    // SAFETY: both initialized transparent payloads are readable; no Drop value is copied.
    unsafe {
        ptr::read_volatile(&a.0);
        ptr::read_volatile(&b.0);
    }
    kani::any()
}

fn w1_general_u64_safety<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    super::super::small_sort_general(&mut v, &mut w1_arbitrary_less);
    kani::cover(true, "wave1 general u64 direct: normal return reachable");
}

fn w1_general_trait_safety<const N: usize>() {
    let payload: [u64; N] = kani::any();
    let mut v = payload.map(W1GeneralU64);
    <W1GeneralU64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut w1_general_arbitrary_less);
    kani::cover(true, "wave1 general non-Copy u64 trait: normal return reachable");
}

fn w1_stable_u64_safety<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut w1_arbitrary_less);
    kani::cover(true, "wave1 stable-Freeze u64 trait: normal return reachable");
}

// Every exact length 2..=32 selects direct general u64, non-Copy unstable general, or stable
// Freeze sorting. Each route has a normal-return cover and uses real callees with scratch 48.
fn w1_upper_routes_safety<const N: usize>() {
    let route: u8 = kani::any();
    match route {
        0 => w1_general_u64_safety::<N>(),
        1 => w1_general_trait_safety::<N>(),
        _ => w1_stable_u64_safety::<N>(),
    }
}

// Sensitivity controls start with an honest ordered four-element merge, then perform one
// deliberately invalid operation. They expect a localized Kani safety failure after normal return.
#[cfg(kani_smallsort_controls)]
fn w2_c5_normal_merge() -> [u64; 4] {
    let v = [0u64, 1, 2, 3];
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source and separate destination, both exactly four
    // elements; honest comparison on two ordered halves.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut |a, b| a < b);
        let out = dst.assume_init();
        kani::cover(true, "wave2 C5: normal merge return before check");
        out
    }
}

// No assertion masking is used for these deliberate safety violations.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn w2_c5_intrinsic_assume() {
    let v = w2_c5_normal_merge();
    // Deliberately violate the intrinsic's precondition after the real merge returns.
    unsafe {
        let first = ptr::read_volatile(&v[0]);
        crate::intrinsics::assume(first != 0);
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn w2_c5_unchecked_add() {
    let _v = w2_c5_normal_merge();
    // Deliberate overflow; volatile input/output retain the operation.
    unsafe {
        let max = ptr::read_volatile(&u8::MAX);
        let mut result = 0u8;
        ptr::write_volatile(&mut result, max.unchecked_add(1));
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn w2_c5_copy_nonoverlapping() {
    let mut v = w2_c5_normal_merge();
    // Deliberate overlap: both regions are within this four-element
    // allocation and aligned, but share elements 1 and 2.
    unsafe {
        let p = v.as_mut_ptr();
        ptr::copy_nonoverlapping(p, p.add(1), 3);
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn w2_c5_ptr_add() {
    let v = w2_c5_normal_merge();
    // Deliberate offset beyond one-past. Only the pointer value is
    // written into a valid local slot; it is never dereferenced.
    unsafe {
        let mut result = ptr::null::<u64>();
        ptr::write_volatile(&mut result, v.as_ptr().add(5));
    }
}

// Paired four-element u64 controls use the real merge and the order-violation panic cut.
// The negative member adds a false assertion; the positive member witnesses normal return.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, w1_abort_ord_violation)]
#[kani::unwind(6)]
fn w2_control_a_assertion() {
    w1_merge_safety::<4>();
    let value: u64 = kani::any();
    assert!(value != value);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, w1_abort_ord_violation)]
#[kani::unwind(6)]
fn w2_control_a_reachable() {
    w1_merge_safety::<4>();
}

macro_rules! w2_top_safety_a {
    ($name:ident, $body:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub(
            crate::slice::sort::shared::smallsort::panic_on_ord_violation,
            w1_abort_ord_violation
        )]
        #[kani::unwind(34)]
        fn $name() {
            $body::<$n>();
        }
    };
}

w2_top_safety_a!(w2_a_merge_u64_len32_safety, w1_merge_safety, 32);
w2_top_safety_a!(w2_a_all_len2_safety, w1_upper_routes_safety, 2);
w2_top_safety_a!(w2_a_all_len3_safety, w1_upper_routes_safety, 3);
w2_top_safety_a!(w2_a_all_len4_safety, w1_upper_routes_safety, 4);
w2_top_safety_a!(w2_a_all_len5_safety, w1_upper_routes_safety, 5);
w2_top_safety_a!(w2_a_all_len6_safety, w1_upper_routes_safety, 6);
w2_top_safety_a!(w2_a_all_len7_safety, w1_upper_routes_safety, 7);
w2_top_safety_a!(w2_a_all_len8_safety, w1_upper_routes_safety, 8);
w2_top_safety_a!(w2_a_all_len9_safety, w1_upper_routes_safety, 9);
w2_top_safety_a!(w2_a_all_len10_safety, w1_upper_routes_safety, 10);
w2_top_safety_a!(w2_a_all_len11_safety, w1_upper_routes_safety, 11);
w2_top_safety_a!(w2_a_all_len12_safety, w1_upper_routes_safety, 12);
w2_top_safety_a!(w2_a_all_len13_safety, w1_upper_routes_safety, 13);
w2_top_safety_a!(w2_a_all_len14_safety, w1_upper_routes_safety, 14);
w2_top_safety_a!(w2_a_all_len15_safety, w1_upper_routes_safety, 15);
w2_top_safety_a!(w2_a_all_len16_safety, w1_upper_routes_safety, 16);
w2_top_safety_a!(w2_a_all_len17_safety, w1_upper_routes_safety, 17);
w2_top_safety_a!(w2_a_all_len18_safety, w1_upper_routes_safety, 18);
w2_top_safety_a!(w2_a_all_len19_safety, w1_upper_routes_safety, 19);
w2_top_safety_a!(w2_a_all_len20_safety, w1_upper_routes_safety, 20);
w2_top_safety_a!(w2_a_all_len21_safety, w1_upper_routes_safety, 21);
w2_top_safety_a!(w2_a_all_len22_safety, w1_upper_routes_safety, 22);
w2_top_safety_a!(w2_a_all_len23_safety, w1_upper_routes_safety, 23);
w2_top_safety_a!(w2_a_all_len24_safety, w1_upper_routes_safety, 24);
w2_top_safety_a!(w2_a_all_len25_safety, w1_upper_routes_safety, 25);
w2_top_safety_a!(w2_a_all_len26_safety, w1_upper_routes_safety, 26);
w2_top_safety_a!(w2_a_all_len27_safety, w1_upper_routes_safety, 27);
w2_top_safety_a!(w2_a_all_len28_safety, w1_upper_routes_safety, 28);
w2_top_safety_a!(w2_a_all_len29_safety, w1_upper_routes_safety, 29);
w2_top_safety_a!(w2_a_all_len30_safety, w1_upper_routes_safety, 30);
w2_top_safety_a!(w2_a_all_len31_safety, w1_upper_routes_safety, 31);
w2_top_safety_a!(w2_a_all_len32_safety, w1_upper_routes_safety, 32);

// Bounded merge correctness for u8/u64 under the strict key order x >> 1. Values remain fully
// symbolic, including equal-key payloads. Exact allocations keep each proof's geometry explicit:
// grouped lengths 2..=4 and fixed lengths 5..=16, with optional u8 diagnostics at 20 and 24.
macro_rules! w2p2_bm_small {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            let len: u8 = kani::any_where(|n: &u8| *n >= 2 && *n <= 4);
            match len {
                2 => {
                    bm_len::<$t, _, 2>($cmp);
                    kani::cover(true, "wave2 P2 merge contract: len 2");
                }
                3 => {
                    bm_len::<$t, _, 3>($cmp);
                    kani::cover(true, "wave2 P2 merge contract: len 3");
                }
                4 => {
                    bm_len::<$t, _, 4>($cmp);
                    kani::cover(true, "wave2 P2 merge contract: len 4");
                }
                _ => {}
            }
        }
    };
}

w2p2_bm_small!(w2p2_bm_u64_len2to4, u64, lt_u64);
w2p2_bm_small!(w2p2_bm_u8_len2to4, u8, lt_u8);

macro_rules! w2p2_bm_fixed {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            bm_len::<$t, _, $n>($cmp);
        }
    };
}

macro_rules! w2p2_r11 {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            set_probe::<$t>();
            let v: [$t; 4] = [6, 0, 2, 4];
            let mut dst = MaybeUninit::<[$t; 4]>::uninit();
            let mut cmp = $cmp;
            kani::cover(true, "wave2 P2 R11: call before violated sorted-half requires");
            // Negative precondition control: all memory conditions hold,
            // but the first two keys [3, 0] are not sorted.
            unsafe {
                bidirectional_merge(&v, dst.as_mut_ptr() as *mut $t, &mut cmp);
            }
        }
    };
}

#[cfg(kani_smallsort_controls)]
w2p2_r11!(w2p2_r11_u64, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
w2p2_r11!(w2p2_r11_u8, u8, lt_u8);

fn w2p2_check_sorted_perm<T, F: FnMut(&T, &T) -> bool, const N: usize>(
    orig: &[T; N],
    out: &[T; N],
    cmp: &mut F,
) {
    for i in 1..N {
        assert!(!cmp(&out[i], &out[i - 1]), "wave2 P2: output sorted");
    }
    assert!(
        CopyOnDrop::<T>::k1_count_u(orig.as_ptr(), N)
            == CopyOnDrop::<T>::k1_count_u(out.as_ptr(), N),
        "wave2 P2: full-value probe multiplicity preserved"
    );
}

// General/stable correctness uses scratch 48 and exact u8/u64 lengths up to 16. Only merge
// is stubbed here; the insertion, sort4 and sort8 bodies remain real. The ordinary instances
// cover u64 0..=12 and 16, and u8 0..=13 and 16; other instances remain optional controls.
fn w2p2_general_stable_len<
    T: kani::Arbitrary + Copy + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut cmp: F,
) {
    const { assert!(N <= 16) };
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    let stable: bool = kani::any();
    if stable {
        let mut scratch = [MaybeUninit::<T>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    } else {
        super::super::small_sort_general(&mut v, &mut cmp);
    }
    w2p2_check_sorted_perm::<T, _, N>(&orig, &v, &mut cmp);
    kani::cover(!stable, "wave2 P2: direct general properties checked");
    kani::cover(stable, "wave2 P2: stable-Freeze properties checked");
}

// Direct fallback correctness on exact u8/u64 arrays up to 16; every insertion body is real.
fn w2p2_fallback_len<T: kani::Arbitrary + Copy, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut cmp: F,
) {
    const { assert!(N <= 16) };
    set_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    super::super::small_sort_fallback(&mut v, &mut cmp);
    w2p2_check_sorted_perm::<T, _, N>(&orig, &v, &mut cmp);
    kani::cover(true, "wave2 P2: fallback properties checked");
}

macro_rules! w2p2_general_fixed {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            w2p2_general_stable_len::<$t, _, $n>($cmp);
        }
    };
}

macro_rules! w2p2_fallback_fixed {
    ($name:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            if kani::any() {
                w2p2_fallback_len::<u64, _, $n>(lt_u64);
            } else {
                w2p2_fallback_len::<u8, _, $n>(lt_u8);
            }
        }
    };
}
w2p2_bm_fixed!(w2p2_bm_u64_len5, u64, lt_u64, 5);
w2p2_bm_fixed!(w2p2_bm_u8_len5, u8, lt_u8, 5);
w2p2_bm_fixed!(w2p2_bm_u64_len6, u64, lt_u64, 6);
w2p2_bm_fixed!(w2p2_bm_u8_len6, u8, lt_u8, 6);
w2p2_bm_fixed!(w2p2_bm_u64_len7, u64, lt_u64, 7);
w2p2_bm_fixed!(w2p2_bm_u8_len7, u8, lt_u8, 7);
w2p2_bm_fixed!(w2p2_bm_u64_len8, u64, lt_u64, 8);
w2p2_bm_fixed!(w2p2_bm_u8_len8, u8, lt_u8, 8);
w2p2_bm_fixed!(w2p2_bm_u64_len9, u64, lt_u64, 9);
w2p2_bm_fixed!(w2p2_bm_u8_len9, u8, lt_u8, 9);
w2p2_bm_fixed!(w2p2_bm_u64_len10, u64, lt_u64, 10);
w2p2_bm_fixed!(w2p2_bm_u8_len10, u8, lt_u8, 10);
w2p2_bm_fixed!(w2p2_bm_u64_len11, u64, lt_u64, 11);
w2p2_bm_fixed!(w2p2_bm_u8_len11, u8, lt_u8, 11);
w2p2_bm_fixed!(w2p2_bm_u64_len12, u64, lt_u64, 12);
w2p2_bm_fixed!(w2p2_bm_u8_len12, u8, lt_u8, 12);
w2p2_bm_fixed!(w2p2_bm_u64_len13, u64, lt_u64, 13);
w2p2_bm_fixed!(w2p2_bm_u8_len13, u8, lt_u8, 13);
w2p2_bm_fixed!(w2p2_bm_u64_len14, u64, lt_u64, 14);
w2p2_bm_fixed!(w2p2_bm_u8_len14, u8, lt_u8, 14);
w2p2_bm_fixed!(w2p2_bm_u64_len15, u64, lt_u64, 15);
w2p2_bm_fixed!(w2p2_bm_u8_len15, u8, lt_u8, 15);
w2p2_bm_fixed!(w2p2_bm_u64_len16, u64, lt_u64, 16);
w2p2_bm_fixed!(w2p2_bm_u8_len16, u8, lt_u8, 16);
w2p2_general_fixed!(w2p2_gs_u64_len0, u64, lt_u64, 0);
w2p2_general_fixed!(w2p2_gs_u8_len0, u8, lt_u8, 0);
w2p2_fallback_fixed!(w2p2_fallback_len0, 0);
w2p2_general_fixed!(w2p2_gs_u64_len1, u64, lt_u64, 1);
w2p2_general_fixed!(w2p2_gs_u8_len1, u8, lt_u8, 1);
w2p2_fallback_fixed!(w2p2_fallback_len1, 1);
w2p2_general_fixed!(w2p2_gs_u64_len2, u64, lt_u64, 2);
w2p2_general_fixed!(w2p2_gs_u8_len2, u8, lt_u8, 2);
w2p2_fallback_fixed!(w2p2_fallback_len2, 2);
w2p2_general_fixed!(w2p2_gs_u64_len3, u64, lt_u64, 3);
w2p2_general_fixed!(w2p2_gs_u8_len3, u8, lt_u8, 3);
w2p2_fallback_fixed!(w2p2_fallback_len3, 3);
w2p2_general_fixed!(w2p2_gs_u64_len4, u64, lt_u64, 4);
w2p2_general_fixed!(w2p2_gs_u8_len4, u8, lt_u8, 4);
w2p2_fallback_fixed!(w2p2_fallback_len4, 4);
w2p2_general_fixed!(w2p2_gs_u64_len5, u64, lt_u64, 5);
w2p2_general_fixed!(w2p2_gs_u8_len5, u8, lt_u8, 5);
w2p2_fallback_fixed!(w2p2_fallback_len5, 5);
w2p2_general_fixed!(w2p2_gs_u64_len6, u64, lt_u64, 6);
w2p2_general_fixed!(w2p2_gs_u8_len6, u8, lt_u8, 6);
w2p2_fallback_fixed!(w2p2_fallback_len6, 6);
w2p2_general_fixed!(w2p2_gs_u64_len7, u64, lt_u64, 7);
w2p2_general_fixed!(w2p2_gs_u8_len7, u8, lt_u8, 7);
w2p2_fallback_fixed!(w2p2_fallback_len7, 7);
w2p2_general_fixed!(w2p2_gs_u64_len8, u64, lt_u64, 8);
w2p2_general_fixed!(w2p2_gs_u8_len8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len8, 8);
w2p2_general_fixed!(w2p2_gs_u64_len9, u64, lt_u64, 9);
w2p2_general_fixed!(w2p2_gs_u8_len9, u8, lt_u8, 9);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len9, 9);
w2p2_general_fixed!(w2p2_gs_u64_len10, u64, lt_u64, 10);
w2p2_general_fixed!(w2p2_gs_u8_len10, u8, lt_u8, 10);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len10, 10);
w2p2_general_fixed!(w2p2_gs_u64_len11, u64, lt_u64, 11);
w2p2_general_fixed!(w2p2_gs_u8_len11, u8, lt_u8, 11);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len11, 11);
w2p2_general_fixed!(w2p2_gs_u64_len12, u64, lt_u64, 12);
w2p2_general_fixed!(w2p2_gs_u8_len12, u8, lt_u8, 12);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len12, 12);
#[cfg(kani_smallsort_controls)]
w2p2_general_fixed!(w2p2_gs_u64_len13, u64, lt_u64, 13);
w2p2_general_fixed!(w2p2_gs_u8_len13, u8, lt_u8, 13);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len13, 13);
#[cfg(kani_smallsort_controls)]
w2p2_general_fixed!(w2p2_gs_u64_len14, u64, lt_u64, 14);
#[cfg(kani_smallsort_controls)]
w2p2_general_fixed!(w2p2_gs_u8_len14, u8, lt_u8, 14);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len14, 14);
#[cfg(kani_smallsort_controls)]
w2p2_general_fixed!(w2p2_gs_u64_len15, u64, lt_u64, 15);
#[cfg(kani_smallsort_controls)]
w2p2_general_fixed!(w2p2_gs_u8_len15, u8, lt_u8, 15);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len15, 15);
w2p2_general_fixed!(w2p2_gs_u64_len16, u64, lt_u64, 16);
w2p2_general_fixed!(w2p2_gs_u8_len16, u8, lt_u8, 16);
#[cfg(kani_smallsort_controls)]
w2p2_fallback_fixed!(w2p2_fallback_len16, 16);

// Per-type fallback correctness on exact arrays of length 8 or 9, with real insertion bodies.
// Sortedness and full symbolic-value probe multiplicity are separate checks.
macro_rules! w2night_fallback_typed {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            w2p2_fallback_len::<$t, _, $n>($cmp);
        }
    };
}

#[cfg(kani_smallsort_controls)]
w2night_fallback_typed!(w2night_fallback_u64_len8, u64, lt_u64, 8);
w2night_fallback_typed!(w2night_fallback_u8_len8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
w2night_fallback_typed!(w2night_fallback_u8_len9, u8, lt_u8, 9);

// Optional u8 merge contract diagnostics at exact lengths 20 and 24.
// These do not extend the ordinary correctness domain.
#[cfg(kani_smallsort_controls)]
w2p2_bm_fixed!(w2night_k12a_bm_u8_len20, u8, lt_u8, 20);
#[cfg(kani_smallsort_controls)]
w2p2_bm_fixed!(w2night_k12a_bm_u8_len24, u8, lt_u8, 24);

// Non-Copy Freeze values with unique identities and observable Drop.
// Tags are tested by a separate arbitrary-tag multiplicity proof, never by
// bytewise equality (this type can have padding). Keys retain all u64 values.
struct W2NightDrop {
    key: u64,
    tag: u8,
}

static mut W2NIGHT_DROP_COUNT: usize = 0;

impl crate::ops::Drop for W2NightDrop {
    fn drop(&mut self) {
        // SAFETY: single-threaded harness, no live references to the counter.
        unsafe {
            let count = ptr::read(ptr::addr_of!(W2NIGHT_DROP_COUNT));
            ptr::write(ptr::addr_of_mut!(W2NIGHT_DROP_COUNT), count + 1);
        }
    }
}

fn w2night_drop_less(a: &W2NightDrop, b: &W2NightDrop) -> bool {
    // SAFETY: both initialized fields are readable; no Drop value is copied.
    unsafe {
        ptr::read_volatile(&a.key);
        ptr::read_volatile(&a.tag);
        ptr::read_volatile(&b.key);
        ptr::read_volatile(&b.tag);
    }
    kani::any()
}

// Fallback/insertion routes do not merge, so their panic cut has no cover obligation.
// General/stable route controls use the covering panic stub above.
fn w2night_drop_abort_quiet() -> ! {
    kani::assume(false);
    unreachable!()
}

// Count and tag proofs are separate for each exact length: fallback/insertion 2/4/8, and
// general/stable 2/4/8/16 with scratch 48. These bounds are normal-return evidence, not unwind
// safety. Duplicate-tag and extra-drop mutants validate the two independent observations.
fn w2night_drop_run<
    const N: usize,
    const UPPER: bool,
    const PERM: bool,
    const MUTANT: u8,
>() -> bool {
    const { assert!(N >= 2 && N <= 32) };
    const { assert!(MUTANT <= 2) };
    // SAFETY: no prior array or counter reference survives into this harness.
    unsafe { ptr::write(ptr::addr_of_mut!(W2NIGHT_DROP_COUNT), 0) };
    let mut v: [W2NightDrop; N] =
        crate::array::from_fn(|tag| W2NightDrop { key: kani::any(), tag: tag as u8 });
    let probe: u8 = kani::any();
    let alternate: bool = kani::any();
    let mut cmp = w2night_drop_less;
    if UPPER {
        if alternate {
            let mut scratch =
                [const { MaybeUninit::<W2NightDrop>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
            <W2NightDrop as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
        } else {
            super::super::small_sort_general(&mut v, &mut cmp);
        }
    } else if alternate {
        super::super::insertion_sort_shift_left(&mut v, 1, &mut cmp);
    } else {
        super::super::small_sort_fallback(&mut v, &mut cmp);
    }
    // Review controls only; ordinary harnesses instantiate MUTANT = 0.
    if MUTANT == 1 {
        // Deliberately duplicate the first output tag and lose the second.
        // Addresses are valid and disjoint; the tag property must fail.
        unsafe {
            let base = v.as_mut_ptr();
            ptr::copy_nonoverlapping(base, base.add(1), 1);
        }
    } else if MUTANT == 2 {
        // Deliberately observe one extra destructor before array destruction.
        unsafe { crate::mem::drop(ptr::read(v.as_ptr())) };
    }
    if PERM {
        let mut count = 0usize;
        for value in &v {
            count += (value.tag == probe) as usize;
        }
        // Input tags are precisely 0..N, each once. Probe covers all u8 tags,
        // including identities outside the input; no assumption on the probe.
        let expected = if (probe as usize) < N { 1 } else { 0 };
        assert!(count == expected);
    }
    crate::mem::drop(v);
    if !PERM {
        // SAFETY: single-threaded harness; the array was explicitly destroyed.
        let count = unsafe { ptr::read(ptr::addr_of!(W2NIGHT_DROP_COUNT)) };
        assert!(count == N);
    }
    alternate
}

macro_rules! w2night_drop_fixed {
    ($name:ident, $n:literal, false, $perm:literal, $abort:ident) => {
        w2night_drop_fixed!(@routes $name, $n, false, $perm, $abort,
            "K14r: fallback normal return and property checked",
            "K14r: insertion offset 1 normal return and property checked");
    };
    ($name:ident, $n:literal, true, $perm:literal, $abort:ident) => {
        w2night_drop_fixed!(@routes $name, $n, true, $perm, $abort,
            "K14r: general normal return and property checked",
            "K14r: stable-Freeze normal return and property checked");
    };
    (@routes $name:ident, $n:literal, $upper:literal, $perm:literal,
        $abort:ident, $first:literal, $second:literal) => {
        #[kani::proof]
        #[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, $abort)]
        #[kani::unwind(34)]
        fn $name() {
            let alternate = w2night_drop_run::<$n, $upper, $perm, 0>();
            kani::cover(!alternate, $first);
            kani::cover(alternate, $second);
        }
    };
}

/// General/stable Drop control at length 2: the final false assertion must remain detectable.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, w1_abort_ord_violation)]
#[kani::unwind(34)]
fn w2night_drop_control_a() {
    let alternate = w2night_drop_run::<2, true, false, 0>();
    kani::cover(!alternate, "K14r: general normal return and property checked");
    kani::cover(alternate, "K14r: stable-Freeze normal return and property checked");
    let drop_control_value: u64 = kani::any();
    assert!(drop_control_value != drop_control_value);
}

#[cfg(kani_smallsort_controls)]
w2night_drop_fixed!(w2night_drop_reachable, 2, true, false, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_low2_count, 2, false, false, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_low2_perm, 2, false, true, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_low4_count, 4, false, false, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_low4_perm, 4, false, true, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_low8_count, 8, false, false, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_low8_perm, 8, false, true, w2night_drop_abort_quiet);
w2night_drop_fixed!(w2night_drop_upper2_count, 2, true, false, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper2_perm, 2, true, true, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper4_count, 4, true, false, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper4_perm, 4, true, true, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper8_count, 8, true, false, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper8_perm, 8, true, true, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper16_count, 16, true, false, w1_abort_ord_violation);
w2night_drop_fixed!(w2night_drop_upper16_perm, 16, true, true, w1_abort_ord_violation);

/// Length-2 fallback/insertion negative control for tag loss paired with duplication.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    w2night_drop_abort_quiet
)]
#[kani::unwind(34)]
fn w2night_drop_duplicate_tag_control() {
    kani::cover(true, "K14r: duplicate-tag control entered");
    w2night_drop_run::<2, false, true, 1>();
}

/// Length-2 fallback/insertion negative control for an extra destructor call.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    w2night_drop_abort_quiet
)]
#[kani::unwind(34)]
fn w2night_drop_extra_drop_control() {
    kani::cover(true, "K14r: extra-drop control entered");
    w2night_drop_run::<2, false, false, 2>();
}
