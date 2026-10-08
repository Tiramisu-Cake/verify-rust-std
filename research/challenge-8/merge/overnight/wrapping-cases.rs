#![feature(core_intrinsics)]
#![allow(internal_features)]
// SPDX-License-Identifier: Apache-2.0 OR MIT
// W1 wrapping arithmetic cases for experimental-merge-wrapping-01-v1.
// Each CASE is an independent proof unit. These cases test pointer arithmetic,
// provenance/metadata retention, and explicit resources only where stated.
// They do not establish allocation bounds, ownership, initialization, or access
// rights from an address calculation. Every executable case has a full normal
// post and an explicit no-unwind post.

// CASE_BEGIN const_add_zero
pub unsafe fn const_add_zero<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(0)
}
// CASE_END const_add_zero

// CASE_BEGIN const_sub_zero
pub unsafe fn const_sub_zero<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(0)
}
// CASE_END const_sub_zero

// CASE_BEGIN mut_add_zero
pub unsafe fn mut_add_zero<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(0)
}
// CASE_END mut_add_zero

// CASE_BEGIN mut_sub_zero
pub unsafe fn mut_sub_zero<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(0)
}
// CASE_END mut_sub_zero

// CASE_BEGIN const_add_one_no_wrap
pub unsafe fn const_add_one_no_wrap<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    (base as pointer).address + std::mem::size_of::<T>() <= usize::MAX;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, std::mem::size_of::<T>()) &*&
    (result as pointer).address == (base as pointer).address + std::mem::size_of::<T>() &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END const_add_one_no_wrap

// CASE_BEGIN const_add_one_wrap
pub unsafe fn const_add_one_wrap<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    usize::MAX < (base as pointer).address + std::mem::size_of::<T>();
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, std::mem::size_of::<T>()) &*&
    (result as pointer).address ==
        (base as pointer).address + std::mem::size_of::<T>() - usize::MAX - 1 &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END const_add_one_wrap

// CASE_BEGIN const_sub_one_no_wrap
pub unsafe fn const_sub_one_no_wrap<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= (base as pointer).address;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, -std::mem::size_of::<T>()) &*&
    (result as pointer).address == (base as pointer).address - std::mem::size_of::<T>() &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END const_sub_one_no_wrap

// CASE_BEGIN const_sub_one_wrap
pub unsafe fn const_sub_one_wrap<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    (base as pointer).address < std::mem::size_of::<T>();
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, -std::mem::size_of::<T>()) &*&
    (result as pointer).address ==
        (base as pointer).address - std::mem::size_of::<T>() + usize::MAX + 1 &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END const_sub_one_wrap

// CASE_BEGIN mut_add_one_no_wrap
pub unsafe fn mut_add_one_no_wrap<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    (base as pointer).address + std::mem::size_of::<T>() <= usize::MAX;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, std::mem::size_of::<T>()) &*&
    (result as pointer).address == (base as pointer).address + std::mem::size_of::<T>() &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END mut_add_one_no_wrap

// CASE_BEGIN mut_add_one_wrap
pub unsafe fn mut_add_one_wrap<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    usize::MAX < (base as pointer).address + std::mem::size_of::<T>();
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, std::mem::size_of::<T>()) &*&
    (result as pointer).address ==
        (base as pointer).address + std::mem::size_of::<T>() - usize::MAX - 1 &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END mut_add_one_wrap

// CASE_BEGIN mut_sub_one_no_wrap
pub unsafe fn mut_sub_one_no_wrap<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= (base as pointer).address;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, -std::mem::size_of::<T>()) &*&
    (result as pointer).address == (base as pointer).address - std::mem::size_of::<T>() &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END mut_sub_one_no_wrap

// CASE_BEGIN mut_sub_one_wrap
pub unsafe fn mut_sub_one_wrap<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>() &*&
    (base as pointer).address < std::mem::size_of::<T>();
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, -std::mem::size_of::<T>()) &*&
    (result as pointer).address ==
        (base as pointer).address - std::mem::size_of::<T>() + usize::MAX + 1 &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END mut_sub_one_wrap

// CASE_BEGIN symbolic_zst_const
pub unsafe fn symbolic_zst_const<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& std::mem::size_of::<T>() == 0;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END symbolic_zst_const

// CASE_BEGIN symbolic_zst_mut
pub unsafe fn symbolic_zst_mut<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& std::mem::size_of::<T>() == 0;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END symbolic_zst_mut

// CASE_BEGIN signed_offset_const
pub unsafe fn signed_offset_const(base: *const u8) -> *const u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, -1) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_offset(-1)
}
// CASE_END signed_offset_const

// CASE_BEGIN arith_offset_const
pub unsafe fn arith_offset_const(base: *const u8) -> *const u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(base as pointer, 1) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    unsafe { std::intrinsics::arith_offset(base, 1) }
}
// CASE_END arith_offset_const

// CASE_BEGIN reverse_cursor_right
pub unsafe fn reverse_cursor_right<T>(right: *const T, is_l: bool) -> *const T
/*@
req 0 <= (right as pointer).address &*& (right as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(
        right as pointer, -(is_l as usize) * std::mem::size_of::<T>()) &*&
    (result as pointer).provenance == (right as pointer).provenance &*&
    (result as pointer).metadata == (right as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    right.wrapping_sub(is_l as usize)
}
// CASE_END reverse_cursor_right

// CASE_BEGIN reverse_cursor_left
pub unsafe fn reverse_cursor_left<T>(left: *const T, is_l: bool) -> *const T
/*@
req 0 <= (left as pointer).address &*& (left as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == wrapping_pointer_offset(
        left as pointer, -(!is_l as usize) * std::mem::size_of::<T>()) &*&
    (result as pointer).provenance == (left as pointer).provenance &*&
    (result as pointer).metadata == (left as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    left.wrapping_sub(!is_l as usize)
}
// CASE_END reverse_cursor_left

// CASE_BEGIN terminal_reentry_const
pub unsafe fn terminal_reentry_const<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let terminal = base.wrapping_sub(1);
    terminal.wrapping_add(1)
}
// CASE_END terminal_reentry_const

// CASE_BEGIN terminal_reentry_mut
pub unsafe fn terminal_reentry_mut<T>(base: *mut T) -> *mut T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let terminal = base.wrapping_sub(1);
    terminal.wrapping_add(1)
}
// CASE_END terminal_reentry_mut

// CASE_BEGIN terminal_reentry_at_address_zero
pub unsafe fn terminal_reentry_at_address_zero(base: *const u8) -> *const u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& (base as pointer).address == 0;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == 0 &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let terminal = base.wrapping_sub(1);
    terminal.wrapping_add(1)
}
// CASE_END terminal_reentry_at_address_zero

// CASE_BEGIN frame_and_read_after_reentry
pub unsafe fn frame_and_read_after_reentry(base: *const u8) -> u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& *base |-> ?stored_value;
@*//*@
ens result == stored_value &*& *base |-> stored_value;
@*//*@
on_unwind_ens false;
@*/
{
    let left_rev = base.wrapping_sub(1);
    let left_end = left_rev.wrapping_add(1);
    unsafe { *left_end }
}
// CASE_END frame_and_read_after_reentry

// CASE_BEGIN unsupported_count_two
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"bin/rust/std/lib.rsspec","error_line":308,"column_start":25,"column_end":27,"message":"Cannot prove condition. (Cannot prove 2 = 0 || 2 = 1.)"}
pub unsafe fn unsupported_count_two<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(2) // TARGET_NEGATIVE verifast_wrapping_add_const count precondition
}
// CASE_END unsupported_count_two

// CASE_BEGIN unsupported_signed_offset
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"bin/rust/std/lib.rsspec","error_line":318,"column_start":35,"column_end":37,"message":"Cannot prove condition. (Cannot prove 2 <= 1.)"}
pub unsafe fn unsupported_signed_offset(base: *const u8) -> *const u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_offset(2) // TARGET_NEGATIVE verifast_wrapping_offset_const count precondition
}
// CASE_END unsupported_signed_offset

// CASE_BEGIN wrong_wrapped_result
// EXPECT_ERROR {"stage":"verifast","predicate":"__result = base","line":"TARGET","column_start":36,"column_end":38}
pub unsafe fn wrong_wrapped_result<T>(base: *const T) -> *const T
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= usize::MAX &*& 0 < std::mem::size_of::<T>();
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let result = base.wrapping_add(1);
    //@ assert (result as pointer) == (base as pointer); // TARGET_NEGATIVE false pointer result
    result
}
// CASE_END wrong_wrapped_result

// CASE_BEGIN read_at_wrapped_minus_one
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":14,"column_end":18,"message":"No matching heap chunks: [_]points_to<u8>(__result, _)"}
pub unsafe fn read_at_wrapped_minus_one(base: *const u8) -> u8
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& *base |-> ?stored_value;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let bad = base.wrapping_sub(1);
    unsafe { *bad } // TARGET_NEGATIVE no points_to at wrapped -1
}
// CASE_END read_at_wrapped_minus_one

// CASE_BEGIN foreign_same_address_no_transfer
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"verified/lib.rs","error_line":"TARGET","column_start":14,"column_end":24,"message":"No matching heap chunks: [_]points_to<u8>(__result0, _)"}
pub unsafe fn foreign_same_address_no_transfer(
    source: *const u8, foreign: *const u8) -> u8
/*@
req 0 <= (source as pointer).address &*& (source as pointer).address <= usize::MAX &*&
    0 <= std::mem::size_of::<u8>() &*& std::mem::size_of::<u8>() <= usize::MAX &*& (source as pointer).address == (foreign as pointer).address &*&
    (source as pointer).provenance != (foreign as pointer).provenance &*&
    *foreign |-> ?stored_value;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let away = source.wrapping_sub(1);
    let reentered = away.wrapping_add(1);
    unsafe { *reentered } // TARGET_NEGATIVE foreign resource cannot supply source provenance
}
// CASE_END foreign_same_address_no_transfer
