#![no_std]
use core::{mem::ManuallyDrop, ptr};

struct CopyOnDrop<T> {
    src: *const T,
    dst: *mut T,
    len: usize,
}

/*@
pred<T> <CopyOnDrop<T>>.own(t, v) =
    type_interp::<T>() &*& v.len == 1 &*&
    (v.src as usize + std::mem::size_of::<T>() <= v.dst as usize ||
     v.dst as usize + std::mem::size_of::<T>() <= v.src as usize) &*&
    [?f](*v.src |-> ?current) &*& *v.dst |-?-> ?old_gap &*&
    <T>.own(t, current);
@*/

/*@
lem initialized_storage_alignment<T>(p: *T)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& p as usize % std::mem::align_of::<T>() == 0;
{
    open [f]points_to::<T>(p, v);
    to_u8s_::<T>(p);
    from_u8s_::<T>(p);
    close [f]points_to::<T>(p, v);
}
@*/

/*@
lem uninitialized_storage_alignment<T>(p: *T)
    req [?f]points_to_::<T>(p, ?v);
    ens [f]points_to_::<T>(p, v) &*& p as usize % std::mem::align_of::<T>() == 0;
{
    to_u8s_::<T>(p);
    from_u8s_::<T>(p);
}
@*/

unsafe fn insertion_onecell<T>(tail: *mut T)/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    tail as usize != 0 &*&
    tail as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(tail, std::mem::size_of::<T>()) == true &*&
    tail as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    *tail |-> ?held &*& <T>.own(t, held);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*&
    *tail |-> held &*& <T>.own(t, held);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*&
    *tail |-> ?unwound &*& <T>.own(t, unwound);
@*/ {
    unsafe {
        let tmp = ManuallyDrop::new(tail.read());
        //@ let held_k = begin_lifetime();
        //@ let held_ref = precreate_ref(&tmp);
        //@ merge_fractions lifetime_token(held_k);
        //@ init_ref_readonly(held_ref, 1/2);
        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };
        //@ assert gap_guard.src == held_ref;
        //@ assert gap_guard.dst == tail; // REPRO: actual destination
        //@ initialized_storage_alignment::<T>(gap_guard.src as *mut T); // REPRO: actual source storage
        //@ points_to_limits::<T>(gap_guard.src as *mut T); // REPRO: actual source limits
        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<T>(); // REPRO: source no overflow
        //@ assert (gap_guard.src as usize + std::mem::size_of::<T>() <= gap_guard.dst as usize || gap_guard.dst as usize + std::mem::size_of::<T>() <= gap_guard.src as usize); // REPRO: constructor span before FBC
        //@ close <CopyOnDrop<T>>.own(t, gap_guard);
        //@ close CopyOnDrop_full_borrow_content::<T>(t, &gap_guard)();
        //@ open CopyOnDrop_full_borrow_content::<T>(t, &gap_guard)();
        //@ open <CopyOnDrop<T>>.own(t, gap_guard);
        //@ initialized_storage_alignment::<T>(gap_guard.src as *mut T);
        //@ points_to_limits::<T>(gap_guard.src as *mut T);
        //@ assert gap_guard.src as usize != 0;
        //@ assert gap_guard.src as usize % std::mem::align_of::<T>() == 0;
        //@ assert object_pointer_within_limits(gap_guard.src, std::mem::size_of::<T>()) == true;
        //@ assert gap_guard.src as usize <= usize::MAX - std::mem::size_of::<T>();
        //@ assert (gap_guard.src as usize + std::mem::size_of::<T>() <= gap_guard.dst as usize || gap_guard.dst as usize + std::mem::size_of::<T>() <= gap_guard.src as usize);
        //@ uninitialized_storage_alignment::<T>(gap_guard.dst);
        //@ points_to__limits::<T>(gap_guard.dst);
        //@ assert gap_guard.dst as usize != 0;
        //@ assert gap_guard.dst as usize % std::mem::align_of::<T>() == 0;
        //@ assert object_pointer_within_limits(gap_guard.dst, std::mem::size_of::<T>()) == true;
        //@ assert gap_guard.dst as usize <= usize::MAX - std::mem::size_of::<T>();
        ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, 1);
        //@ assert [?copy_f](*gap_guard.src |-> ?copied);
        //@ assert *gap_guard.dst |-> copied &*& <T>.own(t, copied);
        //@ end_ref_readonly(held_ref);
        //@ merge_fractions points_to::<T>(&tmp, _);
        //@ end_lifetime(held_k);
        //@ assert *tail |-> held &*& <T>.own(t, held);
    }
}
