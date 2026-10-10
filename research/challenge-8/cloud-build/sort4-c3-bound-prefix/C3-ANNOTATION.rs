// C3 annotation candidate. Insert after the original `a`, `b`, `c`, and `d`
// pointer calculations and immediately before the unchanged C3 call. The
// selected helpers and existing split/recover/join lemmas must be included in
// the same proof unit. No preparation runner consumes this file yet.

        //@ let cmp3_k = begin_lifetime();
        /*@ let_lft 'cmp3 = cmp3_k; @*/
        //@ interior_pointer_limits::<T>(v_base, 4, c1 as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, (!c1) as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, 2 + c2 as usize);
        //@ interior_pointer_limits::<T>(v_base, 4, 2 + (!c2 as usize));
        //@ split_selected_four::<T>(v_base, t, c1, c2);
        //@ close_full_borrow_content::<T>(t, c);
        //@ close_full_borrow_content::<T>(t, a);
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, c));
        //@ borrow(cmp3_k, <T>.full_borrow_content(t, a));
        //@ share_full_borrow::<T>(cmp3_k, t, c);
        //@ share_full_borrow::<T>(cmp3_k, t, a);
        //@ let left3_ref = precreate_ref(c);
        //@ let right3_ref = precreate_ref(a);
        //@ init_ref_share::<T>(cmp3_k, t, left3_ref);
        //@ init_ref_share::<T>(cmp3_k, t, right3_ref);
        //@ close_ref_own::<'cmp3, T>(left3_ref);
        //@ close_ref_own::<'cmp3, T>(right3_ref);
        //@ close <(&'cmp3 T, &'cmp3 T)>.own(t, std_tuple_2_::<&'cmp3 T, &'cmp3 T> { 0: left3_ref, 1: right3_ref });
        //@ open_frac_borrow(cmp3_k, ref_initialized_(left3_ref), 1/4);
        //@ open [?left3_fraction]ref_initialized_::<T>(left3_ref)();
        //@ open_frac_borrow(cmp3_k, ref_initialized_(right3_ref), 1/4);
        //@ open [?right3_fraction]ref_initialized_::<T>(right3_ref)();
/*@ {
            __vf_sort4_third_unwind();
            { close comparison_debt::<T>(t, cmp3_k, c, a, left3_ref, right3_ref, left3_fraction, right3_fraction); }
            { recover_pair::<T>(c, a); }
            { join_selected_four::<T>(v_base, t, c1, c2); }
        } @*/
        let c3 = is_less/*@::<F, (&'cmp3 T, &'cmp3 T), 'cmp3>@*/(&*c, &*a);
        //@ close comparison_debt::<T>(t, cmp3_k, c, a, left3_ref, right3_ref, left3_fraction, right3_fraction);
        //@ end_lft_binding::<'cmp3>();
        //@ recover_pair::<T>(c, a);
        //@ join_selected_four::<T>(v_base, t, c1, c2);
