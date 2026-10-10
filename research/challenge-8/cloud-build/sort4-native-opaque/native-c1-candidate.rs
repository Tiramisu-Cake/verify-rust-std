// DRAFT / NOT_RUN. A source-linked internal bounded entry, not the std caller.
// The checked helper definitions below are copied without changed contracts from
// overnight-sort4/capture.py and overnight-callback/{callback-cases.rs,
// join-four-owned-cells.rs}; see C1-CANDIDATE-CARD.md for their exact identities.
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code, unused_variables)]

use std::marker::Freeze;
use std::mem::{size_of, MaybeUninit};

#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}

/*@
lem interior_pointer_limits<T>(base: *T, count: usize, index: usize)
    req [?f]base[..count] |-> ?xs &*& 1 <= count &*& 0 <= index &*& index <= count;
    ens [f]base[..count] |-> xs &*& pointer_within_limits(base + index) == true;
{
    open array(base, count, xs);
    points_to_limits(base);
    close [f]array(base, count, xs);
    note(0 <= std::mem::size_of::<T>());
    array_inv::<T>();
    mul_mono_l(0, index, std::mem::size_of::<T>());
    mul_mono_l(index, count, std::mem::size_of::<T>());
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + count));
}
@*/
/*@
lem split_four_owned_cells<T>(base: *T, t: thread_id_t)
    req base[..4] |-> ?xs &*& foreach(xs, own::<T>(t));
    ens *base |-> ?first &*& <T>.own(t, first) &*&
        *(base + 1) |-> ?second &*& <T>.own(t, second) &*&
        *(base + 2) |-> ?third &*& <T>.own(t, third) &*&
        *(base + 3) |-> ?fourth &*& <T>.own(t, fourth) &*&
        xs == cons(first, cons(second, cons(third, cons(fourth, nil))));
{
    open array(base, 4, xs);
    assert xs == cons(?first0, ?rest0);
    open foreach(xs, own::<T>(t));
    open own::<T>(t)(first0);
    open array(base + 1, 3, rest0);
    assert rest0 == cons(?second0, ?tail0);
    open foreach(rest0, own::<T>(t));
    open own::<T>(t)(second0);
    open array(base + 2, 2, tail0);
    assert tail0 == cons(?third0, ?rest1);
    open foreach(tail0, own::<T>(t));
    open own::<T>(t)(third0);
    open array(base + 3, 1, rest1);
    assert rest1 == cons(?fourth0, ?empty0);
    open foreach(rest1, own::<T>(t));
    open own::<T>(t)(fourth0);
    open array(base + 4, 0, empty0);
    open foreach(empty0, own::<T>(t));
}
@*/
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

// This function keeps the automatic safe-reference contract. The size guard
// bounds only this internal diagnostic and is not credited to the real caller.
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    let len = v.len();
    if size_of::<T>() == 0 {
        return;
    }

    // slice/mod.rs:778, the exact implementation expression of as_mut_ptr.
    // It does not establish binding of the external method call in SmallSort.
    let v_base = v as *mut [T] as *mut T;

    if len >= 8 {
        /*@
        produce_type_interp::<T>();
        produce_type_interp::<F>();
        assert thread_token(?t);
        assert t == currentThread;
        assert v_base[..len] |-> ?source_all;
        assert foreach(source_all, own::<T>(t));
        let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
        let scratch_len = ptr_len(scratch);
        assert mu_base[..scratch_len] |-> ?mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        assert *is_less |-> ?less_before;
        assert <F>.own(t, less_before);
        array_split::<T>(v_base, 4);
        foreach_split(source_all, own::<T>(t), 4);
        assert v_base[..4] |-> ?first_four;
        interior_pointer_limits::<T>(v_base, 4, 1);
        let cmp_k = begin_lifetime();
        @*/
        unsafe {
/*@ let_lft 'cmp = cmp_k; @*/
            //@ split_four_owned_cells::<T>(v_base, t);
            //@ close_full_borrow_content::<T>(t, v_base + 1);
            //@ close_full_borrow_content::<T>(t, v_base);
            //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base + 1));
            //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base));
            //@ share_full_borrow::<T>(cmp_k, t, v_base + 1);
            //@ share_full_borrow::<T>(cmp_k, t, v_base);
            //@ let left_ref = precreate_ref(v_base + 1);
            //@ let right_ref = precreate_ref(v_base);
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
                // Existing frozen C4 marker, intentionally exposes its exact
                // sort4_stable target restriction for this new native body.
                __vf_sort4_first_unwind();
                { close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction); }
                { recover_pair::<T>(v_base + 1, v_base); }
                { join_four_owned_cells::<T>(v_base, t); }
                { assert v_base[..4] |-> ?first_current;
                  array_join::<T>(v_base);
                  foreach_append(first_current, drop(4, source_all));
                  assert v_base[..len] |-> ?source_current;
                  assert foreach(source_current, own::<T>(t));
                  assert mu_base[..scratch_len] |-> mu_all;
                  assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
                  assert *is_less |-> ?less_current;
                  assert <F>.own(t, less_current);
                  leak type_interp::<T>();
                  leak type_interp::<F>(); }
            } @*/
            let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*v_base.add(1), &*v_base);
            //@ close comparison_debt::<T>(t, cmp_k, v_base + 1, v_base, left_ref, right_ref, left_fraction, right_fraction);
            //@ end_lft_binding::<'cmp>();
        }
        //@ recover_pair::<T>(v_base + 1, v_base);
        //@ join_four_owned_cells::<T>(v_base, t);
        //@ assert v_base[..4] |-> ?first_current;
        //@ array_join::<T>(v_base);
        //@ foreach_append(first_current, drop(4, source_all));
        //@ assert v_base[..len] |-> ?source_current;
        //@ assert foreach(source_current, own::<T>(t));
        //@ assert mu_base[..scratch_len] |-> mu_all;
        //@ assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        //@ assert *is_less |-> ?less_current;
        //@ assert <F>.own(t, less_current);
        //@ leak type_interp::<T>();
        //@ leak type_interp::<F>();
    }
}
