#![no_std]
#![allow(dead_code)]

// Physical one-case fixtures are produced by driver.py. These delimiters are
// never passed together to the compiler, exporter, verifier, or refiner.

// CASE_BEGIN ordinary_default_off
pub unsafe fn ordinary_default_off() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
    }
    //@ end_lifetime(k);
}
// CASE_END ordinary_default_off

// CASE_BEGIN marker_default_off
pub unsafe fn marker_default_off() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_token(k);
        //@ end_lifetime(k);
    }
}
// CASE_END marker_default_off

// CASE_BEGIN positive_basic
pub unsafe fn positive_basic() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_token(k);
        //@ end_lifetime(k);
    }
}
// CASE_END positive_basic

// CASE_BEGIN positive_early_return
pub unsafe fn positive_early_return(early: bool) -> bool
/*@ req true; @*/ /*@ ens lifetime_token(?returned_k); @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        if early {
            return true;
        }
        //@ end_lft_binding::<'cmp>();
        return false;
    }
}
// CASE_END positive_early_return

// CASE_BEGIN cut_may_unwind
pub unsafe fn cut_may_unwind()
/*@ req true; @*/ /*@ ens true; @*/ /*@ on_unwind_ens true; @*/ {
}
// CASE_END cut_may_unwind

// CASE_BEGIN positive_direct_unwind
pub unsafe fn positive_direct_unwind()
/*@ req true; @*/
/*@ ens lifetime_token(?normal_k); @*/
/*@ on_unwind_ens lifetime_token(?unwind_k); @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        unsafe { cut_may_unwind(); }
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END positive_direct_unwind

// CASE_BEGIN positive_outgoing_goto
pub unsafe fn positive_outgoing_goto() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    'out: loop {
        {
            /*@ let_lft 'cmp = k; @*/
            //@ end_lft_binding::<'cmp>();
            break 'out;
        }
    }
    //@ assert lifetime_token(k);
    //@ end_lifetime(k);
}
// CASE_END positive_outgoing_goto

// CASE_BEGIN negative_heap_escape
/*@
pred live<'a, T>() = true;
@*/
pub unsafe fn negative_heap_escape<T>() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ close live::<'cmp, T>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_heap_escape

// CASE_BEGIN negative_outer_type_escape
pub unsafe fn negative_outer_type_escape() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        let _escaped: &'cmp i32 = &1;
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_outer_type_escape

// CASE_BEGIN negative_outer_bound_escape
pub unsafe fn negative_outer_bound_escape<T>()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ assert type_interp::<&'cmp T>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_outer_bound_escape

// CASE_BEGIN negative_wrong_marker
pub unsafe fn negative_wrong_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ end_lft_binding::<'other>();
    }
}
// CASE_END negative_wrong_marker

// CASE_BEGIN negative_duplicate_marker
pub unsafe fn negative_duplicate_marker() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_duplicate_marker

// CASE_BEGIN negative_typed_chunk_survives_cut
/*@
pred live_chunk<'a, T>() = true;
@*/
pub unsafe fn negative_typed_chunk_survives_cut<T>()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ close live_chunk::<'cmp, T>();
        //@ end_lft_binding::<'cmp>();
    }
}
// CASE_END negative_typed_chunk_survives_cut

// CASE_BEGIN negative_type_after_cut
pub unsafe fn negative_type_after_cut() /*@ req true; @*/ /*@ ens true; @*/ {
    //@ let k = begin_lifetime();
    {
        /*@ let_lft 'cmp = k; @*/
        //@ end_lft_binding::<'cmp>();
        //@ assert lifetime_inclusion('cmp, 'cmp) == true;
        //@ assert lifetime_token(k);
        //@ end_lifetime(k);
    }
}
// CASE_END negative_type_after_cut
