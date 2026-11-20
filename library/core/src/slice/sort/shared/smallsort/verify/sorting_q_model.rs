//! Owned threshold summaries for the exact u8/KeyLess<u8> pair.

use super::sorting_model::KeyLess;
use crate::{ptr, ub_checks};

const CAP: usize = 17;
const PREFIX: usize = 13;

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct SwapSnapshot {
    q: u8,
    bits: Option<(bool, bool)>,
}

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct Snapshot {
    q: u8,
    len: usize,
    bits: u32,
}

impl Snapshot {
    const INVALID: Self = Self { q: 0, len: 0, bits: 0 };
}

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct PrefixSnapshot {
    q: u8,
    valid: bool,
    target: u32,
    tail: [u8; CAP - PREFIX],
}

// These methods specialize on the exact pair. The inactive implementation
// dispatches no reads, including when old(...) runs outside the ensures guard.
trait Model<T, F> {
    fn active() -> bool;
    fn q(f: &F) -> u8;
    fn pair(base: *const T, a: usize, b: usize, q: u8) -> Option<(bool, bool)>;
    fn span(begin: *mut T, len: usize, q: u8) -> Snapshot;
    fn prefix(values: &[T], q: u8) -> PrefixSnapshot;
    fn prefix_matches(before: PrefixSnapshot, values: &[T], q: u8) -> bool;
}

impl<T, F> Model<T, F> for () {
    default fn active() -> bool {
        false
    }

    default fn q(_f: &F) -> u8 {
        0
    }

    default fn pair(_base: *const T, _a: usize, _b: usize, _q: u8) -> Option<(bool, bool)> {
        None
    }

    default fn span(_begin: *mut T, _len: usize, _q: u8) -> Snapshot {
        Snapshot::INVALID
    }

    default fn prefix(_values: &[T], q: u8) -> PrefixSnapshot {
        PrefixSnapshot { q, valid: false, target: 0, tail: [0; CAP - PREFIX] }
    }

    default fn prefix_matches(_before: PrefixSnapshot, _values: &[T], _q: u8) -> bool {
        true
    }
}

impl Model<u8, KeyLess<u8>> for () {
    fn active() -> bool {
        true
    }

    fn q(f: &KeyLess<u8>) -> u8 {
        f.q()
    }

    fn pair(base: *const u8, a: usize, b: usize, q: u8) -> Option<(bool, bool)> {
        let a = readable_at(base, a)?;
        let b = readable_at(base, b)?;
        // SAFETY: readable_at checks each pointer before this capture.
        Some(unsafe { (*a >= q, *b >= q) })
    }

    fn span(begin: *mut u8, len: usize, q: u8) -> Snapshot {
        if !(2..=CAP).contains(&len)
            || readable_at(begin, len - 1).is_none()
            || !ub_checks::can_dereference(ptr::slice_from_raw_parts(begin, len))
            || !ub_checks::can_write(ptr::slice_from_raw_parts_mut(begin, len))
        {
            return Snapshot::INVALID;
        }

        // SAFETY: the length and pointer checks above establish a readable in-allocation span.
        let bits = unsafe { threshold_mask(begin, len, q) };
        Snapshot { q, len, bits }
    }

    fn prefix(values: &[u8], q: u8) -> PrefixSnapshot {
        let mut snapshot = PrefixSnapshot { q, valid: false, target: 0, tail: [0; CAP - PREFIX] };
        if values.len() == CAP {
            snapshot.valid = true;
            snapshot.target = order_target(&values[..PREFIX], q);
            snapshot.tail.copy_from_slice(&values[PREFIX..]);
        }
        snapshot
    }

    fn prefix_matches(before: PrefixSnapshot, values: &[u8], q: u8) -> bool {
        before.valid
            && before.q == q
            && values.len() == CAP
            && order_post(&values[..PREFIX], q, &before.target)
            && values[PREFIX..] == before.tail
    }
}

fn readable_at(base: *const u8, index: usize) -> Option<*const u8> {
    if index > isize::MAX as usize
        || (base as isize).checked_add(index as isize).is_none()
        || !ptr::byte_offset_does_not_wrap(base, index as isize)
    {
        return None;
    }
    let p = base.wrapping_add(index);
    (ub_checks::same_allocation(base, p) && ub_checks::can_dereference(p)).then_some(p)
}

fn low_mask(len: usize) -> u32 {
    (1_u32 << len) - 1
}

// SAFETY: len must be at most CAP, and begin must be readable for len bytes.
unsafe fn threshold_mask(begin: *const u8, len: usize, q: u8) -> u32 {
    let mut bits = 0;
    // Keep the offsets constant when the caller's length is symbolic.
    macro_rules! read_bits {
        ($($i:literal),+ $(,)?) => {
            $(
                if $i < len {
                    // SAFETY: the caller guarantees readability up to len.
                    let value = unsafe { *begin.add($i) };
                    bits |= u32::from(value >= q) << $i;
                }
            )+
        };
    }
    read_bits!(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16);
    bits
}

pub(in crate::slice::sort::shared::smallsort) fn active<T, F>() -> bool {
    <() as Model<T, F>>::active()
}

pub(in crate::slice::sort::shared::smallsort) fn swap_capture<T, F>(
    base: *const T,
    a: usize,
    b: usize,
    f: &F,
) -> SwapSnapshot {
    let q = <() as Model<T, F>>::q(f);
    SwapSnapshot { q, bits: <() as Model<T, F>>::pair(base, a, b, q) }
}

fn pair_matches<T, F>(
    before: SwapSnapshot,
    base: *const T,
    a: usize,
    b: usize,
    f: &F,
    left: impl FnOnce(bool, bool) -> bool,
) -> bool {
    if !active::<T, F>() {
        return true;
    }
    let Some((x, y)) = before.bits else { return false };
    let q = <() as Model<T, F>>::q(f);
    q == before.q && <() as Model<T, F>>::pair(base, a, b, q) == Some((left(x, y), x || y))
}

#[cfg(not(kani_smallsort_q_controls))]
pub(in crate::slice::sort::shared::smallsort) fn swap_post<T, F>(
    before: SwapSnapshot,
    base: *const T,
    a: usize,
    b: usize,
    f: &F,
) -> bool {
    pair_matches(before, base, a, b, f, |x, y| x && y)
}

#[cfg(kani_smallsort_q_controls)]
pub(in crate::slice::sort::shared::smallsort) fn swap_false_or_post<T, F>(
    before: SwapSnapshot,
    base: *const T,
    a: usize,
    b: usize,
    f: &F,
) -> bool {
    pair_matches(before, base, a, b, f, |x, y| x || y)
}

pub(in crate::slice::sort::shared::smallsort) fn capture<T, F>(
    begin: *mut T,
    len: usize,
    f: &F,
) -> Snapshot {
    <() as Model<T, F>>::span(begin, len, <() as Model<T, F>>::q(f))
}

pub(in crate::slice::sort::shared::smallsort) fn insert_pre<T, F>(
    begin: *mut T,
    len: usize,
    f: &F,
) -> bool {
    if !active::<T, F>() {
        return true;
    }
    let before = capture(begin, len, f);
    if before.len < 2 {
        return false;
    }
    let prefix_mask = low_mask(before.len - 1);
    let prefix = before.bits & prefix_mask;
    ((prefix << 1) & prefix_mask & !prefix) == 0
}

pub(in crate::slice::sort::shared::smallsort) fn insert_post<T, F>(
    before: Snapshot,
    begin: *mut T,
    len: usize,
    f: &F,
) -> bool {
    if !active::<T, F>() {
        return true;
    }
    let after = capture(begin, len, f);
    if before.len < 2 || before.len != after.len || before.q != after.q {
        return false;
    }
    let expected = if before.bits & (1 << (len - 1)) != 0 {
        before.bits
    } else {
        (before.bits << 1) & low_mask(len)
    };
    after.bits == expected
}

pub(in crate::slice::sort::shared::smallsort) fn prefix_capture<T, F>(
    values: &[T],
    f: &F,
) -> PrefixSnapshot {
    <() as Model<T, F>>::prefix(values, <() as Model<T, F>>::q(f))
}

pub(in crate::slice::sort::shared::smallsort) fn prefix_post<T, F>(
    before: PrefixSnapshot,
    values: &[T],
    f: &F,
) -> bool {
    <() as Model<T, F>>::prefix_matches(before, values, <() as Model<T, F>>::q(f))
}

pub(super) fn order_target(values: &[u8], q: u8) -> u32 {
    let len = values.len();
    assert!(len <= CAP);
    // SAFETY: the slice is readable for len bytes, and the length is at most CAP.
    let count = unsafe { threshold_mask(values.as_ptr(), len, q) }.count_ones() as usize;
    low_mask(len) ^ low_mask(len - count)
}

pub(super) fn order_post(values: &[u8], q: u8, target: &u32) -> bool {
    let len = values.len();
    if len > CAP {
        return false;
    }
    // SAFETY: the slice is readable for len bytes, and the length is at most CAP.
    let bits = unsafe { threshold_mask(values.as_ptr(), len, q) };
    bits == (*target & low_mask(len))
}
