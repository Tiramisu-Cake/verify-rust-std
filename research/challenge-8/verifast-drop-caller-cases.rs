#![allow(dead_code)]

// Isolated caller fragments. The extractor supplies the exact std
// CopyOnDrop<T> block and its current contract from extract-verifast-drop.py.

// CASE_BEGIN cleanup_one
pub unsafe fn cleanup_one<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    [?f]src[..1] |-> ?src_values &*& foreach(src_values, own::<T>(t)) &*&
    dst[..1] |-> _;
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    [f]src[..1] |-> src_values &*& foreach(src_values, own::<T>(t)) &*&
    dst[..1] |-> src_values;
@*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
}
// CASE_END cleanup_one

// CASE_BEGIN cleanup_callback
pub unsafe fn cleanup_callback<T, F: FnMut()>(src: *const T, dst: *mut T, callback: &mut F)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&
    [?f]src[..1] |-> ?src_values &*& foreach(src_values, own::<T>(t)) &*&
    dst[..1] |-> _ &*& *callback |-> ?callback_before &*& <F>.own(t, callback_before);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    [f]src[..1] |-> src_values &*& foreach(src_values, own::<T>(t)) &*&
    dst[..1] |-> src_values &*& *callback |-> ?callback_after &*& <F>.own(t, callback_after);
@*/
/*@ on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    [f]src[..1] |-> src_values &*& foreach(src_values, own::<T>(t)) &*&
    dst[..1] |-> src_values &*& *callback |-> ?callback_after &*& <F>.own(t, callback_after);
@*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
    //@ close_tuple_0_own(t);
    callback();
    //@ open_tuple_0_own(t);
}
// CASE_END cleanup_callback

// CASE_BEGIN negative_missing_source
pub unsafe fn negative_missing_source<T>(src: *const T, dst: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    foreach(?src_values, own::<T>(t)) &*& dst[..1] |-> _;
@*/
/*@ ens true; @*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
}
// CASE_END negative_missing_source

// CASE_BEGIN negative_missing_destination
pub unsafe fn negative_missing_destination<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?src_values &*& foreach(src_values, own::<T>(t));
@*/
/*@ ens true; @*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
}
// CASE_END negative_missing_destination

// CASE_BEGIN negative_missing_own
pub unsafe fn negative_missing_own<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?src_values &*& dst[..1] |-> _;
@*/
/*@ ens true; @*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
}
// CASE_END negative_missing_own

// CASE_BEGIN negative_unannotated_drop
pub unsafe fn negative_unannotated_drop<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?src_values &*& foreach(src_values, own::<T>(t)) &*& dst[..1] |-> _;
@*/
/*@ ens true; @*/ {
    let _guard = CopyOnDrop { src, dst, len: 1 };
}
// CASE_END negative_unannotated_drop

// These types live only in isolated structural-rejection crates. Their
// annotated destructors are intentionally trivial; the test is that an
// unsupported local shape is rejected at its actual local Drop site.
// CASE_BEGIN unsupported_extra_field
struct ExtraField<T> {
    src: *const T,
    dst: *mut T,
    len: usize,
    extra: usize,
}

impl<T> Drop for ExtraField<T> {
    fn drop(&mut self) /*@ req true; @*/ /*@ ens true; @*/ /*@ on_unwind_ens false; @*/ {}
}

pub fn unsupported_extra_field()
/*@ req true; @*/
/*@ ens true; @*/ {
    let _guard = ExtraField::<u8> { src: core::ptr::null(), dst: core::ptr::null_mut(), len: 1, extra: 0 };
}
// CASE_END unsupported_extra_field

// CASE_BEGIN unsupported_copy_bound
struct CopyBound<T: Copy> {
    src: *const T,
    dst: *mut T,
    len: usize,
}

impl<T: Copy> Drop for CopyBound<T> {
    fn drop(&mut self) /*@ req true; @*/ /*@ ens true; @*/ /*@ on_unwind_ens false; @*/ {}
}

pub fn unsupported_copy_bound()
/*@ req true; @*/
/*@ ens true; @*/ {
    let _guard = CopyBound::<u8> { src: core::ptr::null(), dst: core::ptr::null_mut(), len: 1 };
}
// CASE_END unsupported_copy_bound
