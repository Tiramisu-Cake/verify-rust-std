// SPDX-License-Identifier: Apache-2.0 OR MIT
// W1-to-W2 checked pointer/index bridge probes.
// Each CASE is independent. Associations below are established by actual
// ordinary or wrapping pointer calls in the body; no caller-supplied pointer /
// index bridge is used as an axiom. Arithmetic cases create no access rights.

// CASE_BEGIN stride_order_checked
/*@
lem stride_order_checked(i: usize, j: usize, s: usize)
    req 0 < s &*& s <= usize::MAX;
    ens (i * s < j * s) == (i < j) &*&
        (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}
@*/
// CASE_END stride_order_checked

// CASE_BEGIN source_cursor_const
pub unsafe fn source_cursor_const<T>(base: *const T, n: usize, i: usize) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*& i <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true;
@*//*@
ens (result as pointer) == pointer_ctor(
        (base as pointer).provenance,
        (base as pointer).address + i * std::mem::size_of::<T>(),
        (base as pointer).metadata) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address ==
        (base as pointer).address + i * std::mem::size_of::<T>() &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    unsafe { base.add(i) }
}
// CASE_END source_cursor_const

// CASE_BEGIN source_cursor_mut
pub unsafe fn source_cursor_mut<T>(base: *mut T, n: usize, i: usize) -> *mut T
/*@
req 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*& i <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true;
@*//*@
ens (result as pointer) == pointer_ctor(
        (base as pointer).provenance,
        (base as pointer).address + i * std::mem::size_of::<T>(),
        (base as pointer).metadata) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address ==
        (base as pointer).address + i * std::mem::size_of::<T>() &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    unsafe { base.add(i) }
}
// CASE_END source_cursor_mut

// CASE_BEGIN terminal_source_index
pub unsafe fn terminal_source_index<T>(base: *const T, n: usize, index: isize) -> *const T
/*@
req 0 <= std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true &*&
    (index == -1 || (0 <= index && index < n));
@*//*@
ens (result as pointer) ==
        wrapping_pointer_offset(base as pointer,
            (index + 1) * std::mem::size_of::<T>()) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata &*&
    (if index == -1 {
        (result as pointer) == (base as pointer)
    } else {
        (result as pointer).address ==
            (base as pointer).address + (index + 1) * std::mem::size_of::<T>()
    });
@*//*@
on_unwind_ens false;
@*/
{
    if index == -1 {
        let reverse = base.wrapping_sub(1);
        reverse.wrapping_add(1)
    } else {
        //@ mul_mono_l(0, index, std::mem::size_of::<T>());
        //@ mul_mono_l(index + 1, n, std::mem::size_of::<T>());
        let reverse = unsafe { base.add(index as usize) };
        reverse.wrapping_add(1)
    }
}
// CASE_END terminal_source_index

// CASE_BEGIN terminal_source_index_mut
pub unsafe fn terminal_source_index_mut<T>(base: *mut T, n: usize, index: isize) -> *mut T
/*@
req 0 <= std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true &*&
    (index == -1 || (0 <= index && index < n));
@*//*@
ens (result as pointer) ==
        wrapping_pointer_offset(base as pointer,
            (index + 1) * std::mem::size_of::<T>()) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata &*&
    (if index == -1 {
        (result as pointer) == (base as pointer)
    } else {
        (result as pointer).address ==
            (base as pointer).address + (index + 1) * std::mem::size_of::<T>()
    });
@*//*@
on_unwind_ens false;
@*/
{
    if index == -1 {
        let reverse = base.wrapping_sub(1);
        reverse.wrapping_add(1)
    } else {
        //@ mul_mono_l(0, index, std::mem::size_of::<T>());
        //@ mul_mono_l(index + 1, n, std::mem::size_of::<T>());
        let reverse = unsafe { base.add(index as usize) };
        reverse.wrapping_add(1)
    }
}
// CASE_END terminal_source_index_mut

// CASE_BEGIN terminal_minus_one_numerical_wrap
pub unsafe fn terminal_minus_one_numerical_wrap<T>(base: *const T) -> *const T
/*@
req (base as pointer).address == 0 &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == 0 &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let reverse = base.wrapping_sub(1);
    reverse.wrapping_add(1)
}
// CASE_END terminal_minus_one_numerical_wrap

// CASE_BEGIN reverse_boolean_at_zero_with_frame
pub unsafe fn reverse_boolean_at_zero_with_frame<T>(
    base: *const T, take_left: bool, frame: *mut u8) -> *const T
/*@
req 0 <= std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address <= usize::MAX &*&
    *frame |-> ?framed_value;
@*//*@
ens (result as pointer) ==
        (if take_left {
            wrapping_pointer_offset(base as pointer,
                -std::mem::size_of::<T>())
        } else {
            base as pointer
        }) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata &*&
    *frame |-> framed_value;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(take_left as usize)
}
// CASE_END reverse_boolean_at_zero_with_frame

// CASE_BEGIN source_pointer_order
/*@
lem stride_order_checked(i: usize, j: usize, s: usize)
    req 0 < s &*& s <= usize::MAX;
    ens (i * s < j * s) == (i < j) &*&
        (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}
@*/
pub unsafe fn source_pointer_order<T>(
    base: *const T, n: usize, i: usize, j: usize) -> bool
/*@
req 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*& i <= n &*& j <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true;
@*//*@
ens result == (i < j);
@*//*@
on_unwind_ens false;
@*/
{
    //@ stride_order_checked(i, j, std::mem::size_of::<T>());
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    //@ mul_mono_l(0, j, std::mem::size_of::<T>());
    //@ mul_mono_l(j, n, std::mem::size_of::<T>());
    let left = unsafe { base.add(i) };
    let right = unsafe { base.add(j) };
    left < right
}
// CASE_END source_pointer_order

// CASE_BEGIN source_pointer_equal
/*@
lem stride_order_checked(i: usize, j: usize, s: usize)
    req 0 < s &*& s <= usize::MAX;
    ens (i * s < j * s) == (i < j) &*&
        (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}
@*/
pub unsafe fn source_pointer_equal<T>(
    base: *const T, n: usize, i: usize, j: usize) -> bool
/*@
req 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*& i <= n &*& j <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (base as pointer).address &*&
    (base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(base) == true &*&
    pointer_within_limits(base + n) == true;
@*//*@
ens result == (i == j);
@*//*@
on_unwind_ens false;
@*/
{
    //@ stride_order_checked(i, j, std::mem::size_of::<T>());
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    //@ mul_mono_l(0, j, std::mem::size_of::<T>());
    //@ mul_mono_l(j, n, std::mem::size_of::<T>());
    let left = unsafe { base.add(i) };
    let right = unsafe { base.add(j) };
    left == right
}
// CASE_END source_pointer_equal
