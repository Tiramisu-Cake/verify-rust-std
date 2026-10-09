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

// Arbitrary-n identity transfer. These recursive predicates retain the
// current values and pointer limits down to the one-past endpoint; destination
// values use the same points-to-only predicate as source values.
pred current_handoff_owned_array<T>(t: thread_id_t, p: *T,
                                    n: usize, vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        *p |-> ?source_head &*& <T>.own(t, source_head) &*&
        current_handoff_owned_array::<T>(t, p + 1, n - 1, ?source_tail) &*&
        vs == cons(source_head, source_tail)
    };

pred current_handoff_values_array<T>(p: *T, n: usize, vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        *p |-> ?value_head &*&
        current_handoff_values_array::<T>(p + 1, n - 1, ?value_tail) &*&
        vs == cons(value_head, value_tail)
    };

pred current_handoff_array_domain<T>(src: *T, dst: *T, n: usize) =
    0 <= n &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    src as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(src) == true &*&
    pointer_within_limits(src + n) == true &*&
    pointer_within_limits(dst) == true &*&
    pointer_within_limits(dst + n) == true &*&
    (n == 0 || (src as pointer) != (dst as pointer)) &*&
    (src as usize + n * std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + n * std::mem::size_of::<T>() <= src as usize);

lem current_owner_handoff_array_identity_rec<T>(t: thread_id_t,
    src: *T, dst: *T, n: usize, vs: list<T>)
    req current_handoff_owned_array::<T>(t, src, n, vs) &*&
        current_handoff_values_array::<T>(dst, n, vs) &*&
        0 <= n &*&
        0 < std::mem::size_of::<T>() &*&
        std::mem::size_of::<T>() <= isize::MAX &*&
        n * std::mem::size_of::<T>() <= isize::MAX;
    ens current_handoff_values_array::<T>(src, n, vs) &*&
        current_handoff_owned_array::<T>(t, dst, n, vs);
{
    open current_handoff_owned_array::<T>(t, src, n, vs);
    open current_handoff_values_array::<T>(dst, n, vs);
    if n == 0 {
        close current_handoff_values_array::<T>(src, n, vs);
        close current_handoff_owned_array::<T>(t, dst, n, vs);
    } else {
        assert source_head == head(vs);
        assert value_head == head(vs);
        assert source_tail == tail(vs);
        assert value_tail == tail(vs);
        assert source_head == value_head;
        assert source_tail == value_tail;
        assert 0 <= n - 1;
        assert n - 1 <= n;
        mul_mono_l(0, n - 1, std::mem::size_of::<T>());
        mul_mono_l(n - 1, n, std::mem::size_of::<T>());
        assert (n - 1) * std::mem::size_of::<T>() <=
            n * std::mem::size_of::<T>();
        assert (n - 1) * std::mem::size_of::<T>() <= isize::MAX;
        current_owner_handoff_array_identity_rec::<T>(
            t, src + 1, dst + 1, n - 1, source_tail);
        close current_handoff_values_array::<T>(src, n, vs);
        close current_handoff_owned_array::<T>(t, dst, n, vs);
    }
}

lem current_owner_handoff_array_identity_lemma<T>(t: thread_id_t,
    src: *T, dst: *T, n: usize, vs: list<T>)
    req current_handoff_array_domain::<T>(src, dst, n) &*&
        current_handoff_owned_array::<T>(t, src, n, vs) &*&
        current_handoff_values_array::<T>(dst, n, vs);
    ens current_handoff_array_domain::<T>(src, dst, n) &*&
        current_handoff_values_array::<T>(src, n, vs) &*&
        current_handoff_owned_array::<T>(t, dst, n, vs);
{
    open current_handoff_array_domain::<T>(src, dst, n);
    current_owner_handoff_array_identity_rec::<T>(t, src, dst, n, vs);
    close current_handoff_array_domain::<T>(src, dst, n);
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

// Conditional arbitrary-n identity handoff for equal CURRENT source and
// initialized destination lists. This proves only the resource transfer;
// deriving that equality and the actual CopyOnDrop caller contract remains open.
// CASE_BEGIN current_owner_handoff_array_identity
pub unsafe fn current_owner_handoff_array_identity<T, F: FnMut(&T, &T) -> bool>(
    src: *mut T, dst: *mut T, n: usize, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    current_handoff_array_domain::<T>(src, dst, n) &*&
    current_handoff_owned_array::<T>(t, src, n, ?vs) &*&
    current_handoff_values_array::<T>(dst, n, vs) &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    current_handoff_array_domain::<T>(src, dst, n) &*&
    current_handoff_values_array::<T>(src, n, vs) &*&
    current_handoff_owned_array::<T>(t, dst, n, vs) &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ current_owner_handoff_array_identity_lemma::<T>(t, src, dst, n, vs);
}
// CASE_END current_owner_handoff_array_identity
