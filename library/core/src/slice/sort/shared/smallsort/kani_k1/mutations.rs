//! Deliberately changed copies for opt-in controls.

use super::super::*;

// Negates the exchange decision.
pub(super) unsafe fn mutant_swap_if_less<T, F>(
    v_base: *mut T,
    a_pos: usize,
    b_pos: usize,
    is_less: &mut F,
)
where
    F: FnMut(&T, &T) -> bool,
{
    unsafe {
        let v_a = v_base.add(a_pos);
        let v_b = v_base.add(b_pos);

        let should_swap = !is_less(&*v_b, &*v_a);

        let v_a_swap = hint::select_unpredictable(should_swap, v_b, v_a);
        let v_b_swap = hint::select_unpredictable(should_swap, v_a, v_b);

        let v_b_swap_tmp = ManuallyDrop::new(ptr::read(v_b_swap));
        ptr::copy(v_a_swap, v_a, 1);
        ptr::copy_nonoverlapping(&*v_b_swap_tmp, v_b, 1);
    }
}

// Starts sift at tail instead of its predecessor.
pub(super) unsafe fn mutant_insert_tail<T, F: FnMut(&T, &T) -> bool>(
    begin: *mut T,
    tail: *mut T,
    is_less: &mut F,
) {
    unsafe {
        let mut sift = tail;
        if !is_less(&*tail, &*sift) {
            return;
        }

        let tmp = ManuallyDrop::new(tail.read());
        let mut gap_guard = CopyOnDrop {
            src: &*tmp,
            dst: tail,
            len: 1,
        };

        loop {
            ptr::copy_nonoverlapping(sift, gap_guard.dst, 1);
            gap_guard.dst = sift;

            if sift == begin {
                break;
            }

            sift = sift.sub(1);
            if !is_less(&tmp, &*sift) {
                break;
            }
        }
    }
}

// Advances the opposite source pointer.
pub(super) unsafe fn mutant_merge_up<T, F: FnMut(&T, &T) -> bool>(
    mut left_src: *const T,
    mut right_src: *const T,
    mut dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {

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

// Omits the final source-consumption check.
pub(super) unsafe fn mutant_bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &[T],
    dst: *mut T,
    is_less: &mut F,
) {

    let len = v.len();
    let src = v.as_ptr();

    let len_div_2 = len / 2;

    unsafe {
        intrinsics::assume(len_div_2 != 0);
    }

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

        if !len.is_multiple_of(2) {
            let left_nonempty = left < left_end;
            let last_src = if left_nonempty { left } else { right };
            ptr::copy_nonoverlapping(last_src, dst, 1);
            left = left.add(left_nonempty as usize);
            right = right.add((!left_nonempty) as usize);
        }

    }
}

// Treats sort9 output as ten presorted elements, skipping index 9.
pub(super) fn mutant_small_sort_network<T, F>(v: &mut [T], is_less: &mut F)
where
    T: FreezeMarker,
    F: FnMut(&T, &T) -> bool,
{

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
    let mut region = unsafe { slice::from_raw_parts_mut(v_base, initial_region_len) };

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

        unsafe { region = slice::from_raw_parts_mut(v_base.add(len_div_2), len - len_div_2) };
    }

    unsafe {
        let scratch_base = stack_array.as_mut_ptr() as *mut T;
        bidirectional_merge(slice::from_raw_parts_mut(v_base, len), scratch_base, is_less);
        ptr::copy_nonoverlapping(scratch_base, v_base, len);
    }
}
