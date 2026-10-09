#![feature(unboxed_closures)]
#![allow(dead_code)]

// Draft conditional ghost component for handing current source owners to two
// initialized destination cells. There is no runtime read/write/callback.

/*@
pred current_source_pair_owned<T>(t: thread_id_t, src0: *T, src1: *T,
                                  v0: T, v1: T) =
    *src0 |-> v0 &*& <T>.own(t, v0) &*&
    *src1 |-> v1 &*& <T>.own(t, v1);

pred current_source_pair_values<T>(src0: *T, src1: *T, v0: T, v1: T) =
    *src0 |-> v0 &*& *src1 |-> v1;

pred current_destination_pair_values<T>(dst0: *T, dst1: *T,
                                        d0: T, d1: T) =
    *dst0 |-> d0 &*& *dst1 |-> d1;

pred current_destination_pair_owned<T>(t: thread_id_t, dst0: *T, dst1: *T,
                                       d0: T, d1: T) =
    *dst0 |-> d0 &*& <T>.own(t, d0) &*&
    *dst1 |-> d1 &*& <T>.own(t, d1);

// Full pointer inequality plus disjoint byte ranges excludes overlapping
// cells. Positive size rules out ZSTs; explicit bounds keep each cell object
// and address-range calculation inside the supported pointer domain.
pred handoff_four_cells_within_limits<T>(src0: *T, src1: *T,
                                         dst0: *T, dst1: *T) =
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(src0) == true &*&
    pointer_within_limits(src1) == true &*&
    pointer_within_limits(dst0) == true &*&
    pointer_within_limits(dst1) == true &*&
    object_pointer_within_limits(src0, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(src1, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst0, std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst1, std::mem::size_of::<T>()) == true &*&
    src0 as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    src1 as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst0 as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    dst1 as usize <= usize::MAX - std::mem::size_of::<T>() &*&
    src0 as pointer != src1 as pointer &*&
    src0 as pointer != dst0 as pointer &*&
    src0 as pointer != dst1 as pointer &*&
    src1 as pointer != dst0 as pointer &*&
    src1 as pointer != dst1 as pointer &*&
    dst0 as pointer != dst1 as pointer &*&
    (src0 as usize + std::mem::size_of::<T>() <= src1 as usize ||
     src1 as usize + std::mem::size_of::<T>() <= src0 as usize) &*&
    (src0 as usize + std::mem::size_of::<T>() <= dst0 as usize ||
     dst0 as usize + std::mem::size_of::<T>() <= src0 as usize) &*&
    (src0 as usize + std::mem::size_of::<T>() <= dst1 as usize ||
     dst1 as usize + std::mem::size_of::<T>() <= src0 as usize) &*&
    (src1 as usize + std::mem::size_of::<T>() <= dst0 as usize ||
     dst0 as usize + std::mem::size_of::<T>() <= src1 as usize) &*&
    (src1 as usize + std::mem::size_of::<T>() <= dst1 as usize ||
     dst1 as usize + std::mem::size_of::<T>() <= src1 as usize) &*&
    (dst0 as usize + std::mem::size_of::<T>() <= dst1 as usize ||
     dst1 as usize + std::mem::size_of::<T>() <= dst0 as usize);

// The current source cell owners move to destinations whose current bytes
// already equal this pair. No equality to an entry snapshot is claimed.
lem current_owner_handoff_identity_lemma<T>(t: thread_id_t,
    src0: *T, src1: *T, dst0: *T, dst1: *T, v0: T, v1: T)
    req current_source_pair_owned::<T>(t, src0, src1, v0, v1) &*&
        current_destination_pair_values::<T>(dst0, dst1, v0, v1);
    ens current_source_pair_values::<T>(src0, src1, v0, v1) &*&
        current_destination_pair_owned::<T>(t, dst0, dst1, v0, v1);
{
    open current_source_pair_owned::<T>(t, src0, src1, v0, v1);
    open current_destination_pair_values::<T>(dst0, dst1, v0, v1);
    close current_source_pair_values::<T>(src0, src1, v0, v1);
    close current_destination_pair_owned::<T>(t, dst0, dst1, v0, v1);
}

lem current_owner_handoff_swap_lemma<T>(t: thread_id_t,
    src0: *T, src1: *T, dst0: *T, dst1: *T, v0: T, v1: T)
    req current_source_pair_owned::<T>(t, src0, src1, v0, v1) &*&
        current_destination_pair_values::<T>(dst0, dst1, v1, v0);
    ens current_source_pair_values::<T>(src0, src1, v0, v1) &*&
        current_destination_pair_owned::<T>(t, dst0, dst1, v1, v0);
{
    open current_source_pair_owned::<T>(t, src0, src1, v0, v1);
    open current_destination_pair_values::<T>(dst0, dst1, v1, v0);
    close current_source_pair_values::<T>(src0, src1, v0, v1);
    close current_destination_pair_owned::<T>(t, dst0, dst1, v1, v0);
}
@*/

// Conditional positive: destination bytes already equal the current source
// pair in identity order. Equal-valued pairs are permitted and consume their
// exact two source-cell owner resources.
// CASE_BEGIN current_owner_handoff_identity
pub unsafe fn current_owner_handoff_identity<T, F: FnMut(&T, &T) -> bool>(
    src0: *mut T, src1: *mut T, dst0: *mut T, dst1: *mut T,
    is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    handoff_four_cells_within_limits::<T>(src0, src1, dst0, dst1) &*&
    current_source_pair_owned::<T>(t, src0, src1, ?v0, ?v1) &*&
    current_destination_pair_values::<T>(dst0, dst1, v0, v1) &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    handoff_four_cells_within_limits::<T>(src0, src1, dst0, dst1) &*&
    current_source_pair_values::<T>(src0, src1, v0, v1) &*&
    current_destination_pair_owned::<T>(t, dst0, dst1, v0, v1) &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ current_owner_handoff_identity_lemma::<T>(t, src0, src1, dst0, dst1, v0, v1);
}
// CASE_END current_owner_handoff_identity

// Conditional positive: destination bytes already equal the same current
// source pair in swapped order. The owners are transferred, never copied.
// CASE_BEGIN current_owner_handoff_swap
pub unsafe fn current_owner_handoff_swap<T, F: FnMut(&T, &T) -> bool>(
    src0: *mut T, src1: *mut T, dst0: *mut T, dst1: *mut T,
    is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    handoff_four_cells_within_limits::<T>(src0, src1, dst0, dst1) &*&
    current_source_pair_owned::<T>(t, src0, src1, ?v0, ?v1) &*&
    current_destination_pair_values::<T>(dst0, dst1, v1, v0) &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    handoff_four_cells_within_limits::<T>(src0, src1, dst0, dst1) &*&
    current_source_pair_values::<T>(src0, src1, v0, v1) &*&
    current_destination_pair_owned::<T>(t, dst0, dst1, v1, v0) &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ current_owner_handoff_swap_lemma::<T>(t, src0, src1, dst0, dst1, v0, v1);
}
// CASE_END current_owner_handoff_swap
