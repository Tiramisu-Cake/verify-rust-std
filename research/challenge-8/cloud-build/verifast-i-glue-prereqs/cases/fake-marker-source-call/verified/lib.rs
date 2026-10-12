#![no_std]
use core::{mem::ManuallyDrop, ptr};

struct CopyOnDrop {
    src: *const u64,
    dst: *mut u64,
    len: usize,
}

/*@
pred <CopyOnDrop>.own(t, v) =
    type_interp::<u64>() &*& v.len == 1 &*&
    (v.src as usize + std::mem::size_of::<u64>() <= v.dst as usize ||
     v.dst as usize + std::mem::size_of::<u64>() <= v.src as usize) &*&
    [1/4](*v.src |-> ?current) &*& *v.dst |-?-> ?old_gap &*&
    <u64>.own(t, current);
@*/

/*@
lem initialized_storage_alignment(p: *u64)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& p as usize % std::mem::align_of::<u64>() == 0;
{
    open [f]points_to::<u64>(p, v);
    to_u8s_::<u64>(p);
    from_u8s_::<u64>(p);
    close [f]points_to::<u64>(p, v);
}
@*/

/*@
lem uninitialized_storage_alignment(p: *u64)
    req [?f]points_to_::<u64>(p, ?v);
    ens [f]points_to_::<u64>(p, v) &*& p as usize % std::mem::align_of::<u64>() == 0;
{
    to_u8s_::<u64>(p);
    from_u8s_::<u64>(p);
}
@*/

/*@
pred CopyOnDrop_drop_effect(t: thread_id_t, src: *const u64, dst: *mut u64, len: usize;) =
    len == 1 &*& type_interp::<u64>() &*&
    [1/4]src[..1] |-> cons(?current, nil) &*&
    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);
pred_ctor withheld_receiver(p: *mut CopyOnDrop)(;) = (*p).len |-> ?v;
pred_ctor withheld_source(p: *const u64)(;) = [1/4]p[..1] |-> ?vs;
@*/

impl Drop for CopyOnDrop {
    fn drop(&mut self)/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<u64>() &*&
    (*self).src |-> ?src &*& (*self).dst |-> ?dst &*& (*self).len |-> ?len &*&
    struct_CopyOnDrop_padding(self) &*& len == 1 &*&
    [1/4]src[..1] |-> cons(?current, nil) &*& dst[..1] |-> _ &*&
    <u64>.own(t, current) &*&
    0 < std::mem::size_of::<u64>() &*&
    std::mem::size_of::<u64>() <= isize::MAX &*&
    src as usize != 0 &*& dst as usize != 0 &*&
    src as usize % std::mem::align_of::<u64>() == 0 &*&
    dst as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(src, std::mem::size_of::<u64>()) == true &*&
    object_pointer_within_limits(dst, std::mem::size_of::<u64>()) == true &*&
    src as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    dst as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    pointer_within_limits(src) == true &*& pointer_within_limits(src + 1) == true &*&
    pointer_within_limits(dst) == true &*&
    (src as usize + std::mem::size_of::<u64>() <= dst as usize ||
        dst as usize + std::mem::size_of::<u64>() <= src as usize) &*&
    pointer_within_limits(dst + 1) == true;
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*&
    (*self).src |-> src &*& (*self).dst |-> dst &*& (*self).len |-> 1 &*&
    struct_CopyOnDrop_padding(self) &*&
    [1/4]src[..1] |-> cons(current, nil) &*&
    dst[..1] |-> cons(current, nil) &*& <u64>.own(t, current);
@*//*@ on_unwind_ens false; @*//*@
safety_proof {
    open CopyOnDrop_full_borrow_content(_t, self)();
    open <CopyOnDrop>.own(_t, *self);
    assert (*self).src |-> ?guard_src &*& (*self).dst |-> ?guard_dst &*& (*self).len |-> ?guard_len;
    assert guard_len == 1;
        initialized_storage_alignment(guard_src as *mut u64);
        points_to_limits::<u64>(guard_src as *mut u64);
        assert guard_src as usize != 0;
        assert guard_src as usize % std::mem::align_of::<u64>() == 0;
        assert object_pointer_within_limits(guard_src, std::mem::size_of::<u64>()) == true;
        assert guard_src as usize <= usize::MAX - std::mem::size_of::<u64>();
        assert (guard_src as usize + std::mem::size_of::<u64>() <= guard_dst as usize || guard_dst as usize + std::mem::size_of::<u64>() <= guard_src as usize);
        uninitialized_storage_alignment(guard_dst);
        points_to__limits::<u64>(guard_dst);
        assert guard_dst as usize != 0;
        assert guard_dst as usize % std::mem::align_of::<u64>() == 0;
        assert object_pointer_within_limits(guard_dst, std::mem::size_of::<u64>()) == true;
        assert guard_dst as usize <= usize::MAX - std::mem::size_of::<u64>();
    points_to_limits::<u64>(guard_src as *mut u64);
    assert pointer_within_limits(guard_src + 1) == true;
    close [1/4]array::<u64>(guard_src + 1, 0, nil);
    assert [1/4](*guard_src |-> ?source_current);
    close [1/4]array::<u64>(guard_src, 1, cons(source_current, nil));
    points_to__limits::<u64>(guard_dst);
    assert pointer_within_limits(guard_dst + 1) == true;
    close array_::<u64>(guard_dst + 1, 0, nil);
    assert *guard_dst |-?-> ?old_gap;
    close array_::<u64>(guard_dst, 1, cons(old_gap, nil));
    call();
    close CopyOnDrop_drop_effect(_t, guard_src, guard_dst, guard_len);
}
@*/ {
        // SAFETY: `src` must contain `len` initialized elements, and dst must
        // be valid to write `len` elements.
        unsafe {
            ptr::copy_nonoverlapping(self.src, self.dst, self.len);
        }
    }
}


unsafe fn natural_onecell(tail: *mut u64)/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<u64>() &*&
    0 < std::mem::size_of::<u64>() &*&
    std::mem::size_of::<u64>() <= isize::MAX &*&
    tail as usize != 0 &*&
    tail as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(tail, std::mem::size_of::<u64>()) == true &*&
    tail as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    *tail |-> ?held &*& <u64>.own(t, held);
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*&
    *tail |-> held &*& <u64>.own(t, held);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<u64>() &*&
    *tail |-> ?unwound &*& <u64>.own(t, unwound);
@*/ {
    unsafe {
        let tmp = ManuallyDrop::new(tail.read());
        //@ let held_k = begin_lifetime();
        //@ let held_ref = precreate_ref(&tmp);
        //@ merge_fractions lifetime_token(held_k);
        //@ init_ref_readonly(held_ref, 1/2);
        //@ let recovery_src = held_ref;
        //@ let recovery_dst = tail;
        {
        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };
        //@ assert gap_guard.src == held_ref;
        //@ assert gap_guard.dst == tail; // REPRO: actual destination
        //@ initialized_storage_alignment(gap_guard.src as *mut u64); // REPRO: actual source storage
        //@ points_to_limits::<u64>(gap_guard.src as *mut u64); // REPRO: actual source limits
        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<u64>(); // REPRO: source no overflow
        //@ assert (gap_guard.src as usize + std::mem::size_of::<u64>() <= gap_guard.dst as usize || gap_guard.dst as usize + std::mem::size_of::<u64>() <= gap_guard.src as usize); // REPRO: constructor span before FBC
        //@ close <CopyOnDrop>.own(t, gap_guard);
        //@ close [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();
        //@ open [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();
        //@ merge_fractions gap_guard.src |-> _;
        //@ merge_fractions gap_guard.dst |-> _;
        //@ merge_fractions gap_guard.len |-> _;
        //@ open [1/2]<CopyOnDrop>.own(t, gap_guard);
        //@ open [1/2]<CopyOnDrop>.own(t, gap_guard);
        //@ merge_fractions points_to::<u64>(gap_guard.src as *mut u64, _);
        //@ merge_fractions points_to_::<u64>(gap_guard.dst, _);
        //@ merge_fractions type_interp::<u64>();
        //@ assert gap_guard.src == held_ref; // LADDER: FBC pointer identity
        //@ assert gap_guard.dst == tail; // LADDER: FBC destination identity
        //@ assert gap_guard.len == 1; // LADDER: FBC literal-one length
        //@ let fbc_src = gap_guard.src;
        //@ assert [1/4](*fbc_src |-> ?fbc_current); // LADDER: source quarter
        //@ assert [1/4](*held_ref |-> fbc_current); // LADDER: held reference quarter
        //@ assert gap_guard.src |-> ?guard_src &*& gap_guard.dst |-> ?guard_dst &*& gap_guard.len |-> ?guard_len;
        //@ assert guard_src == held_ref &*& guard_dst == tail &*& guard_len == 1;
        //@ initialized_storage_alignment(gap_guard.src as *mut u64);
        //@ points_to_limits::<u64>(gap_guard.src as *mut u64);
        //@ assert gap_guard.src as usize != 0;
        //@ assert gap_guard.src as usize % std::mem::align_of::<u64>() == 0;
        //@ assert object_pointer_within_limits(gap_guard.src, std::mem::size_of::<u64>()) == true;
        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ assert (gap_guard.src as usize + std::mem::size_of::<u64>() <= gap_guard.dst as usize || gap_guard.dst as usize + std::mem::size_of::<u64>() <= gap_guard.src as usize);
        //@ uninitialized_storage_alignment(gap_guard.dst);
        //@ points_to__limits::<u64>(gap_guard.dst);
        //@ assert gap_guard.dst as usize != 0;
        //@ assert gap_guard.dst as usize % std::mem::align_of::<u64>() == 0;
        //@ assert object_pointer_within_limits(gap_guard.dst, std::mem::size_of::<u64>()) == true;
        //@ assert gap_guard.dst as usize <= usize::MAX - std::mem::size_of::<u64>();
        //@ points_to_limits::<u64>(guard_src as *mut u64);
        //@ assert pointer_within_limits(guard_src + 1) == true;
        //@ close [1/4]array::<u64>(guard_src + 1, 0, nil);
        //@ assert [1/4](*guard_src |-> ?source_current);
        //@ close [1/4]array::<u64>(guard_src, 1, cons(source_current, nil));
        //@ points_to__limits::<u64>(guard_dst);
        //@ assert pointer_within_limits(guard_dst + 1) == true;
        //@ close array_::<u64>(guard_dst + 1, 0, nil);
        //@ assert *guard_dst |-?-> ?old_gap;
        //@ close array_::<u64>(guard_dst, 1, cons(old_gap, nil));
        //@ assert thread_token(t) &*& type_interp::<u64>() &*& gap_guard.src |-> guard_src &*& gap_guard.dst |-> guard_dst &*& gap_guard.len |-> guard_len &*& struct_CopyOnDrop_padding(&gap_guard) &*& [1/4]guard_src[..1] |-> cons(?entry_current, nil) &*& guard_dst[..1] |-> _ &*& <u64>.own(t, entry_current); // ENTRY: actual resources
        //@ vf__rust_storage_live(0); // NEGATIVE: source annotation cannot mint an internal MIR receipt
        //@ assert true; // TARGET: C2 diagnostic pre-Drop resource prefix
        ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, gap_guard.len);
        //@ close CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1);
        //@ open CopyOnDrop_drop_effect(t, recovery_src, recovery_dst, 1);
        //@ assert [?copy_f](*recovery_src |-> ?copied);
        //@ assert *recovery_dst |-> copied &*& <u64>.own(t, copied);
        //@ assert recovery_src == held_ref; // LADDER: copy pointer identity
        //@ assert [1/4](*held_ref |-> copied); // LADDER: conserved reference quarter
        //@ end_ref_readonly(held_ref);
        //@ merge_fractions points_to::<u64>(&tmp, _);
        //@ end_lifetime(held_k);
        //@ assert *tail |-> held &*& <u64>.own(t, held);
        let _drop_suppressed = ManuallyDrop::new(gap_guard);
    }
}
