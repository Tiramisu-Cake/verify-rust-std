pub unsafe fn r23_checked_slice_as_mut_ptr<'a>(s: &'a mut [u64]) -> *mut u64
/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<u64>() &*&
    [?q]lifetime_token('a) &*& full_borrow('a, <[u64]>.full_borrow_content(t, s));
@*/
/*@
ens thread_token(t) &*& type_interp::<u64>() &*& [q]lifetime_token('a) &*&
    full_borrow('a, <[u64]>.full_borrow_content(t, s)) &*&
    result == strip_pointer_metadata(s as pointer) as *mut u64;
@*/
/*@ on_unwind_ens false; @*/
{
    s as *mut [u64] as *mut u64
}
