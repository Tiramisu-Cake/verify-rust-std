#![allow(dead_code)]
#![feature(unboxed_closures)]
// Tuple and FnMut frontend diagnostics for callback.patch.
// HRTB cases are support-only: each call has a TARGET marker so the shared
// pointer harness must leave the case INCONCLUSIVE even if its trivial body
// verifies. MERGE_HRTB_* log evidence is not an accepted callback-body proof.

// CASE_BEGIN tuple2_field_resources
pub unsafe fn tuple2_field_resources<T1, T2>(pair: (T1, T2)) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, pair.0) &*& <T2>.own(t, pair.1);
@*/
/*@
ens thread_token(t) &*& type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, result.0) &*& <T2>.own(t, result.1);
@*/
/*@ on_unwind_ens false; @*/
{
    //@ close <(T1, T2)>.own(t, pair);
    //@ open <(T1, T2)>.own(t, pair);
    pair
}
// CASE_END tuple2_field_resources

// CASE_BEGIN tuple2_missing_second_field_own
// EXPECT_REJECTION {"kind":"tuple_resource","error_file":"bin/rust/prelude.rsspec","error_line":15,"column_start":8,"column_end":20,"message":"No matching heap chunks: own(T2_typeid)(t, get_std_tuple_2__1(pair0))"}
pub unsafe fn tuple2_missing_second_field_own<T1, T2>(pair: (T1, T2)) -> (T1, T2)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T1>() &*& type_interp::<T2>() &*&
    <T1>.own(t, pair.0);
@*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ close <(T1, T2)>.own(t, pair); // TARGET: tuple close requires the missing T2 field resource
    pair
}
// CASE_END tuple2_missing_second_field_own

// CASE_BEGIN hrtb_bool_common_lifetime_two_calls
pub unsafe fn hrtb_bool_common_lifetime_two_calls<'cmp, T, F>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) -> bool
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let first = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right);
    let second = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right); // TARGET: both calls are checked; support-only only
    first && second
}
// CASE_END hrtb_bool_common_lifetime_two_calls

// CASE_BEGIN hrtb_wrong_output_u8
pub unsafe fn hrtb_wrong_output_u8<'cmp, T, F>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
) -> u8
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = u8>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right); // TARGET: wrong associated output must not register
    0
}
// CASE_END hrtb_wrong_output_u8

// CASE_BEGIN hrtb_unconstrained_output
pub unsafe fn hrtb_unconstrained_output<'cmp, T, F>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
)
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T)>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right); // TARGET: unconstrained Output must not register
}
// CASE_END hrtb_unconstrained_output

// CASE_BEGIN hrtb_wrong_ghost_function_type
pub unsafe fn hrtb_wrong_ghost_function_type<'cmp, T, F, G>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
)
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/(left, right); // TARGET: ghost F differs from source F
}
// CASE_END hrtb_wrong_ghost_function_type

// CASE_BEGIN hrtb_wrong_ghost_referent_type
pub unsafe fn hrtb_wrong_ghost_referent_type<'cmp, T, U, F>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
)
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/(left, right); // TARGET: ghost T differs from source T
}
// CASE_END hrtb_wrong_ghost_referent_type

// CASE_BEGIN hrtb_unequal_ghost_lifetimes
pub unsafe fn hrtb_unequal_ghost_lifetimes<'left, 'right, T, F>(
    left: &'left T,
    right: &'right T,
    compare: &mut F,
)
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<F, (&'left T, &'right T), 'left>@*/(left, right); // TARGET: unequal ghost field lifetimes must not register
}
// CASE_END hrtb_unequal_ghost_lifetimes

// CASE_BEGIN hrtb_single_region_source_bound
pub unsafe fn hrtb_single_region_source_bound<'cmp, T, F>(
    left: &'cmp T,
    right: &'cmp T,
    compare: &mut F,
)
where
    F: core::ops::FnMut(&'cmp T, &'cmp T) -> bool,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(left, right); // TARGET: one named region is not the two-region source bound
}
// CASE_END hrtb_single_region_source_bound

// CASE_BEGIN hrtb_bound_must_stay_with_its_body
fn hrtb_bound_only<'cmp, T, F>(_: &'cmp T, _: &'cmp T, _: &mut F)
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
}

pub unsafe fn hrtb_unrelated_body_call<G: core::ops::FnMut() -> bool>(callback: &mut G)
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    let _ = callback/*@::<G, (), 'static>@*/(); // TARGET: bound in sibling body must not register
}
// CASE_END hrtb_bound_must_stay_with_its_body
