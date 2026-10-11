pub unsafe fn pointer_value_identity<T>(p: *const T) -> *const T
//@ req thread_token(?tid) &*& tid == currentThread &*& type_interp::<T>() &*& raw_ptr_own::<T>()(tid, p);
//@ ens thread_token(tid) &*& type_interp::<T>() &*& raw_ptr_own::<T>()(tid, result) &*& result == p;
//@ on_unwind_ens false;
{
    p
}
