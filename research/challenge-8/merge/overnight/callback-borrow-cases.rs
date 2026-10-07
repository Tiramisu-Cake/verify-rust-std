#![feature(unboxed_closures)]
#![allow(dead_code)]

// Resource-protocol fixture for callback.patch on stock VeriFast 26.10.
// This isolates the source-reference/borrow/FnMut boundary. It is not an
// extracted merge_up body and proves no relationship to a merge implementation.

// CASE_BEGIN two_shared_callback_refs
pub unsafe fn two_shared_callback_refs<T, F: FnMut(&T, &T) -> bool>(
    left_src: *const T,
    right_src: *const T,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*& <T>.own(t, right0) &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left_src |-> ?left1 &*& <T>.own(t, left1) &*&
    *right_src |-> ?right1 &*& <T>.own(t, right1) &*&
    *is_less |-> ?f1 &*& <F>.own(t, f1);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *left_src |-> ?left_unwound &*& <T>.own(t, left_unwound) &*&
    *right_src |-> ?right_unwound &*& <T>.own(t, right_unwound) &*&
    *is_less |-> ?f_unwound &*& <F>.own(t, f_unwound);
@*/
{
    //@ let cmp_k = begin_lifetime();
    let result;
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
                std_tuple_2_::<&'cmp T, &'cmp T> { 0: right_ref, 1: left_ref }); @*/

        // Keep the same argument order as merge_up's actual comparator call.
        result = !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(
            &*right_src,
            &*left_src,
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
// CASE_END two_shared_callback_refs

// Deliberately absent: Copy/Freeze/purity/no-panic bounds, value equality
// across the callback, and any second full own<T> at a coincident address.
