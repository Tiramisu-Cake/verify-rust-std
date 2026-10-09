// Draft only: insert immediately after the c1 normal-path
// `join_four_owned_cells::<T>(v_base, t);` and immediately before the actual
// second comparator source expression at source 195. This is not a verified
// fixture and is not wired into a preparation runner.
// The four cell values and `is_less` state here are current post-C1 values;
// neither is asserted equal to its function-entry value.

        //@ let cmp2_k = begin_lifetime();
        /*@ let_lft 'cmp2 = cmp2_k; @*/
        //@ interior_pointer_limits::<T>(v_base, 4, 3);
        //@ interior_pointer_limits::<T>(v_base, 4, 2);
        //@ split_four_owned_cells::<T>(v_base, t);
        //@ close_full_borrow_content::<T>(t, v_base + 3);
        //@ close_full_borrow_content::<T>(t, v_base + 2);
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base + 3));
        //@ borrow(cmp2_k, <T>.full_borrow_content(t, v_base + 2));
        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 3);
        //@ share_full_borrow::<T>(cmp2_k, t, v_base + 2);
        //@ let left2_ref = precreate_ref(v_base + 3);
        //@ let right2_ref = precreate_ref(v_base + 2);
        //@ init_ref_share::<T>(cmp2_k, t, left2_ref);
        //@ init_ref_share::<T>(cmp2_k, t, right2_ref);
        //@ close_ref_own::<'cmp2, T>(left2_ref);
        //@ close_ref_own::<'cmp2, T>(right2_ref);
        //@ close <(&'cmp2 T, &'cmp2 T)>.own(t, std_tuple_2_::<&'cmp2 T, &'cmp2 T> { 0: left2_ref, 1: right2_ref });
        //@ open_frac_borrow(cmp2_k, ref_initialized_(left2_ref), 1/4);
        //@ open [?left2_fraction]ref_initialized_::<T>(left2_ref)();
        //@ open_frac_borrow(cmp2_k, ref_initialized_(right2_ref), 1/4);
        //@ open [?right2_fraction]ref_initialized_::<T>(right2_ref)();
/*@ {
            __vf_sort4_second_unwind();
            { close comparison_debt::<T>(t, cmp2_k, v_base + 3, v_base + 2, left2_ref, right2_ref, left2_fraction, right2_fraction); }
            { recover_pair::<T>(v_base + 3, v_base + 2); }
            { join_four_owned_cells::<T>(v_base, t); }
        } @*/
        let c2 = is_less/*@::<F, (&'cmp2 T, &'cmp2 T), 'cmp2>@*/(&*v_base.add(3), &*v_base.add(2));
        //@ close comparison_debt::<T>(t, cmp2_k, v_base + 3, v_base + 2, left2_ref, right2_ref, left2_fraction, right2_fraction);
        //@ end_lft_binding::<'cmp2>();
        //@ recover_pair::<T>(v_base + 3, v_base + 2);
        //@ join_four_owned_cells::<T>(v_base, t);
