//! Merge, insertion-tail and stable-primitive contracts and bounded callers.
//! Probe multiplicity represents full values only for types without padding; Drop uses tag counts.
//! Callers and verified stubs share the arbitrary probe. Ordered proofs use stateless comparators.

#![allow(dead_code)]

#[cfg(kani_smallsort_controls)]
use super::super::insert_tail;
use super::super::{
    CopyOnDrop, SMALL_SORT_GENERAL_SCRATCH_LEN, StableSmallSortTypeImpl, UnstableSmallSortTypeImpl,
    bidirectional_merge, sort4_stable,
};
use crate::mem::{MaybeUninit, size_of};
use crate::slice::sort::shared::FreezeMarker;
use crate::{kani, ptr};

const PROBE_BYTES: usize = 128;

const MAX_UNROLLED_ELEMENTS: usize = 32;

#[repr(C, align(16))]
struct Probe([u8; PROBE_BYTES]);

static mut VALUE_PROBE_BYTES: Probe = Probe([0; PROBE_BYTES]);

pub(crate) fn set_value_probe<T>() {
    assert!(size_of::<T>() <= PROBE_BYTES);
    let bytes: [u8; PROBE_BYTES] = kani::any();
    // SAFETY: single-threaded harness; no reference to the static is alive.
    unsafe { *ptr::addr_of_mut!(VALUE_PROBE_BYTES) = Probe(bytes) };
}

/// `*p` is bytewise equal to the probe. `p` must be valid for reads of one initialized `T`.
/// Guarded word reads avoid nested specification loops during instrumentation.
#[inline(always)]
unsafe fn matches_value_probe<T>(p: *const T) -> bool {
    let a = p as *const u8;
    let n = size_of::<T>();
    let w = n / 8;
    let mut eq = true;
    // SAFETY: `p` is readable for `n` bytes and the probe buffer is larger than `n`; every read
    // below is guarded to lie in `0..n`.
    unsafe {
        let b = ptr::addr_of!(VALUE_PROBE_BYTES) as *const u8;
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

#[inline(always)]
fn call_comparator<T, F: FnMut(&T, &T) -> bool>(
    is_less: &&mut F,
    a: *const T,
    b: *const T,
) -> bool {
    let f = is_less as *const &mut F as *mut &mut F;
    // SAFETY: spec-only aliasing is valid only for stateless comparators; `a` and `b` are valid
    // under the caller's contract.
    unsafe { (*f)(&*a, &*b) }
}

impl<T> CopyOnDrop<T> {
    // These specification helpers live here to mention `T` without adding runtime state.
    pub(crate) fn probe_count(base: *const T, len: usize) -> usize {
        let mut c = 0;
        let mut i = 0;
        while i < len {
            // SAFETY: callers pass a readable, initialized region of `len` elements.
            if unsafe { matches_value_probe(base.add(i)) } {
                c += 1;
            }
            i += 1;
        }
        c
    }

    /// Loop-free count for `len <= MAX_UNROLLED_ELEMENTS`, bounding specification instrumentation.
    pub(crate) fn probe_count_unrolled(base: *const T, len: usize) -> usize {
        let mut c = 0;
        macro_rules! step {
            ($($i:literal)*) => {$(
                // SAFETY: `$i < len`, callers pass a readable region of `len` elements.
                if $i < len && unsafe { matches_value_probe(base.add($i)) } {
                    c += 1;
                }
            )*};
        }
        step!(
            0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        );
        c
    }

    /// `is_sorted` without a loop, for `len <= MAX_UNROLLED_ELEMENTS` (callers check the bound).
    pub(crate) fn is_sorted_unrolled<F: FnMut(&T, &T) -> bool>(
        base: *const T,
        len: usize,
        is_less: &&mut F,
    ) -> bool {
        let mut ok = true;
        macro_rules! step {
            ($($i:literal)*) => {$(
                // SAFETY: `$i < len`, callers pass a readable region of `len` elements.
                if $i < len
                    && call_comparator(
                        is_less,
                        unsafe { base.add($i) },
                        unsafe { base.add($i - 1) },
                    )
                {
                    ok = false;
                }
            )*};
        }
        step!(1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31);
        ok
    }

    pub(crate) fn is_sorted<F: FnMut(&T, &T) -> bool>(
        base: *const T,
        len: usize,
        is_less: &&mut F,
    ) -> bool {
        let mut i = 1;
        while i < len {
            // SAFETY: callers pass a readable, initialized region of `len` elements.
            if call_comparator(is_less, unsafe { base.add(i) }, unsafe { base.add(i - 1) }) {
                return false;
            }
            i += 1;
        }
        true
    }

    pub(crate) fn regions_are_disjoint(a: *const T, n: usize, b: *const T, m: usize) -> bool {
        !kani::mem::same_allocation(a, b) || {
            // SAFETY: same allocation was checked just above.
            let d = unsafe { b.offset_from(a) };
            d >= n as isize || -d >= m as isize
        }
    }

    /// Number of elements in `[begin, tail]`. Only meaningful under `tail_region_is_writable`.
    pub(crate) fn tail_region_len(begin: *const T, tail: *const T) -> usize {
        // SAFETY: under the requires, both pointers are in one allocation.
        (unsafe { tail.offset_from(begin) }) as usize + 1
    }

    /// `begin < tail`, both in one allocation, `[begin, tail]` valid for reads and writes.
    pub(crate) fn tail_region_is_writable(begin: *mut T, tail: *mut T) -> bool {
        // SAFETY: same allocation checked first; instantiated element types are nonzero-sized.
        kani::mem::same_allocation(begin as *const T, tail as *const T)
            && (unsafe { tail.offset_from(begin) }) >= 1
            && kani::mem::can_write(ptr::slice_from_raw_parts_mut(
                begin,
                Self::tail_region_len(begin, tail),
            ))
    }

    /// Check geometry before computing the pointer difference or testing the sorted prefix.
    pub(crate) fn valid_sorted_tail<F: FnMut(&T, &T) -> bool>(
        begin: *mut T,
        tail: *mut T,
        is_less: &&mut F,
    ) -> bool {
        Self::tail_region_is_writable(begin, tail)
            && Self::is_sorted(begin, Self::tail_region_len(begin, tail) - 1, is_less)
    }

    /// Sources also come from mutable slices, so the contract requires writable memory.
    pub(crate) fn is_writable_region(p: *const T, n: usize) -> bool {
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(p as *mut T, n))
    }

    pub(crate) fn valid_sort4_regions(v_base: *const T, dst: *mut T) -> bool {
        Self::is_writable_region(v_base, 4)
            && Self::is_writable_region(dst, 4)
            && Self::regions_are_disjoint(v_base, 4, dst, 4)
    }

    pub(crate) fn valid_merge_destination(v: &[T], dst: *mut T) -> bool {
        kani::mem::can_write(ptr::slice_from_raw_parts_mut(dst, v.len()))
            && Self::regions_are_disjoint(v.as_ptr(), v.len(), dst as *const T, v.len())
    }

    pub(crate) fn merge_inputs_are_sorted<F: FnMut(&T, &T) -> bool>(
        v: &[T],
        is_less: &&mut F,
    ) -> bool {
        let len = v.len();
        let half = len / 2;
        len <= MAX_UNROLLED_ELEMENTS
            && Self::is_sorted_unrolled(v.as_ptr(), half, is_less)
            && Self::is_sorted_unrolled(v.as_ptr().wrapping_add(half), len - half, is_less)
    }
}
// Key orders admit equal keys with different full values; sortedness does not imply permutation.

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

#[cfg(kani_smallsort_controls)]
pub(crate) fn lt_b85(a: &[u8; 85], b: &[u8; 85]) -> bool {
    a[0] < b[0]
}
// Harness bodies, one per concrete length so that every loop has a constant bound.

#[cfg(kani_smallsort_controls)]
macro_rules! dispatch_by_length {
    ($len:expr, $f:ident::<$t:ty>($cmp:expr), [$($n:literal)*]) => {
        match $len {
            $( $n => $f::<$t, _, $n>($cmp), )*
            _ => {}
        }
    };
}

pub(crate) fn merge_length_body<
    T: kani::Arbitrary + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut is_less: F,
) {
    set_value_probe::<T>();
    let v: [T; N] = kani::any();
    let mut dst = MaybeUninit::<[T; N]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut T, &mut is_less) };
    kani::cover(true, "merge returns for a permitted length");
}

#[cfg(kani_smallsort_controls)]
pub(crate) fn insert_tail_len<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool, const N: usize>(
    mut is_less: F,
) {
    set_value_probe::<T>();
    let mut v: [T; N] = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { insert_tail(base, base.add(N - 1), &mut is_less) };
    kani::cover(true, "tail insertion returns for a permitted length");
}

/// Negative precondition control: u64 length 4 violates the verified merge's sorted-halves clause.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
fn merge_rejects_unsorted_halves_control_u64_n4() {
    set_value_probe::<u64>();
    // Comparison keys are [3, 0, 1, 2], so the left half is not sorted.
    let v: [u64; 4] = [6, 0, 2, 4];
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    let mut is_less = lt_u64;
    // SAFETY: dst is a separate local of 4 elements; only the sortedness requires is violated.
    unsafe { bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut is_less) };
    kani::cover(true, "unsorted input call reached");
}
// Stable primitives: exact source/destination arrays, matching the composed caller types.

fn sort4_length_body<T: kani::Arbitrary, F: FnMut(&T, &T) -> bool>(mut is_less: F) {
    set_value_probe::<T>();
    let v: [T; 4] = kani::any();
    let mut dst = MaybeUninit::<[T; 4]>::uninit();
    // SAFETY: contract checked by the enclosing proof_for_contract harness.
    unsafe { sort4_stable(v.as_ptr(), dst.as_mut_ptr() as *mut T, &mut is_less) };
    kani::cover(true, "four-element stable sort returns");
}

/// sort4_stable for all four general element types (direct, no stubs).
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_contract_type_matrix_n4() {
    let t: u8 = kani::any_where(|t: &u8| *t < 4);
    kani::cover(t == 3, "last element type is reachable");
    match t {
        0 => sort4_length_body::<i32, _>(lt_i32),
        1 => sort4_length_body::<u64, _>(lt_u64),
        2 => sort4_length_body::<[u8; 16], _>(lt_b16),
        _ => sort4_length_body::<[u8; 85], _>(lt_b85),
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_contract_i32_control_n4() {
    sort4_length_body::<i32, _>(lt_i32);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_contract_bytes16_control_n4() {
    sort4_length_body::<[u8; 16], _>(lt_b16);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
#[kani::unwind(34)]
fn sort4_contract_bytes85_control_n4() {
    sort4_length_body::<[u8; 85], _>(lt_b85);
}

// Separate sort4 checks: ordered contract, and real-body safety/permutation with arbitrary results.
fn read_sort4_arguments<T: Copy>(a: &T, b: &T) {
    // SAFETY: both references must point to initialized readable elements.
    unsafe {
        ptr::read_volatile(a);
        ptr::read_volatile(b);
    }
}

fn sort4_arbitrary_comparator_body<T: kani::Arbitrary + Copy>() {
    set_value_probe::<T>();
    let v: [T; 4] = kani::any();
    let mut dst = MaybeUninit::<[T; 4]>::uninit();
    let mut cmp = |a: &T, b: &T| {
        read_sort4_arguments(a, b);
        kani::any()
    };
    // SAFETY: two disjoint exact four-element allocations, initialized source;
    // sort4_stable's SAFETY precondition does not require an ordered comparator.
    unsafe { sort4_stable(v.as_ptr(), dst.as_mut_ptr() as *mut T, &mut cmp) };
    assert!(
        CopyOnDrop::<T>::probe_count(v.as_ptr(), 4)
            == CopyOnDrop::<T>::probe_count(dst.as_ptr() as *const T, 4)
    );
    kani::cover(true, "sort returns and preserves values with an arbitrary comparator");
}

macro_rules! define_sort4_contract_and_comparator_harnesses {
    ($contract:ident, $arbitrary:ident, $t:ty, $ordered:ident) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::sort4_stable)]
        #[kani::unwind(34)]
        fn $contract() {
            sort4_length_body::<$t, _>(|a, b| {
                read_sort4_arguments(a, b);
                $ordered(a, b)
            });
        }

        #[kani::proof]
        #[kani::unwind(34)]
        fn $arbitrary() {
            sort4_arbitrary_comparator_body::<$t>();
        }
    };
}

define_sort4_contract_and_comparator_harnesses!(
    sort4_contract_u64_n4,
    sort4_arbitrary_comparator_u64_n4,
    u64,
    lt_u64
);
define_sort4_contract_and_comparator_harnesses!(
    sort4_contract_bytes16_n4,
    sort4_arbitrary_comparator_bytes16_n4,
    [u8; 16],
    lt_b16
);
#[cfg(kani_smallsort_controls)]
define_sort4_contract_and_comparator_harnesses!(
    sort4_contract_bytes85_n4,
    sort4_arbitrary_comparator_bytes85_n4,
    [u8; 85],
    lt_b85
);

/// insert_tail on regions of 2..=16 elements (general inserts up to index 15 of a half).
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(34)]
fn insert_tail_contract_integer_types_n2_to16() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 16);
    kani::cover(len == 2, "length 2 reached");
    kani::cover(len == 16, "length 16 reached");
    if kani::any() {
        dispatch_by_length!(
            len,
            insert_tail_len::<i32>(lt_i32),
            [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]
        );
    } else {
        dispatch_by_length!(
            len,
            insert_tail_len::<u64>(lt_u64),
            [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]
        );
    }
}

/// Byte-array widths 16/85, exact regions 2..=16, ordered prefix supplied by the tail contract.
#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::insert_tail)]
#[kani::unwind(34)]
fn insert_tail_contract_byte_arrays_n2_to16() {
    let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 16);
    kani::cover(len == 2, "length 2 reached");
    kani::cover(len == 16, "length 16 reached");
    if kani::any() {
        dispatch_by_length!(
            len,
            insert_tail_len::<[u8; 16]>(lt_b16),
            [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]
        );
    } else {
        dispatch_by_length!(
            len,
            insert_tail_len::<[u8; 85]>(lt_b85),
            [2 3 4 5 6 7 8 9 10 11 12 13 14 15 16]
        );
    }
}

#[cfg(kani_smallsort_controls)]
macro_rules! define_merge_length_harness {
    ($name:ident, $t:ty, $cmp:expr) => {
        // Exact arrays of each length 2..=32; destination is disjoint.
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            let len: usize = kani::any_where(|l: &usize| *l >= 2 && *l <= 32);
            kani::cover(len == 2, "length 2 reached");
            kani::cover(len == 32, "length 32 reached");
            dispatch_by_length!(len, merge_length_body::<$t>($cmp), [
                2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32
            ]);
        }
    };
}

#[cfg(kani_smallsort_controls)]
define_merge_length_harness!(merge_contract_u8_n2_to32, u8, lt_u8);
#[cfg(kani_smallsort_controls)]
define_merge_length_harness!(merge_contract_i32_n2_to32, i32, lt_i32);
#[cfg(kani_smallsort_controls)]
define_merge_length_harness!(merge_contract_u64_n2_to32, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
define_merge_length_harness!(merge_contract_bytes16_n2_to32, [u8; 16], lt_b16);
#[cfg(kani_smallsort_controls)]
define_merge_length_harness!(merge_contract_bytes85_n2_to32, [u8; 85], lt_b85);
// Real-body safety harnesses use no verified-contract stubs. The manual panic boundary cuts
// order-violation panic paths under abort semantics; it makes no claim about unwinding.

fn arbitrary_u64_order(a: &u64, b: &u64) -> bool {
    // SAFETY: initialized references; volatile reads retain both accesses.
    unsafe {
        ptr::read_volatile(a);
        ptr::read_volatile(b);
    }
    kani::any()
}

fn abort_on_order_violation() -> ! {
    kani::cover(true, "order violation panic path is reachable");
    kani::assume(false);
    unreachable!()
}

// u64 N4 assertion/reachability pair; real merge and arbitrary reading comparator, panic cut only.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(6)]
fn merge_arbitrary_order_permutation_failure_control_u64_n4() {
    let v: [u64; 4] = kani::any();
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source, separate destination for four writes, len >= 2.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut arbitrary_u64_order);
        let out = dst.assume_init();
        kani::cover(true, "merge returns before the mutation check");
        for value in v {
            let before = v.iter().filter(|x| **x == value).count();
            let after = out.iter().filter(|x| **x == value).count();
            assert!(before == after, "input value counts are preserved");
        }
    }
    assert!(v[0] != v[0]);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(6)]
fn merge_arbitrary_order_reachability_check_control_u64_n4() {
    let v: [u64; 4] = kani::any();
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source, separate destination for four writes, len >= 2.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut arbitrary_u64_order);
        let out = dst.assume_init();
        for value in v {
            let before = v.iter().filter(|x| **x == value).count();
            let after = out.iter().filter(|x| **x == value).count();
            assert!(before == after, "input value counts are preserved");
        }
    }
    kani::cover(true, "merge returns and preserves input value counts");
}

// Real merge safety on exact u64 arrays of 2..=32 elements with arbitrary comparisons.
// No sortedness premise is imposed; normal-return covers check that the panic cut is nonvacuous.
#[cfg(kani_smallsort_controls)]
fn merge_safety_body_u64<const N: usize>() {
    const { assert!(N >= 2 && N <= 32) };
    let v: [u64; N] = kani::any();
    let mut dst = MaybeUninit::<[u64; N]>::uninit();
    // SAFETY: each harness uses N >= 2; v is initialized, dst is separate and
    // valid for N writes. Safety does not require ordered halves or comparator.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut arbitrary_u64_order);
    }
    kani::cover(true, "merge returns for arbitrary comparisons");
}

// u64 selects the network through the unstable trait. A transparent non-Copy wrapper also
// exercises the general trait route; stable Freeze sorting selects general directly for u64.
#[repr(transparent)]
struct WrappedU64(u64);

fn arbitrary_wrapped_u64_order(a: &WrappedU64, b: &WrappedU64) -> bool {
    // SAFETY: both initialized transparent payloads are readable; no Drop value is copied.
    unsafe {
        ptr::read_volatile(&a.0);
        ptr::read_volatile(&b.0);
    }
    kani::any()
}

fn unstable_general_u64_safety_body<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    super::super::small_sort_general(&mut v, &mut arbitrary_u64_order);
    kani::cover(true, "general u64 safety: normal return reachable");
}

fn noncopy_general_u64_safety_body<const N: usize>() {
    let payload: [u64; N] = kani::any();
    let mut v = payload.map(WrappedU64);
    <WrappedU64 as UnstableSmallSortTypeImpl>::small_sort(&mut v, &mut arbitrary_wrapped_u64_order);
    kani::cover(true, "non-Copy u64 route safety: normal return reachable");
}

fn stable_general_u64_safety_body<const N: usize>() {
    let mut v: [u64; N] = kani::any();
    let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut arbitrary_u64_order);
    kani::cover(true, "stable u64 route safety: normal return reachable");
}

// Every exact length 2..=32 selects direct general u64, non-Copy unstable general, or stable
// Freeze sorting. Each route has a normal-return cover and uses real callees with scratch 48.
fn all_upper_routes_safety_body<const N: usize>() {
    let route: u8 = kani::any();
    match route {
        0 => unstable_general_u64_safety_body::<N>(),
        1 => noncopy_general_u64_safety_body::<N>(),
        _ => stable_general_u64_safety_body::<N>(),
    }
}

// Sensitivity controls start with an honest ordered four-element merge, then perform one
// deliberately invalid operation. They expect a localized Kani safety failure after normal return.
#[cfg(kani_smallsort_controls)]
fn ordered_merge_before_safety_control_u64_n4() -> [u64; 4] {
    let v = [0u64, 1, 2, 3];
    let mut dst = MaybeUninit::<[u64; 4]>::uninit();
    // SAFETY: initialized source and separate destination, both exactly four
    // elements; honest comparison on two ordered halves.
    unsafe {
        bidirectional_merge(&v, dst.as_mut_ptr() as *mut u64, &mut |a, b| a < b);
        let out = dst.assume_init();
        kani::cover(true, "safety control: normal merge return before check");
        out
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn intrinsic_assumption_safety_control_u64_n4() {
    let v = ordered_merge_before_safety_control_u64_n4();
    // Deliberately violate the intrinsic's precondition after the real merge returns.
    unsafe {
        let first = ptr::read_volatile(&v[0]);
        crate::intrinsics::assume(first != 0);
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn unchecked_add_overflow_control_u64_n4() {
    let _v = ordered_merge_before_safety_control_u64_n4();
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
fn overlapping_copy_control_u64_n4() {
    let mut v = ordered_merge_before_safety_control_u64_n4();
    // Deliberate overlap at elements 1 and 2 of an aligned four-element allocation.
    unsafe {
        let p = v.as_mut_ptr();
        ptr::copy_nonoverlapping(p, p.add(1), 3);
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(6)]
fn out_of_bounds_pointer_control_u64_n4() {
    let v = ordered_merge_before_safety_control_u64_n4();
    // Deliberate offset beyond one-past, without dereferencing it.
    unsafe {
        let mut result = ptr::null::<u64>();
        ptr::write_volatile(&mut result, v.as_ptr().add(5));
    }
}

// Paired four-element u64 controls use the real merge and the order-violation panic cut.
// The negative member adds a false assertion; the positive member witnesses normal return.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(6)]
fn merge_arbitrary_order_assertion_control_u64_n4() {
    merge_safety_body_u64::<4>();
    let value: u64 = kani::any();
    assert!(value != value);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(6)]
fn merge_arbitrary_order_reachability_control_u64_n4() {
    merge_safety_body_u64::<4>();
}

macro_rules! define_route_safety_harness {
    ($name:ident, $body:ident, $n:literal) => {
        #[kani::proof]
        #[kani::stub(
            crate::slice::sort::shared::smallsort::panic_on_ord_violation,
            abort_on_order_violation
        )]
        #[kani::unwind(34)]
        fn $name() {
            $body::<$n>();
        }
    };
}

define_route_safety_harness!(route_safety_all_routes_n2, all_upper_routes_safety_body, 2);
define_route_safety_harness!(route_safety_all_routes_n3, all_upper_routes_safety_body, 3);
define_route_safety_harness!(route_safety_all_routes_n4, all_upper_routes_safety_body, 4);
define_route_safety_harness!(route_safety_all_routes_n5, all_upper_routes_safety_body, 5);
define_route_safety_harness!(route_safety_all_routes_n6, all_upper_routes_safety_body, 6);
define_route_safety_harness!(route_safety_all_routes_n7, all_upper_routes_safety_body, 7);
define_route_safety_harness!(route_safety_all_routes_n8, all_upper_routes_safety_body, 8);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n9, all_upper_routes_safety_body, 9);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n10, all_upper_routes_safety_body, 10);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n11, all_upper_routes_safety_body, 11);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n12, all_upper_routes_safety_body, 12);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n13, all_upper_routes_safety_body, 13);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n14, all_upper_routes_safety_body, 14);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n15, all_upper_routes_safety_body, 15);
define_route_safety_harness!(route_safety_all_routes_n16, all_upper_routes_safety_body, 16);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n17, all_upper_routes_safety_body, 17);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n18, all_upper_routes_safety_body, 18);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n19, all_upper_routes_safety_body, 19);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n20, all_upper_routes_safety_body, 20);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n21, all_upper_routes_safety_body, 21);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n22, all_upper_routes_safety_body, 22);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n23, all_upper_routes_safety_body, 23);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n24, all_upper_routes_safety_body, 24);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n25, all_upper_routes_safety_body, 25);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n26, all_upper_routes_safety_body, 26);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n27, all_upper_routes_safety_body, 27);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n28, all_upper_routes_safety_body, 28);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n29, all_upper_routes_safety_body, 29);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n30, all_upper_routes_safety_body, 30);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n31, all_upper_routes_safety_body, 31);
#[cfg(kani_smallsort_controls)]
define_route_safety_harness!(route_safety_all_routes_n32, all_upper_routes_safety_body, 32);

// Merge contracts: u8/u64, upper-bit key order, exact arrays N2..16; optional u8 N20/24
// diagnostics.
macro_rules! define_small_merge_contract_harness {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            let len: u8 = kani::any_where(|n: &u8| *n >= 2 && *n <= 4);
            match len {
                2 => {
                    merge_length_body::<$t, _, 2>($cmp);
                    kani::cover(true, "merge contract: length 2");
                }
                3 => {
                    merge_length_body::<$t, _, 3>($cmp);
                    kani::cover(true, "merge contract: length 3");
                }
                4 => {
                    merge_length_body::<$t, _, 4>($cmp);
                    kani::cover(true, "merge contract: length 4");
                }
                _ => {}
            }
        }
    };
}

define_small_merge_contract_harness!(merge_contract_u64_n2_to4, u64, lt_u64);
define_small_merge_contract_harness!(merge_contract_u8_n2_to4, u8, lt_u8);

macro_rules! define_merge_contract_harness {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            merge_length_body::<$t, _, $n>($cmp);
        }
    };
}

#[cfg(kani_smallsort_controls)]
macro_rules! define_unsorted_halves_control {
    ($name:ident, $t:ty, $cmp:expr) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            set_value_probe::<$t>();
            let v: [$t; 4] = [6, 0, 2, 4];
            let mut dst = MaybeUninit::<[$t; 4]>::uninit();
            let mut cmp = $cmp;
            kani::cover(true, "merge call reaches the unsorted-halves check");
            // Valid memory, but prefix keys [3, 0] violate sortedness.
            unsafe {
                bidirectional_merge(&v, dst.as_mut_ptr() as *mut $t, &mut cmp);
            }
        }
    };
}

#[cfg(kani_smallsort_controls)]
define_unsorted_halves_control!(merge_unsorted_halves_control_u64_n4, u64, lt_u64);
#[cfg(kani_smallsort_controls)]
define_unsorted_halves_control!(merge_unsorted_halves_control_u8_n4, u8, lt_u8);

fn assert_sorted_and_probe_preserved<T, F: FnMut(&T, &T) -> bool, const N: usize>(
    orig: &[T; N],
    out: &[T; N],
    cmp: &mut F,
) {
    for i in 1..N {
        assert!(!cmp(&out[i], &out[i - 1]), "output is sorted");
    }
    assert!(
        CopyOnDrop::<T>::probe_count_unrolled(orig.as_ptr(), N)
            == CopyOnDrop::<T>::probe_count_unrolled(out.as_ptr(), N),
        "input value counts are preserved"
    );
}

// General/stable correctness with 48 scratch elements and a shared full-value oracle.
fn general_route_properties<
    T: kani::Arbitrary + Copy + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut cmp: F,
) {
    const { assert!(N <= 16) };
    set_value_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    let stable: bool = kani::any();
    if stable {
        let mut scratch = [MaybeUninit::<T>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
        <T as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    } else {
        super::super::small_sort_general(&mut v, &mut cmp);
    }
    assert_sorted_and_probe_preserved::<T, _, N>(&orig, &v, &mut cmp);
    kani::cover(!stable, "general route properties checked");
    kani::cover(stable, "stable route properties checked");
}

fn general_route_const_u64_properties<const N: usize>() {
    const { assert!(N <= 16) };
    set_value_probe::<u64>();
    let mut v: [u64; N] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    let stable: bool = kani::any();
    if stable {
        let mut scratch = [const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
        <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    } else {
        super::super::small_sort_general(&mut v, &mut cmp);
    }
    assert_sorted_and_probe_preserved::<u64, _, N>(&orig, &v, &mut cmp);
    kani::cover(!stable, "general route properties checked");
    kani::cover(stable, "stable route properties checked");
}

// Direct fallback correctness on exact u8/u64 arrays up to 16; every insertion body is real.
fn fallback_route_properties<
    T: kani::Arbitrary + Copy,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut cmp: F,
) {
    const { assert!(N <= 16) };
    set_value_probe::<T>();
    let mut v: [T; N] = kani::any();
    let orig = v;
    super::super::small_sort_fallback(&mut v, &mut cmp);
    assert_sorted_and_probe_preserved::<T, _, N>(&orig, &v, &mut cmp);
    kani::cover(true, "fallback route properties checked");
}

// Stubbed callers: only merge is stubbed; insertion and sort4 remain real.
macro_rules! define_general_sortedness_harness {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            general_route_properties::<$t, _, $n>($cmp);
        }
    };
}

// Direct callers retain the same oracle and routes, with the real merge body.
macro_rules! define_general_direct_harness {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            general_route_properties::<$t, _, $n>($cmp);
        }
    };
}

#[kani::proof]
#[kani::unwind(34)]
fn general_stable_direct_u64_n2() {
    general_route_const_u64_properties::<2>();
}

#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_nonconst_u64_n2, u64, lt_u64, 2);

#[kani::proof]
#[kani::unwind(34)]
fn general_stable_direct_u64_n3() {
    general_route_const_u64_properties::<3>();
}

#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_nonconst_u64_n3, u64, lt_u64, 3);

#[kani::proof]
#[kani::unwind(34)]
fn general_stable_direct_u64_n4() {
    general_route_const_u64_properties::<4>();
}

#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_nonconst_u64_n4, u64, lt_u64, 4);

#[kani::proof]
#[kani::unwind(34)]
fn general_stable_direct_u64_n5() {
    general_route_const_u64_properties::<5>();
}

#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_nonconst_u64_n5, u64, lt_u64, 5);

#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_u64_n6, u64, lt_u64, 6);
#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_u64_n7, u64, lt_u64, 7);
#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_u64_n8, u64, lt_u64, 8);
define_general_direct_harness!(general_stable_direct_u8_n2, u8, lt_u8, 2);
define_general_direct_harness!(general_stable_direct_u8_n3, u8, lt_u8, 3);
define_general_direct_harness!(general_stable_direct_u8_n4, u8, lt_u8, 4);
define_general_direct_harness!(general_stable_direct_u8_n5, u8, lt_u8, 5);
define_general_direct_harness!(general_stable_direct_u8_n6, u8, lt_u8, 6);
define_general_direct_harness!(general_stable_direct_u8_n7, u8, lt_u8, 7);
define_general_direct_harness!(general_stable_direct_u8_n8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
define_general_direct_harness!(general_stable_direct_u8_n9, u8, lt_u8, 9);

// Direct u64 routes use real merge bodies and the shared full-value oracle.
fn scratch_view<T>(
    holder: &mut MaybeUninit<[T; SMALL_SORT_GENERAL_SCRATCH_LEN]>,
) -> &mut [MaybeUninit<T>] {
    // SAFETY: the pointer retains the provenance of the exclusively borrowed holder.
    // Arrays and MaybeUninit preserve element size/alignment, so all 48 slots fit.
    // Only MaybeUninit<T> references are formed; no T needs to be initialized.
    // The returned lifetime is tied to holder, which cannot be accessed during this borrow.
    unsafe {
        crate::slice::from_raw_parts_mut(
            holder.as_mut_ptr().cast::<MaybeUninit<T>>(),
            SMALL_SORT_GENERAL_SCRATCH_LEN,
        )
    }
}

fn general_direct_u64_properties<const N: usize>() {
    const { assert!(N >= 6 && N <= 9) };
    set_value_probe::<u64>();
    let mut v: [u64; N] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    super::super::small_sort_general(&mut v, &mut cmp);
    assert_sorted_and_probe_preserved::<u64, _, N>(&orig, &v, &mut cmp);
    kani::cover(true, "general direct split properties checked");
}

fn stable_direct_u64_properties<const N: usize>() {
    const { assert!(N >= 6 && N <= 9) };
    set_value_probe::<u64>();
    let mut v: [u64; N] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    let mut scratch = [const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    assert_sorted_and_probe_preserved::<u64, _, N>(&orig, &v, &mut cmp);
    kani::cover(true, "stable direct split properties checked");
}

#[cfg(kani_smallsort_controls)]
fn stable_direct_aggregate_u64_properties<const N: usize>() {
    const { assert!(N == 6 || N == 7 || N == 8) };
    set_value_probe::<u64>();
    let mut v: [u64; N] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();
    let scratch = scratch_view(&mut holder);
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, scratch, &mut cmp);
    assert_sorted_and_probe_preserved::<u64, _, N>(&orig, &v, &mut cmp);
    kani::cover(true, "stable direct split properties checked");
}

macro_rules! define_direct_u64_route_harness {
    ($name:ident, $body:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            $body::<$n>();
        }
    };
}

define_direct_u64_route_harness!(general_direct_u64_n6, general_direct_u64_properties, 6);
define_direct_u64_route_harness!(general_direct_u64_n7, general_direct_u64_properties, 7);
define_direct_u64_route_harness!(general_direct_u64_n8, general_direct_u64_properties, 8);
define_direct_u64_route_harness!(stable_direct_u64_n6, stable_direct_u64_properties, 6);
define_direct_u64_route_harness!(stable_direct_u64_n7, stable_direct_u64_properties, 7);
define_direct_u64_route_harness!(stable_direct_u64_n8, stable_direct_u64_properties, 8);

define_direct_u64_route_harness!(general_direct_u64_n9, general_direct_u64_properties, 9);
define_direct_u64_route_harness!(stable_direct_u64_n9, stable_direct_u64_properties, 9);

#[cfg(kani_smallsort_controls)]
define_direct_u64_route_harness!(
    stable_direct_aggregate_u64_n6,
    stable_direct_aggregate_u64_properties,
    6
);
#[cfg(kani_smallsort_controls)]
define_direct_u64_route_harness!(
    stable_direct_aggregate_u64_n7,
    stable_direct_aggregate_u64_properties,
    7
);
#[cfg(kani_smallsort_controls)]
define_direct_u64_route_harness!(
    stable_direct_aggregate_u64_n8,
    stable_direct_aggregate_u64_properties,
    8
);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
fn stable_direct_value_corruption_control_u64_n2() {
    set_value_probe::<u64>();
    let mut v: [u64; 2] = kani::any();
    let orig = v;
    let mut cmp = lt_u64;
    let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();
    let scratch = scratch_view(&mut holder);
    <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, scratch, &mut cmp);
    kani::cover(true, "aggregate stable sort returns before payload corruption");
    // The low bit is payload under lt_u64; sortedness survives this mutation.
    v[0] ^= 1;
    assert_sorted_and_probe_preserved::<u64, _, 2>(&orig, &v, &mut cmp);
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn merge_aggregate_unsorted_halves_control_u64_n4() {
    set_value_probe::<u64>();
    let input: [u64; 4] = [6, 0, 2, 4];
    let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();
    let scratch = scratch_view(&mut holder);
    let src = scratch.as_mut_ptr().cast::<u64>();
    let mut dst: [u64; 4] = kani::any();
    let mut cmp = lt_u64;
    kani::cover(true, "aggregate unsorted-halves call reached");
    // SAFETY: prefix 4 is writable; dst is initialized and disjoint. The left-half
    // keys [3, 0] deliberately violate only the stub's sorted-halves precondition.
    unsafe {
        ptr::copy_nonoverlapping(input.as_ptr(), src, 4);
        bidirectional_merge(crate::slice::from_raw_parts(src, 4), dst.as_mut_ptr(), &mut cmp);
    }
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
fn merge_aggregate_allocation_bounds_control_u64() {
    let mut holder = MaybeUninit::<[u64; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();
    let scratch = scratch_view(&mut holder);
    let outside = scratch.as_mut_ptr().cast::<u64>().wrapping_add(SMALL_SORT_GENERAL_SCRATCH_LEN);
    kani::cover(true, "aggregate allocation bounds control reaches raw write");
    // Deliberately write one past the entire non-ZST allocation, without safe indexing.
    unsafe { ptr::write(outside, 0) };
}

// Flip a payload bit after real sorting: keys stay sorted, full-value counts must detect it.
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::unwind(34)]
fn general_stable_direct_value_corruption_control_u64_n2() {
    set_value_probe::<u64>();
    let mut v: [u64; 2] = kani::any();
    let orig = v;
    let stable: bool = kani::any();
    let mut cmp = lt_u64;
    if stable {
        let mut scratch = [const { MaybeUninit::<u64>::uninit() }; SMALL_SORT_GENERAL_SCRATCH_LEN];
        <u64 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    } else {
        super::super::small_sort_general(&mut v, &mut cmp);
    }
    kani::cover(true, "general/stable direct sort returns before payload corruption");
    v[0] ^= 1;
    assert_sorted_and_probe_preserved::<u64, _, 2>(&orig, &v, &mut cmp);
}

// Match both callers' scratch allocations: only prefix N is initialized, dst is separate.
fn merge_scratch48_length_body<
    T: kani::Arbitrary + Copy + FreezeMarker,
    F: FnMut(&T, &T) -> bool,
    const N: usize,
>(
    mut cmp: F,
) {
    const { assert!(N >= 2 && N <= 32) };
    set_value_probe::<T>();
    let input: [T; N] = kani::any();
    let mut dst: [T; N] = kani::any();
    let stable: bool = kani::any();
    let mut stable_scratch = [MaybeUninit::<T>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let mut general_scratch = MaybeUninit::<[T; SMALL_SORT_GENERAL_SCRATCH_LEN]>::uninit();
    let src = if stable {
        stable_scratch.as_mut_ptr() as *mut T
    } else {
        general_scratch.as_mut_ptr() as *mut T
    };
    // SAFETY: prefix N fits either backing allocation; dst is initialized and disjoint.
    unsafe {
        ptr::copy_nonoverlapping(input.as_ptr(), src, N);
        bidirectional_merge(crate::slice::from_raw_parts(src, N), dst.as_mut_ptr(), &mut cmp);
    }
    kani::cover(!stable, "general scratch48 merge contract checked");
    kani::cover(stable, "stable scratch48 merge contract checked");
}

macro_rules! define_merge_scratch48_contract_harness {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(34)]
        fn $name() {
            merge_scratch48_length_body::<$t, _, $n>($cmp);
        }
    };
}

#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u64_n5, u64, lt_u64, 5);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u64_n6, u64, lt_u64, 6);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u64_n7, u64, lt_u64, 7);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u64_n8, u64, lt_u64, 8);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u8_n5, u8, lt_u8, 5);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u8_n6, u8, lt_u8, 6);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u8_n7, u8, lt_u8, 7);
#[cfg(kani_smallsort_controls)]
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u8_n8, u8, lt_u8, 8);
define_merge_scratch48_contract_harness!(merge_scratch48_contract_u8_n9, u8, lt_u8, 9);

// Correct scratch48/destination memory, but deliberately unsorted left-half keys [3, 0].
#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn merge_scratch48_unsorted_halves_control_u64_n4() {
    set_value_probe::<u64>();
    let input: [u64; 4] = [6, 0, 2, 4];
    let mut scratch = [MaybeUninit::<u64>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let src = scratch.as_mut_ptr() as *mut u64;
    let mut dst: [u64; 4] = kani::any();
    let mut cmp = lt_u64;
    kani::cover(true, "scratch48 unsorted-halves call reached");
    // SAFETY: the two four-element regions are initialized and disjoint.
    unsafe {
        ptr::copy_nonoverlapping(input.as_ptr(), src, 4);
        bidirectional_merge(crate::slice::from_raw_parts(src, 4), dst.as_mut_ptr(), &mut cmp);
    }
}

macro_rules! define_fallback_property_harness {
    ($name:ident, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            if kani::any() {
                fallback_route_properties::<u64, _, $n>(lt_u64);
            } else {
                fallback_route_properties::<u8, _, $n>(lt_u8);
            }
        }
    };
}
define_merge_contract_harness!(merge_contract_u64_n5, u64, lt_u64, 5);
define_merge_contract_harness!(merge_contract_u8_n5, u8, lt_u8, 5);
define_merge_contract_harness!(merge_contract_u64_n6, u64, lt_u64, 6);
define_merge_contract_harness!(merge_contract_u8_n6, u8, lt_u8, 6);
define_merge_contract_harness!(merge_contract_u64_n7, u64, lt_u64, 7);
define_merge_contract_harness!(merge_contract_u8_n7, u8, lt_u8, 7);
define_merge_contract_harness!(merge_contract_u64_n8, u64, lt_u64, 8);
define_merge_contract_harness!(merge_contract_u8_n8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n9, u64, lt_u64, 9);
define_merge_contract_harness!(merge_contract_u8_n9, u8, lt_u8, 9);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n10, u64, lt_u64, 10);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n10, u8, lt_u8, 10);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n11, u64, lt_u64, 11);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n11, u8, lt_u8, 11);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n12, u64, lt_u64, 12);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n12, u8, lt_u8, 12);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n13, u64, lt_u64, 13);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n13, u8, lt_u8, 13);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n14, u64, lt_u64, 14);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n14, u8, lt_u8, 14);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n15, u64, lt_u64, 15);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n15, u8, lt_u8, 15);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u64_n16, u64, lt_u64, 16);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n16, u8, lt_u8, 16);
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n0, u64, lt_u64, 0);
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n0, u8, lt_u8, 0);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n0, 0);
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n1, u64, lt_u64, 1);
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n1, u8, lt_u8, 1);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n1, 1);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n2, u64, lt_u64, 2);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n2, u8, lt_u8, 2);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n2, 2);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n3, u64, lt_u64, 3);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n3, u8, lt_u8, 3);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n3, 3);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n4, u64, lt_u64, 4);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n4, u8, lt_u8, 4);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n4, 4);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n5, u64, lt_u64, 5);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n5, u8, lt_u8, 5);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n5, 5);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n6, u64, lt_u64, 6);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n6, u8, lt_u8, 6);
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n6, 6);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n7, u64, lt_u64, 7);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n7, u8, lt_u8, 7);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n7, 7);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n8, u64, lt_u64, 8);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n8, 8);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n9, u64, lt_u64, 9);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n9, u8, lt_u8, 9);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n9, 9);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n10, u64, lt_u64, 10);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n10, u8, lt_u8, 10);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n10, 10);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n11, u64, lt_u64, 11);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n11, u8, lt_u8, 11);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n11, 11);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n12, u64, lt_u64, 12);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n12, u8, lt_u8, 12);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n12, 12);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n13, u64, lt_u64, 13);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n13, u8, lt_u8, 13);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n13, 13);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n14, u64, lt_u64, 14);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n14, u8, lt_u8, 14);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n14, 14);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n15, u64, lt_u64, 15);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n15, u8, lt_u8, 15);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n15, 15);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u64_n16, u64, lt_u64, 16);
#[cfg(kani_smallsort_controls)]
define_general_sortedness_harness!(general_stable_sorted_permutation_u8_n16, u8, lt_u8, 16);
#[cfg(kani_smallsort_controls)]
define_fallback_property_harness!(fallback_sorted_permutation_u8_u64_n16, 16);

// Per-type fallback correctness on exact N8/9 arrays, with real insertion.
#[cfg(kani_smallsort_controls)]
macro_rules! define_fallback_route_harness {
    ($name:ident, $t:ty, $cmp:expr, $n:literal) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            fallback_route_properties::<$t, _, $n>($cmp);
        }
    };
}

#[cfg(kani_smallsort_controls)]
define_fallback_route_harness!(fallback_sorted_permutation_u64_n8, u64, lt_u64, 8);
#[cfg(kani_smallsort_controls)]
define_fallback_route_harness!(fallback_sorted_permutation_u8_n8, u8, lt_u8, 8);
#[cfg(kani_smallsort_controls)]
define_fallback_route_harness!(fallback_sorted_permutation_u8_n9, u8, lt_u8, 9);

// Optional u8 merge contract diagnostics at exact lengths 20 and 24.
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n20, u8, lt_u8, 20);
#[cfg(kani_smallsort_controls)]
define_merge_contract_harness!(merge_contract_u8_n24, u8, lt_u8, 24);

// Drop values can have padding; test tag multiplicity rather than bytewise equality.
struct DropTaggedValue {
    key: u64,
    tag: u8,
}

static mut DROP_COUNT: usize = 0;

impl crate::ops::Drop for DropTaggedValue {
    fn drop(&mut self) {
        // SAFETY: single-threaded harness, no live references to the counter.
        unsafe {
            let count = ptr::read(ptr::addr_of!(DROP_COUNT));
            ptr::write(ptr::addr_of_mut!(DROP_COUNT), count + 1);
        }
    }
}

fn arbitrary_drop_value_order(a: &DropTaggedValue, b: &DropTaggedValue) -> bool {
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
fn abort_without_order_cover() -> ! {
    kani::assume(false);
    unreachable!()
}

// Separate count/tag proofs: fallback/insertion N2/4/8; general/stable N2/4/8/16, a 48-element
// scratch array.
// Normal return only; duplicate-tag and extra-drop controls distinguish the observations.
fn drop_route_properties<const N: usize, const UPPER: bool, const PERM: bool, const MUTANT: u8>()
-> bool {
    const { assert!(N >= 2 && N <= 32) };
    const { assert!(MUTANT <= 2) };
    // SAFETY: no prior array or counter reference survives into this harness.
    unsafe { ptr::write(ptr::addr_of_mut!(DROP_COUNT), 0) };
    let mut v: [DropTaggedValue; N] =
        crate::array::from_fn(|tag| DropTaggedValue { key: kani::any(), tag: tag as u8 });
    let probe: u8 = kani::any();
    let alternate: bool = kani::any();
    let mut cmp = arbitrary_drop_value_order;
    if UPPER {
        if alternate {
            let mut scratch = [const { MaybeUninit::<DropTaggedValue>::uninit() };
                SMALL_SORT_GENERAL_SCRATCH_LEN];
            <DropTaggedValue as StableSmallSortTypeImpl>::small_sort(
                &mut v,
                &mut scratch,
                &mut cmp,
            );
        } else {
            super::super::small_sort_general(&mut v, &mut cmp);
        }
    } else if alternate {
        super::super::insertion_sort_shift_left(&mut v, 1, &mut cmp);
    } else {
        super::super::small_sort_fallback(&mut v, &mut cmp);
    }
    if MUTANT == 1 {
        // Negative control: duplicate a tag, losing another; addresses remain valid/disjoint.
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
        // Input tags are 0..N, each once; the arbitrary probe also covers absent tags.
        let expected = if (probe as usize) < N { 1 } else { 0 };
        assert!(count == expected);
    }
    crate::mem::drop(v);
    if !PERM {
        // SAFETY: single-threaded harness; the array was explicitly destroyed.
        let count = unsafe { ptr::read(ptr::addr_of!(DROP_COUNT)) };
        assert!(count == N);
    }
    alternate
}

macro_rules! define_drop_route_harness {
    ($name:ident, $n:literal, false, $perm:literal, $abort:ident) => {
        define_drop_route_harness!(@routes $name, $n, false, $perm, $abort,
            "fallback route returns with the property checked",
            "insertion route returns with the property checked");
    };
    ($name:ident, $n:literal, true, $perm:literal, $abort:ident) => {
        define_drop_route_harness!(@routes $name, $n, true, $perm, $abort,
            "general route returns with the property checked",
            "stable route returns with the property checked");
    };
    (@routes $name:ident, $n:literal, $upper:literal, $perm:literal,
        $abort:ident, $first:literal, $second:literal) => {
        #[kani::proof]
        #[kani::stub(crate::slice::sort::shared::smallsort::panic_on_ord_violation, $abort)]
        #[kani::unwind(34)]
        fn $name() {
            let alternate = drop_route_properties::<$n, $upper, $perm, 0>();
            kani::cover(!alternate, $first);
            kani::cover(alternate, $second);
        }
    };
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_on_order_violation
)]
#[kani::unwind(34)]
fn drop_general_reachability_control_n2() {
    let alternate = drop_route_properties::<2, true, false, 0>();
    kani::cover(!alternate, "general route returns with the property checked");
    kani::cover(alternate, "stable route returns with the property checked");
    let drop_control_value: u64 = kani::any();
    assert!(drop_control_value != drop_control_value);
}

#[cfg(kani_smallsort_controls)]
define_drop_route_harness!(drop_general_reachability_n2, 2, true, false, abort_on_order_violation);
define_drop_route_harness!(drop_fallback_drop_count_n2, 2, false, false, abort_without_order_cover);
define_drop_route_harness!(
    drop_fallback_tag_permutation_n2,
    2,
    false,
    true,
    abort_without_order_cover
);
define_drop_route_harness!(drop_fallback_drop_count_n4, 4, false, false, abort_without_order_cover);
define_drop_route_harness!(
    drop_fallback_tag_permutation_n4,
    4,
    false,
    true,
    abort_without_order_cover
);
define_drop_route_harness!(drop_fallback_drop_count_n8, 8, false, false, abort_without_order_cover);
define_drop_route_harness!(
    drop_fallback_tag_permutation_n8,
    8,
    false,
    true,
    abort_without_order_cover
);
define_drop_route_harness!(drop_general_drop_count_n2, 2, true, false, abort_on_order_violation);
define_drop_route_harness!(
    drop_general_tag_permutation_n2,
    2,
    true,
    true,
    abort_on_order_violation
);
define_drop_route_harness!(drop_general_drop_count_n4, 4, true, false, abort_on_order_violation);
define_drop_route_harness!(
    drop_general_tag_permutation_n4,
    4,
    true,
    true,
    abort_on_order_violation
);
define_drop_route_harness!(drop_general_drop_count_n8, 8, true, false, abort_on_order_violation);
define_drop_route_harness!(
    drop_general_tag_permutation_n8,
    8,
    true,
    true,
    abort_on_order_violation
);
define_drop_route_harness!(drop_general_drop_count_n16, 16, true, false, abort_on_order_violation);
#[cfg(kani_smallsort_controls)]
define_drop_route_harness!(
    drop_general_tag_permutation_n16,
    16,
    true,
    true,
    abort_on_order_violation
);

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_without_order_cover
)]
#[kani::unwind(34)]
fn drop_duplicate_tag_control_n2() {
    kani::cover(true, "duplicate-tag control entered");
    drop_route_properties::<2, false, true, 1>();
}

#[cfg(kani_smallsort_controls)]
#[kani::proof]
#[kani::stub(
    crate::slice::sort::shared::smallsort::panic_on_ord_violation,
    abort_without_order_cover
)]
#[kani::unwind(34)]
fn drop_extra_drop_control_n2() {
    kani::cover(true, "extra-drop control entered");
    drop_route_properties::<2, false, false, 2>();
}

// Direct u8 N9 routes retain nonconst scratch and the shared full-value oracle.
fn general_direct_u8_n9_properties() {
    set_value_probe::<u8>();
    let mut v: [u8; 9] = kani::any();
    let orig = v;
    let mut cmp = lt_u8;
    super::super::small_sort_general(&mut v, &mut cmp);
    assert_sorted_and_probe_preserved::<u8, _, 9>(&orig, &v, &mut cmp);
    kani::cover(true, "general route properties checked");
}

fn stable_direct_nonconst_u8_n9_properties() {
    set_value_probe::<u8>();
    let mut v: [u8; 9] = kani::any();
    let orig = v;
    let mut cmp = lt_u8;
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    <u8 as StableSmallSortTypeImpl>::small_sort(&mut v, &mut scratch, &mut cmp);
    assert_sorted_and_probe_preserved::<u8, _, 9>(&orig, &v, &mut cmp);
    kani::cover(true, "stable route properties checked");
}

macro_rules! define_direct_u8_n9_route_harness {
    ($name:ident, $body:ident) => {
        #[kani::proof]
        #[kani::unwind(34)]
        fn $name() {
            $body();
        }
    };
}

define_direct_u8_n9_route_harness!(general_direct_u8_n9, general_direct_u8_n9_properties);

define_direct_u8_n9_route_harness!(
    stable_direct_nonconst_u8_n9,
    stable_direct_nonconst_u8_n9_properties
);
