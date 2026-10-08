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

lem replace_two_negative_indices_noop<T>(vs: list<T>, i: i32, j: i32,
                                         vi: T, vj: T)
    req i < 0 &*& j < 0;
    ens replace_two::<T>(vs, i, j, vi, vj) == vs;
{
    match vs {
        nil => {
            assert replace_two::<T>(vs, i, j, vi, vj) == vs;
        }
        cons(head, tail) => {
            replace_two_negative_indices_noop::<T>(tail, i - 1, j - 1, vi, vj);
            assert replace_two::<T>(vs, i, j, vi, vj) == vs;
        }
    }
}

lem replace_two_old_values<T>(vs: list<T>, i: i32, j: i32)
    req 0 <= j &*& i < j &*& j < length(vs);
    ens replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
{
    match vs {
        nil => {
            assert false;
        }
        cons(head, tail) => {
            if i == 0 {
                replace_two_old_values::<T>(tail, i - 1, j - 1);
                assert nth(i, vs) == head;
                assert nth(j, vs) == nth(j - 1, tail);
                assert replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
            } else if j == 0 {
                replace_two_negative_indices_noop::<T>(tail, i - 1, j - 1,
                    nth(i, vs), nth(j, vs));
                assert nth(j, vs) == head;
                assert replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
            } else {
                replace_two_old_values::<T>(tail, i - 1, j - 1);
                assert nth(i, vs) == nth(i - 1, tail);
                assert nth(j, vs) == nth(j - 1, tail);
                assert replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
            }
        }
    }
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

// CASE_BEGIN owned_array_extract_restore_old_values_and_frame
pub unsafe fn owned_array_extract_restore_old_values_and_frame<T>(
    p: *mut T, n: usize, i: i32, j: i32, frame: *mut u32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    owned_array::<T>(t, p, n, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    owned_array::<T>(t, p, n, vs) &*& *frame |-> frame_value &*&
    <u32>.own(t, frame_value); @*/
/*@ on_unwind_ens false; @*/
{
    //@ owned_array_extract_two::<T>(t, p, n, i, j, nth(i, vs), nth(j, vs));
    //@ replace_two_old_values::<T>(vs, i, j);
    //@ owned_array_restore_two::<T>(t, p, n, i, j, nth(i, vs), nth(j, vs));
}
// CASE_END owned_array_extract_restore_old_values_and_frame

// CASE_BEGIN owned_array_restore_current_values_and_owners
pub unsafe fn owned_array_restore_current_values_and_owners<T>(
    p: *mut T, n: usize, i: i32, j: i32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *(p + i) |-> ?vi &*& *(p + j) |-> ?vj &*&
    <T>.own(t, vi) &*& <T>.own(t, vj); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    owned_array::<T>(t, p, n, replace_two::<T>(vs, i, j, vi, vj)); @*/
/*@ on_unwind_ens false; @*/
{
    //@ owned_array_restore_two::<T>(t, p, n, i, j, vi, vj);
}
// CASE_END owned_array_restore_current_values_and_owners

// CASE_BEGIN owned_array_restore_concrete_u32_current_values
pub unsafe fn owned_array_restore_concrete_u32_current_values(
    p: *mut u32, n: usize, i: i32, j: i32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<u32>() &*&
    owned_array_two_holes::<u32>(t, p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*&
    0 < std::mem::size_of::<u32>() &*&
    n * std::mem::size_of::<u32>() <= isize::MAX &*&
    *(p + i) |-> 41 &*& *(p + j) |-> 73 &*&
    <u32>.own(t, 41) &*& <u32>.own(t, 73); @*/
/*@ ens thread_token(t) &*& type_interp::<u32>() &*&
    owned_array::<u32>(t, p, n,
        replace_two::<u32>(vs, i, j, 41, 73)); @*/
/*@ on_unwind_ens false; @*/
{
    //@ owned_array_restore_two::<u32>(t, p, n, i, j, 41, 73);
}
// CASE_END owned_array_restore_concrete_u32_current_values

// CASE_BEGIN owned_array_extract_does_not_duplicate_owner
pub unsafe fn owned_array_extract_does_not_duplicate_owner<T>(p: *mut T, n: usize, i: i32, j: i32)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    owned_array::<T>(t, p, n, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX; @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ owned_array_extract_two::<T>(t, p, n, i, j, nth(i, vs), nth(j, vs));
    //@ assert <T>.own(t, nth(i, vs)) &*& <T>.own(t, nth(i, vs)); // TARGET: extraction must not mint a second owner
}
// CASE_END owned_array_extract_does_not_duplicate_owner

// CASE_BEGIN owned_array_wrong_value_restoration_does_not_restore_old_array
pub unsafe fn owned_array_wrong_value_restoration_does_not_restore_old_array<T>(
    p: *mut T, n: usize, i: i32, j: i32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    owned_array_two_holes::<T>(t, p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *(p + i) |-> ?vi &*& *(p + j) |-> ?vj &*& vi != nth(i, vs) &*&
    <T>.own(t, vi) &*& <T>.own(t, vj); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ owned_array_restore_two::<T>(t, p, n, i, j, vi, vj);
    //@ assert owned_array::<T>(t, p, n, vs); // TARGET: changed current value cannot restore the old owned array
}
// CASE_END owned_array_wrong_value_restoration_does_not_restore_old_array
