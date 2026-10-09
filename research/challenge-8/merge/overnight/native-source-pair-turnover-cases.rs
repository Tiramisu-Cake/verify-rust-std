#![feature(unboxed_closures)]
#![allow(dead_code)]

// Draft native-index source resource component. It isolates how current source
// owners are partitioned and restored; it performs no runtime reads, writes,
// callback, or claim about the actual merge caller.

/*@
fix native_pair_step(index: option<usize>) -> option<usize> {
    match index {
        none => none,
        some(k) => if k == 0 { none } else { some(k - 1) }
    }
}

fix native_pair_replace<T>(vs: list<T>, i: option<usize>, j: option<usize>,
                           vi: T, vj: T) -> list<T> {
    match vs {
        nil => nil,
        cons(head, tail) => if i == some(0) {
            cons(vi, native_pair_replace::<T>(tail,
                native_pair_step(i), native_pair_step(j), vi, vj))
        } else if j == some(0) {
            cons(vj, native_pair_replace::<T>(tail,
                native_pair_step(i), native_pair_step(j), vi, vj))
        } else {
            cons(head, native_pair_replace::<T>(tail,
                native_pair_step(i), native_pair_step(j), vi, vj))
        }
    }
}

fix native_pair_current_matches<T>(vs: list<T>, index: option<usize>, value: T) -> bool {
    match index {
        none => true,
        some(k) => value == nth(k, vs)
    }
}

fix native_pair_index_in_range(index: option<usize>, n: usize) -> bool {
    match index {
        none => true,
        some(k) => 0 <= k && k < n
    }
}

fix native_pair_ordered_distinct(i: option<usize>, j: option<usize>) -> bool {
    match i {
        none => true,
        some(left) => match j {
            none => true,
            some(right) => left < right
        }
    }
}

// The holes own exactly the non-selected current cells. Indices are relative
// to p and are stepped in lockstep with the recursively represented suffix.
pred native_pair_holes<T>(t: thread_id_t, p: *T, n: usize,
                          i: option<usize>, j: option<usize>, vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        vs == cons(?current, ?tail) &*&
        (if i == some(0) || j == some(0) {
            true
        } else {
            *p |-> current &*& <T>.own(t, current)
        }) &*&
        native_pair_holes::<T>(t, p + 1, n - 1,
            native_pair_step(i), native_pair_step(j), tail);
    };

// The selected predicate carries the full current points-to and owner chunk
// for each active index. Ordered distinctness ensures a selected cell is never
// represented twice.
pred native_pair_selected<T>(t: thread_id_t, p: *T, n: usize,
                             i: option<usize>, j: option<usize>, vi: T, vj: T) =
    pointer_within_limits(p) == true &*&
    if n == 0 {
        i == none &*& j == none
    } else {
        (if i == some(0) {
            *p |-> vi &*& <T>.own(t, vi)
        } else if j == some(0) {
            *p |-> vj &*& <T>.own(t, vj)
        } else { true }) &*&
        native_pair_selected::<T>(t, p + 1, n - 1,
            native_pair_step(i), native_pair_step(j), vi, vj);
    };

pred native_pair_owned_array<T>(t: thread_id_t, p: *T, n: usize,
                                vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        *p |-> head(vs) &*& <T>.own(t, head(vs)) &*&
        native_pair_owned_array::<T>(t, p + 1, n - 1, tail(vs))
    };

lem native_pair_replace_length<T>(vs: list<T>, i: option<usize>,
                                  j: option<usize>, vi: T, vj: T)
    req true;
    ens length(native_pair_replace::<T>(vs, i, j, vi, vj)) == length(vs);
{
    match vs {
        nil => {},
        cons(head, tail) => {
            native_pair_replace_length::<T>(tail,
                native_pair_step(i), native_pair_step(j), vi, vj);
            assert length(native_pair_replace::<T>(vs, i, j, vi, vj)) ==
                1 + length(native_pair_replace::<T>(tail,
                    native_pair_step(i), native_pair_step(j), vi, vj));
            assert length(vs) == 1 + length(tail);
        }
    }
}

pred native_pair_array_domain<T>(p: *T, n: usize) =
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    p as usize <= usize::MAX - n * std::mem::size_of::<T>() &*&
    pointer_within_limits(p) == true &*&
    pointer_within_limits(p + n) == true;

lem native_pair_index_step_in_range(index: option<usize>, n: usize)
    req n > 0 &*& native_pair_index_in_range(index, n);
    ens native_pair_index_in_range(native_pair_step(index), n - 1);
{
    match index {
        none => {},
        some(k) => {
            if k == 0 {
                assert native_pair_step(index) == none;
            } else {
                assert 0 < k;
                assert 0 <= k - 1;
                assert k - 1 < n - 1;
            }
        }
    }
}

lem native_pair_ordered_step(i: option<usize>, j: option<usize>, n: usize)
    req n > 0 &*& native_pair_index_in_range(i, n) &*&
        native_pair_index_in_range(j, n) &*&
        native_pair_ordered_distinct(i, j);
    ens native_pair_ordered_distinct(native_pair_step(i), native_pair_step(j));
{
    match i {
        none => {},
        some(left) => match j {
            none => {},
            some(right) => {
                if left == 0 {
                    assert 0 < right;
                    assert native_pair_step(i) == none;
                    assert 0 <= right - 1;
                } else {
                    assert 0 < left;
                    assert 0 < right;
                    assert left - 1 < right - 1;
                }
            }
        }
    }
}

lem native_pair_extract_rec<T>(t: thread_id_t, p: *T, n: usize,
    i: option<usize>, j: option<usize>, vs: list<T>, vi: T, vj: T)
    req native_pair_owned_array::<T>(t, p, n, vs) &*&
        native_pair_index_in_range(i, n) &*&
        native_pair_index_in_range(j, n) &*&
        native_pair_ordered_distinct(i, j) &*&
        native_pair_current_matches::<T>(vs, i, vi) &*&
        native_pair_current_matches::<T>(vs, j, vj);
    ens native_pair_holes::<T>(t, p, n, i, j, vs) &*&
        native_pair_selected::<T>(t, p, n, i, j, vi, vj);
{
    open native_pair_owned_array::<T>(t, p, n, vs);
    if n == 0 {
        close native_pair_holes::<T>(t, p, n, i, j, vs);
        close native_pair_selected::<T>(t, p, n, i, j, vi, vj);
    } else {
        native_pair_index_step_in_range(i, n);
        native_pair_index_step_in_range(j, n);
        native_pair_ordered_step(i, j, n);
        native_pair_extract_rec::<T>(t, p + 1, n - 1,
            native_pair_step(i), native_pair_step(j), tail(vs), vi, vj);
        close native_pair_holes::<T>(t, p, n, i, j, vs);
        close native_pair_selected::<T>(t, p, n, i, j, vi, vj);
    }
}

// Restore the selected *current* cell values. The output list is expressed
// through the pure replacement relation, so it does not refer to an entry
// snapshot; when callers restore the extracted owners, each replacement is
// the same value currently present at that selected position.
lem native_pair_restore_rec<T>(t: thread_id_t, p: *T, n: usize,
    i: option<usize>, j: option<usize>, vs: list<T>,
    vi: T, vj: T)
    req native_pair_holes::<T>(t, p, n, i, j, vs) &*&
        native_pair_selected::<T>(t, p, n, i, j, vi, vj) &*&
        native_pair_index_in_range(i, n) &*&
        native_pair_index_in_range(j, n) &*&
        native_pair_ordered_distinct(i, j);
    ens native_pair_owned_array::<T>(t, p, n,
        native_pair_replace::<T>(vs, i, j, vi, vj));
{
    native_pair_replace_length::<T>(vs, i, j, vi, vj);
    open native_pair_holes::<T>(t, p, n, i, j, vs);
    open native_pair_selected::<T>(t, p, n, i, j, vi, vj);
    if n == 0 {
        close native_pair_owned_array::<T>(t, p, n,
            native_pair_replace::<T>(vs, i, j, vi, vj));
    } else {
        native_pair_index_step_in_range(i, n);
        native_pair_index_step_in_range(j, n);
        native_pair_ordered_step(i, j, n);
        native_pair_restore_rec::<T>(t, p + 1, n - 1,
            native_pair_step(i), native_pair_step(j), tail(vs),
            vi, vj);
        close native_pair_owned_array::<T>(t, p, n,
            native_pair_replace::<T>(vs, i, j, vi, vj));
    }
}

lem native_pair_extract<T>(t: thread_id_t, p: *T, n: usize,
    i: option<usize>, j: option<usize>, vs: list<T>, vi: T, vj: T)
    req native_pair_array_domain::<T>(p, n) &*&
        native_pair_owned_array::<T>(t, p, n, vs) &*&
        native_pair_index_in_range(i, n) &*&
        native_pair_index_in_range(j, n) &*&
        native_pair_ordered_distinct(i, j) &*&
        native_pair_current_matches::<T>(vs, i, vi) &*&
        native_pair_current_matches::<T>(vs, j, vj);
    ens native_pair_array_domain::<T>(p, n) &*&
        native_pair_holes::<T>(t, p, n, i, j, vs) &*&
        native_pair_selected::<T>(t, p, n, i, j, vi, vj);
{
    open native_pair_array_domain::<T>(p, n);
    native_pair_extract_rec::<T>(t, p, n, i, j, vs, vi, vj);
    close native_pair_array_domain::<T>(p, n);
}

lem native_pair_restore<T>(t: thread_id_t, p: *T, n: usize,
    i: option<usize>, j: option<usize>, vs: list<T>,
    vi: T, vj: T)
    req native_pair_array_domain::<T>(p, n) &*&
        native_pair_holes::<T>(t, p, n, i, j, vs) &*&
        native_pair_selected::<T>(t, p, n, i, j, vi, vj) &*&
        native_pair_index_in_range(i, n) &*&
        native_pair_index_in_range(j, n) &*&
        native_pair_ordered_distinct(i, j);
    ens native_pair_array_domain::<T>(p, n) &*&
        native_pair_owned_array::<T>(t, p, n,
            native_pair_replace::<T>(vs, i, j, vi, vj));
{
    open native_pair_array_domain::<T>(p, n);
    native_pair_restore_rec::<T>(t, p, n, i, j, vs, vi, vj);
    close native_pair_array_domain::<T>(p, n);
}
@*/

// Baseline extract/restore control: selected values are the current array
// values, and the full normal post keeps the explicit replacement relation.
// CASE_BEGIN native_source_pair_extract_restore_current
pub unsafe fn native_source_pair_extract_restore_current<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: usize, j: usize,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_owned_array::<T>(t, p, n, ?vs) &*&
    i < j &*& j < n &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_owned_array::<T>(t, p, n,
        native_pair_replace::<T>(vs, some(i), some(j), nth(i, vs), nth(j, vs))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ native_pair_extract::<T>(t, p, n, some(i), some(j), vs,
    //@     nth(i, vs), nth(j, vs));
    //@ native_pair_restore::<T>(t, p, n, some(i), some(j), vs,
    //@     nth(i, vs), nth(j, vs));
}
// CASE_END native_source_pair_extract_restore_current

// Same-pair turnover starts from old holes plus arbitrary current selected
// owners. The current selected values need not equal the historical list.
// CASE_BEGIN native_source_pair_turnover_same_pair
pub unsafe fn native_source_pair_turnover_same_pair<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: usize, j: usize,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_holes::<T>(t, p, n, some(i), some(j), ?oldvs) &*&
    native_pair_selected::<T>(t, p, n, some(i), some(j), ?vi, ?vj) &*&
    i < j &*& j < n &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_holes::<T>(t, p, n, some(i), some(j),
        native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)) &*&
    native_pair_selected::<T>(t, p, n, some(i), some(j),
        nth(i, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)),
        nth(j, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ native_pair_restore::<T>(t, p, n, some(i), some(j), oldvs, vi, vj);
    //@ native_pair_extract::<T>(t, p, n, some(i), some(j),
    //@     native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj),
    //@     nth(i, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)),
    //@     nth(j, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)));
}
// CASE_END native_source_pair_turnover_same_pair

// The old and next pairs may overlap arbitrarily. Their indices are native
// ghost usize options; this does not assert the actual Rust caller supplies
// these resource transitions.
// CASE_BEGIN native_source_pair_turnover_overlap
pub unsafe fn native_source_pair_turnover_overlap<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: usize, j: usize, k: usize, l: usize,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_holes::<T>(t, p, n, some(i), some(j), ?oldvs) &*&
    native_pair_selected::<T>(t, p, n, some(i), some(j), ?vi, ?vj) &*&
    i < j &*& j < n &*& k < l &*& l < n &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    native_pair_array_domain::<T>(p, n) &*&
    native_pair_holes::<T>(t, p, n, some(k), some(l),
        native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)) &*&
    native_pair_selected::<T>(t, p, n, some(k), some(l),
        nth(k, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)),
        nth(l, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ native_pair_restore::<T>(t, p, n, some(i), some(j), oldvs, vi, vj);
    //@ native_pair_extract::<T>(t, p, n, some(k), some(l),
    //@     native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj),
    //@     nth(k, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)),
    //@     nth(l, native_pair_replace::<T>(oldvs, some(i), some(j), vi, vj)));
}
// CASE_END native_source_pair_turnover_overlap
