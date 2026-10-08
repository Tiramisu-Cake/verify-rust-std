#![no_std]
#![allow(dead_code)]

// Source template for physical, one-case VeriFast fixtures. The runner strips
// the CASE delimiters and sends each selected source separately to the readonly
// compiler-MIR exporter, decoder, and verifier. This combined template is never
// a verifier input.

// CASE_BEGIN positive_basic
pub unsafe fn positive_basic() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_token(cmp_k);
        //@ end_lifetime(cmp_k);
    }
}
// CASE_END positive_basic

// CASE_BEGIN ordinary_unmarked
pub unsafe fn ordinary_unmarked() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
    }
    //@ end_lifetime(cmp_k);
}
// CASE_END ordinary_unmarked

// CASE_BEGIN positive_early_return
pub unsafe fn positive_early_return(early: bool) -> bool
/*@ req true; @*/ /*@ ens lifetime_token(?returned_k); @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        if early {
            return true;
        }
        //@ end_lft_binding::<'cmp>();
        return false;
    }
}
// CASE_END positive_early_return

// CASE_BEGIN positive_direct_unwind
// Both bodies must be verified in the same unit; the callee summary has a
// genuine unwind branch but introduces no heap resource or assumed fact.
pub unsafe fn cut_maybe_unwind()
/*@ req true; @*/ /*@ ens true; @*/ /*@ on_unwind_ens true; @*/ {
}
pub unsafe fn positive_direct_unwind()
/*@ req true; @*/
/*@ ens lifetime_token(?normal_k); @*/
/*@ on_unwind_ens lifetime_token(?unwind_k); @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        unsafe { cut_maybe_unwind(); }
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END positive_direct_unwind

// CASE_BEGIN negative_wrong_marker
pub unsafe fn negative_wrong_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'other>();
    }
}
// CASE_END negative_wrong_marker

// CASE_BEGIN negative_duplicate_marker
pub unsafe fn negative_duplicate_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_duplicate_marker

// CASE_BEGIN negative_marker_outside_binding
pub unsafe fn negative_marker_outside_binding() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
    }
    //@ end_lft_binding::<'cmp>();
}
// CASE_END negative_marker_outside_binding

// CASE_BEGIN negative_unknown_binding
pub unsafe fn negative_unknown_binding() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    //@ end_lft_binding::<'missing>();
}
// CASE_END negative_unknown_binding

// CASE_BEGIN negative_nested_marker
pub unsafe fn negative_nested_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let outer_k = begin_lifetime();
    {
        /*@ let_lft 'outer = outer_k; @*/
        //@ let inner_k = begin_lifetime();
        {
            /*@ let_lft 'inner = inner_k; @*/
            //@ end_lft_binding::<'outer>();
        }
    }
}
// CASE_END negative_nested_marker

// CASE_BEGIN negative_malformed_marker
pub unsafe fn negative_malformed_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>(1);
    }
}
// CASE_END negative_malformed_marker

// CASE_BEGIN negative_type_name_after_cut
pub unsafe fn negative_type_name_after_cut() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_inclusion('cmp, 'cmp) == true;
        //@ assert lifetime_token(cmp_k);
        //@ end_lifetime(cmp_k);
    }
}
// CASE_END negative_type_name_after_cut

// CASE_BEGIN negative_type_argument_after_cut
pub unsafe fn negative_type_argument_after_cut() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert type_interp::<&'cmp i32>();
        //@ end_lifetime(cmp_k);
    }
}
// CASE_END negative_type_argument_after_cut

// CASE_BEGIN negative_typed_chunk_survives_cut
/*@
pred live<'a, T>() = true;
@*/
pub unsafe fn negative_typed_chunk_survives_cut<T>()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close live::<'cmp, T>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_typed_chunk_survives_cut

// CASE_BEGIN negative_unclosed_fractional_access
/*@
pred_ctor payload()(;) = true;
@*/
pub unsafe fn negative_unclosed_fractional_access()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ close payload()();
        //@ borrow(cmp_k, payload());
        //@ full_borrow_into_frac(cmp_k, payload());
        //@ open_frac_borrow(cmp_k, payload(), 1/2);
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_token(cmp_k);
    }
}
// CASE_END negative_unclosed_fractional_access

// CASE_BEGIN negative_reserved_half_after_lifetime_end
pub unsafe fn negative_reserved_half_after_lifetime_end()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_token(cmp_k);
        //@ end_lifetime(cmp_k);
    }
    //@ assert [1/2]lifetime_token(cmp_k);
}
// CASE_END negative_reserved_half_after_lifetime_end

// CASE_BEGIN negative_end_lifetime_twice
pub unsafe fn negative_end_lifetime_twice() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let cmp_k = begin_lifetime();
    {
        /*@ let_lft 'cmp = cmp_k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ end_lifetime(cmp_k);
        //@ end_lifetime(cmp_k);
    }
}
// CASE_END negative_end_lifetime_twice

// CASE_BEGIN positive_f_bound
// Adapted from the independently hosted callback_positive source; its
// complete predicate/lemma are included so this case is isolated.
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
        //@ end_lft_binding::<'cmp>();
    };
    //@ recover_pair::<T>(left, right);
    result
}
// CASE_END positive_f_bound
