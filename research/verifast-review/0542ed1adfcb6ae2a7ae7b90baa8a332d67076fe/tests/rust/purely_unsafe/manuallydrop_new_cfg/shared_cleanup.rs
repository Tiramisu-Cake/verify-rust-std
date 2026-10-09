pub unsafe fn new(b: bool)
//@ req thread_token(?tid) &*& tid == currentThread;
//@ ens thread_token(tid);
//@ on_unwind_ens thread_token(tid);
{
    if b {
        panic!("ManuallyDrop CFG regression");
    }
}

pub unsafe fn ordinary_caller(b: bool)
//@ req thread_token(?tid) &*& tid == currentThread;
//@ ens thread_token(tid);
//@ on_unwind_ens thread_token(tid);
{
    new(b);
}

pub unsafe fn shared_cleanup<T>(t: T, b: bool)
//@ req thread_token(?tid) &*& tid == currentThread;
//@ ens thread_token(tid);
//@ on_unwind_ens thread_token(tid);
{
    let _ = std::mem::ManuallyDrop::new(t);
    new(b);
}
