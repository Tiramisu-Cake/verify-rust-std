// Minimal exact threshold body/method probes; trait reduced to the tested method.
// CASE_BEGIN threshold-body-positive
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;
fn selected_threshold_body<T: FreezeMarker>() -> usize
/*@ req thread_token(?t) &*& t == currentThread; @*/
/*@ ens thread_token(t) &*& result == 32; @*/
/*@ on_unwind_ens thread_token(t); @*/
{
    SMALL_SORT_GENERAL_THRESHOLD
}
// CASE_END threshold-body-positive
// CASE_BEGIN threshold-selected-positive
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;
}
impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 16; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_FALLBACK_THRESHOLD
    }
}
impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }
}
const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;
fn selected_freeze_threshold<T: FreezeMarker>() {
    let threshold = T::small_sort_threshold();
    //@ assert threshold == 32;
}
// CASE_END threshold-selected-positive
// CASE_BEGIN threshold-selected-false-31
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;
}
impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 16; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_FALLBACK_THRESHOLD
    }
}
impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }
}
const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;
fn selected_freeze_threshold<T: FreezeMarker>() {
    let threshold = T::small_sort_threshold();
    //@ assert threshold == 31;
}
// CASE_END threshold-selected-false-31
// CASE_BEGIN threshold-default-control
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;
}
impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 16; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_FALLBACK_THRESHOLD
    }
}
impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }
}
const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;
fn default_threshold() {
    let threshold = std::cell::Cell::<u8>::small_sort_threshold();
    //@ assert threshold == 16;
}
// CASE_END threshold-default-control
