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

/*@
pred single_borrow_debt<T>(
    t: thread_id_t, k: lifetime_t, tmp: *T, tmp_ref: *T,
    first_fraction: real, second_fraction: real) =
    [first_fraction]ref_initialized::<T>(tmp_ref) &*&
    close_frac_borrow_token(
        first_fraction, ref_initialized_::<T>(tmp_ref), 1/4, k) &*&
    [second_fraction]ref_initialized::<T>(tmp_ref) &*&
    close_frac_borrow_token(
        second_fraction, ref_initialized_::<T>(tmp_ref), 1/4, k) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, tmp));

lem recover_single<T>(tmp: *T)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*&
        single_borrow_debt::<T>(
            t, ?k, tmp, ?tmp_ref, ?first_fraction, ?second_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        *tmp |-> ?tmp_after &*& <T>.own(t, tmp_after);
{
    open single_borrow_debt::<T>(
        t, k, tmp, tmp_ref, first_fraction, second_fraction);
    close [first_fraction]ref_initialized_::<T>(tmp_ref)();
    close_frac_borrow(first_fraction, ref_initialized_::<T>(tmp_ref));
    close [second_fraction]ref_initialized_::<T>(tmp_ref)();
    close_frac_borrow(second_fraction, ref_initialized_::<T>(tmp_ref));
    merge_fractions lifetime_token(k);
    end_lifetime(k);
    borrow_end(k, <T>.full_borrow_content(t, tmp));
    open_full_borrow_content::<T>(t, tmp);
}
@*/

// CASE_BEGIN positive_i32
pub unsafe fn positive_i32(left: *mut i32, right: *mut i32)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<i32>() &*&
    *left |-> ?left_value &*& <i32>.own(t, left_value) &*&
    *right |-> ?right_value &*& <i32>.own(t, right_value);
@*/
/*@ ens thread_token(t) &*& type_interp::<i32>() &*&
    *left |-> ?left_after &*& <i32>.own(t, left_after) &*&
    *right |-> ?right_after &*& <i32>.own(t, right_after);
@*/ {
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<i32>(t, left);
    //@ close_full_borrow_content::<i32>(t, right);
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, right));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<i32>(cmp_k, t, left);
        //@ share_full_borrow::<i32>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<i32>(cmp_k, t, left_ref);
        //@ init_ref_share::<i32>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<i32>(left_ref)();
        let _left_shared = &*left;
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<i32>(right_ref)();
        let _right_shared = &*right;
        //@ close comparison_debt::<i32>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    }
    //@ recover_pair::<i32>(left, right);
}
// CASE_END positive_i32

// CASE_BEGIN positive_generic
pub unsafe fn positive_generic<T>(left: *mut T, right: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    *left |-> ?left_value &*& <T>.own(t, left_value) &*&
    *right |-> ?right_value &*& <T>.own(t, right_value);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    *left |-> ?left_after &*& <T>.own(t, left_after) &*&
    *right |-> ?right_after &*& <T>.own(t, right_after);
@*/ {
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<T>(t, left);
    //@ close_full_borrow_content::<T>(t, right);
    //@ borrow(cmp_k, <T>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <T>.full_borrow_content(t, right));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<T>(cmp_k, t, left);
        //@ share_full_borrow::<T>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<T>(left_ref)();
        let _left_shared = &*left;
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<T>(right_ref)();
        let _right_shared = &*right;
        //@ close comparison_debt::<T>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    }
    //@ recover_pair::<T>(left, right);
}
// CASE_END positive_generic

// CASE_BEGIN negative_missing_token
pub unsafe fn negative_missing_token(left: *mut i32, right: *mut i32)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<i32>() &*&
    *left |-> ?left_value &*& <i32>.own(t, left_value) &*&
    *right |-> ?right_value &*& <i32>.own(t, right_value);
@*/
/*@ ens thread_token(t) &*& type_interp::<i32>() &*&
    *left |-> ?left_after &*& <i32>.own(t, left_after) &*&
    *right |-> ?right_after &*& <i32>.own(t, right_after);
@*/ {
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<i32>(t, left);
    //@ close_full_borrow_content::<i32>(t, right);
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, right));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<i32>(cmp_k, t, left);
        //@ share_full_borrow::<i32>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<i32>(cmp_k, t, left_ref);
        //@ init_ref_share::<i32>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<i32>(left_ref)();
        let _left_shared = &*left;
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<i32>(right_ref)();
        let _right_shared = &*right;
        //@ close comparison_debt::<i32>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    }
    //@ leak [1/2]lifetime_token(cmp_k);
    //@ recover_pair::<i32>(left, right);
}
// CASE_END negative_missing_token

// CASE_BEGIN negative_missing_debt
pub unsafe fn negative_missing_debt(left: *mut i32, right: *mut i32)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<i32>() &*&
    *left |-> ?left_value &*& <i32>.own(t, left_value) &*&
    *right |-> ?right_value &*& <i32>.own(t, right_value);
@*/
/*@ ens thread_token(t) &*& type_interp::<i32>() &*&
    *left |-> ?left_after &*& <i32>.own(t, left_after) &*&
    *right |-> ?right_after &*& <i32>.own(t, right_after);
@*/ {
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<i32>(t, left);
    //@ close_full_borrow_content::<i32>(t, right);
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, right));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<i32>(cmp_k, t, left);
        //@ share_full_borrow::<i32>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<i32>(cmp_k, t, left_ref);
        //@ init_ref_share::<i32>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<i32>(left_ref)();
        let _left_shared = &*left;
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<i32>(right_ref)();
        let _right_shared = &*right;
    }
    //@ recover_pair::<i32>(left, right);
}
// CASE_END negative_missing_debt

// CASE_BEGIN negative_false_post
pub unsafe fn negative_false_post(left: *mut i32, right: *mut i32)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<i32>() &*&
    *left |-> ?left_value &*& <i32>.own(t, left_value) &*&
    *right |-> ?right_value &*& <i32>.own(t, right_value);
@*/
/*@ ens thread_token(t) &*& type_interp::<i32>() &*&
    *left |-> ?left_after &*& <i32>.own(t, left_after) &*&
    *right |-> ?right_after &*& <i32>.own(t, right_after) &*&
    left_after != left_after;
@*/ {
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<i32>(t, left);
    //@ close_full_borrow_content::<i32>(t, right);
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, left));
    //@ borrow(cmp_k, <i32>.full_borrow_content(t, right));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<i32>(cmp_k, t, left);
        //@ share_full_borrow::<i32>(cmp_k, t, right);
        //@ let left_ref = precreate_ref(left);
        //@ let right_ref = precreate_ref(right);
        //@ init_ref_share::<i32>(cmp_k, t, left_ref);
        //@ init_ref_share::<i32>(cmp_k, t, right_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<i32>(left_ref)();
        let _left_shared = &*left;
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<i32>(right_ref)();
        let _right_shared = &*right;
        //@ close comparison_debt::<i32>(t, cmp_k, left, right, left_ref, right_ref, left_fraction, right_fraction);
    }
    //@ recover_pair::<i32>(left, right);
}
// CASE_END negative_false_post


// CASE_BEGIN positive_manually_drop
pub unsafe fn positive_manually_drop<T>(cell: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    *cell |-> ?cell_before &*& <T>.own(t, cell_before);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    *cell |-> ?cell_after &*& <T>.own(t, cell_after);
@*/ {
    let value = cell.read();
    let tmp = core::mem::ManuallyDrop::new(value);
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<T>(t, &tmp);
    //@ borrow(cmp_k, <T>.full_borrow_content(t, &tmp));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<T>(cmp_k, t, &tmp);
        //@ let tmp_ref = precreate_ref(&tmp);
        //@ init_ref_share::<T>(cmp_k, t, tmp_ref);
        //@ open_frac_borrow(cmp_k, ref_initialized_(tmp_ref), 1/4);
        //@ open [?first_fraction]ref_initialized_::<T>(tmp_ref)();
        //@ open_frac_borrow(cmp_k, ref_initialized_(tmp_ref), 1/4);
        //@ open [?second_fraction]ref_initialized_::<T>(tmp_ref)();
        let _tmp_shared = &*tmp;
        //@ close single_borrow_debt::<T>(t, cmp_k, &tmp, tmp_ref, first_fraction, second_fraction);
    }
    //@ recover_single::<T>(&tmp);
    let tmp_ptr = core::ptr::addr_of!(tmp) as *const T;
    let value = tmp_ptr.read();
    cell.write(value);
}
// CASE_END positive_manually_drop

// CASE_BEGIN negative_manually_drop_missing_init
pub unsafe fn negative_manually_drop_missing_init<T>(cell: *mut T)
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    *cell |-> ?cell_before &*& <T>.own(t, cell_before);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    *cell |-> ?cell_after &*& <T>.own(t, cell_after);
@*/ {
    let value = cell.read();
    let tmp = core::mem::ManuallyDrop::new(value);
    //@ let cmp_k = begin_lifetime();
    //@ close_full_borrow_content::<T>(t, &tmp);
    //@ borrow(cmp_k, <T>.full_borrow_content(t, &tmp));
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ share_full_borrow::<T>(cmp_k, t, &tmp);
        //@ let tmp_ref = precreate_ref(&tmp);
        let _tmp_shared = &*tmp;
    }
}
// CASE_END negative_manually_drop_missing_init
