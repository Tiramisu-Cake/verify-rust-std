#![feature(unboxed_closures)]
#![allow(dead_code)]

// Prepared FnMut HRTB controls. These use the stock lifetime/loan API and
// source-cell, comparator, and reference-tuple resources. Only the exact-bound
// positive is a candidate body proof. TARGET cases remain INCONCLUSIVE until
// hosted diagnostics show the intended gate; marker output alone is never a
// proof that Output typing or the resource protocol succeeded.

// CASE_BEGIN prepared_hrtb_bool_shared_references
pub unsafe fn prepared_hrtb_bool_shared_references<T, F>(
    left_src: *const T,
    right_src: *const T,
    compare: &mut F,
) -> bool
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*& <T>.own(t, right0) &*&
    *compare |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left_src |-> ?left1 &*& <T>.own(t, left1) &*&
    *right_src |-> ?right1 &*& <T>.own(t, right1) &*&
    *compare |-> ?f1 &*& <F>.own(t, f1);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left_src |-> ?left_unwound &*& <T>.own(t, left_unwound) &*&
    *right_src |-> ?right_unwound &*& <T>.own(t, right_unwound) &*&
    *compare |-> ?f_unwound &*& <F>.own(t, f_unwound);
@*/
{
    //@ let cmp_k = begin_lifetime();
    let result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/

        //@ close_full_borrow_content::<T>(t, left_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, left_src as *T);

        //@ close_full_borrow_content::<T>(t, right_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, right_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, right_src as *T);

        //@ let left_ref = precreate_ref(left_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ let right_ref = precreate_ref(right_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_ref_own::<'cmp, T>(right_ref);
        /*@ close <(&'cmp T, &'cmp T)>.own(t,
                std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref }); @*/

        result = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(
            &*left_src,
            &*right_src,
        );

        //@ close [left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_frac_borrow(left_ref_frac, ref_initialized_(left_ref));
        //@ close [right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_frac_borrow(right_ref_frac, ref_initialized_(right_ref));
    }

    //@ end_lifetime(cmp_k);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T));
    //@ open_full_borrow_content::<T>(t, left_src as *T);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T));
    //@ open_full_borrow_content::<T>(t, right_src as *T);
    result
}
// CASE_END prepared_hrtb_bool_shared_references

// CASE_BEGIN prepared_hrtb_wrong_ghost_function_type
pub unsafe fn prepared_hrtb_wrong_ghost_function_type<T, F, G>(
    left_src: *const T,
    right_src: *const T,
    compare: &mut F,
) -> bool
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*& type_interp::<G>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*& <T>.own(t, right0) &*&
    *compare |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*& type_interp::<G>() &*&
    *left_src |-> ?left1 &*& <T>.own(t, left1) &*&
    *right_src |-> ?right1 &*& <T>.own(t, right1) &*&
    *compare |-> ?f1 &*& <F>.own(t, f1);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*& type_interp::<G>() &*&
    *left_src |-> ?left_unwound &*& <T>.own(t, left_unwound) &*&
    *right_src |-> ?right_unwound &*& <T>.own(t, right_unwound) &*&
    *compare |-> ?f_unwound &*& <F>.own(t, f_unwound);
@*/
{
    //@ let cmp_k = begin_lifetime();
    let result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close_full_borrow_content::<T>(t, left_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, left_src as *T);
        //@ close_full_borrow_content::<T>(t, right_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, right_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, right_src as *T);
        //@ let left_ref = precreate_ref(left_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ let right_ref = precreate_ref(right_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_ref_own::<'cmp, T>(right_ref);
        /*@ close <(&'cmp T, &'cmp T)>.own(t,
                std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref }); @*/

        result = compare/*@::<G, (&'cmp T, &'cmp T), 'cmp>@*/(
            &*left_src,
            &*right_src,
        ); // TARGET: ghost F differs; resources for source F/T are prepared

        //@ close [left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_frac_borrow(left_ref_frac, ref_initialized_(left_ref));
        //@ close [right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_frac_borrow(right_ref_frac, ref_initialized_(right_ref));
    }
    //@ end_lifetime(cmp_k);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T));
    //@ open_full_borrow_content::<T>(t, left_src as *T);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T));
    //@ open_full_borrow_content::<T>(t, right_src as *T);
    result
}
// CASE_END prepared_hrtb_wrong_ghost_function_type

// CASE_BEGIN prepared_hrtb_wrong_ghost_referent_type
pub unsafe fn prepared_hrtb_wrong_ghost_referent_type<T, U, F>(
    left_src: *const T,
    right_src: *const T,
    compare: &mut F,
) -> bool
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<U>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*& <T>.own(t, right0) &*&
    *compare |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<U>() &*& type_interp::<F>() &*&
    *left_src |-> ?left1 &*& <T>.own(t, left1) &*&
    *right_src |-> ?right1 &*& <T>.own(t, right1) &*&
    *compare |-> ?f1 &*& <F>.own(t, f1);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<U>() &*& type_interp::<F>() &*&
    *left_src |-> ?left_unwound &*& <T>.own(t, left_unwound) &*&
    *right_src |-> ?right_unwound &*& <T>.own(t, right_unwound) &*&
    *compare |-> ?f_unwound &*& <F>.own(t, f_unwound);
@*/
{
    //@ let cmp_k = begin_lifetime();
    let result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close_full_borrow_content::<T>(t, left_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, left_src as *T);
        //@ close_full_borrow_content::<T>(t, right_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, right_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, right_src as *T);
        //@ let left_ref = precreate_ref(left_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ let right_ref = precreate_ref(right_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_ref_own::<'cmp, T>(right_ref);
        /*@ close <(&'cmp T, &'cmp T)>.own(t,
                std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref }); @*/

        result = compare/*@::<F, (&'cmp U, &'cmp U), 'cmp>@*/(
            &*left_src,
            &*right_src,
        ); // TARGET: ghost referent U differs; source T resources are complete

        //@ close [left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_frac_borrow(left_ref_frac, ref_initialized_(left_ref));
        //@ close [right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_frac_borrow(right_ref_frac, ref_initialized_(right_ref));
    }
    //@ end_lifetime(cmp_k);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T));
    //@ open_full_borrow_content::<T>(t, left_src as *T);
    //@ borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T));
    //@ open_full_borrow_content::<T>(t, right_src as *T);
    result
}
// CASE_END prepared_hrtb_wrong_ghost_referent_type

// CASE_BEGIN prepared_hrtb_missing_comparator_own
pub unsafe fn prepared_hrtb_missing_comparator_own<T, F>(
    left_src: *const T,
    right_src: *const T,
    compare: &mut F,
) -> bool
where
    F: for<'a, 'b> core::ops::FnMut<(&'a T, &'b T), Output = bool>,
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*& <T>.own(t, right0) &*& *compare |-> ?f0;
@*/
/*@ ens true; @*/
/*@ on_unwind_ens true; @*/
{
    //@ let cmp_k = begin_lifetime();
    let result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close_full_borrow_content::<T>(t, left_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, left_src as *T);
        //@ close_full_borrow_content::<T>(t, right_src as *T);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, right_src as *T));
        //@ share_full_borrow::<T>(cmp_k, t, right_src as *T);
        //@ let left_ref = precreate_ref(left_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ let right_ref = precreate_ref(right_src as *T);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_ref_frac]ref_initialized_::<T>(left_ref)();
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_ref_frac]ref_initialized_::<T>(right_ref)();
        //@ close_ref_own::<'cmp, T>(right_ref);
        /*@ close <(&'cmp T, &'cmp T)>.own(t,
                std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref }); @*/

        result = compare/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(
            &*left_src,
            &*right_src,
        ); // TARGET: comparator state is present but own(F) is missing
    }
    result
}
// CASE_END prepared_hrtb_missing_comparator_own
