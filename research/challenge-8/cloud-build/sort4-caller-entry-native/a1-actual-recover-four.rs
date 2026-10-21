#![no_std]
#![allow(dead_code)]

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

/*@
pred callback_four_debt<T>(
    t: thread_id_t, k: lifetime_t, base: *T,
    left_ref: *T, right_ref: *T,
    left_fraction: real, right_fraction: real) =
    [left_fraction]ref_initialized::<T>(left_ref) &*&
    close_frac_borrow_token(
        left_fraction, ref_initialized_::<T>(left_ref), 1/4, k) &*&
    [right_fraction]ref_initialized::<T>(right_ref) &*&
    close_frac_borrow_token(
        right_fraction, ref_initialized_::<T>(right_ref), 1/4, k) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base + 1)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base + 2)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base + 3));
@*/

/*@
lem recover_four_sources<T>(base: *T)
    nonghost_callers_only
    req thread_token(?t) &*& type_interp::<T>() &*&
        callback_four_debt::<T>(
            t, ?k, base, ?left_ref, ?right_ref,
            ?left_fraction, ?right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        base[..4] |-> ?current &*& foreach(current, own::<T>(t));
{
    open callback_four_debt::<T>(
        t, k, base, left_ref, right_ref, left_fraction, right_fraction);
    close [left_fraction]ref_initialized_::<T>(left_ref)();
    close_frac_borrow(left_fraction, ref_initialized_::<T>(left_ref));
    close [right_fraction]ref_initialized_::<T>(right_ref)();
    close_frac_borrow(right_fraction, ref_initialized_::<T>(right_ref));
    merge_fractions lifetime_token(k);
    end_lifetime(k);
    borrow_end(k, <T>.full_borrow_content(t, base));
    open_full_borrow_content::<T>(t, base);
    borrow_end(k, <T>.full_borrow_content(t, base + 1));
    open_full_borrow_content::<T>(t, base + 1);
    borrow_end(k, <T>.full_borrow_content(t, base + 2));
    open_full_borrow_content::<T>(t, base + 2);
    borrow_end(k, <T>.full_borrow_content(t, base + 3));
    open_full_borrow_content::<T>(t, base + 3);
    join_four_owned_cells::<T>(base, t);
}
@*/

/*@
pred callback_four_debt_without_fourth<T>(
    t: thread_id_t, k: lifetime_t, base: *T,
    left_ref: *T, right_ref: *T,
    left_fraction: real, right_fraction: real) =
    [left_fraction]ref_initialized::<T>(left_ref) &*&
    close_frac_borrow_token(
        left_fraction, ref_initialized_::<T>(left_ref), 1/4, k) &*&
    [right_fraction]ref_initialized::<T>(right_ref) &*&
    close_frac_borrow_token(
        right_fraction, ref_initialized_::<T>(right_ref), 1/4, k) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base + 1)) &*&
    borrow_end_token(k, <T>.full_borrow_content(t, base + 2));
@*/

// CASE_BEGIN recover_four_missing_fourth_end_token_negative
/*@
lem recover_four_missing_fourth_end_token_negative<T>(
    base: *T, left_ref: *T, right_ref: *T,
    left_fraction: real, right_fraction: real)
    req thread_token(?t) &*& type_interp::<T>() &*&
        callback_four_debt_without_fourth::<T>(
            t, ?k, base, left_ref, right_ref,
            left_fraction, right_fraction) &*&
        [1/2]lifetime_token(k);
    ens thread_token(t) &*& type_interp::<T>() &*&
        callback_four_debt::<T>(
            t, k, base, left_ref, right_ref, left_fraction, right_fraction) &*&
        [1/2]lifetime_token(k);
{
    open callback_four_debt_without_fourth::<T>(
        t, k, base, left_ref, right_ref, left_fraction, right_fraction);
    close callback_four_debt::<T>(
        t, k, base, left_ref, right_ref, left_fraction, right_fraction);
}
@*/
// CASE_END recover_four_missing_fourth_end_token_negative

// Generic MIR target anchor only. It does not relate either reference debt
// to any source cell or add a runtime assumption.
#[allow(dead_code)]
pub fn r15_recover_four_sources_type_anchor<T>(base: *const T) {
    let _ = base;
}
