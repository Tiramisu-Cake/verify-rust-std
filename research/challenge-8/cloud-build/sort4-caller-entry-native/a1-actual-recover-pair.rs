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
lem join_four_owned_cells<T>(base: *T, t: thread_id_t)
    req *base |-> ?first &*& <T>.own(t, first) &*&
        *(base + 1) |-> ?second &*& <T>.own(t, second) &*&
        *(base + 2) |-> ?third &*& <T>.own(t, third) &*&
        *(base + 3) |-> ?fourth &*& <T>.own(t, fourth);
    ens base[..4] |-> cons(first, cons(second, cons(third, cons(fourth, nil)))) &*&
        foreach(cons(first, cons(second, cons(third, cons(fourth, nil)))),
            own::<T>(t));
{
    points_to_limits(base);
    points_to_limits(base + 1);
    points_to_limits(base + 2);
    points_to_limits(base + 3);
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + 1));
    note(pointer_within_limits(base + 2));
    note(pointer_within_limits(base + 3));
    note(pointer_within_limits(base + 4));
    close own::<T>(t)(first);
    close own::<T>(t)(second);
    close own::<T>(t)(third);
    close own::<T>(t)(fourth);
    close foreach(nil, own::<T>(t));
    close foreach(cons(fourth, nil), own::<T>(t));
    close foreach(cons(third, cons(fourth, nil)), own::<T>(t));
    close foreach(cons(second, cons(third, cons(fourth, nil))), own::<T>(t));
    close foreach(cons(first, cons(second, cons(third, cons(fourth, nil)))),
        own::<T>(t));
    close array(base + 4, 0, nil);
    close array(base + 3, 1, cons(fourth, nil));
    close array(base + 2, 2, cons(third, cons(fourth, nil)));
    close array(base + 1, 3, cons(second, cons(third, cons(fourth, nil))));
    close array(base, 4, cons(first, cons(second, cons(third, cons(fourth, nil)))));
}
@*/

// CASE_BEGIN recover_pair_missing_reserved_half_negative
// Expected rejection: the recover_pair call below lacks the reserved 1/4
// lifetime-token half; classify only that call's recover_pair precondition.
pub unsafe fn recover_pair_missing_reserved_half<T>(left: *const T, right: *const T)
/*@
req thread_token(?t) &*& type_interp::<T>() &*&
    comparison_debt::<T>(t, ?k, left, right, ?left_ref, ?right_ref,
        ?left_fraction, ?right_fraction) &*&
    [1/4]lifetime_token(k);
@*/
/*@ ens thread_token(t) &*& type_interp::<T>(); @*/
/*@ on_unwind_ens false; @*/
{
    //@ recover_pair::<T>(left, right);
}
// CASE_END recover_pair_missing_reserved_half_negative

// Generic type anchor for export/focus discovery. It has no comparator call
// and makes no claim about the sort4 body or comparator runtime behavior.
#[allow(dead_code)]
pub fn r15_recover_pair_type_anchor<T>(left: *const T, right: *const T) {
    let _ = (left, right);
}
