#![allow(dead_code)]
// Restricted positive-size one-element model cases for copy.patch.
// Every TARGET case has no guessed EXPECT_ERROR oracle and stays
// INCONCLUSIVE until a hosted log establishes its stage/predicate/location.

/*@
pred copy_one_domain<T>(src: *T, dst: *T) =
    0 < src as usize &*& 0 < dst as usize &*&
    src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    src as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(src, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<T>()) == true &*&
    (src as usize + std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + std::mem::size_of::<T>() <= src as usize);
@*/

// Harness prefix helper: this body directly checks the trusted intrinsic
// contract. It transfers initializedness/value only and mentions no own<T>.
unsafe fn copy_one<T>(src: *mut T, dst: *mut T)
/*@ req copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*& *dst |-?-> ?old_dst; @*/
/*@ ens copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v; @*/
/*@ on_unwind_ens false; @*/
{
    //@ open copy_one_domain::<T>(src, dst);
    core::ptr::copy_nonoverlapping(src, dst, 1);
    //@ close copy_one_domain::<T>(src, dst);
}

// CASE_BEGIN copy_one_uninit_preserves_single_owner
pub unsafe fn copy_one_uninit_preserves_single_owner<T>(src: *mut T, dst: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*& *dst |-?-> none &*&
    <T>.own(t, v); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v &*&
    <T>.own(t, v); @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst);
}
// CASE_END copy_one_uninit_preserves_single_owner

// CASE_BEGIN copy_one_does_not_duplicate_own
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"verified/lib.rs","error_line":44,"column_start":41,"column_end":42,"message":"No matching heap chunks: own(T_typeid)(t, v)"}
pub unsafe fn copy_one_does_not_duplicate_own<T>(src: *mut T, dst: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*& *dst |-?-> none &*&
    <T>.own(t, v); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v &*&
    <T>.own(t, v); @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst);
    //@ assert <T>.own(t, v) &*& <T>.own(t, v); // TARGET: a byte copy cannot duplicate value ownership
}
// CASE_END copy_one_does_not_duplicate_own

// CASE_BEGIN copy_one_existing_valid_maybe_value
pub unsafe fn copy_one_existing_valid_maybe_value<T>(src: *mut T, dst: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*&
    *dst |-?-> some(?old_value) &*& <T>.own(t, v); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v &*&
    <T>.own(t, v); @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst);
}
// CASE_END copy_one_existing_valid_maybe_value

// CASE_BEGIN copy_one_preserves_disjoint_frame
pub unsafe fn copy_one_preserves_disjoint_frame<T>(src: *mut T, dst: *mut T, frame: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*&
    *dst |-?-> ?old_dst &*& *frame |-> ?frame_value &*& <T>.own(t, v); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v &*&
    *frame |-> frame_value &*& <T>.own(t, v); @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst);
}
// CASE_END copy_one_preserves_disjoint_frame

// CASE_BEGIN copy_one_does_not_require_or_create_own
pub unsafe fn copy_one_does_not_require_or_create_own<T>(src: *mut T, dst: *mut T)
/*@ req copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v) &*& *dst |-?-> none; @*/
/*@ ens copy_one_domain::<T>(src, dst) &*& [f](*src |-> v) &*& *dst |-> v; @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst);
}
// CASE_END copy_one_does_not_require_or_create_own

// CASE_BEGIN copy_one_missing_destination_write
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"verified/lib.rs","error_line":24,"column_start":71,"column_end":76,"message":"No matching heap chunks: points_to_<T>(dst, _)"}
pub unsafe fn copy_one_missing_destination_write<T>(src: *mut T, dst: *mut T)
/*@ req copy_one_domain::<T>(src, dst) &*& [?f](*src |-> ?v); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst); // TARGET: missing writable destination initialization chunk
}
// CASE_END copy_one_missing_destination_write

// CASE_BEGIN copy_one_uninitialized_source
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"bin/rust/prelude_core.rsspec","error_line":231,"column_start":53,"column_end":57,"message":"Cannot prove that 'none' is not an instance of constructor 'none'"}
pub unsafe fn copy_one_uninitialized_source<T>(src: *mut T, dst: *mut T)
/*@ req copy_one_domain::<T>(src, dst) &*& *src |-?-> none &*& *dst |-?-> none; @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    copy_one(src, dst); // TARGET: source bytes are uninitialized
}
// CASE_END copy_one_uninitialized_source

// CASE_BEGIN copy_one_overlapping_ranges
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"bin/rust/std/lib.rsspec","error_line":622,"column_start":562,"column_end":564,"message":"Cannot prove condition. (Cannot prove (get_pointer_address(ptr) + sizeof(T_typeid)) <= get_pointer_address(ptr) || (get_pointer_address(ptr) + sizeof(T_typeid)) <= get_pointer_address(ptr).)"}
pub unsafe fn copy_one_overlapping_ranges<T>(ptr: *mut T)
/*@ req 0 < ptr as usize &*& 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    ptr as usize % std::mem::align_of::<T>() == 0 &*&
    ptr as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(ptr, std::mem::size_of::<T>()) == true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    core::ptr::copy_nonoverlapping(ptr, ptr, 1); // TARGET: source and destination byte ranges overlap
}
// CASE_END copy_one_overlapping_ranges

// CASE_BEGIN copy_one_misaligned_source
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"bin/rust/std/lib.rsspec","error_line":622,"column_start":143,"column_end":145,"message":"Cannot prove condition. (Cannot prove %(get_pointer_address(src), alignof(T_typeid)) = 0.)"}
pub unsafe fn copy_one_misaligned_source<T>(src: *mut T, dst: *mut T)
/*@ req 0 < src as usize &*& 0 < dst as usize &*& 1 < std::mem::align_of::<T>() &*&
    src as usize % std::mem::align_of::<T>() != 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    src as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(src, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<T>()) == true &*&
    (src as usize + std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + std::mem::size_of::<T>() <= src as usize); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    core::ptr::copy_nonoverlapping(src, dst, 1); // TARGET: source alignment requirement
}
// CASE_END copy_one_misaligned_source

// CASE_BEGIN copy_one_misaligned_destination
// EXPECT_REJECTION {"kind":"primitive_precondition","error_file":"bin/rust/std/lib.rsspec","error_line":622,"column_start":193,"column_end":195,"message":"Cannot prove condition. (Cannot prove %(get_pointer_address(dst), alignof(T_typeid)) = 0.)"}
pub unsafe fn copy_one_misaligned_destination<T>(src: *mut T, dst: *mut T)
/*@ req 0 < src as usize &*& 0 < dst as usize &*& 1 < std::mem::align_of::<T>() &*&
    src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() != 0 &*&
    0 < std::mem::size_of::<T>() &*& std::mem::size_of::<T>() <= isize::MAX &*&
    src as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    object_pointer_within_limits(src, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<T>()) == true &*&
    (src as usize + std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + std::mem::size_of::<T>() <= src as usize); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    core::ptr::copy_nonoverlapping(src, dst, 1); // TARGET: destination alignment requirement
}
// CASE_END copy_one_misaligned_destination

// CASE_BEGIN copy_zero_count_uses_old_initialized_array_contract
pub unsafe fn copy_zero_count_uses_old_initialized_array_contract(src: *mut u8, dst: *mut u8)
/*@ req 0 < src as usize &*& 0 < dst as usize &*&
    src[..0] |-> [] &*& dst[..0] |-> []; @*/
/*@ ens 0 < src as usize &*& 0 < dst as usize &*&
    src[..0] |-> [] &*& dst[..0] |-> []; @*/
/*@ on_unwind_ens false; @*/
{
    core::ptr::copy_nonoverlapping(src, dst, 0);
}
// CASE_END copy_zero_count_uses_old_initialized_array_contract

// CASE_BEGIN copy_two_count_uses_old_initialized_array_contract
pub unsafe fn copy_two_count_uses_old_initialized_array_contract(src: *mut u8, dst: *mut u8)
/*@ req 0 < src as usize &*& 0 < dst as usize &*&
    src[..2] |-> ?values &*& dst[..2] |-> _; @*/
/*@ ens 0 < src as usize &*& 0 < dst as usize &*&
    src[..2] |-> values &*& dst[..2] |-> values; @*/
/*@ on_unwind_ens false; @*/
{
    core::ptr::copy_nonoverlapping(src, dst, 2);
}
// CASE_END copy_two_count_uses_old_initialized_array_contract

// CASE_BEGIN copy_zst_count_one_mapping_boundary_calibration
struct CopyControlZst;

pub unsafe fn copy_zst_count_one_mapping_boundary_calibration(src: *mut CopyControlZst, dst: *mut CopyControlZst)
/*@ req 0 < src as usize &*& 0 < dst as usize &*&
    src[..1] |-> ?values &*& dst[..1] |-> _; @*/
/*@ ens 0 < src as usize &*& 0 < dst as usize &*&
    src[..1] |-> values &*& dst[..1] |-> values; @*/
/*@ on_unwind_ens false; @*/
{
    // TARGET: support-only mapping calibration; no acceptance claim for ZSTs.
    core::ptr::copy_nonoverlapping(src, dst, 1);
}
// CASE_END copy_zst_count_one_mapping_boundary_calibration
