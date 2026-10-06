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
