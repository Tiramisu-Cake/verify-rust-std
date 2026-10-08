#![no_std]
#![allow(dead_code)]

pub unsafe fn join_four_control<T, F>(
    base: *const T,
    dst: *mut T,
    is_less: *mut F,
) /*@
req thread_token(?t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    0 < std::mem::size_of::<T>() &*&
    *base |-> ?x0 &*& <T>.own(t, x0) &*&
    *(base + 1) |-> ?x1 &*& <T>.own(t, x1) &*&
    *(base + 2) |-> ?x2 &*& <T>.own(t, x2) &*&
    *(base + 3) |-> ?x3 &*& <T>.own(t, x3) &*&
    array_::<T>(dst, 4, ?destination) &*&
    *is_less |-> ?f &*& <F>.own(t, f);
@*/ /*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    0 < std::mem::size_of::<T>() &*&
    base[..4] |-> cons(x0, cons(x1, cons(x2, cons(x3, nil)))) &*&
    foreach(cons(x0, cons(x1, cons(x2, cons(x3, nil)))), own::<T>(t)) &*&
    array_::<T>(dst, 4, destination) &*&
    *is_less |-> f &*& <F>.own(t, f);
@*/ {
    //@ join_four_owned_cells::<T>(base, t);
}
