// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated experimental fieldless-layout matrix. Hosted checker extracts one
// marked case per source so unsupported/negative cases cannot block positives.

// CASE_BEGIN zst_mut_add
#[repr(align(8))]
pub struct Z;

pub unsafe fn zst_mut_add(base: *mut Z, i: usize) -> *mut Z
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
// CASE_END zst_mut_add

// CASE_BEGIN repr_rust_empty
#[repr(Rust, align(8))]
pub struct Z;

pub fn repr_rust_empty() -> usize
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
// CASE_END repr_rust_empty

// CASE_BEGIN repr_rust_empty_default
#[repr(Rust)]
pub struct RustEmpty;

pub fn repr_rust_empty_default() -> usize
/*@
req true;
@*//*@
ens result == 1 &*& std::mem::size_of::<RustEmpty>() == 0 &*& std::mem::align_of::<RustEmpty>() == 1;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<RustEmpty>();
    let alignment = core::mem::align_of::<RustEmpty>();
    //@ assert size == 0;
    //@ assert alignment == 1;
    alignment
}
// CASE_END repr_rust_empty_default

// CASE_BEGIN repr_c_empty
#[repr(C, align(8))]
pub struct CEmpty;

pub fn repr_c_empty() -> usize
/*@
req true;
@*//*@
ens result == 8 &*& std::mem::size_of::<CEmpty>() == 0 &*& std::mem::align_of::<CEmpty>() == 8;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<CEmpty>();
    let alignment = core::mem::align_of::<CEmpty>();
    //@ assert size == 0;
    //@ assert alignment == 8;
    alignment
}
// CASE_END repr_c_empty

// CASE_BEGIN repr_c_empty_default
#[repr(C)]
pub struct CEmptyDefault;

pub fn repr_c_empty_default() -> usize
/*@
req true;
@*//*@
ens result == 1 &*& std::mem::size_of::<CEmptyDefault>() == 0 &*& std::mem::align_of::<CEmptyDefault>() == 1;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<CEmptyDefault>();
    let alignment = core::mem::align_of::<CEmptyDefault>();
    //@ assert size == 0;
    //@ assert alignment == 1;
    alignment
}
// CASE_END repr_c_empty_default

// CASE_BEGIN negative_zst_size
#[repr(align(8))]
pub struct Z;

pub fn negative_zst_size()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<Z>();
    // TARGET_ASSERTION
    //@ assert size == 1;
}
// CASE_END negative_zst_size

// CASE_BEGIN negative_zst_alignment
#[repr(align(8))]
pub struct Z;

pub fn negative_zst_alignment()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let alignment = core::mem::align_of::<Z>();
    // TARGET_ASSERTION
    //@ assert alignment == 16;
}
// CASE_END negative_zst_alignment

// CASE_BEGIN negative_zst_nonzero_stride
#[repr(align(8))]
pub struct Z;

pub unsafe fn negative_zst_nonzero_stride(base: *const Z, i: usize) -> *const Z
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
    //@ array__inv::<u8>();
    //@ ptr_provenance_min_addr_limits((base as pointer).provenance);
    //@ ptr_provenance_max_addr_limits((base as pointer).provenance);
    //@ assert pointer_within_limits(base) == true;
    // POINTER_OPERATION
    let result = base.add(i);
    // TARGET_ASSERTION
    //@ assert result != base;
    result
}
// CASE_END negative_zst_nonzero_stride

// CASE_BEGIN negative_assert_false
#[repr(align(8))]
pub struct Z;

pub fn negative_assert_false()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let _size = core::mem::size_of::<Z>();
    // TARGET_ASSERTION
    //@ assert false;
}
// CASE_END negative_assert_false

// CASE_BEGIN negative_absent_layout
#[repr(align(8))]
pub struct Z;

pub fn negative_absent_layout() -> usize
/*@
req true;
@*//*@
ens result == 0;
@*//*@
on_unwind_ens false;
@*/
{
    let size = core::mem::size_of::<Z>();
    // TARGET_ASSERTION
    //@ assert size == 0;
    size
}
// CASE_END negative_absent_layout

// CASE_BEGIN metadata_control_body
#[repr(align(8))]
pub struct Z;

pub fn metadata_control_body() -> usize
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
// CASE_END metadata_control_body

// CASE_BEGIN unsupported_fielded
pub struct Fielded {
    byte: u8,
}

pub fn unsupported_fielded() -> usize
/*@
req true;
@*//*@
ens result == std::mem::size_of::<Fielded>();
@*//*@
on_unwind_ens false;
@*/
{
    core::mem::size_of::<Fielded>()
}
// CASE_END unsupported_fielded

// CASE_BEGIN unsupported_phantom_field
use core::marker::PhantomData;

pub struct PhantomField {
    marker: PhantomData<u8>,
}

pub fn unsupported_phantom_field() -> usize
/*@
req true;
@*//*@
ens result == std::mem::size_of::<PhantomField>();
@*//*@
on_unwind_ens false;
@*/
{
    core::mem::size_of::<PhantomField>()
}
// CASE_END unsupported_phantom_field

// CASE_BEGIN unsupported_generic_adt
use core::marker::PhantomData;

pub struct GenericField<T> {
    marker: PhantomData<T>,
}

pub fn unsupported_generic_adt() -> usize
/*@
req true;
@*//*@
ens result == std::mem::size_of::<GenericField<u8>>();
@*//*@
on_unwind_ens false;
@*/
{
    core::mem::size_of::<GenericField<u8>>()
}
// CASE_END unsupported_generic_adt

// CASE_BEGIN unsupported_packed
#[repr(C, packed)]
pub struct PackedField {
    byte: u8,
    word: u32,
}

pub fn unsupported_packed() -> usize
/*@
req true;
@*//*@
ens result == std::mem::size_of::<PackedField>();
@*//*@
on_unwind_ens false;
@*/
{
    core::mem::size_of::<PackedField>()
}
// CASE_END unsupported_packed

// CASE_BEGIN unsupported_transparent
#[repr(transparent)]
pub struct TransparentField(u8);

pub fn unsupported_transparent() -> usize
/*@
req true;
@*//*@
ens result == std::mem::size_of::<TransparentField>();
@*//*@
on_unwind_ens false;
@*/
{
    core::mem::size_of::<TransparentField>()
}
// CASE_END unsupported_transparent
