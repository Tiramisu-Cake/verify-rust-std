//! K-15 negative controls: runtime-body copies, enabled only by kani_smallsort_controls.
//! Each copy differs only at its marked mutation; runtime std is untouched.

use super::super::*;

pub(super) unsafe fn mutant_swap_if_less<T, F>(v_base: *mut T, a_pos: usize, b_pos: usize, is_less: &mut F)
where
    F: FnMut(&T, &T) -> bool,
{
    // SAFETY: the caller must guarantee that `a_pos` and `b_pos` each added to `v_base` yield valid
    // pointers into `v_base`, and are properly aligned, and part of the same allocation.
    unsafe {
        let v_a = v_base.add(a_pos);
        let v_b = v_base.add(b_pos);

        // PANIC SAFETY: if is_less panics, no scratch memory was created and the slice should still be
        // in a well defined state, without duplicates.

        // Important to only swap if it is more and not if it is equal. is_less should return false for
        // equal, so we don't swap.
        let should_swap = !is_less(&*v_b, &*v_a);

        // This is a branchless version of swap if.
        // The equivalent code with a branch would be:
        //
        // if should_swap {
        //     ptr::swap(v_a, v_b, 1);
        // }

        // The goal is to generate cmov instructions here.
        let v_a_swap = hint::select_unpredictable(should_swap, v_b, v_a);
        let v_b_swap = hint::select_unpredictable(should_swap, v_a, v_b);

        let v_b_swap_tmp = ManuallyDrop::new(ptr::read(v_b_swap));
        ptr::copy(v_a_swap, v_a, 1);
        ptr::copy_nonoverlapping(&*v_b_swap_tmp, v_b, 1);
    }
}

pub(super) unsafe fn mutant_insert_tail<T, F: FnMut(&T, &T) -> bool>(begin: *mut T, tail: *mut T, is_less: &mut F) {
    // SAFETY: see individual comments.
    unsafe {
        // SAFETY: in-bounds as tail > begin.
        let mut sift = tail;
        if !is_less(&*tail, &*sift) {
            return;
        }

        // SAFETY: after this read tail is never read from again, as we only ever
        // read from sift, sift < tail and we only ever decrease sift. Thus this is
        // effectively a move, not a copy. Should a panic occur, or we have found
        // the correct insertion position, gap_guard ensures the element is moved
        // back into the array.
        let tmp = ManuallyDrop::new(tail.read());
        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };

        loop {
            // SAFETY: we move sift into the gap (which is valid), and point the
            // gap guard destination at sift, ensuring that if a panic occurs the
            // gap is once again filled.
            ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);
            gap_guard.dst = sift;

            if sift == begin {
                break;
            }

            // SAFETY: we checked that sift != begin, thus this is in-bounds.
            sift = sift.sub(1);
            if !is_less(&tmp, &*sift) {
                break;
            }
        }
    }
}

pub(super) unsafe fn mutant_merge_up<T, F: FnMut(&T, &T) -> bool>(
    mut left_src: *const T,
    mut right_src: *const T,
    mut dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {
    // This is a branchless merge utility function.
    // The equivalent code with a branch would be:
    //
    // if !is_less(&*right_src, &*left_src) {
    //     ptr::copy_nonoverlapping(left_src, dst, 1);
    //     left_src = left_src.add(1);
    // } else {
    //     ptr::copy_nonoverlapping(right_src, dst, 1);
    //     right_src = right_src.add(1);
    // }
    // dst = dst.add(1);

    // SAFETY: The caller must guarantee that `left_src`, `right_src` are valid
    // to read and `dst` is valid to write, while not aliasing.
    unsafe {
        let is_l = !is_less(&*right_src, &*left_src);
        let src = if is_l { left_src } else { right_src };
        ptr::copy_nonoverlapping(src, dst, 1);
        right_src = right_src.add(is_l as usize);
        left_src = left_src.add(!is_l as usize);
        dst = dst.add(1);
    }

    (left_src, right_src, dst)
}

pub(super) unsafe fn mutant_bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &[T],
    dst: *mut T,
    is_less: &mut F,
) {
    // It helps to visualize the merge:
    //
    // Initial:
    //
    //  |dst (in dst)
    //  |left               |right
    //  v                   v
    // [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
    //                     ^                   ^
    //                     |left_rev           |right_rev
    //                                         |dst_rev (in dst)
    //
    // After:
    //
    //                      |dst (in dst)
    //        |left         |           |right
    //        v             v           v
    // [xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx]
    //       ^             ^           ^
    //       |left_rev     |           |right_rev
    //                     |dst_rev (in dst)
    //
    // In each iteration one of left or right moves up one position, and one of
    // left_rev or right_rev moves down one position, whereas dst always moves
    // up one position and dst_rev always moves down one position. Assuming
    // the input was sorted and the comparison function is correctly implemented
    // at the end we will have left == left_rev + 1, and right == right_rev + 1,
    // fully consuming the input having written it to dst.

    let len = v.len();
    let src = v.as_ptr();

    let len_div_2 = len / 2;

    // SAFETY: The caller has to ensure that len >= 2.
    unsafe {
        intrinsics::assume(len_div_2 != 0); // This can avoid useless code-gen.
    }

    // SAFETY: no matter what the result of the user-provided comparison function
    // is, all 4 read pointers will always be in-bounds. Writing `dst` and `dst_rev`
    // will always be in bounds if the caller guarantees that `dst` is valid for
    // `v.len()` writes.
    unsafe {
        let mut left = src;
        let mut right = src.add(len_div_2);
        let mut dst = dst;

        let mut left_rev = src.add(len_div_2 - 1);
        let mut right_rev = src.add(len - 1);
        let mut dst_rev = dst.add(len - 1);

        for _ in 0..len_div_2 {
            (left, right, dst) = merge_up(left, right, dst, is_less);
            (left_rev, right_rev, dst_rev) = merge_down(left_rev, right_rev, dst_rev, is_less);
        }

        let left_end = left_rev.wrapping_add(1);
        let right_end = right_rev.wrapping_add(1);

        // Odd length, so one element is left unconsumed in the input.
        if !len.is_multiple_of(2) {
            let left_nonempty = left < left_end;
            let last_src = if left_nonempty { left } else { right };
            ptr::copy_nonoverlapping(last_src, dst, 1);
            left = left.add(left_nonempty as usize);
            right = right.add((!left_nonempty) as usize);
        }

        // We now should have consumed the full input exactly once. This can only fail if the
        // user-provided comparison function fails to implement a strict weak ordering. In that case
        // we panic and never access the inconsistent state in dst.
        // MUTATION: final consumption check removed.
    }
}

pub(super) fn mutant_small_sort_network<T, F>(v: &mut [T], is_less: &mut F)
where
    T: FreezeMarker,
    F: FnMut(&T, &T) -> bool,
{
    // This implementation is tuned to be efficient for integer types.

    let len = v.len();
    if len < 2 {
        return;
    }

    if len > SMALL_SORT_NETWORK_SCRATCH_LEN {
        intrinsics::abort_immediate();
    }

    let mut stack_array = MaybeUninit::<[T; SMALL_SORT_NETWORK_SCRATCH_LEN]>::uninit();

    let len_div_2 = len / 2;
    let no_merge = len < 18;

    let v_base = v.as_mut_ptr();
    let initial_region_len = if no_merge { len } else { len_div_2 };
    // SAFETY: Both possible values of `initial_region_len` are in-bounds.
    let mut region = unsafe { slice::from_raw_parts_mut(v_base, initial_region_len) };

    // Avoid compiler unrolling, we *really* don't want that to happen here for binary-size reasons.
    loop {
        let presorted_len = if region.len() >= 13 {
            sort13_optimal(region, is_less);
            13
        } else if region.len() >= 9 {
            sort9_optimal(region, is_less);
            10
        } else {
            1
        };

        insertion_sort_shift_left(region, presorted_len, is_less);

        if no_merge {
            return;
        }

        if region.as_ptr() != v_base {
            break;
        }

        // SAFETY: The right side of `v` based on `len_div_2` is guaranteed in-bounds.
        unsafe { region = slice::from_raw_parts_mut(v_base.add(len_div_2), len - len_div_2) };
    }

    // SAFETY: We checked that T is Freeze and thus observation safe.
    // Should is_less panic v was not modified in parity_merge and retains it's original input.
    // scratch and v must not alias and scratch has v.len() space.
    unsafe {
        let scratch_base = stack_array.as_mut_ptr() as *mut T;
        bidirectional_merge(slice::from_raw_parts_mut(v_base, len), scratch_base, is_less);
        ptr::copy_nonoverlapping(scratch_base, v_base, len);
    }
}
