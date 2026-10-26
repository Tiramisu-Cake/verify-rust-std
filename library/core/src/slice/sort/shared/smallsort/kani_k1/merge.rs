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

use super::super::{
    CopyOnDrop, SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl,
    UnstableSmallSortFreezeTypeImpl, bidirectional_merge, insert_tail, sort4_stable, sort8_stable,
};
use crate::kani;
use crate::mem::{MaybeUninit, size_of};
use crate::ptr;
use crate::slice::sort::shared::FreezeMarker;

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
/// `set_probe`) and a 4/2/1-byte tail. With loop contracts CBMC unwinds the remaining loops in
/// goto-instrument, before constant propagation, so a loop here nested in the `k1_count` loop
/// multiplied the program (job 17: goto-instrument out of memory).
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

/// Light probe test (formulation 3): `is_probe` specialized per element type, so that a probe count
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
                // SAFETY: `p` is readable (caller); the probe buffer is 16-aligned and larger than
                // the integer.
                unsafe { ptr::read_unaligned(p) == *(ptr::addr_of!(K1_PROBE) as *const $t) }
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

    /// `k1_count` without a loop, for `len <= K1_UNROLL` (callers check the bound). Used in the loop
    /// invariant: DFCC inlines the invariant into the function with the loop contract, and a loop
    /// there made goto-instrument run out of memory (jobs 17 and 19).
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
        step!(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
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
                if $i < len && call_less(is_less, unsafe { base.add($i) }, unsafe { base.add($i - 1) }) {
                    ok = false;
                }
            )*};
        }
        step!(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
        ok
    }

    /// `k1_sorted` as one quantifier over the constant range `1..K1_UNROLL` (the SAT backend of the
    /// Kani pin encodes only quantifiers with constant bounds), guarded by `i < len`. For
    /// `len <= K1_UNROLL`. Not used by the contracts at HEAD; phase 4 run B (job 32) showed that this
    /// quantified `ensures` passes goto-instrument together with a loop contract.
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
                if $i < len && unsafe { <T as K1Probe>::k1_probe(base.add($i)) } {
                    c += 1;
                }
            )*};
        }
        step!(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
        c
    }

    /// Permutation by the light probe count: `a[..len]` and `b[..len]` hold equally many probes.
    /// For `len <= K1_UNROLL`.
    pub(crate) fn k1_perm_l(a: *const T, b: *const T, len: usize) -> bool {
        Self::k1_count_l(a, len) == Self::k1_count_l(b, len)
    }

    /// `k1_merge_halves_sorted` with quantified sortedness (formulation 3).
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

    /// Loop invariant of the main loop of `bidirectional_merge` (`idx` = iterations done).
    /// Notation: `s = src`, `h = len / 2`; the up-merge consumed `s[..a]` and `s[h..h + b]`, the
    /// down-merge consumed `s[h - c..h]` and `s[len - d..]`; the output holds `u` elements at each end
    /// of `d0[..len]`. The remaining elements are `s[a..h - c]` and `s[h + b..len - d]`.
    ///
    /// Formulation 2, NOT ATTACHED to the loop: with the unrolled function specification, the loop
    /// contract ran goto-instrument out of memory under the 13 GiB cap on the Kani pin (jobs 17-24
    /// and 29, RESULT-merge.md D13, D15, finding 6). Kept as a record; formulation 3 is `k1_bm_inv3`.
    /// `K1BmInv` selected the invariant per element type for the phase 2 bisection.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv<F: FnMut(&T, &T) -> bool>(
        src: *const T,
        len: usize,
        d0: *mut T,
        idx: usize,
        left: *const T,
        right: *const T,
        dst: *mut T,
        left_rev: *const T,
        right_rev: *const T,
        dst_rev: *mut T,
        is_less: &&mut F,
    ) -> bool {
        <T as K1BmInv>::k1_bm_inv_sel(
            src, len, d0, idx, left, right, dst, left_rev, right_rev, dst_rev, is_less,
        )
    }

    /// The full invariant: `k1_bm_inv_core` plus conservation of the probe count.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv_full<F: FnMut(&T, &T) -> bool>(
        src: *const T,
        len: usize,
        d0: *mut T,
        idx: usize,
        left: *const T,
        right: *const T,
        dst: *mut T,
        left_rev: *const T,
        right_rev: *const T,
        dst_rev: *mut T,
        is_less: &&mut F,
    ) -> bool {
        match Self::k1_bm_inv_core(
            src, len, d0, idx, left, right, dst, left_rev, right_rev, dst_rev, is_less,
        ) {
            Some((a, b, c, d, u)) => Self::k1_bm_inv_count(src, len, d0, a, b, c, d, u),
            None => false,
        }
    }

    /// Probe count: output so far plus remaining input equals the whole input.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv_count(
        src: *const T,
        len: usize,
        d0: *mut T,
        a: usize,
        b: usize,
        c: usize,
        d: usize,
        u: usize,
    ) -> bool {
        let h = len / 2;
        let d0c = d0 as *const T;
        // SAFETY: indices are in bounds by the arithmetic checked in `k1_bm_inv_core`.
        unsafe {
            Self::k1_count_u(d0c, u)
                + Self::k1_count_u(d0c.add(len - u), u)
                + Self::k1_count_u(src.add(a), h - c - a)
                + Self::k1_count_u(src.add(h + b), len - d - h - b)
                == Self::k1_count_u(src, len)
        }
    }

    /// Formulation 3 (phase 5), ATTACHED to the loop: `k1_bm_inv_core` plus conservation of the
    /// light probe count (`k1_bm_inv_count_l`).
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv3<F: FnMut(&T, &T) -> bool>(
        src: *const T,
        len: usize,
        d0: *mut T,
        idx: usize,
        left: *const T,
        right: *const T,
        dst: *mut T,
        left_rev: *const T,
        right_rev: *const T,
        dst_rev: *mut T,
        is_less: &&mut F,
    ) -> bool {
        match Self::k1_bm_inv_core(
            src, len, d0, idx, left, right, dst, left_rev, right_rev, dst_rev, is_less,
        ) {
            Some((a, b, c, d, u)) => Self::k1_bm_inv_count_l(src, len, d0, a, b, c, d, u),
            None => false,
        }
    }

    /// Light probe count of the invariant in one pass over `0..K1_UNROLL`: the probes in the output
    /// written so far (`d0[..u]`, `d0[len - u..len]`) equal the probes in the consumed input
    /// (`s[..a]`, `s[h - c..h + b]`, `s[len - d..len]`). Same statement as `k1_bm_inv_count` (the
    /// remaining input is the complement of the consumed one), two `K1Probe` tests per position.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv_count_l(
        src: *const T,
        len: usize,
        d0: *mut T,
        a: usize,
        b: usize,
        c: usize,
        d: usize,
        u: usize,
    ) -> bool {
        let h = len / 2;
        let d0c = d0 as *const T;
        let (mut co, mut cc) = (0usize, 0usize);
        macro_rules! step {
            ($($i:literal)*) => {$(
                if $i < len {
                    // SAFETY: `$i < len`; the output is read only where it was written.
                    if ($i < u || $i >= len - u) && unsafe { <T as K1Probe>::k1_probe(d0c.add($i)) } {
                        co += 1;
                    }
                    // SAFETY: `$i < len`, the input is initialized.
                    if ($i < a || ($i >= h - c && $i < h + b) || $i >= len - d)
                        && unsafe { <T as K1Probe>::k1_probe(src.add($i)) }
                    {
                        cc += 1;
                    }
                }
            )*};
        }
        step!(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
        co == cc
    }

    /// Everything of the invariant except the probe count. Returns the consumed counts
    /// `(a, b, c, d, u)` when it holds.
    #[allow(clippy::too_many_arguments)]
    pub(crate) fn k1_bm_inv_core<F: FnMut(&T, &T) -> bool>(
        src: *const T,
        len: usize,
        d0: *mut T,
        idx: usize,
        left: *const T,
        right: *const T,
        dst: *mut T,
        left_rev: *const T,
        right_rev: *const T,
        dst_rev: *mut T,
        is_less: &&mut F,
    ) -> Option<(usize, usize, usize, usize, usize)> {
        let same = |p: *const T, q: *const T| kani::mem::same_allocation(p, q);
        let d0c = d0 as *const T;
        // The unrolled helpers below cover at most K1_UNROLL elements (K-1 lengths are <= 32).
        if len > K1_UNROLL {
            return None;
        }
        if !(same(left, src)
            && same(right, src)
            && same(left_rev, src)
            && same(right_rev, src)
            && same(dst as *const T, d0c)
            && same(dst_rev as *const T, d0c))
        {
            return None;
        }
        let h = len / 2;
        let (hi, li) = (h as isize, len as isize);
        // Element offsets from byte addresses: the loop havocs these pointers, so a byte offset
        // that is not a multiple of the element size must make the invariant false, not trip the
        // UB check of `offset_from`.
        let sz = size_of::<T>() as isize;
        let bytes = |p: *const T, q: *const T| (p.addr() as isize).wrapping_sub(q.addr() as isize);
        let (ba, br, blr, brr, bu, bur) = (
            bytes(left, src),
            bytes(right, src),
            bytes(left_rev, src),
            bytes(right_rev, src),
            bytes(dst as *const T, d0c),
            bytes(dst_rev as *const T, d0c),
        );
        if ba % sz != 0 || br % sz != 0 || blr % sz != 0 || brr % sz != 0 || bu % sz != 0 || bur % sz != 0
        {
            return None;
        }
        let (oa, or, olr, orr, ou, our) = (ba / sz, br / sz, blr / sz, brr / sz, bu / sz, bur / sz);
        let (a, b, c, d, u) = (oa, or - hi, hi - 1 - olr, li - 1 - orr, ou);
        if !(u == idx as isize
            && li - 1 - our == u
            && a >= 0
            && b >= 0
            && c >= 0
            && d >= 0
            && a + b == u
            && c + d == u
            && a + c <= hi
            && b + d <= li - hi
            && u <= hi)
        {
            return None;
        }
        let (a, b, c, d, u) = (a as usize, b as usize, c as usize, d as usize, u as usize);
        let lrem = a + c < h;
        let rrem = b + d < len - h;
        // SAFETY (all `add` below): indices are in bounds by the arithmetic checked above.
        let at = |i: usize| unsafe { src.add(i) };
        let out = |i: usize| unsafe { d0c.add(i) };
        // x <= y and x < y in the comparator's order.
        let le = |x: *const T, y: *const T| !call_less(is_less, y, x);
        let lt = |x: *const T, y: *const T| call_less(is_less, x, y);

        // Output ends sorted, and the up end below the down end. Formulation 3: one quantifier per
        // end (`k1_sorted_q`); formulation 2 used the unrolled `k1_sorted_u` here (record: 312576a9).
        if !Self::k1_sorted_q(d0c, u, is_less) || !Self::k1_sorted_q(out(len - u), u, is_less) {
            return None;
        }
        if u > 0 {
            let (lo, top) = (out(u - 1), out(len - u));
            if !le(lo, top) {
                return None;
            }
            if lrem && !(le(lo, at(a)) && le(at(h - c - 1), top)) {
                return None;
            }
            if rrem && !(le(lo, at(h + b)) && le(at(len - d - 1), top)) {
                return None;
            }
        }
        // Consumed versus remaining elements across the halves (needed when a head is exhausted).
        if c > 0 && rrem && !lt(at(len - d - 1), at(h - c)) {
            return None;
        }
        if d > 0 && lrem && !le(at(h - c - 1), at(len - d)) {
            return None;
        }
        if a > 0 && rrem && !le(at(a - 1), at(h + b)) {
            return None;
        }
        if b > 0 && lrem && !lt(at(h + b - 1), at(a)) {
            return None;
        }
        Some((a, b, c, d, u))
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

/// Selects the loop invariant of `bidirectional_merge` per element type (see `k1_bm_inv`). Default:
/// the full invariant. `u16`: a trivial invariant, `i16`: the invariant without the probe count;
/// those two types occurred only in the phase 2 bisection harnesses (removed), never in a proof or stub.
pub(crate) trait K1BmInv: Sized {
    #[allow(clippy::too_many_arguments)]
    fn k1_bm_inv_sel<F: FnMut(&Self, &Self) -> bool>(
        src: *const Self,
        len: usize,
        d0: *mut Self,
        idx: usize,
        left: *const Self,
        right: *const Self,
        dst: *mut Self,
        left_rev: *const Self,
        right_rev: *const Self,
        dst_rev: *mut Self,
        is_less: &&mut F,
    ) -> bool;
}

impl<T> K1BmInv for T {
    default fn k1_bm_inv_sel<F: FnMut(&T, &T) -> bool>(
        src: *const T,
        len: usize,
        d0: *mut T,
        idx: usize,
        left: *const T,
        right: *const T,
        dst: *mut T,
        left_rev: *const T,
        right_rev: *const T,
        dst_rev: *mut T,
        is_less: &&mut F,
    ) -> bool {
        CopyOnDrop::<T>::k1_bm_inv_full(
            src, len, d0, idx, left, right, dst, left_rev, right_rev, dst_rev, is_less,
        )
    }
}

impl K1BmInv for u16 {
    fn k1_bm_inv_sel<F: FnMut(&u16, &u16) -> bool>(
        _src: *const u16,
        len: usize,
        _d0: *mut u16,
        idx: usize,
        _left: *const u16,
        _right: *const u16,
        _dst: *mut u16,
        _left_rev: *const u16,
        _right_rev: *const u16,
        _dst_rev: *mut u16,
        _is_less: &&mut F,
    ) -> bool {
        idx <= len / 2
    }
}

impl K1BmInv for i16 {
    fn k1_bm_inv_sel<F: FnMut(&i16, &i16) -> bool>(
        src: *const i16,
        len: usize,
        d0: *mut i16,
        idx: usize,
        left: *const i16,
        right: *const i16,
        dst: *mut i16,
        left_rev: *const i16,
        right_rev: *const i16,
        dst_rev: *mut i16,
        is_less: &&mut F,
    ) -> bool {
        CopyOnDrop::<i16>::k1_bm_inv_core(
            src, len, d0, idx, left, right, dst, left_rev, right_rev, dst_rev, is_less,
        )
        .is_some()
    }
}

// ---------------------------------------------------------------------------------------------
// Comparators: strict orders by key, so that elements with equal keys but different full values
// exist and the permutation property is not implied by sortedness.

/// For K1-network (u8 is a network type, not a general one).
pub(crate) fn lt_u8(a: &u8, b: &u8) -> bool {
    (*a >> 1) < (*b >> 1)
}

pub(crate) fn lt_u16(a: &u16, b: &u16) -> bool {
    (*a >> 1) < (*b >> 1)
}

pub(crate) fn lt_i16(a: &i16, b: &i16) -> bool {
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

pub(crate) fn insert_tail_len<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool, const N: usize>(mut is_less: F) {
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
#[kani::unwind(34)]
fn bm_u64_upto8() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 8);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 8, "len 8");
    by_len!(len, bm_len::<u64>(lt_u64), [2 3 4 5 6 7 8]);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn bm_u64_upto32() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 32);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 32, "len 32");
    by_len!(len, bm_len::<u64>(lt_u64),
        [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32]);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(34)]
fn insert_tail_u64_upto8() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 8);
    kani::cover(len == 2, "len 2");
    kani::cover(len == 8, "len 8");
    by_len!(len, insert_tail_len::<u64>(lt_u64), [2 3 4 5 6 7 8]);
}

// Scaling probes (diagnostic): one fixed length per harness.

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn bm_u64_len12() {
    bm_len::<u64, _, 12>(lt_u64);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn bm_u64_len16() {
    bm_len::<u64, _, 16>(lt_u64);
}

// Phase 3 tool control (TASK-merge.md «Фаза 3» p. 2): are loop contracts on the Kani pin broken
// for any `for` loop over a `Range` on an array of up to 32 elements, or only inside
// `bidirectional_merge`? Trivial invariant, plain proof, nothing from smallsort.

fn toy_loop(a: &mut [u64; 32], n: usize) {
    #[cfg_attr(kani, kani::loop_invariant(kani::index <= n && n <= 32))]
    for i in 0..n {
        a[i] = a[i].wrapping_add(1);
    }
}

#[kani::proof]
#[kani::unwind(34)]
fn toy_loop_contract() {
    let mut a: [u64; 32] = kani::any();
    let n: usize = kani::any_where(|n: &usize| *n <= 32);
    kani::cover(n == 32, "toy: n == 32 reachable under the assume");
    toy_loop(&mut a, n);
    kani::cover(true, "toy: end of harness reached");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn bm_u64_len32() {
    bm_len::<u64, _, 32>(lt_u64);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_u64() {
    sort4_body::<u64, _>(lt_u64);
}

/// R11 control: the caller violates the "halves sorted" requires of a `stub_verified` callee.
/// Expected FAILED on the requires check `k1_merge_halves_sorted`.
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

// Per-type contract proofs for measurement (one harness per type, EXPERIMENT.md §2 p. 4).

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_i32() {
    sort4_body::<i32, _>(lt_i32);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_b16() {
    sort4_body::<[u8; 16], _>(lt_b16);
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_b85() {
    sort4_body::<[u8; 85], _>(lt_b85);
}

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

sort8_harness!(sort8_i32, i32, lt_i32);
sort8_harness!(sort8_u64, u64, lt_u64);
sort8_harness!(sort8_b16, [u8; 16], lt_b16);

/// insert_tail on regions of 2..=16 elements (general inserts up to index 15 of a half).
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

macro_rules! bm_harness {
    ($name:ident, $t:ty, $cmp:expr) => {
        /// bidirectional_merge on 2..=32 elements.
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 32);
            kani::cover(len == 2, "len 2");
            kani::cover(len == 32, "len 32");
            by_len!(len, bm_len::<$t>($cmp),
                [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32]);
        }
    };
}

bm_harness!(bm_u8, u8, lt_u8); // used by K1-network's small_sort_network (len 18..=32)
bm_harness!(bm_i32, i32, lt_i32);
bm_harness!(bm_u64, u64, lt_u64);
bm_harness!(bm_b16, [u8; 16], lt_b16);
bm_harness!(bm_b85, [u8; 85], lt_b85);

// ---------------------------------------------------------------------------------------------
// Top harnesses: real trait entrypoints, every length 0..=32, callees replaced by their verified
// contracts. Checks: no UB (Kani default checks), output sorted, output a permutation of the input.

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
            by_len!(len, $body::<$t>($cmp),
                [0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32]);
        }
    };
}

general_harness!(general_i32, general_stable_len, i32, lt_i32);
general_harness!(general_u64, general_stable_len, u64, lt_u64);
general_harness!(general_b16, general_unstable_len, [u8; 16], lt_b16);
general_harness!(general_b85, general_unstable_len, [u8; 85], lt_b85);

/// One band of lengths `[$($n)*]` of a top harness. The family of bands of one type covers every
/// length 0..=32 (EXPERIMENT.md §2 p. 2). Covers: every boundary length of R12 that lies in the band,
/// listed explicitly in `[$($c)*]`, so that every cover of the harness is satisfiable.
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
general_band!(general_u64_len32, general_stable_len, u64, lt_u64, [32], covers [32]);
