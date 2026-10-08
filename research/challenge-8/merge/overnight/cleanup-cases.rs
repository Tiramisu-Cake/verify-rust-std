#![feature(unboxed_closures)]
#![allow(dead_code)]

// Resource-protocol fixture for callback.patch plus cleanup.patch.
// Each marked case has a real FnMut call and full normal/unwind ownership posts.

// CASE_BEGIN callback_cleanup_positive
pub unsafe fn callback_cleanup_positive<T, F: FnMut(&T, &T) -> bool>(
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// CASE_END callback_cleanup_positive

// CASE_BEGIN callback_cleanup_false_unwind
pub unsafe fn callback_cleanup_false_unwind<T, F: FnMut(&T, &T) -> bool>(
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
    *is_less |-> ?f_unwound &*& <F>.own(t, f_unwound) &*& false;
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
        result = !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/( // TARGET: body reaches the false unwind post
            &*right_src,
            &*left_src,
        );
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"unwind_post","error_file":"verified/lib.rs","error_line":28,"column_start":59,"column_end":64,"message":"Cannot prove condition. (Cannot prove false.)"}
// CASE_END callback_cleanup_false_unwind

// CASE_BEGIN callback_cleanup_missing_frac
pub unsafe fn callback_cleanup_missing_frac<T, F: FnMut(&T, &T) -> bool>(
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac + 1, ref_initialized_(right_ref)); } // TARGET: missing reference fraction
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"rust_belt/lifetime_logic.rsspec","error_line":282,"column_start":9,"column_end":10,"message":"No matching heap chunks: [(result0 + 1)]ref_initialized_(T_typeid, right_ref)()"}
// CASE_END callback_cleanup_missing_frac

// CASE_BEGIN callback_cleanup_escaped_typed_resource
pub unsafe fn callback_cleanup_escaped_typed_resource<T, F: FnMut(&T, &T) -> bool>(
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
        //@ close_ref_own::<'cmp, T>(left_ref); // TARGET: deliberately escaped typed reference resource
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"leak_check","error_file":"verified/lib.rs","error_line":69,"column_start":1,"column_end":2,"message":"Function leaks heap chunks: own(ref_typeid(typeid_of_lft(cmp_k), T_typeid))(t, left_ref)"}
// CASE_END callback_cleanup_escaped_typed_resource

// CASE_BEGIN callback_cleanup_wrong_marker
pub unsafe fn callback_cleanup_wrong_marker<T, F: FnMut(&T, &T) -> bool>(
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'wrong>(); // TARGET: wrong cleanup marker lifetime
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":31,"error_end_line":32,"column_start":5,"column_end":1,"message":"Incomplete or ambiguous callback cleanup markers"}
// CASE_END callback_cleanup_wrong_marker

// Deliberately absent: Copy/Freeze/purity/no-panic bounds, value equality
// across the callback, and any second full own<T> at a coincident address.


// CASE_BEGIN callback_cleanup_wrong_local_type
pub unsafe fn callback_cleanup_wrong_local_type<T, F: FnMut(&T, &T) -> bool>(
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
        //@ borrow(cmp_k, <&'cmp T>.full_borrow_content(t, right_src as *T)); // TARGET: local lifetime hidden in predicate term
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":41,"column_start":9,"column_end":129,"message":"Unexpected callback borrow protocol command: right borrow"}
// CASE_END callback_cleanup_wrong_local_type

// CASE_BEGIN callback_cleanup_wrong_physical_lifetime
pub unsafe fn callback_cleanup_wrong_physical_lifetime<T, F: FnMut(&T, &T) -> bool>(
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
        //@ borrow(static_lifetime, <T>.full_borrow_content(t, right_src as *T)); // TARGET: wrong physical lifetime
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":41,"column_start":9,"column_end":117,"message":"Unexpected callback borrow protocol command: right borrow"}
// CASE_END callback_cleanup_wrong_physical_lifetime

// CASE_BEGIN callback_cleanup_wrong_predicate_operand
pub unsafe fn callback_cleanup_wrong_predicate_operand<T, F: FnMut(&T, &T) -> bool>(
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
        //@ borrow(cmp_k, <T>.full_borrow_content(t, left_src as *T)); // TARGET: wrong predicate source operand
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"frontend_admission","error_file":"verified/lib.rs","error_line":41,"column_start":9,"column_end":113,"message":"Unexpected callback borrow protocol command: right borrow"}
// CASE_END callback_cleanup_wrong_predicate_operand

// CASE_BEGIN callback_cleanup_missing_left_owner
pub unsafe fn callback_cleanup_missing_left_owner<T, F: FnMut(&T, &T) -> bool>(
    left_src: *const T,
    right_src: *const T,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*&
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

        //@ close_full_borrow_content::<T>(t, left_src as *T); // TARGET: missing original owner resource
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"rust_belt/general.rsspec","error_line":203,"column_start":32,"column_end":33,"message":"No matching heap chunks: own(T_typeid)(t, left0)"}
// CASE_END callback_cleanup_missing_left_owner

// CASE_BEGIN callback_cleanup_missing_right_owner
pub unsafe fn callback_cleanup_missing_right_owner<T, F: FnMut(&T, &T) -> bool>(
    left_src: *const T,
    right_src: *const T,
    is_less: &mut F,
) -> bool
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    left_src as pointer != right_src as pointer &*&
    *left_src |-> ?left0 &*& <T>.own(t, left0) &*&
    *right_src |-> ?right0 &*&
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

        //@ close_full_borrow_content::<T>(t, right_src as *T); // TARGET: missing original owner resource
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
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"rust_belt/general.rsspec","error_line":203,"column_start":32,"column_end":33,"message":"No matching heap chunks: own(T_typeid)(t, right0)"}
// CASE_END callback_cleanup_missing_right_owner

// CASE_BEGIN callback_cleanup_missing_comparator_owner
pub unsafe fn callback_cleanup_missing_comparator_owner<T, F: FnMut(&T, &T) -> bool>(
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
    *is_less |-> ?f0;
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
        result = !is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/( // TARGET: missing original owner resource
            &*right_src,
            &*left_src,
        );
        //@ { callback_close::<'cmp>(); close [left_ref_frac]ref_initialized_::<T>(left_ref)(); close_frac_borrow(left_ref_frac, ref_initialized_(left_ref)); close [right_ref_frac]ref_initialized_::<T>(right_ref)(); close_frac_borrow(right_ref_frac, ref_initialized_(right_ref)); }
        //@ callback_scope_end::<'cmp>();
        //@ { callback_recover::<'cmp>(); end_lifetime(cmp_k); borrow_end(cmp_k, <T>.full_borrow_content(t, left_src as *T)); open_full_borrow_content::<T>(t, left_src as *T); borrow_end(cmp_k, <T>.full_borrow_content(t, right_src as *T)); open_full_borrow_content::<T>(t, right_src as *T); }
        let _after_cleanup = result;
    }
    result
}
// EXPECT_REJECTION {"kind":"memory_permission","error_file":"std/lib.rsspec","error_line":47,"column_start":69,"column_end":70,"message":"No matching heap chunks: own(F_typeid)(t, f0)"}
// CASE_END callback_cleanup_missing_comparator_owner
