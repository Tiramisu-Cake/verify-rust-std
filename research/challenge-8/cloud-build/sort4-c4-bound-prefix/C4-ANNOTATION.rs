// C4 source annotation candidate, conditional on a verified C3 bound prefix.
// Insert immediately after C3's normal recover_pair/join_selected_four and
// before the unchanged `let c4 = is_less(&*d, &*b);` call. The same-version
// selected-four helpers must precede sort4_stable in the proof unit.
// This is a candidate only; no C4 preparation runner consumes it yet.

        //@ let cmp4_k = begin_lifetime();
        /*@ let_lft 'cmp4 = cmp4_k; @*/
        //@ interior_pointer_limits::<T>(v_base, 4, c1 as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, (!c1) as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, 2 + c2 as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, 2 + (!c2 as usize));
        //@ split_selected_four::<T>(v_base, t, c1, c2);
        //@ close_full_borrow_content::<T>(t, d);
        //@ close_full_borrow_content::<T>(t, b);
        //@ borrow(cmp4_k, <T>.full_borrow_content(t, d));
        //@ borrow(cmp4_k, <T>.full_borrow_content(t, b));
        //@ share_full_borrow::<T>(cmp4_k, t, d);
        //@ share_full_borrow::<T>(cmp4_k, t, b);
        //@ let left4_ref = precreate_ref(d);
        //@ let right4_ref = precreate_ref(b);
        //@ init_ref_share::<T>(cmp4_k, t, left4_ref);
        //@ init_ref_share::<T>(cmp4_k, t, right4_ref);
        //@ close_ref_own::<'cmp4, T>(left4_ref);
        //@ close_ref_own::<'cmp4, T>(right4_ref);
        //@ close <(&'cmp4 T, &'cmp4 T)>.own(t, std_tuple_2_::<&'cmp4 T, &'cmp4 T> { 0: left4_ref, 1: right4_ref });
        //@ open_frac_borrow(cmp4_k, ref_initialized_(left4_ref), 1/4);
        //@ open [?left4_fraction]ref_initialized_::<T>(left4_ref)();
        //@ open_frac_borrow(cmp4_k, ref_initialized_(right4_ref), 1/4);
        //@ open [?right4_fraction]ref_initialized_::<T>(right4_ref)();
/*@ {
            __vf_sort4_fourth_unwind();
            { close comparison_debt::<T>(t, cmp4_k, d, b, left4_ref, right4_ref, left4_fraction, right4_fraction); }
            { recover_pair::<T>(d, b); }
            { join_selected_four::<T>(v_base, t, c1, c2); }
        } @*/
        let c4 = is_less/*@::<F, (&'cmp4 T, &'cmp4 T), 'cmp4>@*/(&*d, &*b);
        //@ close comparison_debt::<T>(t, cmp4_k, d, b, left4_ref, right4_ref, left4_fraction, right4_fraction);
        //@ end_lft_binding::<'cmp4>();
        //@ recover_pair::<T>(d, b);
        //@ join_selected_four::<T>(v_base, t, c1, c2);
