// Cloud-only, source-independent four-copy resource component for Select-R15.
// This checks raw representation copying and ownership framing only; it does
// not verify the sort4 callback sequence or bind a pointer to std source.
#![allow(dead_code)]

use std::ptr;

// The proof follows the stock array invariant: an interior pointer is derived
// from an initialized four-element array, without reasoning from addresses.
/*@
lem four_copy_interior_pointer_limits<T>(base: *T, index: usize)
    req [?f]base[..4] |-> ?xs &*& 0 <= index &*& index < 4;
    ens [f]base[..4] |-> xs &*& pointer_within_limits(base + index) == true;
{
    open array(base, 4, xs);
    points_to_limits(base);
    close [f]array(base, 4, xs);
    note(0 <= std::mem::size_of::<T>());
    array_inv::<T>();
    mul_mono_l(0, index, std::mem::size_of::<T>());
    mul_mono_l(index, 4, std::mem::size_of::<T>());
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + 4));
}

lem four_copy_optional_destination_limits<T>(base: *T, index: usize)
    req [?f]base[..4] |-?-> ?slots &*& 0 <= index &*& index < 4;
    ens [f]base[..4] |-?-> slots &*& pointer_within_limits(base + index) == true;
{
    note(0 <= std::mem::size_of::<T>());
    array__inv::<T>();
    mul_mono_l(0, index, std::mem::size_of::<T>());
    mul_mono_l(index, 4, std::mem::size_of::<T>());
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + 4));
}
@*/

// CASE_BEGIN raw-four-copy-identity-positive
unsafe fn copy_four_raw_representations_identity<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..4] |-> ?values &*& foreach(values, own::<T>(t)) &*&
    dst[..4] |-?-> cons(none, cons(none, cons(none, cons(none, nil))));
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
    dst[..4] |-> values;
@*/
/*@ on_unwind_ens false; @*/
{
    // Establish the source interior pointers using the checked array-based
    // bounds lemma, then split only representation permissions. The single
    // foreach owner remains framed over all four primitive calls.
    //@ four_copy_interior_pointer_limits::<T>(src, 0);
    //@ four_copy_interior_pointer_limits::<T>(src, 1);
    //@ four_copy_interior_pointer_limits::<T>(src, 2);
    //@ four_copy_interior_pointer_limits::<T>(src, 3);
    //@ four_copy_optional_destination_limits::<T>(dst, 0);
    //@ four_copy_optional_destination_limits::<T>(dst, 1);
    //@ four_copy_optional_destination_limits::<T>(dst, 2);
    //@ four_copy_optional_destination_limits::<T>(dst, 3);

    //@ array_split::<T>(src, 1);
    //@ array_split::<T>(src + 1, 1);
    //@ array_split::<T>(src + 2, 1);

    //@ array__split::<T>(dst, 1);
    //@ array__split::<T>(dst + 1, 1);
    //@ array__split::<T>(dst + 2, 1);

    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(1), dst.add(1), 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(2), dst.add(2), 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(3), dst.add(3), 1) };

    //@ array_join::<T>(dst);
    //@ array_join::<T>(dst);
    //@ array_join::<T>(dst);
    //@ array_join::<T>(src);
    //@ array_join::<T>(src);
    //@ array_join::<T>(src);
}
// CASE_END raw-four-copy-identity-positive

// CASE_BEGIN raw-four-copy-duplicate-owner-negative
unsafe fn copy_four_raw_representations_duplicate_owner<T>(src: *const T, dst: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..4] |-> ?values &*& foreach(values, own::<T>(t)) &*&
    dst[..4] |-?-> cons(none, cons(none, cons(none, cons(none, nil))));
@*/
/*@
ens thread_token(t) &*& t == currentThread &*& type_interp::<T>() &*&
    src[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
    dst[..4] |-> values &*& foreach(values, own::<T>(t));
@*/
/*@ on_unwind_ens false; @*/
{
    // Repeat the body so the negative case has no dependency on another
    // fixture case's verified summary. The requested extra owner is absent.
    //@ four_copy_interior_pointer_limits::<T>(src, 0);
    //@ four_copy_interior_pointer_limits::<T>(src, 1);
    //@ four_copy_interior_pointer_limits::<T>(src, 2);
    //@ four_copy_interior_pointer_limits::<T>(src, 3);
    //@ four_copy_optional_destination_limits::<T>(dst, 0);
    //@ four_copy_optional_destination_limits::<T>(dst, 1);
    //@ four_copy_optional_destination_limits::<T>(dst, 2);
    //@ four_copy_optional_destination_limits::<T>(dst, 3);

    //@ array_split::<T>(src, 1);
    //@ array_split::<T>(src + 1, 1);
    //@ array_split::<T>(src + 2, 1);

    //@ array__split::<T>(dst, 1);
    //@ array__split::<T>(dst + 1, 1);
    //@ array__split::<T>(dst + 2, 1);

    unsafe { ptr::copy_nonoverlapping(src, dst, 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(1), dst.add(1), 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(2), dst.add(2), 1) };
    unsafe { ptr::copy_nonoverlapping(src.add(3), dst.add(3), 1) };

    //@ array_join::<T>(dst);
    //@ array_join::<T>(dst);
    //@ array_join::<T>(dst);
    //@ array_join::<T>(src);
    //@ array_join::<T>(src);
    //@ array_join::<T>(src);
}
// CASE_END raw-four-copy-duplicate-owner-negative
