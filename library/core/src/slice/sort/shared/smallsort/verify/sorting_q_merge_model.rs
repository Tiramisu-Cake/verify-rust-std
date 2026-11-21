//! Byte and cursor contracts for Pilot 11's exact u8/KeyLess<u8> profile.

use super::sorting_model::KeyLess;
use crate::{ptr, ub_checks};

const INSERT_LEN: usize = 10;

// The fallback does not read the comparator or element memory. In particular,
// lifted old(...) expressions can call it before any postcondition guard.
trait ByteModel<T, F> {
    fn active() -> bool;
    fn threshold(f: &F) -> Option<u8>;
}

impl<T, F> ByteModel<T, F> for () {
    default fn active() -> bool {
        false
    }

    default fn threshold(_f: &F) -> Option<u8> {
        None
    }
}

impl ByteModel<u8, KeyLess<u8>> for () {
    fn active() -> bool {
        true
    }

    fn threshold(f: &KeyLess<u8>) -> Option<u8> {
        Some(f.q())
    }
}

pub(super) fn active<T, F>() -> bool {
    <() as ByteModel<T, F>>::active()
}

fn offset_in_allocation(p: *const u8, offset: isize) -> bool {
    (p as isize).checked_add(offset).is_some()
        && ptr::byte_offset_does_not_wrap(p, offset)
        && ub_checks::same_allocation(p, p.wrapping_offset(offset))
}

fn readable_at(base: *const u8, index: usize) -> Option<*const u8> {
    if index > isize::MAX as usize || !offset_in_allocation(base, index as isize) {
        return None;
    }
    let p = base.wrapping_add(index);
    ub_checks::can_dereference(p).then_some(p)
}

pub(in crate::slice::sort::shared::smallsort) fn swap_capture<T, F>(
    base: *const T,
    a: usize,
    b: usize,
) -> Option<(u8, u8)> {
    if !active::<T, F>() {
        return None;
    }
    let a = readable_at(base.cast(), a)?;
    let b = readable_at(base.cast(), b)?;
    // SAFETY: the exact pair has T = u8, and both reads were checked above.
    Some(unsafe { (*a, *b) })
}

pub(in crate::slice::sort::shared::smallsort) fn swap_byte_post<T, F>(
    before: Option<(u8, u8)>,
    base: *const T,
    a: usize,
    b: usize,
) -> bool {
    !active::<T, F>()
        || before
            .is_some_and(|(x, y)| swap_capture::<T, F>(base, a, b) == Some((x.min(y), x.max(y))))
}

pub(super) fn numeric_order(bytes: &[u8]) -> bool {
    bytes.windows(2).all(|pair| pair[0] <= pair[1])
}

fn read_order(begin: *const u8, len: usize) -> Option<bool> {
    let end = len.checked_sub(1)?;
    if len > INSERT_LEN
        || !offset_in_allocation(begin, end as isize)
        || !ub_checks::can_dereference(ptr::slice_from_raw_parts(begin, len))
    {
        return None;
    }
    // SAFETY: the checks cover the full initialized span in a single allocation.
    Some(numeric_order(unsafe {
        crate::slice::from_raw_parts(begin, len)
    }))
}

pub(in crate::slice::sort::shared::smallsort) fn insert_capture<T, F>(
    begin: *const T,
    len: usize,
) -> Option<bool> {
    if !active::<T, F>() || len != INSERT_LEN {
        return None;
    }
    read_order(begin.cast(), INSERT_LEN - 1)
}

pub(in crate::slice::sort::shared::smallsort) fn insert_numeric_post<T, F>(
    prefix_ordered: Option<bool>,
    begin: *const T,
    len: usize,
) -> bool {
    if !active::<T, F>() || len != INSERT_LEN {
        return true;
    }
    match prefix_ordered {
        Some(false) => true,
        Some(true) => read_order(begin.cast(), INSERT_LEN) == Some(true),
        None => false,
    }
}

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) enum Direction {
    Up,
    Down,
}

pub(in crate::slice::sort::shared::smallsort) fn step_pre<T, F>(
    left: *const T,
    right: *const T,
    dst: *mut T,
    direction: Direction,
) -> bool {
    if !active::<T, F>() {
        return true;
    }
    let left = left.cast::<u8>();
    let right = right.cast::<u8>();
    let dst = dst.cast::<u8>();
    ub_checks::can_dereference(left)
        && ub_checks::can_dereference(right)
        && ub_checks::can_write(dst)
        && left != dst.cast_const()
        && right != dst.cast_const()
        && match direction {
            Direction::Up => {
                offset_in_allocation(left, 1)
                    && offset_in_allocation(right, 1)
                    && offset_in_allocation(dst, 1)
            }
            Direction::Down => offset_in_allocation(dst, -1),
        }
}

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct StepSnapshot {
    left: *const u8,
    right: *const u8,
    dst: *mut u8,
    left_byte: u8,
    right_byte: u8,
    q: u8,
}

pub(in crate::slice::sort::shared::smallsort) fn step_capture<T, F>(
    left: *const T,
    right: *const T,
    dst: *mut T,
    f: &F,
) -> Option<StepSnapshot> {
    let q = <() as ByteModel<T, F>>::threshold(f)?;
    let left = readable_at(left.cast(), 0)?;
    let right = readable_at(right.cast(), 0)?;
    // SAFETY: the exact pair has T = u8, and both source reads were checked.
    // The destination is saved as a pointer value only.
    let (left_byte, right_byte) = unsafe { (*left, *right) };
    Some(StepSnapshot {
        left,
        right,
        dst: dst.cast(),
        left_byte,
        right_byte,
        q,
    })
}

impl StepSnapshot {
    fn written_byte(self) -> Option<u8> {
        if !ub_checks::can_dereference(self.dst) {
            return None;
        }
        // SAFETY: checked for a single byte at the original destination after the copy.
        Some(unsafe { *self.dst })
    }

    fn up_takes_right(self) -> bool {
        self.right_byte < self.left_byte
    }
}

pub(in crate::slice::sort::shared::smallsort) fn step_byte_post<T, F>(
    before: Option<StepSnapshot>,
    direction: Direction,
) -> bool {
    !active::<T, F>()
        || before.is_some_and(|before| {
            let expected = match (direction, before.up_takes_right()) {
                (Direction::Up, true) | (Direction::Down, false) => before.right_byte,
                (Direction::Up, false) | (Direction::Down, true) => before.left_byte,
            };
            before.written_byte() == Some(expected)
        })
}

pub(in crate::slice::sort::shared::smallsort) fn step_q_post<T, F>(
    before: Option<StepSnapshot>,
    f: &F,
    direction: Direction,
) -> bool {
    !active::<T, F>()
        || before.is_some_and(|before| {
            let left = before.left_byte >= before.q;
            let right = before.right_byte >= before.q;
            let expected = match direction {
                Direction::Up => left && right,
                Direction::Down => left || right,
            };
            <() as ByteModel<T, F>>::threshold(f) == Some(before.q)
                && before
                    .written_byte()
                    .is_some_and(|byte| (byte >= before.q) == expected)
        })
}

type Cursors<T> = (*const T, *const T, *mut T);

fn cursors_are<T>(actual: &Cursors<T>, expected: Cursors<u8>) -> bool {
    (actual.0.cast(), actual.1.cast(), actual.2.cast()) == expected
}

fn up_cursors<T>(before: StepSnapshot, actual: &Cursors<T>, take_right: bool) -> bool {
    let left = before.left.wrapping_add(usize::from(!take_right));
    let right = before.right.wrapping_add(usize::from(take_right));
    cursors_are(actual, (left, right, before.dst.wrapping_add(1)))
}

#[cfg(not(kani_smallsort_q_merge_bad_tie))]
pub(in crate::slice::sort::shared::smallsort) fn merge_up_cursors<T, F>(
    before: Option<StepSnapshot>,
    actual: &Cursors<T>,
) -> bool {
    !active::<T, F>()
        || before.is_some_and(|before| up_cursors(before, actual, before.up_takes_right()))
}

#[cfg(kani_smallsort_q_merge_bad_tie)]
pub(in crate::slice::sort::shared::smallsort) fn merge_up_wrong_tie_cursors<T, F>(
    before: Option<StepSnapshot>,
    actual: &Cursors<T>,
) -> bool {
    !active::<T, F>()
        || before
            .is_some_and(|before| up_cursors(before, actual, before.right_byte <= before.left_byte))
}

pub(in crate::slice::sort::shared::smallsort) fn merge_down_cursors<T, F>(
    before: Option<StepSnapshot>,
    actual: &Cursors<T>,
) -> bool {
    !active::<T, F>()
        || before.is_some_and(|before| {
            let take_left = before.up_takes_right();
            let left = before.left.wrapping_sub(usize::from(take_left));
            let right = before.right.wrapping_sub(usize::from(!take_left));
            cursors_are(actual, (left, right, before.dst.wrapping_sub(1)))
        })
}
