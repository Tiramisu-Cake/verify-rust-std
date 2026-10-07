// SPDX-License-Identifier: Apache-2.0 OR MIT
// Partial pointer/index projections; never execute as ordinary programs.
// No comparator, references, copies, loop, or whole-merge refinement claim.

// CASE_BEGIN g2_steps
/*@
lem g2_step(m: usize, e: usize, k: usize, a: usize, d: usize, up: bool, down: bool)
    req 1 <= m &*& (e == 0 || e == 1) &*& 0 <= a &*& a <= k &*& 0 <= d &*& d <= k &*& k < m;
    ens 0 <= a &*& a < 2 * m + e &*&
        0 <= m + k - a &*& m + k - a < 2 * m + e &*&
        0 <= m - 1 - k + d &*& m - 1 - k + d < 2 * m + e &*&
        0 <= 2 * m + e - 1 - d &*& 2 * m + e - 1 - d < 2 * m + e &*&
        1 <= 2 * m + e - 1 - k &*& 0 <= 2 * m + e - 2 - k &*&
        m + k - a + (if up { 0 } else { 1 }) == m + (k + 1) - (a + (if up { 1 } else { 0 })) &*&
        m - 1 - k + d - (if down { 0 } else { 1 }) == m - 1 - (k + 1) + (d + (if down { 1 } else { 0 })) &*&
        2 * m + e - 1 - d - (if down { 1 } else { 0 }) == 2 * m + e - 1 - (d + (if down { 1 } else { 0 })) &*&
        -1 <= m - 1 - k + d - (if down { 0 } else { 1 }) &*&
        a + (if up { 1 } else { 0 }) <= k + 1 &*& d + (if down { 1 } else { 0 }) <= k + 1;
{
    if up {
        assert m + k - a == m + (k + 1) - (a + 1);
    } else {
        assert m + k - a + 1 == m + (k + 1) - a;
    }
    if down {
        assert m - 1 - k + d == m - 1 - (k + 1) + (d + 1);
    } else {
        assert m - 1 - k + d - 1 == m - 1 - (k + 1) + d;
    }
}

lem g2_terminal(m: usize, e: usize, a: usize, d: usize, h: bool)
    req 1 <= m &*& (e == 0 || e == 1) &*& 0 <= a &*& a <= m &*& 0 <= d &*& d <= m;
    ens -1 <= d - 1 &*& d - 1 < m &*& 0 <= d &*& d <= m &*&
        (d - 1) + 1 == d &*& (2 * m + e - 1 - d) + 1 == 2 * m + e - d &*&
        (if e == 0 {
            ((a == d && 2 * m - a == 2 * m - d) == (a == d))
        } else {
            (a < 2 * m + e && 2 * m - a < 2 * m + e &&
             a + (if h { 1 } else { 0 }) <= 2 * m + e &&
             2 * m - a + (if h { 0 } else { 1 }) <= 2 * m + e)
        });
{
    if e == 0 {
        assert (a == d && 2 * m - a == 2 * m - d) == (a == d);
    } else {
        assert e == 1;
        if h {
            assert a + 1 <= 2 * m + e;
        } else {
            assert 2 * m - a + 1 <= 2 * m + e;
        }
    }
}
@*/
// CASE_END g2_steps

// CASE_BEGIN init_const
pub unsafe fn init_const<T>(base: *const T, n: usize, i: usize) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*& i <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + i &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    result as usize == base as usize + i * std::mem::size_of::<T>();
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    let result = base.add(i);
    result
}
// CASE_END init_const

// CASE_BEGIN init_mut
pub unsafe fn init_mut<T>(base: *mut T, n: usize, i: usize) -> *mut T
/*@
req 0 < std::mem::size_of::<T>() &*& i <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + i &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    result as usize == base as usize + i * std::mem::size_of::<T>();
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    let result = base.add(i);
    result
}
// CASE_END init_mut

// CASE_BEGIN destination_up
pub unsafe fn destination_up<T>(base: *mut T, n: usize, i: usize) -> *mut T
/*@
req 0 < std::mem::size_of::<T>() &*& i < n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + (i + 1) &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i + 1, n, std::mem::size_of::<T>());
    let mut dst = base.add(i);
    dst = dst.add(1);
    dst
}
// CASE_END destination_up

// CASE_BEGIN forward_left
pub unsafe fn forward_left<T>(base: *const T, n: usize, i: usize, is_l: bool) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*& i < n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + (i + (if is_l { 1 } else { 0 })) &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i + 1, n, std::mem::size_of::<T>());
    let mut left_src = base.add(i);
    left_src = left_src.add(is_l as usize);
    left_src
}
// CASE_END forward_left

// CASE_BEGIN forward_right
pub unsafe fn forward_right<T>(base: *const T, n: usize, i: usize, is_l: bool) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*& i < n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + (i + (if is_l { 0 } else { 1 })) &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i + 1, n, std::mem::size_of::<T>());
    let mut right_src = base.add(i);
    right_src = right_src.add(!is_l as usize);
    right_src
}
// CASE_END forward_right

// CASE_BEGIN destination_down
pub unsafe fn destination_down<T>(base: *mut T, n: usize, i: usize) -> *mut T
/*@
req 0 < std::mem::size_of::<T>() &*& 1 <= i &*& i < n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens result == base + (i - 1) &*& pointer_within_limits(result) == true &*&
    (result as pointer).provenance == (base as pointer).provenance;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i - 1, std::mem::size_of::<T>());
    //@ mul_mono_l(i, n, std::mem::size_of::<T>());
    let mut dst = base.add(i);
    dst = dst.sub(1);
    dst
}
// CASE_END destination_down

// CASE_BEGIN pointer_order
/*@
lem stride_order(i: usize, j: usize, s: usize)
    req 0 < s;
    ens (i * s < j * s) == (i < j) &*& (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}
@*/
pub unsafe fn pointer_order<T>(base: *const T, left: *const T, left_end: *const T, i: usize, j: usize) -> bool
/*@
req 0 < std::mem::size_of::<T>() &*& left == base + i &*& left_end == base + j &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(left) == true &*&
    pointer_within_limits(left_end) == true;
@*//*@
ens result == (i < j);
@*//*@
on_unwind_ens false;
@*/
{
    //@ stride_order(i, j, std::mem::size_of::<T>());
    let left_nonempty = left < left_end;
    left_nonempty
}
// CASE_END pointer_order

// CASE_BEGIN pointer_guard
/*@
lem stride_equal(i: usize, j: usize, s: usize)
    req 0 < s;
    ens (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}
@*/
pub unsafe fn pointer_guard<T>(base: *const T, left: *const T, left_end: *const T,
    right: *const T, right_end: *const T, i: usize, j: usize, r: usize, t: usize) -> bool
/*@
req 0 < std::mem::size_of::<T>() &*& left == base + i &*& left_end == base + j &*&
    right == base + r &*& right_end == base + t &*& pointer_within_limits(base) == true &*&
    pointer_within_limits(left) == true &*& pointer_within_limits(left_end) == true &*&
    pointer_within_limits(right) == true &*& pointer_within_limits(right_end) == true;
@*//*@
ens result == (i != j || r != t);
@*//*@
on_unwind_ens false;
@*/
{
    //@ stride_equal(i, j, std::mem::size_of::<T>());
    //@ stride_equal(r, t, std::mem::size_of::<T>());
    left != left_end || right != right_end
}
// CASE_END pointer_guard

// CASE_BEGIN wrapping_down
pub fn wrapping_down<T>(base: *const T, is_l: bool) -> *const T
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let mut right_src = base;
    right_src = right_src.wrapping_sub(is_l as usize);
    right_src
}
// CASE_END wrapping_down

// CASE_BEGIN wrapping_end
pub fn wrapping_end<T>(left_rev: *const T) -> *const T
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    let left_end = left_rev.wrapping_add(1);
    left_end
}
// CASE_END wrapping_end

// CASE_BEGIN wrapping_reentry
pub unsafe fn wrapping_reentry<T>(base: *const T) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*& pointer_within_limits(base) == true;
@*//*@
ens result == base &*& (result as pointer).provenance == (base as pointer).provenance;
@*//*@
on_unwind_ens false;
@*/
{
    let left_rev = base.wrapping_sub(1);
    let left_end = left_rev.wrapping_add(1);
    left_end
}
// CASE_END wrapping_reentry

// CASE_BEGIN wrapped_read
pub unsafe fn wrapped_read(base: *const u8) -> u8
/*@
req *base |-> ?stored_value;
@*//*@
ens *base |-> stored_value;
@*//*@
on_unwind_ens false;
@*/
{
    let bad = base.wrapping_sub(1);
    let value = *bad; // TARGET_NEGATIVE missing points_to at wrapped -1
    value
}
// CASE_END wrapped_read

// CASE_BEGIN wrong_cursor
// EXPECT_ERROR {"stage":"verifast","predicate":"ptr_add_(ptr_add_(base, i, T_typeid), 1, T_typeid) = ptr_add_(base, (i + 2), T_typeid)","line":"TARGET","column_start":23,"column_end":25}
pub unsafe fn wrong_cursor<T>(base: *const T, n: usize, i: usize) -> *const T
/*@
req 0 < std::mem::size_of::<T>() &*& i + 2 <= n &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    pointer_within_limits(base) == true &*& pointer_within_limits(base + n) == true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    //@ mul_mono_l(0, i, std::mem::size_of::<T>());
    //@ mul_mono_l(i + 2, n, std::mem::size_of::<T>());
    let current = base.add(i);
    let result = current.add(1);
    //@ assert result == base + (i + 2); // TARGET_NEGATIVE wrong step
    result
}
// CASE_END wrong_cursor

// CASE_BEGIN address_index
// EXPECT_ERROR {"stage":"verifast","predicate":"i = j","line":"TARGET","column_start":18,"column_end":20}
pub unsafe fn address_index<T>(left: *const T, right: *const T, i: usize, j: usize)
/*@
req 0 < std::mem::size_of::<T>() &*& left as usize == right as usize;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert i == j; // TARGET_NEGATIVE absent base/index correspondence
}
// CASE_END address_index
