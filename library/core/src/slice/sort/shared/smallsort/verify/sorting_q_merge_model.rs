//! Byte and cursor contracts for Pilot 11's exact u8/KeyLess<u8> profile.

use super::sorting_model::KeyLess;
use crate::{ptr, ub_checks};

const INSERT_LEN: usize = 10;

fn supported_insert_len(len: usize) -> bool {
    if cfg!(kani_smallsort_q_merge_wide) {
        matches!(len, 10..=12 | 14..=16)
    } else {
        len == INSERT_LEN
    }
}

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
    if len > 16
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
    if !active::<T, F>() || !supported_insert_len(len) {
        return None;
    }
    read_order(begin.cast(), len - 1)
}

pub(in crate::slice::sort::shared::smallsort) fn insert_numeric_post<T, F>(
    prefix_ordered: Option<bool>,
    begin: *const T,
    len: usize,
) -> bool {
    if !active::<T, F>() || !supported_insert_len(len) {
        return true;
    }
    match prefix_ordered {
        Some(false) => true,
        Some(true) => read_order(begin.cast(), len) == Some(true),
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

#[cfg(all(
    kani_smallsort_q_merge_b,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
pub(in crate::slice::sort::shared::smallsort) mod merge_b {
    use super::{ByteModel, active, numeric_order};
    use crate::slice::sort::shared::smallsort::merge_contract_regions_disjoint;
    use crate::{ptr, ub_checks};

    const LEFT_LEN: usize = 9;

    fn supported_len(len: usize) -> bool {
        matches!(len, 18 | 19)
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_geometry<T, F>(
        input: &[T],
        dst: *mut T,
    ) -> bool {
        !active::<T, F>()
            || (supported_len(input.len())
                && ub_checks::can_dereference(input as *const [T])
                && ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, input.len()))
                && merge_contract_regions_disjoint(input.as_ptr(), dst, input.len()))
    }

    fn merge_input<T, F>(input: &[T]) -> Option<&[u8]> {
        if !active::<T, F>()
            || !supported_len(input.len())
            || !ub_checks::can_dereference(input as *const [T])
        {
            return None;
        }
        // SAFETY: the active pair has T = u8, and the initialized source span is readable.
        Some(unsafe { crate::slice::from_raw_parts(input.as_ptr().cast(), input.len()) })
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_halves_numeric_order<T, F>(
        input: &[T],
    ) -> bool {
        !active::<T, F>()
            || merge_input::<T, F>(input).is_some_and(|bytes| {
                let (left, right) = bytes.split_at(LEFT_LEN);
                numeric_order(left) && numeric_order(right)
            })
    }

    #[derive(Clone, Copy)]
    pub(in crate::slice::sort::shared::smallsort) struct MergeSnapshot {
        q: u8,
        len: usize,
        target: u32,
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_capture<T, F>(
        input: &[T],
        f: &F,
    ) -> Option<MergeSnapshot> {
        let q = <() as ByteModel<T, F>>::threshold(f)?;
        let input = merge_input::<T, F>(input)?;
        let len = input.len();
        let below = input.iter().filter(|&&byte| byte < q).count();
        // The sorted threshold mask has zeros below q and ones in the rest of the span.
        let target = (1_u32 << len) - (1_u32 << below);
        Some(MergeSnapshot { q, len, target })
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_q_post<T, F>(
        before: Option<MergeSnapshot>,
        dst: *mut T,
        f: &F,
    ) -> bool {
        let Some(q) = <() as ByteModel<T, F>>::threshold(f) else {
            return true;
        };
        let Some(before) = before else {
            return false;
        };
        let output = ptr::slice_from_raw_parts(dst.cast::<u8>(), before.len);
        if q != before.q || !ub_checks::can_dereference(output) {
            return false;
        }
        // SAFETY: Check reads after normal return, when the two write streams and
        // the N19 odd copy have initialized this span. Replace havocs this same span.
        let output = unsafe { &*output };
        let mask = output
            .iter()
            .enumerate()
            .fold(0, |mask, (i, &byte)| mask | (u32::from(byte >= q) << i));
        mask == before.target
    }
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
pub(in crate::slice::sort::shared::smallsort) mod sort9 {
    use super::{ByteModel, active, numeric_order};
    use crate::ub_checks;

    const PREFIX_LEN: usize = 9;

    fn in_domain<T, F>(v: &[T]) -> bool {
        active::<T, F>() && matches!(v.len(), 9 | 10)
    }

    pub(in crate::slice::sort::shared::smallsort) fn geometry<T, F>(v: &mut [T]) -> bool {
        in_domain::<T, F>(v)
            && ub_checks::can_dereference(v as *const [T])
            && ub_checks::can_write(v.as_mut_ptr().cast::<[T; PREFIX_LEN]>())
    }

    fn prefix<T, F>(v: &[T]) -> Option<&[u8]> {
        if !in_domain::<T, F>(v) {
            return None;
        }
        // SAFETY: the exact pair has T = u8 and the shared slice covers nine initialized bytes.
        Some(unsafe { crate::slice::from_raw_parts(v.as_ptr().cast(), PREFIX_LEN) })
    }

    pub(in crate::slice::sort::shared::smallsort) fn numeric_post<T, F>(v: &[T]) -> bool {
        prefix::<T, F>(v).is_some_and(numeric_order)
    }

    #[derive(Clone, Copy)]
    pub(in crate::slice::sort::shared::smallsort) struct Snapshot {
        q: u8,
        below: usize,
    }

    fn count_below(bytes: &[u8], q: u8) -> usize {
        bytes.iter().filter(|&&byte| byte < q).count()
    }

    pub(in crate::slice::sort::shared::smallsort) fn capture<T, F>(
        v: &[T],
        f: &F,
    ) -> Option<Snapshot> {
        let prefix = prefix::<T, F>(v)?;
        let q = <() as ByteModel<T, F>>::threshold(f)?;
        Some(Snapshot {
            q,
            below: count_below(prefix, q),
        })
    }

    pub(in crate::slice::sort::shared::smallsort) fn q_post<T, F>(
        before: Option<Snapshot>,
        v: &[T],
        f: &F,
    ) -> bool {
        // Numeric order makes the below-threshold bytes a contiguous prefix.
        // Its length therefore determines the entire threshold mask.
        before.is_some_and(|before| {
            capture(v, f).is_some_and(|after| after.q == before.q && after.below == before.below)
        })
    }
}

#[cfg(all(
    kani_smallsort_q_merge_b,
    kani_smallsort_q_merge_sort9,
    kani_smallsort_q_merge_wide,
    not(any(
        kani_smallsort_s2_assumed,
        kani_smallsort_q_controls,
        kani_smallsort_q_merge_bad_tie
    )),
))]
pub(in crate::slice::sort::shared::smallsort) mod merge_wide {
    use super::{ByteModel, active, numeric_order};
    use crate::slice::sort::shared::smallsort::merge_contract_regions_disjoint;
    use crate::{ptr, ub_checks};

    fn presort_readable<T, F, const PREFIX: usize>(v: &[T]) -> bool {
        active::<T, F>()
            && match PREFIX {
                9 => matches!(v.len(), 9..=12),
                #[cfg(kani_smallsort_q_no_merge_sort13)]
                13 => matches!(v.len(), 13..=17),
                #[cfg(not(kani_smallsort_q_no_merge_sort13))]
                13 => matches!(v.len(), 13..=16),
                _ => false,
            }
            && ub_checks::can_dereference(v as *const [T])
    }

    pub(in crate::slice::sort::shared::smallsort) fn presort_geometry<T, F, const PREFIX: usize>(
        v: &mut [T],
    ) -> bool {
        presort_readable::<T, F, PREFIX>(v)
            && ub_checks::can_write(v.as_mut_ptr().cast::<[T; PREFIX]>())
    }

    fn presort_prefix<T, F, const PREFIX: usize>(v: &[T]) -> Option<&[u8]> {
        if !presort_readable::<T, F, PREFIX>(v) {
            return None;
        }
        // SAFETY: the exact pair has T = u8 and the checked span contains PREFIX bytes.
        Some(unsafe { crate::slice::from_raw_parts(v.as_ptr().cast(), PREFIX) })
    }

    #[derive(Clone, Copy)]
    pub(in crate::slice::sort::shared::smallsort) struct PrefixSnapshot {
        q: u8,
        below: usize,
    }

    pub(in crate::slice::sort::shared::smallsort) fn presort_capture<T, F, const PREFIX: usize>(
        v: &[T],
        f: &F,
    ) -> Option<PrefixSnapshot> {
        let prefix = presort_prefix::<T, F, PREFIX>(v)?;
        let q = <() as ByteModel<T, F>>::threshold(f)?;
        #[cfg(all(kani_smallsort_q_no_merge_sort13, kani_smallsort_q_compact_presort13))]
        if PREFIX == 13 {
            let mut below = 0_u8;
            let mut i = 0;
            while i < 13 {
                below += u8::from(prefix[i] < q);
                i += 1;
            }
            return Some(PrefixSnapshot { q, below: usize::from(below) });
        }
        Some(PrefixSnapshot { q, below: prefix.iter().filter(|&&byte| byte < q).count() })
    }

    pub(in crate::slice::sort::shared::smallsort) fn presort_post<T, F, const PREFIX: usize>(
        before: Option<PrefixSnapshot>,
        v: &[T],
        f: &F,
    ) -> bool {
        let (Some(before), Some(prefix), Some(q)) =
            (before, presort_prefix::<T, F, PREFIX>(v), <() as ByteModel<T, F>>::threshold(f))
        else {
            return false;
        };
        #[cfg(all(kani_smallsort_q_no_merge_sort13, kani_smallsort_q_compact_presort13))]
        if PREFIX == 13 {
            if q != before.q {
                return false;
            }
            let mut previous = prefix[0];
            let mut below = u8::from(previous < q);
            let mut i = 1;
            while i < 13 {
                let byte = prefix[i];
                if previous > byte {
                    return false;
                }
                below += u8::from(byte < q);
                previous = byte;
                i += 1;
            }
            return usize::from(below) == before.below;
        }
        // Order and count determine every bit of the threshold mask.
        q == before.q
            && numeric_order(prefix)
            && prefix.iter().filter(|&&byte| byte < q).count() == before.below
    }

    fn supported_merge_len(len: usize) -> bool {
        matches!(len, 20..=32)
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_geometry<T, F>(
        input: &[T],
        dst: *mut T,
    ) -> bool {
        active::<T, F>()
            && supported_merge_len(input.len())
            && ub_checks::can_dereference(input as *const [T])
            && ub_checks::can_write(ptr::slice_from_raw_parts_mut(dst, input.len()))
            && merge_contract_regions_disjoint(input.as_ptr(), dst, input.len())
    }

    fn merge_input<T, F>(input: &[T]) -> Option<&[u8]> {
        if !active::<T, F>()
            || !supported_merge_len(input.len())
            || !ub_checks::can_dereference(input as *const [T])
        {
            return None;
        }
        // SAFETY: the exact pair has T = u8, and the initialized source span is readable.
        Some(unsafe { crate::slice::from_raw_parts(input.as_ptr().cast(), input.len()) })
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_halves_numeric_order<T, F>(
        input: &[T],
    ) -> bool {
        merge_input::<T, F>(input).is_some_and(|bytes| {
            let (left, right) = bytes.split_at(bytes.len() / 2);
            numeric_order(left) && numeric_order(right)
        })
    }

    #[derive(Clone, Copy)]
    pub(in crate::slice::sort::shared::smallsort) struct MergeSnapshot {
        q: u8,
        len: usize,
        target: MergeTarget,
    }

    #[derive(Clone, Copy)]
    enum MergeTarget {
        Mask(u32),
        // Captured only for the 32-byte span.
        #[cfg(kani_smallsort_q_compact_merge32)]
        Below(u8),
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_target_mask(input: &[u8], q: u8) -> u32 {
        let below = input.iter().filter(|&&byte| byte < q).count();
        // 0 <= below <= len <= 32. The intermediate needs 33 bits at len == 32.
        ((1_u64 << input.len()) - (1_u64 << below)) as u32
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_matches_mask(
        output: &[u8],
        q: u8,
        target: u32,
    ) -> bool {
        let mask = output
            .iter()
            .enumerate()
            .fold(0, |mask, (i, &byte)| mask | (u32::from(byte >= q) << i));
        mask == target
    }

    #[cfg(kani_smallsort_q_compact_merge32)]
    pub(in crate::slice::sort::shared::smallsort) fn merge32_count_below(
        input: &[u8],
        q: u8,
    ) -> u8 {
        let mut below = 0_u8;
        let mut i = 0;
        while i < 32 {
            below += u8::from(input[i] < q);
            i += 1;
        }
        below
    }

    #[cfg(kani_smallsort_q_compact_merge32)]
    pub(in crate::slice::sort::shared::smallsort) fn merge32_matches_below(
        output: &[u8],
        q: u8,
        below: u8,
    ) -> bool {
        let mut matches = true;
        let mut i = 0_u8;
        while i < 32 {
            matches &= (output[usize::from(i)] < q) == (i < below);
            i += 1;
        }
        matches
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_capture<T, F>(
        input: &[T],
        f: &F,
    ) -> Option<MergeSnapshot> {
        let input = merge_input::<T, F>(input)?;
        let q = <() as ByteModel<T, F>>::threshold(f)?;
        let len = input.len();
        #[cfg(kani_smallsort_q_compact_merge32)]
        if len == 32 {
            return Some(MergeSnapshot {
                q,
                len,
                target: MergeTarget::Below(merge32_count_below(input, q)),
            });
        }
        Some(MergeSnapshot { q, len, target: MergeTarget::Mask(merge_target_mask(input, q)) })
    }

    pub(in crate::slice::sort::shared::smallsort) fn merge_q_post<T, F>(
        before: Option<MergeSnapshot>,
        dst: *mut T,
        f: &F,
    ) -> bool {
        let (Some(before), Some(q)) = (before, <() as ByteModel<T, F>>::threshold(f)) else {
            return false;
        };
        let output = ptr::slice_from_raw_parts(dst.cast::<u8>(), before.len);
        if q != before.q || !supported_merge_len(before.len) || !ub_checks::can_dereference(output)
        {
            return false;
        }
        // SAFETY: Check reads the active span after normal return. The two write
        // streams and the odd copy fill it, and Replace havocs this same span.
        let output = unsafe { &*output };
        match before.target {
            MergeTarget::Mask(target) => merge_matches_mask(output, q, target),
            #[cfg(kani_smallsort_q_compact_merge32)]
            MergeTarget::Below(below) => merge32_matches_below(output, q, below),
        }
    }
}
