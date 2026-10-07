#![no_std]
#![allow(dead_code)]

pub struct NonCopy {
    value: u32,
}

pub struct Other<T>(pub T);

// CASE_BEGIN tuple2_close_generic
pub unsafe fn tuple2_close_generic<T1, T2>(first: T1, second: T2) -> (T1, T2)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, first) &*& <T2>.own(t, second);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <(T1, T2)>.own(t, result);
@*/
{
    let pair = (first, second);
    //@ close <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_close_generic

// CASE_BEGIN tuple2_open_generic
pub unsafe fn tuple2_open_generic<T1, T2>(pair: (T1, T2)) -> (T1, T2)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <(T1, T2)>.own(t, pair);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1);
@*/
{
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_open_generic

// CASE_BEGIN tuple2_noncopy_refs
pub unsafe fn tuple2_noncopy_refs<'a>(
    left: &'a NonCopy,
    right: &'a NonCopy,
) -> (&'a NonCopy, &'a NonCopy)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<NonCopy>() &*&
    <&'a NonCopy>.own(t, left) &*& <&'a NonCopy>.own(t, right);
@*/
/*@ ens thread_token(t) &*& type_interp::<NonCopy>() &*&
    <(&'a NonCopy, &'a NonCopy)>.own(t, result);
@*/
{
    let pair = (left, right);
    //@ close <(&'a NonCopy, &'a NonCopy)>.own(t, pair);
    pair
}
// CASE_END tuple2_noncopy_refs

// CASE_BEGIN tuple2_share_compat
pub unsafe fn tuple2_share_compat<'a, T1, T2>(pair: &(T1, T2))
/*@ req thread_token(?t) &*& t == currentThread &*&
    [?q]lifetime_token('a) &*&
    [_](<T1>.share('a, t, &(*pair).0)) &*&
    [_](<T2>.share('a, t, &(*pair).1));
@*/
/*@ ens thread_token(t) &*& [q]lifetime_token('a) &*&
    [_](<(T1, T2)>.share('a, t, pair));
@*/
{
    //@ close <(T1, T2)>.share('a, t, pair);
}
// CASE_END tuple2_share_compat

// CASE_BEGIN tuple2_false_post
pub unsafe fn tuple2_false_post<T1, T2>(first: T1, second: T2) -> (T1, T2)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, first) &*& <T2>.own(t, second);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <(T1, T2)>.own(t, result) &*& false;
@*/
{
    let pair = (first, second);
    //@ close <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_false_post

// CASE_BEGIN tuple2_resource_loss
pub unsafe fn tuple2_resource_loss<T1, T2>(pair: (T1, T2)) -> (T1, T2)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <(T1, T2)>.own(t, pair);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*&
    <T1>.own(t, result.0);
@*/
{
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_resource_loss

// CASE_BEGIN tuple2_resource_duplication
pub unsafe fn tuple2_resource_duplication<T>(pair: (T, T)) -> (T, T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    <(T, T)>.own(t, pair);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    <T>.own(t, result.0) &*& <T>.own(t, result.0) &*& <T>.own(t, result.1);
@*/
{
    //@ open <(T, T)>.own(t, pair);
    pair
}
// CASE_END tuple2_resource_duplication

// CASE_BEGIN tuple1_opaque_control
pub unsafe fn tuple1_opaque_control<T>(first: T) -> (T,)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    <T>.own(t, first);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*& <(T,)>.own(t, result);
@*/
{
    let tuple = (first,);
    //@ close <(T,)>.own(t, tuple);
    tuple
}
// CASE_END tuple1_opaque_control

// CASE_BEGIN tuple3_opaque_control
pub unsafe fn tuple3_opaque_control<T1, T2, T3>(first: T1, second: T2, third: T3)
    -> (T1, T2, T3)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*& type_interp::<T3>() &*&
    <T1>.own(t, first) &*& <T2>.own(t, second) &*& <T3>.own(t, third);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    type_interp::<T3>() &*& <(T1, T2, T3)>.own(t, result);
@*/
{
    let tuple = (first, second, third);
    //@ close <(T1, T2, T3)>.own(t, tuple);
    tuple
}
// CASE_END tuple3_opaque_control

// CASE_BEGIN tuple4_opaque_control
pub unsafe fn tuple4_opaque_control<T1, T2, T3, T4>(
    first: T1, second: T2, third: T3, fourth: T4,
) -> (T1, T2, T3, T4)
/*@ req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    type_interp::<T3>() &*& type_interp::<T4>() &*&
    <T1>.own(t, first) &*& <T2>.own(t, second) &*&
    <T3>.own(t, third) &*& <T4>.own(t, fourth);
@*/
/*@ ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    type_interp::<T3>() &*& type_interp::<T4>() &*&
    <(T1, T2, T3, T4)>.own(t, result);
@*/
{
    let tuple = (first, second, third, fourth);
    //@ close <(T1, T2, T3, T4)>.own(t, tuple);
    tuple
}
// CASE_END tuple4_opaque_control

// CASE_BEGIN unrelated_struct_opaque_control
pub unsafe fn unrelated_struct_opaque_control<T>(value: T) -> Other<T>
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    <T>.own(t, value);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*& <Other<T>>.own(t, result);
@*/
{
    let wrapped = Other(value);
    //@ close <Other<T>>.own(t, wrapped);
    wrapped
}
// CASE_END unrelated_struct_opaque_control
