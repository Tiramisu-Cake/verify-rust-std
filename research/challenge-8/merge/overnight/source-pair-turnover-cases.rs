#![allow(dead_code)]
// Checked ghost resource component for the future M3 actual-source proof.
// This fixture is a positive-stride, non-ZST resource model. It does not call
// FnMut, read/copy T values, or claim anything about an actual merge body.

/*@
pred owned_array<T>(t: thread_id_t, p: *T, n: usize, vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        *p |-> ?head &*& <T>.own(t, head) &*&
        owned_array::<T>(t, p + 1, n - 1, ?tail) &*& vs == cons(head, tail)
    };

// The signed indices are offsets from this predicate's current p. A value of
// -1 means that the corresponding hole has already been passed by recursion.
pred owned_array_two_holes<T>(t: thread_id_t, p: *T, n: usize,
                              i: i32, j: i32, vs: list<T>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else if i == 0 || j == 0 {
        owned_array_two_holes::<T>(t, p + 1, n - 1, i - 1, j - 1, ?tail) &*&
        vs == cons(nth(0, vs), tail)
    } else {
        *p |-> ?head &*& <T>.own(t, head) &*&
        owned_array_two_holes::<T>(t, p + 1, n - 1, i - 1, j - 1, ?tail) &*&
        vs == cons(head, tail)
    };

fix replace_two<T>(vs: list<T>, i: i32, j: i32, vi: T, vj: T) -> list<T> {
    match vs {
        nil => nil,
        cons(head, tail) => if i == 0 {
            cons(vi, replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        } else if j == 0 {
            cons(vj, replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        } else {
            cons(head, replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        }
    }
}

lem replace_two_length<T>(vs: list<T>, i: i32, j: i32, vi: T, vj: T)
    req true;
    ens length(replace_two::<T>(vs, i, j, vi, vj)) == length(vs);
{
    match vs {
        nil => {
            assert length(replace_two::<T>(vs, i, j, vi, vj)) == length(vs);
        }
        cons(head, tail) => {
            replace_two_length::<T>(tail, i - 1, j - 1, vi, vj);
            assert length(replace_two::<T>(vs, i, j, vi, vj)) ==
                1 + length(replace_two::<T>(tail, i - 1, j - 1, vi, vj));
            assert length(vs) == 1 + length(tail);
        }
    }
}

// A negative index has already passed its selected cell; its carried value is
// irrelevant. This stronger checked lemma keeps the fixed old selected values
// while recursion moves either index below zero.
lem replace_two_matching_old_values<T>(vs: list<T>, i: i32, j: i32,
                                       vi: T, vj: T)
    req (i < 0 || vi == nth(i, vs)) &*&
        (j < 0 || vj == nth(j, vs));
    ens replace_two::<T>(vs, i, j, vi, vj) == vs;
{
    match vs {
        nil => {
            assert replace_two::<T>(vs, i, j, vi, vj) == nil;
        }
        cons(head, tail) => {
            if i == 0 {
                assert vi == head;
                assert i - 1 < 0;
                assert j - 1 < 0 || vj == nth(j - 1, tail);
                replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert replace_two::<T>(vs, i, j, vi, vj) == vs;
            } else if j == 0 {
                assert vj == head;
                assert i - 1 < 0 || vi == nth(i - 1, tail);
                assert j - 1 < 0;
                replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert replace_two::<T>(vs, i, j, vi, vj) == vs;
            } else {
                assert i - 1 < 0 || vi == nth(i - 1, tail);
                assert j - 1 < 0 || vj == nth(j - 1, tail);
                replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert replace_two::<T>(vs, i, j, vi, vj) == vs;
            }
        }
    }
}

lem replace_two_old_values<T>(vs: list<T>, i: i32, j: i32)
    req true;
    ens replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
{
    replace_two_matching_old_values::<T>(vs, i, j, nth(i, vs), nth(j, vs));
}

// i may be -1 after the first selected cell was extracted. The body recurses
// over every array cell and carries its real points-to/own chunks explicitly.
lem owned_array_extract_two<T>(t: thread_id_t, p: *T, n: usize, i: i32, j: i32,
                               vi: T, vj: T)
    req owned_array::<T>(t, p, n, ?vs) &*&
        i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
        n * std::mem::size_of::<T>() <= isize::MAX &*&
        (i < 0 || vi == nth(i, vs)) &*& (j < 0 || vj == nth(j, vs));
    ens owned_array_two_holes::<T>(t, p, n, i, j, vs) &*&
        (if 0 <= i { *(p + i) |-> vi &*& <T>.own(t, vi) } else { true }) &*&
        (if 0 <= j { *(p + j) |-> vj &*& <T>.own(t, vj) } else { true });
{
    open owned_array::<T>(t, p, n, vs);
    if n == 0 {
        close owned_array_two_holes::<T>(t, p, n, i, j, vs);
    } else if i == 0 {
        owned_array_extract_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        close owned_array_two_holes::<T>(t, p, n, i, j, vs);
        assert nth(i, vs) == head(vs);
        assert vi == head(vs);
        assert nth(j, vs) == nth(j - 1, tail(vs));
    } else if j == 0 {
        owned_array_extract_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        close owned_array_two_holes::<T>(t, p, n, i, j, vs);
        assert nth(j, vs) == head(vs);
        assert vj == head(vs);
        assert nth(i, vs) == nth(i - 1, tail(vs));
    } else {
        owned_array_extract_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        close owned_array_two_holes::<T>(t, p, n, i, j, vs);
        assert nth(i, vs) == nth(i - 1, tail(vs));
        assert nth(j, vs) == nth(j - 1, tail(vs));
    }
}

lem owned_array_restore_two<T>(t: thread_id_t, p: *T, n: usize, i: i32, j: i32,
                               vi: T, vj: T)
    req owned_array_two_holes::<T>(t, p, n, i, j, ?vs) &*&
        i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
        n * std::mem::size_of::<T>() <= isize::MAX &*&
        *(p + i) |-> vi &*& <T>.own(t, vi) &*&
        *(p + j) |-> vj &*& <T>.own(t, vj);
    ens owned_array::<T>(t, p, n, replace_two::<T>(vs, i, j, vi, vj)) &*&
        (if i < 0 { *(p + i) |-> vi &*& <T>.own(t, vi) } else { true }) &*&
        (if j < 0 { *(p + j) |-> vj &*& <T>.own(t, vj) } else { true });
{
    open owned_array_two_holes::<T>(t, p, n, i, j, vs);
    if n == 0 {
        replace_two_length::<T>(vs, i, j, vi, vj);
        close owned_array::<T>(t, p, n, replace_two::<T>(vs, i, j, vi, vj));
    } else if i == 0 {
        owned_array_restore_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        replace_two_length::<T>(vs, i, j, vi, vj);
        close owned_array::<T>(t, p, n,
            replace_two::<T>(vs, i, j, vi, vj));
        assert nth(0, replace_two::<T>(vs, i, j, vi, vj)) == vi;
    } else if j == 0 {
        owned_array_restore_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        replace_two_length::<T>(vs, i, j, vi, vj);
        close owned_array::<T>(t, p, n,
            replace_two::<T>(vs, i, j, vi, vj));
        assert nth(0, replace_two::<T>(vs, i, j, vi, vj)) == vj;
    } else {
        owned_array_restore_two::<T>(t, p + 1, n - 1, i - 1, j - 1, vi, vj);
        replace_two_length::<T>(vs, i, j, vi, vj);
        close owned_array::<T>(t, p, n,
            replace_two::<T>(vs, i, j, vi, vj));
    }
}
@*/

// Conditional experimental kernel boundary: this draft composes the existing
// checked source-array extract/restore lemmas. It does not call a comparator or
// claim any relation to the actual merge helper.

/*@
lem owned_array_pair_turnover<T>(t: thread_id_t, p: *T, n: usize,
                                 i: i32, j: i32, vi: T, vj: T,
                                 k: i32, l: i32)
    req owned_array_two_holes::<T>(t, p, n, i, j, ?oldvs) &*&
        n >= 2 &*& 0 <= i &*& i < j &*& j < n &*&
        0 <= k &*& k < l &*& l < n &*&
        0 < std::mem::size_of::<T>() &*&
        n * std::mem::size_of::<T>() <= isize::MAX &*&
        *(p + i) |-> vi &*& <T>.own(t, vi) &*&
        *(p + j) |-> vj &*& <T>.own(t, vj);
    ens owned_array_two_holes::<T>(t, p, n, k, l,
            replace_two::<T>(oldvs, i, j, vi, vj)) &*&
        *(p + k) |-> nth(k, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
        <T>.own(t, nth(k, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
        *(p + l) |-> nth(l, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
        <T>.own(t, nth(l, replace_two::<T>(oldvs, i, j, vi, vj)));
{
    owned_array_restore_two::<T>(t, p, n, i, j, vi, vj);
    owned_array_extract_two::<T>(t, p, n, k, l,
        nth(k, replace_two::<T>(oldvs, i, j, vi, vj)),
        nth(l, replace_two::<T>(oldvs, i, j, vi, vj)));
}
@*/

// The pair indices use the checked fixture's signed i32 interface; this draft
// does not claim native-usize/full arbitrary-n loop coverage. The first and
// second ordered pairs can overlap arbitrarily. Destination option cells and
// current comparator state are caller-owned frame chunks.
// CASE_BEGIN source_pair_turnover_overlap
pub unsafe fn source_pair_turnover_overlap<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: i32, j: i32, k: i32, l: i32,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j, ?oldvs) &*&
    n >= 2 &*& 0 <= i &*& i < j &*& j < n &*&
    0 <= k &*& k < l &*& l < n &*&
    0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *(p + i) |-> ?vi &*& <T>.own(t, vi) &*&
    *(p + j) |-> ?vj &*& <T>.own(t, vj) &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, k, l,
        replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    *(p + k) |-> nth(k, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(k, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *(p + l) |-> nth(l, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(l, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ owned_array_pair_turnover::<T>(t, p, n, i, j, vi, vj, k, l);
}
// CASE_END source_pair_turnover_overlap

// A same-pair positive confirms restoration and re-extraction of the current
// values. It remains a resource component and makes no callback/runtime claim.
// CASE_BEGIN source_pair_turnover_same_pair
pub unsafe fn source_pair_turnover_same_pair<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: i32, j: i32,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j, ?oldvs) &*&
    n >= 2 &*& 0 <= i &*& i < j &*& j < n &*&
    0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *(p + i) |-> ?vi &*& <T>.own(t, vi) &*&
    *(p + j) |-> ?vj &*& <T>.own(t, vj) &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j,
        replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    *(p + i) |-> nth(i, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(i, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *(p + j) |-> nth(j, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(j, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ owned_array_pair_turnover::<T>(t, p, n, i, j, vi, vj, i, j);
}
// CASE_END source_pair_turnover_same_pair

// This target is uncalibrated until a Cloud run establishes its exact stage,
// predicate and location. It matches the overlap positive contract and frames.
// CASE_BEGIN source_pair_turnover_does_not_duplicate_owner
// EXPECT_REJECTION_CALIBRATION {"kind":"memory_permission","message":"uncalibrated duplicate-owner rejection after source-pair turnover","location":"UNCALIBRATED"}
pub unsafe fn source_pair_turnover_does_not_duplicate_owner<T, F: FnMut(&T, &T) -> bool>(
    p: *mut T, n: usize, i: i32, j: i32, k: i32, l: i32,
    dst0: *mut T, dst1: *mut T, is_less: &mut F,
)
/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j, ?oldvs) &*&
    n >= 2 &*& 0 <= i &*& i < j &*& j < n &*&
    0 <= k &*& k < l &*& l < n &*&
    0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *(p + i) |-> ?vi &*& <T>.own(t, vi) &*&
    *(p + j) |-> ?vj &*& <T>.own(t, vj) &*&
    dst0 as pointer != dst1 as pointer &*&
    *dst0 |-?-> ?dst0_old &*& *dst1 |-?-> ?dst1_old &*&
    *is_less |-> ?f0 &*& <F>.own(t, f0);
@*//*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    owned_array_two_holes::<T>(t, p, n, k, l,
        replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    *(p + k) |-> nth(k, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(k, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *(p + l) |-> nth(l, replace_two::<T>(oldvs, i, j, vi, vj)) &*&
    <T>.own(t, nth(l, replace_two::<T>(oldvs, i, j, vi, vj))) &*&
    *dst0 |-?-> dst0_old &*& *dst1 |-?-> dst1_old &*&
    *is_less |-> f0 &*& <F>.own(t, f0);
@*//*@
on_unwind_ens false;
@*/
{
    //@ owned_array_pair_turnover::<T>(t, p, n, i, j, vi, vj, k, l);
    //@ assert <T>.own(t, nth(k, replace_two::<T>(oldvs, i, j, vi, vj))) &*& <T>.own(t, nth(k, replace_two::<T>(oldvs, i, j, vi, vj))); // TARGET: turnover must not duplicate a current owner
}
// CASE_END source_pair_turnover_does_not_duplicate_owner
