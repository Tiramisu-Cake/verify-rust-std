// Draft canonical ghost envelope for the original runtime expression.
// Do not execute/generate actual proof inputs locally; Cloud-UNVERIFIED.
//@ let r23_borrow_k = begin_lifetime();
//@ r23_source_array_borrow_adapter(r23_borrow_k, values);
//@ let r23_array_p = &values as *mut [u64; 3];
//@ assert array::<u64>(r23_array_p as *u64, 3, ?r23_borrow_values);
//@ array_to_Array(r23_array_p);
//@ assert *r23_array_p |-> ?r23_borrow_array;
//@ r9_make_u64_owners(t, Array_elems(r23_borrow_array));
//@ close r23_u64_array3_own(t, r23_borrow_array);
//@ close r23_u64_array3_fbc(t, r23_array_p)();
//@ borrow(r23_borrow_k, r23_u64_array3_fbc(t, r23_array_p));
//@ let_lft 'r23_borrow = r23_borrow_k;
let begin = values.as_mut_ptr();
//@ r23_source_array_borrow_adapter_end(r23_borrow_k, values, begin, r23_borrow_values);
//@ end_lifetime(r23_borrow_k);
//@ borrow_end(r23_borrow_k, r23_u64_array3_fbc(t, r23_array_p));
//@ r23_dispose_dead_array3_borrow(r23_borrow_k, t, r23_array_p);
//@ open r23_u64_array3_fbc(t, r23_array_p)();
//@ assert *r23_array_p |-> ?r23_restored_array;
//@ open r23_u64_array3_own(t, r23_restored_array);
//@ r9_drop_u64_owners(t, Array_elems(r23_restored_array));
//@ Array_to_array(r23_array_p);
// Method-unwind only: after the same checked post epilogue, run
// array_to_array_(r23_array_p as *u64) before the original unwind action.
// Normal path retains the initialized array for the original insert_tail call.
