// Cloud-only template for the source-bound stable quicksort Freeze route.
// Each case is independently extracted and keeps the selected branch only.

// CASE_BEGIN selected-branch-positive
pub(crate) trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }

    fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        small_sort_general_with_scratch(v, scratch, is_less);
    }
}

// Freeze-qualified diagnostic wrapper retaining quicksort's actual parameter
// shape, initial loop, threshold call, selected small_sort call, and slices.
// The extra bound qualifies this theorem only; it is not in std quicksort's
// runtime signature. The return cuts the non-base continuation.
fn selected_freeze_basecase<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();

        if len <= T::small_sort_threshold() {
            //@ assert len <= 32;
            T::small_sort(v, scratch, is_less);
            return;
        }

        // Diagnostic cut before limit/pivot/partition work.
        return;
    }
}

fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    //@ assert ptr_len(v) <= 32;
    let len = v.len();
    if len < 2 {
        return;
    }

    if scratch.len() < len + 16 {
        intrinsics::abort();
    }

    let v_base = v.as_mut_ptr();
    let len_div_2 = len / 2;

    unsafe {
        let scratch_base = scratch.as_mut_ptr() as *mut T;

        let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {
            // Diagnostic cut before the actual sort8 calls.
            return;
        } else if len >= 8 {
            //@ produce_type_interp::<T>();
            //@ produce_type_interp::<F>();
            //@ assert thread_token(?t);
            //@ assert t == currentThread;
            //@ assert v_base == strip_pointer_metadata(v as pointer) as *mut T;
            //@ assert scratch_base == strip_pointer_metadata(scratch as pointer) as *mut T;
            //@ assert v_base[..len] |-> ?source_current;
            //@ assert foreach(source_current, own::<T>(t));
            //@ let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
            //@ let scratch_len = ptr_len(scratch);
            //@ assert mu_base[..scratch_len] |-> ?mu_current;
            //@ assert foreach(mu_current, own::<std::mem::MaybeUninit<T>>(t));
            //@ assert *is_less |-> ?less_current;
            //@ assert <F>.own(t, less_current);
            //@ leak type_interp::<T>();
            //@ leak type_interp::<F>();
            // Exact first sort4_stable call boundary; no callee summary.
            return;
        } else {
            // Diagnostic cut before the actual short-copy path.
            return;
        };
    }
}
// CASE_END selected-branch-positive

// CASE_BEGIN selected-branch-false-bound-31
pub(crate) trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }

    fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        small_sort_general_with_scratch(v, scratch, is_less);
    }
}

fn selected_freeze_basecase_false_31<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            // Intended semantic negative: the selected threshold admits len=32.
            //@ assert len <= 31;
            T::small_sort(v, scratch, is_less);
            return;
        }
        return;
    }
}

fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    //@ assert ptr_len(v) <= 32;
    let len = v.len();
    if len < 2 {
        return;
    }
    if scratch.len() < len + 16 {
        intrinsics::abort();
    }
    let v_base = v.as_mut_ptr();
    let len_div_2 = len / 2;
    unsafe {
        let scratch_base = scratch.as_mut_ptr() as *mut T;
        let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {
            return;
        } else if len >= 8 {
            //@ produce_type_interp::<T>();
            //@ produce_type_interp::<F>();
            //@ assert thread_token(?t);
            //@ assert t == currentThread;
            //@ assert v_base == strip_pointer_metadata(v as pointer) as *mut T;
            //@ assert scratch_base == strip_pointer_metadata(scratch as pointer) as *mut T;
            //@ assert v_base[..len] |-> ?source_current;
            //@ assert foreach(source_current, own::<T>(t));
            //@ let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
            //@ let scratch_len = ptr_len(scratch);
            //@ assert mu_base[..scratch_len] |-> ?mu_current;
            //@ assert foreach(mu_current, own::<std::mem::MaybeUninit<T>>(t));
            //@ assert *is_less |-> ?less_current;
            //@ assert <F>.own(t, less_current);
            //@ leak type_interp::<T>();
            //@ leak type_interp::<F>();
            return;
        } else {
            return;
        };
    }
}
// CASE_END selected-branch-false-bound-31

// CASE_BEGIN selected-branch-missing-source-array
pub(crate) trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize
    /*@ req thread_token(?t) &*& t == currentThread; @*/
    /*@ ens thread_token(t) &*& result == 32; @*/
    /*@ on_unwind_ens thread_token(t); @*/
    {
        SMALL_SORT_GENERAL_THRESHOLD
    }

    fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        small_sort_general_with_scratch(v, scratch, is_less);
    }
}

fn selected_freeze_basecase_missing_source_array<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            //@ assert len <= 32;
            //@ let source_base = strip_pointer_metadata(v as pointer) as *T;
            //@ assert source_base[..ptr_len(v)] |-> ?source_current;
            //@ assert foreach(source_current, own::<T>(currentThread));
            // Intentional authority removal; failure belongs at the selected
            // trait call's actual source-array precondition.
            //@ leak source_base[..ptr_len(v)] |-> source_current;
            T::small_sort(v, scratch, is_less);
            return;
        }
        return;
    }
}

fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    //@ assert ptr_len(v) <= 32;
    let len = v.len();
    if len < 2 {
        return;
    }
    if scratch.len() < len + 16 {
        intrinsics::abort();
    }
    let v_base = v.as_mut_ptr();
    let len_div_2 = len / 2;
    unsafe {
        let scratch_base = scratch.as_mut_ptr() as *mut T;
        let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {
            return;
        } else if len >= 8 {
            //@ produce_type_interp::<T>();
            //@ produce_type_interp::<F>();
            //@ assert thread_token(?t);
            //@ assert t == currentThread;
            //@ assert v_base == strip_pointer_metadata(v as pointer) as *mut T;
            //@ assert scratch_base == strip_pointer_metadata(scratch as pointer) as *mut T;
            //@ assert v_base[..len] |-> ?source_current;
            //@ assert foreach(source_current, own::<T>(t));
            //@ let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
            //@ let scratch_len = ptr_len(scratch);
            //@ assert mu_base[..scratch_len] |-> ?mu_current;
            //@ assert foreach(mu_current, own::<std::mem::MaybeUninit<T>>(t));
            //@ assert *is_less |-> ?less_current;
            //@ assert <F>.own(t, less_current);
            //@ leak type_interp::<T>();
            //@ leak type_interp::<F>();
            return;
        } else {
            return;
        };
    }
}
// CASE_END selected-branch-missing-source-array
