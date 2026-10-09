#![feature(unboxed_closures)]

// Conditional ghost resource operation only. This fixture performs no runtime
// read, write, copy, callback, or actual SmallSort call.

/*@
fix transposition_replace_at<T>(vs: list<T>, index: usize, value: T) -> list<T> {
    match vs {
        nil => nil,
        cons(head, tail) => if index == 0 {
            cons(value, tail)
        } else {
            cons(head, transposition_replace_at::<T>(tail, index - 1, value))
        }
    }
}

fix transposition_values<T>(vs: list<T>, i: usize, j: usize) -> list<T> {
    match vs {
        nil => nil,
        cons(head, tail) => if i == 0 {
            cons(nth(j, vs), transposition_replace_at::<T>(tail, j - 1, head))
        } else {
            cons(head, transposition_values::<T>(tail, i - 1, j - 1))
        }
    }
}

lem transposition_replace_at_length<T>(vs: list<T>, index: usize, value: T)
    req 0 <= index &*& index < length(vs);
    ens length(transposition_replace_at::<T>(vs, index, value)) == length(vs);
{
    match vs {
        nil => {}
        cons(head, tail) => {
            if index == 0 {
                assert length(transposition_replace_at::<T>(vs, index, value)) == length(vs);
            } else {
                transposition_replace_at_length::<T>(tail, index - 1, value);
                assert length(transposition_replace_at::<T>(vs, index, value)) ==
                    1 + length(transposition_replace_at::<T>(tail, index - 1, value));
                assert length(vs) == 1 + length(tail);
            }
        }
    }
}

lem transposition_values_length<T>(vs: list<T>, i: usize, j: usize)
    req 0 <= i &*& 0 <= j &*& i < j &*& j < length(vs);
    ens length(transposition_values::<T>(vs, i, j)) == length(vs);
{
    match vs {
        nil => {}
        cons(head, tail) => {
            if i == 0 {
                assert 0 < j;
                assert j - 1 < length(tail);
                transposition_replace_at_length::<T>(tail, j - 1, head);
                assert length(transposition_values::<T>(vs, i, j)) ==
                    1 + length(transposition_replace_at::<T>(tail, j - 1, head));
                assert length(vs) == 1 + length(tail);
            } else {
                assert 0 < i;
                assert i - 1 < j - 1;
                assert j - 1 < length(tail);
                transposition_values_length::<T>(tail, i - 1, j - 1);
                assert length(transposition_values::<T>(vs, i, j)) ==
                    1 + length(transposition_values::<T>(tail, i - 1, j - 1));
                assert length(vs) == 1 + length(tail);
            }
        }
    }
}

// Replace one owner value at an arbitrary native-usize list position. Keep
// the canonical foreach predicate throughout; the displaced CURRENT owner is
// returned as a singleton foreach, with no wrapper/direct-owner conversion.
lem transposition_owner_replace_at<T>(t: thread_id_t, vs: list<T>,
                                     index: usize, value: T)
    req 0 <= index &*& index < length(vs) &*&
        foreach(vs, own::<T>(t)) &*& foreach(cons(value, nil), own::<T>(t));
    ens foreach(transposition_replace_at::<T>(vs, index, value), own::<T>(t)) &*&
        foreach(cons(nth(index, vs), nil), own::<T>(t));
{
    match vs {
        nil => {}
        cons(head, tail) => {
            open foreach(vs, own::<T>(t));
            if index == 0 {
                open foreach(cons(value, nil), own::<T>(t));
                assert nth(0, vs) == head;
                assert transposition_replace_at::<T>(vs, index, value) == cons(value, tail);
                close foreach(cons(head, nil), own::<T>(t));
                close foreach(cons(value, tail), own::<T>(t));
            } else {
                assert 0 < index;
                assert index - 1 < length(tail);
                transposition_owner_replace_at::<T>(t, tail, index - 1, value);
                assert nth(index, vs) == nth(index - 1, tail);
                assert transposition_replace_at::<T>(vs, index, value) ==
                    cons(head, transposition_replace_at::<T>(tail, index - 1, value));
                close foreach(cons(head,
                    transposition_replace_at::<T>(tail, index - 1, value)), own::<T>(t));
            }
        }
    }
}

// Exchange the owner resources at i and j by opening only the owner list.
// The source list is the current list in the precondition, never an entry
// snapshot from a runtime copy or earlier callback.
lem transposition_owner_exchange_rec<T>(t: thread_id_t, vs: list<T>,
                                        i: usize, j: usize)
    req 0 <= i &*& 0 <= j &*& i < j &*& j < length(vs) &*&
        foreach(vs, own::<T>(t));
    ens foreach(transposition_values::<T>(vs, i, j), own::<T>(t));
{
    match vs {
        nil => {}
        cons(head, tail) => {
            open foreach(vs, own::<T>(t));
            if i == 0 {
                assert 0 < j;
                assert j - 1 < length(tail);
                close foreach(nil, own::<T>(t));
                close foreach(cons(head, nil), own::<T>(t));
                transposition_owner_replace_at::<T>(t, tail, j - 1, head);
                assert nth(j, vs) == nth(j - 1, tail);
                assert transposition_values::<T>(vs, i, j) ==
                    cons(nth(j, vs), transposition_replace_at::<T>(tail, j - 1, head));
                open foreach(cons(nth(j, vs), nil), own::<T>(t));
                open foreach(nil, own::<T>(t));
                close foreach(cons(nth(j, vs),
                    transposition_replace_at::<T>(tail, j - 1, head)), own::<T>(t));
            } else {
                assert 0 < i;
                assert i - 1 < j - 1;
                assert j - 1 < length(tail);
                transposition_owner_exchange_rec::<T>(t, tail, i - 1, j - 1);
                assert transposition_values::<T>(vs, i, j) ==
                    cons(head, transposition_values::<T>(tail, i - 1, j - 1));
                close foreach(cons(head,
                    transposition_values::<T>(tail, i - 1, j - 1)), own::<T>(t));
            }
        }
    }
}

pred current_owner_transposition_domain<T>(src: *T, dst: *T, n: usize) =
    0 <= n &*&
    n >= 2 &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    src != 0 &*& dst != 0 &*&
    src as usize % std::mem::align_of::<T>() == 0 &*&
    dst as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(src, n * std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(dst, n * std::mem::size_of::<T>()) == true &*&
    src as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    dst as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(src) == true &*&
    pointer_within_limits(src + n) == true &*&
    pointer_within_limits(dst) == true &*&
    pointer_within_limits(dst + n) == true &*&
    (src as pointer) != (dst as pointer) &*&
    (src as usize + n * std::mem::size_of::<T>() <= dst as usize ||
     dst as usize + n * std::mem::size_of::<T>() <= src as usize);

pred current_owner_transposition_source_owned<T>(t: thread_id_t, p: *T,
                                                  n: usize, vs: list<T>) =
    n == length(vs) &*& array::<T>(p, n, vs) &*& foreach(vs, own::<T>(t));

pred current_owner_transposition_source_values<T>(p: *T, n: usize,
                                                   vs: list<T>) =
    n == length(vs) &*& array::<T>(p, n, vs);

pred current_owner_transposition_destination_values<T>(p: *T, n: usize,
                                                        vs: list<T>) =
    n == length(vs) &*& array::<T>(p, n, vs);

pred current_owner_transposition_destination_owned<T>(t: thread_id_t, p: *T,
                                                        n: usize, vs: list<T>) =
    n == length(vs) &*& array::<T>(p, n, vs) &*& foreach(vs, own::<T>(t));

lem current_owner_transposition_resource<T>(t: thread_id_t, src: *T, dst: *T,
                                             n: usize, vs: list<T>,
                                             i: usize, j: usize)
    req current_owner_transposition_domain::<T>(src, dst, n) &*&
        current_owner_transposition_source_owned::<T>(t, src, n, vs) &*&
        current_owner_transposition_destination_values::<T>(dst, n,
            transposition_values::<T>(vs, i, j)) &*&
        0 <= i &*& 0 <= j &*& i < j &*& j < n;
    ens current_owner_transposition_domain::<T>(src, dst, n) &*&
        current_owner_transposition_source_values::<T>(src, n, vs) &*&
        current_owner_transposition_destination_owned::<T>(t, dst, n,
            transposition_values::<T>(vs, i, j));
{
    open current_owner_transposition_domain::<T>(src, dst, n);
    open current_owner_transposition_source_owned::<T>(t, src, n, vs);
    open current_owner_transposition_destination_values::<T>(dst, n,
        transposition_values::<T>(vs, i, j));
    transposition_values_length::<T>(vs, i, j);
    transposition_owner_exchange_rec::<T>(t, vs, i, j);
    close current_owner_transposition_source_values::<T>(src, n, vs);
    close current_owner_transposition_destination_owned::<T>(t, dst, n,
        transposition_values::<T>(vs, i, j));
    close current_owner_transposition_domain::<T>(src, dst, n);
}
@*/

// Isolated head-cell permission probe. The only changed proof obligation below
// is the physical destination head permission after the shared owner transfer.
// CASE_BEGIN current_owner_transposition_memory_cell_positive
pub unsafe fn current_owner_transposition_memory_cell_positive<T, F: FnMut(&T, &T) -> bool>(
    src: *mut T, dst: *mut T, n: usize, i: usize, j: usize, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    current_owner_transposition_domain::<T>(src, dst, n) &*&
    current_owner_transposition_source_owned::<T>(t, src, n, ?vs) &*&
    current_owner_transposition_destination_values::<T>(dst, n,
        transposition_values::<T>(vs, i, j)) &*&
    0 <= i &*& 0 <= j &*& i < j &*& j < n &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    current_owner_transposition_domain::<T>(src, dst, n) &*&
    current_owner_transposition_source_values::<T>(src, n, vs) &*&
    current_owner_transposition_destination_owned::<T>(t, dst, n,
        transposition_values::<T>(vs, i, j)) &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ current_owner_transposition_resource::<T>(t, src, dst, n, vs, i, j);
    //@ open current_owner_transposition_destination_owned::<T>(t, dst, n, transposition_values::<T>(vs, i, j));
    //@ open array::<T>(dst, n, transposition_values::<T>(vs, i, j));
    //@ assert *dst |-> head(transposition_values::<T>(vs, i, j));
    //@ close array::<T>(dst, n, transposition_values::<T>(vs, i, j));
    //@ close current_owner_transposition_destination_owned::<T>(t, dst, n, transposition_values::<T>(vs, i, j));
}
// CASE_END current_owner_transposition_memory_cell_positive

// Same complete domain and posts. This asks the heap model to grant two full
// permissions to one physical head cell; the first Cloud run is calibration.
// CASE_BEGIN current_owner_transposition_memory_cell_duplicate_negative
pub unsafe fn current_owner_transposition_memory_cell_duplicate_negative<T, F: FnMut(&T, &T) -> bool>(
    src: *mut T, dst: *mut T, n: usize, i: usize, j: usize, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    current_owner_transposition_domain::<T>(src, dst, n) &*&
    current_owner_transposition_source_owned::<T>(t, src, n, ?vs) &*&
    current_owner_transposition_destination_values::<T>(dst, n,
        transposition_values::<T>(vs, i, j)) &*&
    0 <= i &*& 0 <= j &*& i < j &*& j < n &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    current_owner_transposition_domain::<T>(src, dst, n) &*&
    current_owner_transposition_source_values::<T>(src, n, vs) &*&
    current_owner_transposition_destination_owned::<T>(t, dst, n,
        transposition_values::<T>(vs, i, j)) &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ current_owner_transposition_resource::<T>(t, src, dst, n, vs, i, j);
    //@ open current_owner_transposition_destination_owned::<T>(t, dst, n, transposition_values::<T>(vs, i, j));
    //@ open array::<T>(dst, n, transposition_values::<T>(vs, i, j));
    //@ assert *dst |-> head(transposition_values::<T>(vs, i, j)) &*& *dst |-> head(transposition_values::<T>(vs, i, j)); // TARGET: request duplicate full permission for the same physical destination cell
    //@ close array::<T>(dst, n, transposition_values::<T>(vs, i, j));
    //@ close current_owner_transposition_destination_owned::<T>(t, dst, n, transposition_values::<T>(vs, i, j));
}
// CASE_END current_owner_transposition_memory_cell_duplicate_negative
