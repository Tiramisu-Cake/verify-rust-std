// Cloud-only, source-independent raw-copy ownership component for Select-R15.
// This fixture checks the stock primitive contract, not the actual
// sort4_stable body or its call-site/source binding.
#![allow(dead_code)]

use std::ptr;

// CASE_BEGIN raw-copy-one-owner-positive
unsafe fn copy_one_raw_representation<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?values &*& foreach(values, own::<T>(t)) &*&
    dst[..1] |-?-> cons(none, nil);
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> values &*& foreach(values, own::<T>(t)) &*&
    dst[..1] |-> values;
@*/
/*@ on_unwind_ens false; @*/
{
    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
}
// CASE_END raw-copy-one-owner-positive

// CASE_BEGIN raw-copy-one-owner-duplicate-negative
unsafe fn copy_one_raw_representation_duplicate_owner<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?values &*& foreach(values, own::<T>(t)) &*&
    dst[..1] |-?-> cons(none, nil);
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> values &*& foreach(values, own::<T>(t)) &*&
    dst[..1] |-> values &*& foreach(values, own::<T>(t));
@*/
/*@ on_unwind_ens false; @*/
{
    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
}
// CASE_END raw-copy-one-owner-duplicate-negative

// CASE_BEGIN raw-copy-missing-initialized-source-negative
unsafe fn copy_one_raw_representation_missing_source<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-?-> cons(none, nil) &*&
    dst[..1] |-?-> cons(none, nil);
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-?-> cons(none, nil) &*&
    dst[..1] |-?-> cons(none, nil);
@*/
/*@ on_unwind_ens false; @*/
{
    // Expected to fail at the primitive precondition: a raw copy reads a
    // fully initialized source element.
    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
}
// CASE_END raw-copy-missing-initialized-source-negative

// CASE_BEGIN raw-copy-missing-destination-rights-negative
unsafe fn copy_one_raw_representation_missing_destination<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> ?values &*& foreach(values, own::<T>(t));
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..1] |-> values &*& foreach(values, own::<T>(t));
@*/
/*@ on_unwind_ens false; @*/
{
    // Expected to fail at the primitive precondition: the destination has no
    // writable optional points-to permission.
    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
}
// CASE_END raw-copy-missing-destination-rights-negative
