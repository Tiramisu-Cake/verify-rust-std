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
    bits: [bool; CAP],
}

impl Snapshot {
    const INVALID: Self = Self { q: 0, len: 0, bits: [false; CAP] };
}

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct PrefixSnapshot {
    q: u8,
    valid: bool,
    target: [bool; CAP],
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
        PrefixSnapshot { q, valid: false, target: [false; CAP], tail: [0; CAP - PREFIX] }
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

        let mut snapshot = Snapshot { q, len, bits: [false; CAP] };
        for i in 0..len {
            // SAFETY: the checks above establish a readable in-allocation span.
            snapshot.bits[i] = unsafe { *begin.add(i) >= q };
        }
        snapshot
    }

    fn prefix(values: &[u8], q: u8) -> PrefixSnapshot {
        let mut snapshot =
            PrefixSnapshot { q, valid: false, target: [false; CAP], tail: [0; CAP - PREFIX] };
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
    before.len >= 2 && (1..before.len - 1).all(|i| !before.bits[i - 1] || before.bits[i])
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
    if before.bits[len - 1] {
        (0..len).all(|i| after.bits[i] == before.bits[i])
    } else {
        !after.bits[0] && (1..len).all(|i| after.bits[i] == before.bits[i - 1])
    }
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

pub(super) fn order_target(values: &[u8], q: u8) -> [bool; CAP] {
    assert!(values.len() <= CAP);
    // After processing i input bits, at_least[k] means at least k of those bits
    // are set. The descending update uses the old at_least[k - 1].
    let mut at_least = [false; CAP + 1];
    at_least[0] = true;
    for (i, &value) in values.iter().enumerate() {
        let bit = value >= q;
        for k in (1..=i + 1).rev() {
            at_least[k] |= bit && at_least[k - 1];
        }
    }
    let mut target = [false; CAP];
    for i in 0..values.len() {
        target[i] = at_least[values.len() - i];
    }
    target
}

pub(super) fn order_post(values: &[u8], q: u8, target: &[bool; CAP]) -> bool {
    values.len() <= CAP && values.iter().zip(target).all(|(&value, &bit)| (value >= q) == bit)
}
