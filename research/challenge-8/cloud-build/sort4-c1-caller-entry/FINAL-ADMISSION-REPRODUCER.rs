#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features)]

use std::{intrinsics, mem::{MaybeUninit, size_of}};
use std::marker::Freeze;

/// SAFETY: this is safety relevant, how does this interact with the soundness holes in
/// specialization?
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}

impl<T: Freeze> FreezeMarker for T {}

fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    let len = v.len();
    if const { size_of::<T>() <= 16 } && len >= 16 {
        return;
    }
    if len < 8 {
        return;
    }
/*@
if (true) {
    let v_len_base = strip_pointer_metadata(v as pointer) as *T;
    assert v_len_base[..len] |-> ?v_len_elems;
    array_inv::<T>();
    if (16 < std::mem::size_of::<T>()) {
        mul_mono_l(1, std::mem::size_of::<T>(), len);
    } else {
        assert len < 16;
    }
}
@*/
    if len < 2 {
        return;
    }

    if scratch.len() < len + 16 {
        intrinsics::abort();
    }

    let v_base = v.as_mut_ptr();
    let len_div_2 = len / 2;

    // SAFETY: See individual comments.
    unsafe {
        let scratch_base = scratch.as_mut_ptr() as *mut T;
        if const { size_of::<T>() <= 16 } && len >= 16 {
            return;
        } else if len >= 8 {
            return;
        } else {
            return;
        }
    }
}