#![no_std]
#![allow(dead_code)]

/*@
pred comparison_debt<T>(
    t: thread_id_t, k: lifetime_t, left: *T, right: *T,
    left_ref: *T, right_ref: *T, left_fraction: real, right_fraction: real) =
    [left_fraction]ref_initialized::<T>(left_ref) &*&
    close_frac_borrow_token(
        left_fraction, ref_initialized_::<T>(left_ref), 1/4, k) &*&
    [right_fraction]ref_initialized::<T>(right_ref) &*&
    close_frac_borrow_token(
        right_fraction, ref_initialized_::<T>(right_ref), 1/4, k) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, left)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, right));
@*/

/*@
lem recover_pair<T>(left: *T, right: *T)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*&
        comparison_debt::<T>(
            t, ?k, left, right, ?left_ref, ?right_ref,
            ?left_fraction, ?right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        *left |-> ?left_after &*& <T>.own(t, left_after) &*&
        *right |-> ?right_after &*& <T>.own(t, right_after);
{
    open comparison_debt::<T>(
        t, k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    close [left_fraction]ref_initialized_::<T>(left_ref)();
    close_frac_borrow(left_fraction, ref_initialized_::<T>(left_ref));
    close [right_fraction]ref_initialized_::<T>(right_ref)();
    close_frac_borrow(right_fraction, ref_initialized_::<T>(right_ref));
    merge_fractions lifetime_token(k);
    end_lifetime(k);
    borrow_end(k, <T>.full_borrow_content(t, left));
    open_full_borrow_content::<T>(t, left);
    borrow_end(k, <T>.full_borrow_content(t, right));
    open_full_borrow_content::<T>(t, right);
}
@*/

// CASE_BEGIN callback_positive
pub unsafe fn callback_positive<T, F: FnMut(&T, &T) -> bool>(
    left: *const T,
    right: *const T,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_before &*& <T>.own(t, left_before) &*&
    *right |-> ?right_before &*& <T>.own(t, right_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_after &*& <T>.own(t, left_after) &*&
    *right |-> ?right_after &*& <T>.own(t, right_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_after &*& <T>.own(t, left_after) &*&
    *right |-> ?right_after &*& <T>.own(t, right_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
{
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<T>(t, left);
    //@ close_full_borrow_content::<T>(t, right);
    //@ borrow(cmp_k, <T>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <T>.full_borrow_content(t, right));
    let mut result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<T>(cmp_k, t, left);
        //@ share_full_borrow::<T>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ close_ref_own::<'cmp, T>(right_ref);
        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref });
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<T>(left_ref)();
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<T>(right_ref)();
        /*@ {
            __vf_callback_unwind_pair();
            { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(left, right); }
        } @*/
        let answer = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*left, &*right);
        //@ close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
        result = answer;
    };
    //@ recover_pair::<T>(left, right);
    result
}
// CASE_END callback_positive

// CASE_BEGIN callback_false_post
pub unsafe fn callback_false_post<T, F: FnMut(&T, &T) -> bool>(
    left: *const T,
    right: *const T,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_before &*& <T>.own(t, left_before) &*&
    *right |-> ?right_before &*& <T>.own(t, right_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_after &*& <T>.own(t, left_after) &*&
    *right |-> ?right_after &*& <T>.own(t, right_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after) &*& false;
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left |-> ?left_after &*& <T>.own(t, left_after) &*&
    *right |-> ?right_after &*& <T>.own(t, right_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
{
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<T>(t, left);
    //@ close_full_borrow_content::<T>(t, right);
    //@ borrow(cmp_k, <T>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <T>.full_borrow_content(t, right));
    let mut result: bool;
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<T>(cmp_k, t, left);
        //@ share_full_borrow::<T>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ close_ref_own::<'cmp, T>(right_ref);
        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref });
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<T>(left_ref)();
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<T>(right_ref)();
        /*@ {
            __vf_callback_unwind_pair();
            { close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction); }
            { recover_pair::<T>(left, right); }
        } @*/
        let answer = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*left, &*right);
        //@ close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
        result = answer;
    };
    //@ recover_pair::<T>(left, right);
    result
}
// CASE_END callback_false_post
