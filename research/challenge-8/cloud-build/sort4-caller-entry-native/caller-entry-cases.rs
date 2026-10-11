// Cloud-only source template. The driver extracts one CASE block per fixture.
// The body of core::slice::<impl [T]>::as_mut_ptr is checked against the pinned
// same-version slice/mod.rs before any component or consumer verification.

// CASE_BEGIN canonical-generic
fn canonical_slice_as_mut_ptr<T>(slice: &mut [T]) -> *mut T {
    slice as *mut [T] as *mut T
}
// CASE_END canonical-generic

// CASE_BEGIN canonical-mu
fn canonical_slice_as_mut_ptr_mu<T>(slice: &mut [MaybeUninit<T>]) -> *mut MaybeUninit<T> {
    slice as *mut [MaybeUninit<T>] as *mut MaybeUninit<T>
}
// CASE_END canonical-mu

// CASE_BEGIN consumer-positive
fn native_slice_pointer_consumer<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    let v_base = v.as_mut_ptr();
    let scratch_base = scratch.as_mut_ptr() as *mut T;
    //@ let source_base = strip_pointer_metadata(v as pointer) as *T;
    //@ let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
    //@ assert v_base == source_base;
    //@ assert scratch_base == strip_pointer_metadata(scratch as pointer) as *mut T;
    //@ assert source_base[..ptr_len(v)] |-> ?source_current;
    //@ assert foreach(source_current, own::<T>(currentThread));
    //@ assert mu_base[..ptr_len(scratch)] |-> ?mu_current;
    //@ assert foreach(mu_current, own::<std::mem::MaybeUninit<T>>(currentThread));
}
// CASE_END consumer-positive

// CASE_BEGIN consumer-wrong-pointer
fn native_slice_pointer_consumer<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    let v_base = v.as_mut_ptr();
    let _scratch_base = scratch.as_mut_ptr();
    //@ let source_base = strip_pointer_metadata(v as pointer) as *T;
    //@ assert v_base != source_base;
}
// CASE_END consumer-wrong-pointer

// CASE_BEGIN consumer-missing-raw-rights
fn native_slice_pointer_consumer<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>], unrelated: *mut T) {
    let v_base = v.as_mut_ptr();
    let _scratch_base = scratch.as_mut_ptr();
    /*@ if (unrelated != v_base) {
            assert unrelated[..1] |-> ?unrelated_values;
        } @*/
}
// CASE_END consumer-missing-raw-rights

// CASE_BEGIN consumer-mu-cast-no-initialized-T
fn native_slice_pointer_consumer<T>(v: &mut [T], scratch: &mut [MaybeUninit<T>]) {
    let _v_base = v.as_mut_ptr();
    let scratch_base = scratch.as_mut_ptr() as *mut T;
    if scratch.len() >= 1 {
        //@ let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
        //@ assert mu_base[..ptr_len(scratch)] |-> ?mu_current;
        //@ assert foreach(mu_current, own::<std::mem::MaybeUninit<T>>(currentThread));
        //@ assert scratch_base[..1] |-> ?initialized_values;
    }
}
// CASE_END consumer-mu-cast-no-initialized-T

// CASE_BEGIN actual-unfiltered-prefix
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
        let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {
            // Explicit diagnostic stop for the unselected sort8 branch.
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
            // This is the exact first sort4_stable callsite boundary. No callee
            // summary is supplied and no later SmallSort statement is credited.
            return;
        } else {
            // Explicit diagnostic stop for the unselected short path.
            return;
        };
    }
}
// CASE_END actual-unfiltered-prefix

// CASE_BEGIN public-guard-positive
pub fn sort<T, F>(v: &mut [T], is_less: &mut F)
where
    F: FnMut(&T, &T) -> bool,
{
    if T::IS_ZST {
        return;
    }
    //@ assert std::mem::size_of::<T>() > 0;
    //@ produce_type_interp::<T>();
    //@ produce_type_interp::<F>();
    //@ assert thread_token(?t);
    //@ assert t == currentThread;
    //@ let v_base = strip_pointer_metadata(v as pointer) as *T;
    //@ assert v_base[..ptr_len(v)] |-> ?source_current;
    //@ assert foreach(source_current, own::<T>(t));
    //@ assert *is_less |-> ?less_current;
    //@ assert <F>.own(t, less_current);
    //@ leak type_interp::<T>();
    //@ leak type_interp::<F>();
}
// CASE_END public-guard-positive

// CASE_BEGIN public-guard-false-positive-size
pub fn sort<T, F>(v: &mut [T], is_less: &mut F)
where
    F: FnMut(&T, &T) -> bool,
{
    if T::IS_ZST {
        return;
    }
    //@ assert std::mem::size_of::<T>() == 0;
}
// CASE_END public-guard-false-positive-size

// CASE_BEGIN public-guard-zst-branch-false
pub fn sort<T, F>(v: &mut [T], is_less: &mut F)
where
    F: FnMut(&T, &T) -> bool,
{
    if T::IS_ZST {
        //@ assert false;
        return;
    }
}
// CASE_END public-guard-zst-branch-false
