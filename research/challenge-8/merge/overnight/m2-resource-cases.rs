#![allow(dead_code)]
// Generic tuple-2 ownership controls for the pinned callback profile.
// These cases establish field-owner threading, exact value ownership and an
// unrelated frame obligation; they do not use FnMut or imply a merge proof.

// CASE_BEGIN tuple2_owner_thread_value_frame_positive
pub unsafe fn tuple2_owner_thread_value_frame_positive<T1, T2>(
    pair: (T1, T2), frame: *mut u32,
) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, pair.0) &*& <T2>.own(t, pair.1) &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value);
@*//*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?unwound_first) &*& <T2>.own(t, ?unwound_second) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*/
{
    //@ close <(T1, T2)>.own(t, pair);
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_owner_thread_value_frame_positive

// CASE_BEGIN tuple2_missing_first_field_owner
// EXPECT_REJECTION {"kind":"tuple_resource","error_file":"bin/rust/prelude.rsspec","error_line":15,"column_start":8,"column_end":20,"message":"No matching heap chunks: own(T1_typeid)(t, get_std_tuple_2__0(pair0))"}
pub unsafe fn tuple2_missing_first_field_owner<T1, T2>(
    pair: (T1, T2), frame: *mut u32,
) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T2>.own(t, pair.1) &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value);
@*//*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?unwound_first) &*& <T2>.own(t, ?unwound_second) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*/
{
    //@ close <(T1, T2)>.own(t, pair); // TARGET: tuple expansion must require the first field owner
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_missing_first_field_owner

// CASE_BEGIN tuple2_wrong_thread_first_field_owner
// EXPECT_REJECTION {"kind":"tuple_resource","error_file":"bin/rust/prelude.rsspec","error_line":15,"column_start":8,"column_end":20,"message":"No matching heap chunks: own(T1_typeid)(t, get_std_tuple_2__0(pair0))"}
pub unsafe fn tuple2_wrong_thread_first_field_owner<T1, T2>(
    pair: (T1, T2), frame: *mut u32,
) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(?other_thread, pair.0) &*& other_thread != t &*&
    <T2>.own(t, pair.1) &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value);
@*//*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?unwound_first) &*& <T2>.own(t, ?unwound_second) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*/
{
    //@ close <(T1, T2)>.own(t, pair); // TARGET: field ownership at another thread cannot satisfy this tuple
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_wrong_thread_first_field_owner

// CASE_BEGIN tuple2_wrong_value_first_field_owner
// EXPECT_REJECTION {"kind":"tuple_resource","error_file":"bin/rust/prelude.rsspec","error_line":15,"column_start":8,"column_end":20,"message":"No matching heap chunks: own(T1_typeid)(t, get_std_tuple_2__0(pair0))"}
pub unsafe fn tuple2_wrong_value_first_field_owner<T1, T2>(
    pair: (T1, T2), frame: *mut u32,
) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?other_first) &*& other_first != pair.0 &*&
    <T2>.own(t, pair.1) &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value);
@*//*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?unwound_first) &*& <T2>.own(t, ?unwound_second) &*&
    *frame |-> frame_value &*& <u32>.own(t, frame_value);
@*/
{
    //@ close <(T1, T2)>.own(t, pair); // TARGET: a same-thread owner for another value is insufficient
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_wrong_value_first_field_owner

// CASE_BEGIN tuple2_frame_value_retention_negative
// Calibration oracle intentionally pending: record the exact assertion
// diagnostic before assigning a proof-negative classification.
pub unsafe fn tuple2_frame_value_retention_negative<T1, T2>(
    pair: (T1, T2), frame: *mut u32,
) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, pair.0) &*& <T2>.own(t, pair.1) &*&
    *frame |-> 41 &*& <u32>.own(t, 41);
@*//*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1) &*&
    *frame |-> 41 &*& <u32>.own(t, 41);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, ?unwound_first) &*& <T2>.own(t, ?unwound_second) &*&
    *frame |-> 41 &*& <u32>.own(t, 41);
@*/
{
    //@ close <(T1, T2)>.own(t, pair);
    //@ open <(T1, T2)>.own(t, pair);
    //@ assert *frame |-> 73; // TARGET: the unrelated frame still owns value 41
    pair
}
// CASE_END tuple2_frame_value_retention_negative
