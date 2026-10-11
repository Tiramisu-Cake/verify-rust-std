// Cloud-only source-bound diagnostic template. These are source fragments,
// not a proof of quicksort or small_sort. Bind each copied method to the exact
// current std source before verification. The actual trait calls are retained.

// CASE_BEGIN quicksort-base-unconstrained
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize {
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize {
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

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

// This copies the actual quicksort signature and the initial loop/base-case
// statements. The return after the non-base branch is an explicit diagnostic
// cut before limit/pivot/partition work; it has no whole-quicksort credit.
fn quicksort_base_prefix<T, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();

        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }

        // Diagnostic cut at the first non-base continuation.
        return;
    }
}
// CASE_END quicksort-base-unconstrained

// CASE_BEGIN selected-freeze-threshold-positive
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize {
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize {
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

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

// The bound explicitly selects the FreezeMarker specialization. Preserve the
// trait call so compiler-derived binding, not a literal replacement, must
// establish the postcondition.
fn selected_freeze_threshold<T: FreezeMarker>() {
    let threshold = T::small_sort_threshold();
    //@ assert threshold == 32;
}

// Freeze-qualified source diagnostic wrapper around the same base-case
// transfer. The extra trait bound qualifies this theorem only; it does not
// change quicksort's runtime signature or prove dispatch for unconstrained T.
fn selected_freeze_quicksort_base_prefix<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }

        // Diagnostic cut at the first non-base continuation.
        return;
    }
}
// CASE_END selected-freeze-threshold-positive

// CASE_BEGIN selected-freeze-threshold-false-31
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize {
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize {
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

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

fn selected_freeze_threshold_false_31<T: FreezeMarker>() {
    let threshold = T::small_sort_threshold();
    //@ assert threshold == 31;
}
// CASE_END selected-freeze-threshold-false-31

// CASE_BEGIN default-specialization-admission
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize {
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize {
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

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

// Cell<u8> is the non-Freeze control. This must remain on the actual default
// implementation, preventing a mistaken default-16 binding from satisfying
// the selected Freeze threshold gate above.
fn default_specialization_stays_16() {
    let threshold = std::cell::Cell::<u8>::small_sort_threshold();
    //@ assert threshold == 16;
}
// CASE_END default-specialization-admission

// CASE_BEGIN selected-small-sort-helper-prefix
trait StableSmallSortTypeImpl: Sized {
    fn small_sort_threshold() -> usize;

    fn small_sort<F: FnMut(&Self, &Self) -> bool>(
        v: &mut [Self],
        scratch: &mut [MaybeUninit<Self>],
        is_less: &mut F,
    );
}

impl<T> StableSmallSortTypeImpl for T {
    default fn small_sort_threshold() -> usize {
        SMALL_SORT_FALLBACK_THRESHOLD
    }

    default fn small_sort<F: FnMut(&T, &T) -> bool>(
        v: &mut [T],
        _scratch: &mut [MaybeUninit<T>],
        is_less: &mut F,
    ) {
        if v.len() >= 2 {
            insertion_sort_shift_left(v, 1, is_less);
        }
    }
}

impl<T: FreezeMarker> StableSmallSortTypeImpl for T {
    fn small_sort_threshold() -> usize {
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

const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;
const SMALL_SORT_GENERAL_THRESHOLD: usize = 32;

// Freeze-qualified quicksort base-case wrapper. This keeps the actual threshold
// and selected small_sort calls, with the same slice/callback transfer. The
// bound is a diagnostic theorem qualifier, not a runtime-signature change.
fn selected_freeze_quicksort_base_prefix<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
            return;
        }
        // Diagnostic cut at the first non-base continuation.
        return;
    }
}

// Exact selected impl method: the identical v, scratch, and callback flow to
// the helper. No owned arrays, threshold literal, or replacement summary.
fn selected_small_sort_method<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
    T::small_sort(v, scratch, is_less);
}

// Source-bound diagnostic prefix copied from the actual helper. It keeps the
// len<2 return, len+16 abort guard, both native slice pointer operations, the
// const/length branch and the first sort4 call boundary. The return in the
// selected branch is a diagnostic cut at that call boundary.
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    is_less: &mut F,
) {
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

        let _presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {
            // Diagnostic cut before the unselected sort8 calls.
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
            // Exact first sort4_stable callsite boundary; no callee summary.
            return;
        } else {
            // Diagnostic cut before the short-copy path.
            return;
        };
    }
}
// CASE_END selected-small-sort-helper-prefix
