#![allow(dead_code)]
// Checked model of two writable MaybeUninit destination slots. The resource
// carries stock option-valued points_to_<T> cells and never creates T.own.

/*@
pred scratch_option_array<T>(p: *T, n: usize, vs: list<option<T>>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else {
        points_to_::<T>(p, ?head) &*&
        scratch_option_array::<T>(p + 1, n - 1, ?tail) &*&
        vs == cons(head, tail)
    };

pred scratch_option_array_two_holes<T>(p: *T, n: usize, i: i32, j: i32,
                                       vs: list<option<T>>) =
    n == length(vs) &*& pointer_within_limits(p) == true &*&
    if n == 0 {
        vs == nil
    } else if i == 0 || j == 0 {
        scratch_option_array_two_holes::<T>(p + 1, n - 1, i - 1, j - 1, ?tail) &*&
        vs == cons(nth(0, vs), tail)
    } else {
        points_to_::<T>(p, ?head) &*&
        scratch_option_array_two_holes::<T>(p + 1, n - 1, i - 1, j - 1, ?tail) &*&
        vs == cons(head, tail)
    };

fix scratch_replace_two<T>(vs: list<option<T>>, i: i32, j: i32,
                           vi: option<T>, vj: option<T>) -> list<option<T>> {
    match vs {
        nil => nil,
        cons(head, tail) => if i == 0 {
            cons(vi, scratch_replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        } else if j == 0 {
            cons(vj, scratch_replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        } else {
            cons(head, scratch_replace_two::<T>(tail, i - 1, j - 1, vi, vj))
        }
    }
}

lem scratch_replace_two_length<T>(vs: list<option<T>>, i: i32, j: i32,
                                  vi: option<T>, vj: option<T>)
    req true;
    ens length(scratch_replace_two::<T>(vs, i, j, vi, vj)) == length(vs);
{
    match vs {
        nil => {
            assert length(scratch_replace_two::<T>(vs, i, j, vi, vj)) == length(vs);
        }
        cons(head, tail) => {
            scratch_replace_two_length::<T>(tail, i - 1, j - 1, vi, vj);
            assert length(scratch_replace_two::<T>(vs, i, j, vi, vj)) ==
                1 + length(scratch_replace_two::<T>(tail, i - 1, j - 1, vi, vj));
            assert length(vs) == 1 + length(tail);
        }
    }
}

lem scratch_replace_two_matching_old_values<T>(vs: list<option<T>>, i: i32, j: i32,
                                                vi: option<T>, vj: option<T>)
    req (i < 0 || vi == nth(i, vs)) &*&
        (j < 0 || vj == nth(j, vs));
    ens scratch_replace_two::<T>(vs, i, j, vi, vj) == vs;
{
    match vs {
        nil => {
            assert scratch_replace_two::<T>(vs, i, j, vi, vj) == nil;
        }
        cons(head, tail) => {
            if i == 0 {
                assert vi == head;
                assert i - 1 < 0;
                assert j - 1 < 0 || vj == nth(j - 1, tail);
                scratch_replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert scratch_replace_two::<T>(vs, i, j, vi, vj) == vs;
            } else if j == 0 {
                assert vj == head;
                assert i - 1 < 0 || vi == nth(i - 1, tail);
                assert j - 1 < 0;
                scratch_replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert scratch_replace_two::<T>(vs, i, j, vi, vj) == vs;
            } else {
                assert i - 1 < 0 || vi == nth(i - 1, tail);
                assert j - 1 < 0 || vj == nth(j - 1, tail);
                scratch_replace_two_matching_old_values::<T>(tail, i - 1, j - 1, vi, vj);
                assert scratch_replace_two::<T>(vs, i, j, vi, vj) == vs;
            }
        }
    }
}

lem scratch_replace_two_old_values<T>(vs: list<option<T>>, i: i32, j: i32)
    req true;
    ens scratch_replace_two::<T>(vs, i, j, nth(i, vs), nth(j, vs)) == vs;
{
    scratch_replace_two_matching_old_values::<T>(vs, i, j, nth(i, vs), nth(j, vs));
}

// Extract exactly the two indexed option cells. The rest remain in the
// recursive two-hole predicate; values and ownership are not conflated.
lem scratch_option_extract_two<T>(p: *T, n: usize, i: i32, j: i32,
                                  vi: option<T>, vj: option<T>)
    req scratch_option_array::<T>(p, n, ?vs) &*&
        i < j &*& j < n &*&
        0 < std::mem::size_of::<T>() &*&
        n * std::mem::size_of::<T>() <= isize::MAX &*&
        (i < 0 || vi == nth(i, vs)) &*& (j < 0 || vj == nth(j, vs));
    ens scratch_option_array_two_holes::<T>(p, n, i, j, vs) &*&
        (if 0 <= i { points_to_::<T>(p + i, vi) } else { true }) &*&
        (if 0 <= j { points_to_::<T>(p + j, vj) } else { true });
{
    open scratch_option_array::<T>(p, n, vs);
    if n == 0 {
        close scratch_option_array_two_holes::<T>(p, n, i, j, vs);
    } else if i == 0 {
        scratch_option_extract_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        close scratch_option_array_two_holes::<T>(p, n, i, j, vs);
        assert nth(i, vs) == head(vs);
        assert vi == head(vs);
    } else if j == 0 {
        scratch_option_extract_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        close scratch_option_array_two_holes::<T>(p, n, i, j, vs);
        assert nth(j, vs) == head(vs);
        assert vj == head(vs);
    } else {
        scratch_option_extract_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        close scratch_option_array_two_holes::<T>(p, n, i, j, vs);
        assert nth(i, vs) == nth(i - 1, tail(vs));
        assert nth(j, vs) == nth(j - 1, tail(vs));
    }
}

lem scratch_option_restore_two<T>(p: *T, n: usize, i: i32, j: i32,
                                  vi: option<T>, vj: option<T>)
    req scratch_option_array_two_holes::<T>(p, n, i, j, ?vs) &*&
        i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
        n * std::mem::size_of::<T>() <= isize::MAX &*&
        points_to_::<T>(p + i, vi) &*& points_to_::<T>(p + j, vj);
    ens scratch_option_array::<T>(p, n,
            scratch_replace_two::<T>(vs, i, j, vi, vj)) &*&
        (if i < 0 { points_to_::<T>(p + i, vi) } else { true }) &*&
        (if j < 0 { points_to_::<T>(p + j, vj) } else { true });
{
    open scratch_option_array_two_holes::<T>(p, n, i, j, vs);
    if n == 0 {
        scratch_replace_two_length::<T>(vs, i, j, vi, vj);
        close scratch_option_array::<T>(p, n,
            scratch_replace_two::<T>(vs, i, j, vi, vj));
    } else if i == 0 {
        scratch_option_restore_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        scratch_replace_two_length::<T>(vs, i, j, vi, vj);
        close scratch_option_array::<T>(p, n,
            scratch_replace_two::<T>(vs, i, j, vi, vj));
        assert nth(0, scratch_replace_two::<T>(vs, i, j, vi, vj)) == vi;
    } else if j == 0 {
        scratch_option_restore_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        scratch_replace_two_length::<T>(vs, i, j, vi, vj);
        close scratch_option_array::<T>(p, n,
            scratch_replace_two::<T>(vs, i, j, vi, vj));
        assert nth(0, scratch_replace_two::<T>(vs, i, j, vi, vj)) == vj;
    } else {
        scratch_option_restore_two::<T>(p + 1, n - 1, i - 1, j - 1, vi, vj);
        scratch_replace_two_length::<T>(vs, i, j, vi, vj);
        close scratch_option_array::<T>(p, n,
            scratch_replace_two::<T>(vs, i, j, vi, vj));
    }
}
@*/

// CASE_BEGIN scratch_option_extract_restore_old_values_and_frame
pub unsafe fn scratch_option_extract_restore_old_values_and_frame<T>(
    p: *mut T, n: usize, i: i32, j: i32, frame: *mut u32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    scratch_option_array::<T>(p, n, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    *frame |-> ?frame_value &*& <u32>.own(t, frame_value); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    scratch_option_array::<T>(p, n, vs) &*& *frame |-> frame_value &*&
    <u32>.own(t, frame_value); @*/
/*@ on_unwind_ens false; @*/
{
    //@ scratch_option_extract_two::<T>(p, n, i, j, nth(i, vs), nth(j, vs));
    //@ scratch_replace_two_old_values::<T>(vs, i, j);
    //@ scratch_option_restore_two::<T>(p, n, i, j, nth(i, vs), nth(j, vs));
}
// CASE_END scratch_option_extract_restore_old_values_and_frame

// CASE_BEGIN scratch_option_restore_current_values
pub unsafe fn scratch_option_restore_current_values<T>(p: *mut T, n: usize, i: i32, j: i32)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    scratch_option_array_two_holes::<T>(p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    points_to_::<T>(p + i, ?vi) &*& points_to_::<T>(p + j, ?vj); @*/
/*@ ens thread_token(t) &*& type_interp::<T>() &*&
    scratch_option_array::<T>(p, n,
        scratch_replace_two::<T>(vs, i, j, vi, vj)); @*/
/*@ on_unwind_ens false; @*/
{
    //@ scratch_option_restore_two::<T>(p, n, i, j, vi, vj);
}
// CASE_END scratch_option_restore_current_values

// This restoration-only fixture is given current physical slot resources by
// its caller. Its saved list retains the distinct old hole values; no write is
// performed or modeled in this body.
// CASE_BEGIN scratch_option_restore_concrete_u32_current_values
pub unsafe fn scratch_option_restore_concrete_u32_current_values(
    p: *mut u32, n: usize, i: i32, j: i32,
)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<u32>() &*&
    scratch_option_array_two_holes::<u32>(p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*&
    0 < std::mem::size_of::<u32>() &*&
    n * std::mem::size_of::<u32>() <= isize::MAX &*&
    nth(i, vs) == none &*& nth(j, vs) == some(73) &*&
    points_to_::<u32>(p + i, some(41)) &*&
    points_to_::<u32>(p + j, none); @*/
/*@ ens thread_token(t) &*& type_interp::<u32>() &*&
    scratch_option_array::<u32>(p, n,
        scratch_replace_two::<u32>(vs, i, j, some(41), none)); @*/
/*@ on_unwind_ens false; @*/
{
    //@ scratch_option_restore_two::<u32>(p, n, i, j, some(41), none);
}
// CASE_END scratch_option_restore_concrete_u32_current_values

// CASE_BEGIN scratch_option_duplicate_write_permission
pub unsafe fn scratch_option_duplicate_write_permission<T>(p: *mut T, n: usize,
                                                            i: i32, j: i32)
/*@ req scratch_option_array_two_holes::<T>(p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    points_to_::<T>(p + i, ?vi) &*& points_to_::<T>(p + j, ?vj); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ assert points_to_::<T>(p + i, vi) &*& points_to_::<T>(p + i, vi); // TARGET: a single option cell cannot supply two writable chunks
}
// CASE_END scratch_option_duplicate_write_permission

// CASE_BEGIN scratch_option_wrong_old_list_rejected
pub unsafe fn scratch_option_wrong_old_list_rejected<T>(p: *mut T, n: usize,
                                                         i: i32, j: i32)
/*@ req scratch_option_array_two_holes::<T>(p, n, i, j, ?vs) &*& n >= 2 &*&
    0 <= i &*& i < j &*& j < n &*& 0 < std::mem::size_of::<T>() &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    points_to_::<T>(p + i, ?vi) &*& points_to_::<T>(p + j, ?vj) &*&
    vi != nth(i, vs); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ scratch_option_restore_two::<T>(p, n, i, j, vi, vj);
    //@ assert scratch_replace_two::<T>(vs, i, j, vi, vj) == vs; // TARGET: changed option value cannot restore the saved list
}
// CASE_END scratch_option_wrong_old_list_rejected

// CASE_BEGIN scratch_option_does_not_create_owner
pub unsafe fn scratch_option_does_not_create_owner<T>(p: *mut T)
/*@ req thread_token(?t) &*& t == currentThread &*& type_interp::<T>() &*&
    scratch_option_array::<T>(p, 1, cons(some(?v), nil)); @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ open scratch_option_array::<T>(p, 1, cons(some(v), nil));
    //@ assert <T>.own(t, v); // TARGET: an initialized option cell does not imply value ownership
}
// CASE_END scratch_option_does_not_create_owner
