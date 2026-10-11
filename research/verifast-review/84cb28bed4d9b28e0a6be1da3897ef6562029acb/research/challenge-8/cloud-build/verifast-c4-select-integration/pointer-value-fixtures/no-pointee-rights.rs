pub unsafe fn pointer_value_cannot_own_pointee<T>(p: *const T) -> *const T
//@ req thread_token(?tid) &*& tid == currentThread &*& type_interp::<T>() &*& raw_ptr_own::<T>()(tid, p);
//@ ens thread_token(tid) &*& type_interp::<T>() &*& raw_ptr_own::<T>()(tid, result) &*& result == p &*& *result |-> _;
//@ on_unwind_ens false;
{
    p
}
