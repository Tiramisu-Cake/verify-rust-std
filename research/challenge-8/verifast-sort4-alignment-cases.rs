// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// H_align fixtures only; never execute these functions as ordinary programs.
// Storage alignment is an explicit adopted-domain premise, not a points_to axiom.

// CASE_BEGIN positive_generic_const
/*@
lem aligned_step_const(address: usize, stride: usize, alignment: usize)
    req 0 <= address &*& 0 <= stride &*& 0 < alignment &*& address % alignment == 0 &*& stride % alignment == 0 &*& address + stride <= usize::MAX;
    ens (address + stride) % alignment == 0;
{
    div_rem_nonneg(address, alignment);
    div_rem_nonneg(stride, alignment);
    div_rem_nonneg_unique(address + stride, alignment, address / alignment + stride / alignment, 0);
}
@*/
pub unsafe fn positive_generic_const<T>(base: *const T, i: usize) -> *const T
/*@
req array_::<u8>(base as *u8, 4 * std::mem::size_of::<T>(), ?bytes) &*&
    base != 0 &*& base as usize % std::mem::align_of::<T>() == 0 &*& i <= 3;
@*//*@
ens array_::<u8>(base as *u8, 4 * std::mem::size_of::<T>(), bytes) &*&
    result == base + i &*& pointer_within_limits(result) == true &*&
    result as usize % std::mem::align_of::<T>() == 0;
@*//*@
on_unwind_ens false;
@*/
{
    //@ array__inv::<u8>();
    //@ ptr_provenance_min_addr_limits((base as pointer).provenance);
    //@ ptr_provenance_max_addr_limits((base as pointer).provenance);
    //@ assert pointer_within_limits(base) == true;
    //@ assert 0 <= base as usize;
    //@ std::alloc::is_valid_layout_size_of_align_of::<T>();
    //@ is_power_of_2_pos(std::mem::align_of::<T>());
    //@ size_align::<T>();
    //@ assert 0 <= std::mem::size_of::<T>();
    //@ assert base as usize + 4 * std::mem::size_of::<T>() <= usize::MAX;
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, 4, std::mem::size_of::<T>());
    // POINTER_OPERATION
    let result = base.add(i);
    /*@
    if i < 1 {
        assert i == 0;
        assert result == base;
        assert result as usize % std::mem::align_of::<T>() == 0;
    } else if i < 2 {
        assert i == 1;
        aligned_step_const(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
    } else if i < 3 {
        assert i == 2;
        aligned_step_const(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_const(base as usize + std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
    } else {
        assert i == 3;
        aligned_step_const(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_const(base as usize + std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_const(base as usize + 2 * std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
    }
    @*/
    result
}
// CASE_END positive_generic_const

// CASE_BEGIN positive_generic_mut
/*@
lem aligned_step_mut(address: usize, stride: usize, alignment: usize)
    req 0 <= address &*& 0 <= stride &*& 0 < alignment &*& address % alignment == 0 &*& stride % alignment == 0 &*& address + stride <= usize::MAX;
    ens (address + stride) % alignment == 0;
{
    div_rem_nonneg(address, alignment);
    div_rem_nonneg(stride, alignment);
    div_rem_nonneg_unique(address + stride, alignment, address / alignment + stride / alignment, 0);
}
@*/
pub unsafe fn positive_generic_mut<T>(base: *mut T, i: usize) -> *mut T
/*@
req array_::<u8>(base as *u8, 4 * std::mem::size_of::<T>(), ?bytes) &*&
    base != 0 &*& base as usize % std::mem::align_of::<T>() == 0 &*& i <= 3;
@*//*@
ens array_::<u8>(base as *u8, 4 * std::mem::size_of::<T>(), bytes) &*&
    result == base + i &*& pointer_within_limits(result) == true &*&
    result as usize % std::mem::align_of::<T>() == 0;
@*//*@
on_unwind_ens false;
@*/
{
    //@ array__inv::<u8>();
    //@ ptr_provenance_min_addr_limits((base as pointer).provenance);
    //@ ptr_provenance_max_addr_limits((base as pointer).provenance);
    //@ assert pointer_within_limits(base) == true;
    //@ assert 0 <= base as usize;
    //@ std::alloc::is_valid_layout_size_of_align_of::<T>();
    //@ is_power_of_2_pos(std::mem::align_of::<T>());
    //@ size_align::<T>();
    //@ assert 0 <= std::mem::size_of::<T>();
    //@ assert base as usize + 4 * std::mem::size_of::<T>() <= usize::MAX;
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, 4, std::mem::size_of::<T>());
    // POINTER_OPERATION
    let result = base.add(i);
    /*@
    if i < 1 {
        assert i == 0;
        assert result == base;
        assert result as usize % std::mem::align_of::<T>() == 0;
    } else if i < 2 {
        assert i == 1;
        aligned_step_mut(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
    } else if i < 3 {
        assert i == 2;
        aligned_step_mut(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_mut(base as usize + std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
    } else {
        assert i == 3;
        aligned_step_mut(base as usize, std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_mut(base as usize + std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
        aligned_step_mut(base as usize + 2 * std::mem::size_of::<T>(), std::mem::size_of::<T>(), std::mem::align_of::<T>());
    }
    @*/
    result
}
// CASE_END positive_generic_mut

// CASE_BEGIN positive_zst_layout
#[repr(align(8))]
pub struct Z;

pub fn positive_zst_layout() -> usize
/*@
req true;
@*//*@
ens result == 8 &*& std::mem::size_of::<Z>() == 0 &*& std::mem::align_of::<Z>() == 8;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<Z>();
    let alignment = core::mem::align_of::<Z>();
    //@ assert size == 0;
    //@ assert alignment == 8;
    alignment
}
// CASE_END positive_zst_layout

// CASE_BEGIN positive_zst_add
#[repr(align(8))]
pub struct Z;

pub unsafe fn positive_zst_add(base: *const Z, i: usize) -> *const Z
/*@
req array_::<u8>(base as *u8, 0, ?bytes) &*&
    base != 0 &*& base as usize % 8 == 0 &*& i <= 3;
@*//*@
ens array_::<u8>(base as *u8, 0, bytes) &*& result == base &*&
    pointer_within_limits(result) == true &*& result as usize % 8 == 0;
@*//*@
on_unwind_ens false;
@*/
{
    // POINTER_OPERATION
    let result = base.add(i);
    result
}
// CASE_END positive_zst_add

// CASE_BEGIN negative_source_byte_offset
#[repr(align(8))]
pub struct Z;

pub unsafe fn negative_source_byte_offset(src: *const Z, dst: *mut Z)
/*@
req array_::<u8>(src as *u8, 8, ?src_bytes) &*&
    array_::<u8>(dst as *u8, 8, ?dst_bytes) &*&
    src != 0 &*& dst != 0 &*& src as usize % 8 == 0 &*& dst as usize % 8 == 0;
@*//*@
ens array_::<u8>(src as *u8, 8, src_bytes) &*&
    array_::<u8>(dst as *u8, 8, dst_bytes);
@*//*@
on_unwind_ens false;
@*/
{
    // POINTER_OPERATION
    let bad_bytes = (src as *const u8).add(1);
    let bad = bad_bytes as *const Z;
    // ALIGNMENT_OBLIGATION
    //@ assert bad as usize % 8 == 0;
}
// CASE_END negative_source_byte_offset

// CASE_BEGIN negative_destination_byte_offset
#[repr(align(8))]
pub struct Z;

pub unsafe fn negative_destination_byte_offset(src: *const Z, dst: *mut Z)
/*@
req array_::<u8>(src as *u8, 8, ?src_bytes) &*&
    array_::<u8>(dst as *u8, 8, ?dst_bytes) &*&
    src != 0 &*& dst != 0 &*& src as usize % 8 == 0 &*& dst as usize % 8 == 0;
@*//*@
ens array_::<u8>(src as *u8, 8, src_bytes) &*&
    array_::<u8>(dst as *u8, 8, dst_bytes);
@*//*@
on_unwind_ens false;
@*/
{
    // POINTER_OPERATION
    let bad_bytes = (dst as *mut u8).add(1);
    let bad = bad_bytes as *mut Z;
    // ALIGNMENT_OBLIGATION
    //@ assert bad as usize % 8 == 0;
}
// CASE_END negative_destination_byte_offset
