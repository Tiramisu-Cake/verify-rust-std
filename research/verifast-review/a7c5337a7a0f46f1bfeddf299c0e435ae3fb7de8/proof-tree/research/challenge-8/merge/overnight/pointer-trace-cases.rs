// SPDX-License-Identifier: Apache-2.0 OR MIT
// Complete arbitrary-length G2 pointer-trace projection for W1.
// This is a hand-written unsafe adapter, not the actual merge implementation.
// It reads only the two initialized Boolean decision buffers. It does not read
// source T values, copy values, call FnMut, or claim any source/destination
// access permission, ownership, unwind, or merge-safety theorem. ZST is outside
// this projection: stride is explicitly positive.

// CASE_BEGIN g2_pointer_trace_projection
// Type alias only: keep the terminal trace as a balanced tree of stock tuple-2
// products, avoiding local-ADT-generated Send/Sync/padding helper obligations.
// Leaf order: eight pointers (left, right, dst, left_rev, right_rev, dst_rev,
// left_end, right_end), two counts, odd-left choice, residual guard.
pub type G2PointerTrace<T> = (
    (
        ((*const T, *const T), (*mut T, *const T)),
        ((*const T, *mut T), (*const T, *const T)),
    ),
    ((usize, usize), (bool, bool)),
);

/*@
fix trace_source_pointer(p: pointer, i: i32, s: i32) -> pointer {
    if i == -1 {
        wrapping_pointer_offset(p, -s)
    } else {
        pointer_ctor(p.provenance, p.address + i * s, p.metadata)
    }
}

fix trace_destination_pointer(p: pointer, i: i32, s: i32) -> pointer {
    pointer_ctor(p.provenance, p.address + i * s, p.metadata)
}

fix trace_true_prefix(xs: list<bool>, k: usize) -> usize {
    match xs {
        nil => 0,
        cons(h, tail) => if k == 0 {
            0
        } else {
            (if h { 1 } else { 0 }) + trace_true_prefix(tail, k - 1)
        }
    }
}

lem trace_source_nonnegative_index(p: pointer, i: i32, s: i32)
    req 0 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*& p.address + i * s <= usize::MAX;
    ens ptr_add(p, i * s) == trace_source_pointer(p, i, s);
{
    assert trace_source_pointer(p, i, s) ==
        pointer_ctor(p.provenance, p.address + i * s, p.metadata);
}

lem trace_destination_nonnegative_index(p: pointer, i: i32, s: i32)
    req 0 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*& p.address + i * s <= usize::MAX;
    ens ptr_add(p, i * s) == trace_destination_pointer(p, i, s);
{
    assert trace_destination_pointer(p, i, s) ==
        pointer_ctor(p.provenance, p.address + i * s, p.metadata);
}

lem trace_true_prefix_zero(xs: list<bool>)
    req true;
    ens trace_true_prefix(xs, 0) == 0;
{
    match xs {
        nil => {
            assert trace_true_prefix(xs, 0) == 0;
        }
        cons(h, tail) => {
            assert trace_true_prefix(xs, 0) == 0;
        }
    }
}

lem trace_true_prefix_step(xs: list<bool>, k: usize)
    req 0 <= k &*& k < length(xs);
    ens trace_true_prefix(xs, k + 1) ==
        trace_true_prefix(xs, k) + (if nth(k, xs) { 1 } else { 0 });
{
    match xs {
        nil => {
            assert false;
        }
        cons(h, tail) => {
            if k == 0 {
                trace_true_prefix_zero(tail);
                assert trace_true_prefix(xs, 1) == (if h { 1 } else { 0 });
                assert trace_true_prefix(xs, 0) == 0;
                assert nth(0, xs) == h;
            } else {
                assert 0 < k;
                assert k - 1 < length(tail);
                trace_true_prefix_step(tail, k - 1);
                assert trace_true_prefix(xs, k + 1) ==
                    (if h { 1 } else { 0 }) + trace_true_prefix(tail, k);
                assert trace_true_prefix(xs, k) ==
                    (if h { 1 } else { 0 }) + trace_true_prefix(tail, k - 1);
                assert nth(k, xs) == nth(k - 1, tail);
            }
            assert trace_true_prefix(xs, k + 1) ==
                trace_true_prefix(xs, k) + (if nth(k, xs) { 1 } else { 0 });
        }
    }
}

lem trace_source_reverse_step(p: pointer, i: i32, s: i32, step: bool)
    req 0 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*& p.address + i * s <= usize::MAX;
    ens wrapping_pointer_offset(
            trace_source_pointer(p, i, s),
            -(if step { 1 } else { 0 }) * s) ==
        trace_source_pointer(p, i - (if step { 1 } else { 0 }), s);
{
    if step {
        if i == 0 {
            assert trace_source_pointer(p, 0, s) ==
                pointer_ctor(p.provenance, p.address, p.metadata);
            assert trace_source_pointer(p, -1, s) == wrapping_pointer_offset(p, -s);
            if p.address < s {
                assert p.address - s < 0;
                assert 0 <= p.address - s + usize::MAX + 1;
                assert p.address - s + usize::MAX + 1 <= usize::MAX;
                assert wrapping_pointer_offset(p, -s).address ==
                    p.address - s + usize::MAX + 1;
                assert wrapping_pointer_offset(
                    trace_source_pointer(p, 0, s), -s).address ==
                    p.address - s + usize::MAX + 1;
            } else {
                assert 0 <= p.address - s;
                assert p.address - s <= usize::MAX;
                assert wrapping_pointer_offset(p, -s).address == p.address - s;
                assert wrapping_pointer_offset(
                    trace_source_pointer(p, 0, s), -s).address ==
                    p.address - s;
            }
            assert wrapping_pointer_offset(
                trace_source_pointer(p, 0, s), -s) ==
                trace_source_pointer(p, -1, s);
        } else {
            assert 0 < i;
            assert 0 <= i - 1;
            mul_mono_l(0, i - 1, s);
            mul_mono_l(i - 1, i, s);
            assert trace_source_pointer(p, i, s) ==
                pointer_ctor(p.provenance, p.address + i * s, p.metadata);
            assert trace_source_pointer(p, i - 1, s) ==
                pointer_ctor(p.provenance, p.address + (i - 1) * s, p.metadata);
            assert p.address + (i - 1) * s == p.address + i * s - s;
            assert 0 <= p.address + i * s - s;
            assert p.address + i * s - s <= usize::MAX;
            assert wrapping_pointer_offset(
                trace_source_pointer(p, i, s), -s).address ==
                p.address + i * s - s;
            assert wrapping_pointer_offset(
                trace_source_pointer(p, i, s), -s) ==
                trace_source_pointer(p, i - 1, s);
        }
    } else {
        mul_mono_l(0, i, s);
        assert 0 <= p.address + i * s;
        assert p.address + i * s <= usize::MAX;
        assert wrapping_pointer_offset(trace_source_pointer(p, i, s), 0) ==
            trace_source_pointer(p, i, s);
        assert trace_source_pointer(p, i, s) ==
            trace_source_pointer(p, i, s);
    }
}

lem trace_source_forward_step(p: pointer, i: i32, s: i32, step: bool)
    req 0 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*&
        p.address + (i + (if step { 1 } else { 0 })) * s <= usize::MAX;
    ens ptr_add(trace_source_pointer(p, i, s),
            (if step { 1 } else { 0 }) * s) ==
        trace_source_pointer(p, i + (if step { 1 } else { 0 }), s);
{
    if step {
        mul_mono_l(0, i, s);
        mul_mono_l(i, i + 1, s);
        assert trace_source_pointer(p, i, s) ==
            pointer_ctor(p.provenance, p.address + i * s, p.metadata);
        assert trace_source_pointer(p, i + 1, s) ==
            pointer_ctor(p.provenance, p.address + (i + 1) * s, p.metadata);
    } else {
        mul_mono_l(0, i, s);
        assert trace_source_pointer(p, i, s) == trace_source_pointer(p, i, s);
    }
}

lem trace_source_terminal_step(p: pointer, i: i32, s: i32)
    req -1 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*& p.address <= usize::MAX &*&
        p.address + (i + 1) * s <= usize::MAX;
    ens wrapping_pointer_offset(trace_source_pointer(p, i, s), s) ==
        trace_source_pointer(p, i + 1, s);
{
    if i == -1 {
        assert trace_source_pointer(p, -1, s) == wrapping_pointer_offset(p, -s);
        assert trace_source_pointer(p, 0, s) ==
            pointer_ctor(p.provenance, p.address, p.metadata);
        if p.address < s {
            assert wrapping_pointer_offset(p, -s).address == p.address - s + usize::MAX + 1;
            assert wrapping_pointer_offset(
                wrapping_pointer_offset(p, -s), s).address == p.address;
            assert wrapping_pointer_offset(
                trace_source_pointer(p, -1, s), s) == trace_source_pointer(p, 0, s);
        } else {
            assert wrapping_pointer_offset(p, -s).address == p.address - s;
            assert wrapping_pointer_offset(
                wrapping_pointer_offset(p, -s), s).address == p.address;
            assert wrapping_pointer_offset(
                trace_source_pointer(p, -1, s), s) == trace_source_pointer(p, 0, s);
        }
    } else {
        mul_mono_l(0, i, s);
        mul_mono_l(i, i + 1, s);
        assert trace_source_pointer(p, i, s) ==
            pointer_ctor(p.provenance, p.address + i * s, p.metadata);
        assert trace_source_pointer(p, i + 1, s) ==
            pointer_ctor(p.provenance, p.address + (i + 1) * s, p.metadata);
        assert wrapping_pointer_offset(
            trace_source_pointer(p, i, s), s).address == p.address + (i + 1) * s;
        assert wrapping_pointer_offset(
            trace_source_pointer(p, i, s), s) == trace_source_pointer(p, i + 1, s);
    }
}

lem trace_bool_choice_open(p: *const bool, values: list<bool>, count: usize, k: usize)
    req [?f]p[..count] |-> values &*& count == length(values) &*&
        0 <= k &*& k < count;
    ens [f]p[..k] |-> take(k, values) &*&
        [f](*(p + k) |-> nth(k, values)) &*&
        [f]p[k + 1..count] |-> drop(k + 1, values);
{
    array_split(p, k);
    array_split(p + k, 1);
    drop_n_plus_one(k, values);
    assert take(1, drop(k, values)) == cons(nth(k, values), nil);
    open [f]array::<bool>(p + k, 1, cons(nth(k, values), nil));
    open [f]array::<bool>(p + k + 1, 0, nil);
}

lem trace_bool_choice_close(p: *const bool, values: list<bool>, count: usize, k: usize)
    req [?f]p[..k] |-> take(k, values) &*&
        [f](*(p + k) |-> nth(k, values)) &*&
        [f]p[k + 1..count] |-> drop(k + 1, values) &*&
        count == length(values) &*& 0 <= k &*& k < count;
    ens [f]p[..count] |-> values;
{
    assert pointer_within_limits(p + k + 1) == true;
    close [f]array::<bool>(p + k + 1, 0, nil);
    close [f]array::<bool>(p + k, 1, cons(nth(k, values), nil));
    array_join(p + k);
    drop_n_plus_one(k, values);
    append_take_drop_n(values, k);
    array_join(p);
}

lem trace_destination_forward_step(p: pointer, i: i32, s: i32, step: bool)
    req 0 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*&
        p.address + (i + (if step { 1 } else { 0 })) * s <= usize::MAX;
    ens ptr_add(trace_destination_pointer(p, i, s),
            (if step { 1 } else { 0 }) * s) ==
        trace_destination_pointer(p, i + (if step { 1 } else { 0 }), s);
{
    if step {
        mul_mono_l(0, i, s);
        mul_mono_l(i, i + 1, s);
        assert trace_destination_pointer(p, i, s) ==
            pointer_ctor(p.provenance, p.address + i * s, p.metadata);
        assert trace_destination_pointer(p, i + 1, s) ==
            pointer_ctor(p.provenance, p.address + (i + 1) * s, p.metadata);
    } else {
        mul_mono_l(0, i, s);
        assert trace_destination_pointer(p, i, s) ==
            trace_destination_pointer(p, i, s);
    }
}

lem trace_destination_reverse_step(p: pointer, i: i32, s: i32)
    req 1 <= i &*& 0 < s &*& s <= usize::MAX &*&
        0 <= p.address &*& p.address + i * s <= usize::MAX;
    ens ptr_add(trace_destination_pointer(p, i, s), -s) ==
        trace_destination_pointer(p, i - 1, s);
{
    mul_mono_l(0, i - 1, s);
    mul_mono_l(i - 1, i, s);
    assert trace_destination_pointer(p, i, s) ==
        pointer_ctor(p.provenance, p.address + i * s, p.metadata);
    assert trace_destination_pointer(p, i - 1, s) ==
        pointer_ctor(p.provenance, p.address + (i - 1) * s, p.metadata);
}

lem trace_stride_order(i: usize, j: usize, s: usize)
    req 0 <= i &*& 0 <= j &*& 0 < s &*& s <= usize::MAX;
    ens (i * s < j * s) == (i < j) &*&
        (i * s == j * s) == (i == j);
{
    if i < j {
        mul_mono_l(i + 1, j, s);
    } else if j < i {
        mul_mono_l(j + 1, i, s);
    }
}

lem g2_trace_step(m: usize, n: usize, e: usize, k: usize,
        a: usize, d: usize, up: bool, down: bool)
    req 1 <= m &*& 0 <= n &*& n == 2 * m + e &*&
        0 <= e &*& (e == 0 || e == 1) &*& 0 <= k &*& k < m &*&
        0 <= a &*& a <= k &*& 0 <= d &*& d <= k;
    ens 0 <= a &*& a < n &*&
        0 <= m + k - a &*& m + k - a < n &*&
        0 <= m - 1 - k + d &*& m - 1 - k + d < n &*&
        0 <= n - 1 - d &*& n - 1 - d < n &*&
        0 <= k &*& k < n &*& 0 <= n - 1 - k &*& n - 1 - k < n &*&
        1 <= n - 1 - k &*&
        0 <= a + (if up { 1 } else { 0 }) &*&
        a + (if up { 1 } else { 0 }) <= k + 1 &*&
        0 <= d + (if down { 1 } else { 0 }) &*&
        d + (if down { 1 } else { 0 }) <= k + 1 &*&
        0 <= m + (k + 1) - (a + (if up { 1 } else { 0 })) &*&
        m + (k + 1) - (a + (if up { 1 } else { 0 })) <= n &*&
        -1 <= m - 1 - (k + 1) + (d + (if down { 1 } else { 0 })) &*&
        m - 1 - (k + 1) + (d + (if down { 1 } else { 0 })) < n &*&
        0 <= n - 1 - (d + (if down { 1 } else { 0 })) &*&
        n - 1 - (d + (if down { 1 } else { 0 })) < n &*&
        0 <= k + 1 &*& k + 1 <= n &*&
        0 <= n - 1 - (k + 1) &*& n - 1 - (k + 1) < n;
{
    assert 0 <= a &*& a <= k;
    assert 0 <= d &*& d <= k;
    assert 0 <= m - 1 - k + d;
    assert m - 1 - k + d <= m - 1;
    assert 0 <= n - 1 - d;
    assert 0 <= n - 1 - k;
    assert k + 1 <= m;
    if up {
        assert a + 1 <= k + 1;
    } else {
        assert a <= k + 1;
    }
    if down {
        assert d + 1 <= k + 1;
    } else {
        assert d <= k + 1;
    }
    assert m + k - a + (if up { 0 } else { 1 }) ==
        m + (k + 1) - (a + (if up { 1 } else { 0 }));
    assert m - 1 - k + d - (if down { 0 } else { 1 }) ==
        m - 1 - (k + 1) + (d + (if down { 1 } else { 0 }));
}
@*/

pub unsafe fn g2_pointer_trace_projection<T>(
    src: *const T,
    dst_base: *mut T,
    n: usize,
    m: usize,
    e: usize,
    up_choices: *const bool,
    down_choices: *const bool,
) -> G2PointerTrace<T>
/*@
req 1 <= m &*& n == 2 * m + e &*& (e == 0 || e == 1) &*&
    2 <= n &*& 0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= usize::MAX &*&
    n * std::mem::size_of::<T>() <= isize::MAX &*&
    0 <= (src as pointer).address &*& 0 <= (dst_base as pointer).address &*&
    (src as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    (dst_base as pointer).address + n * std::mem::size_of::<T>() <= usize::MAX &*&
    pointer_within_limits(src) == true &*&
    pointer_within_limits(src + n) == true &*&
    pointer_within_limits(dst_base) == true &*&
    pointer_within_limits(dst_base + n) == true &*&
    [?fu]up_choices[..m] |-> ?up_values &*&
    [?fd]down_choices[..m] |-> ?down_values;
@*//*@
ens (((result.1).0).0) == trace_true_prefix(up_values, m) &*&
    (((result.1).0).1) == trace_true_prefix(down_values, m) &*&
    ((result.1).0).0 <= m &*& ((result.1).0).1 <= m &*&
    ((((result.0).0).0).0) as pointer == trace_source_pointer(
        src as pointer, ((result.1).0).0 +
            (if ((result.1).1).0 { 1 } else { 0 }),
        std::mem::size_of::<T>()) &*&
    ((((result.0).0).0).1) as pointer == trace_source_pointer(
        src as pointer, 2 * m - ((result.1).0).0 +
            (if e == 1 && !((result.1).1).0 { 1 } else { 0 }),
        std::mem::size_of::<T>()) &*&
    (((result.0).0).1).1 as pointer == trace_source_pointer(
        src as pointer, ((result.1).0).1 - 1, std::mem::size_of::<T>()) &*&
    (((result.0).1).0).0 as pointer == trace_source_pointer(
        src as pointer, n - 1 - ((result.1).0).1, std::mem::size_of::<T>()) &*&
    (((result.0).0).1).0 as pointer == trace_destination_pointer(
        dst_base as pointer, m, std::mem::size_of::<T>()) &*&
    (((result.0).1).0).1 as pointer == trace_destination_pointer(
        dst_base as pointer, n - 1 - m, std::mem::size_of::<T>()) &*&
    (((result.0).1).1).0 as pointer == trace_source_pointer(
        src as pointer, ((result.1).0).1, std::mem::size_of::<T>()) &*&
    (((result.0).1).1).1 as pointer == trace_source_pointer(
        src as pointer, n - ((result.1).0).1, std::mem::size_of::<T>()) &*&
    ((result.1).1).0 ==
        (e == 1 && ((result.1).0).0 < ((result.1).0).1) &*&
    ((result.1).1).1 ==
        (((result.1).0).0 +
            (if ((result.1).1).0 { 1 } else { 0 }) != ((result.1).0).1 ||
         2 * m - ((result.1).0).0 +
            (if e == 1 && !((result.1).1).0 { 1 } else { 0 }) !=
                n - ((result.1).0).1) &*&
    [fu]up_choices[..m] |-> up_values &*&
    [fd]down_choices[..m] |-> down_values;
@*//*@
on_unwind_ens false;
@*/
{
    //@ let s = std::mem::size_of::<T>();
    //@ assert m == length(up_values);
    //@ assert m == length(down_values);
    //@ mul_mono_l(0, m, s);
    //@ mul_mono_l(m, n, s);
    //@ mul_mono_l(0, m - 1, s);
    //@ mul_mono_l(m - 1, n, s);
    //@ mul_mono_l(0, n - 1, s);
    //@ mul_mono_l(n - 1, n, s);
    //@ trace_source_nonnegative_index(src as pointer, 0, s);
    //@ trace_source_nonnegative_index(src as pointer, m, s);
    //@ trace_source_nonnegative_index(src as pointer, m - 1, s);
    //@ trace_source_nonnegative_index(src as pointer, n - 1, s);
    //@ trace_destination_nonnegative_index(dst_base as pointer, 0, s);
    //@ trace_destination_nonnegative_index(dst_base as pointer, n - 1, s);

    let mut left = src;
    let mut right = unsafe { src.add(m) };
    let mut dst = dst_base;
    let mut left_rev = unsafe { src.add(m - 1) };
    let mut right_rev = unsafe { src.add(n - 1) };
    let mut dst_rev = unsafe { dst_base.add(n - 1) };

    let mut k = 0usize;
    let mut a = 0usize;
    let mut d = 0usize;

    //@ trace_true_prefix_zero(up_values);
    //@ trace_true_prefix_zero(down_values);

    loop {
    /*@ inv 1 <= m &*& n == 2 * m + e &*& (e == 0 || e == 1) &*&
            0 <= k &*& 0 <= a &*& 0 <= d &*&
            k <= m &*& a <= k &*& d <= k &*&
            a == trace_true_prefix(up_values, k) &*&
            d == trace_true_prefix(down_values, k) &*&
            left as pointer == trace_source_pointer(src as pointer, a, std::mem::size_of::<T>()) &*&
            right as pointer == trace_source_pointer(src as pointer, m + k - a, std::mem::size_of::<T>()) &*&
            left_rev as pointer == trace_source_pointer(src as pointer, m - 1 - k + d, std::mem::size_of::<T>()) &*&
            right_rev as pointer == trace_source_pointer(src as pointer, n - 1 - d, std::mem::size_of::<T>()) &*&
            dst as pointer == trace_destination_pointer(dst_base as pointer, k, std::mem::size_of::<T>()) &*&
            dst_rev as pointer == trace_destination_pointer(dst_base as pointer, n - 1 - k, std::mem::size_of::<T>()) &*&
            lifetime_token(func_lft) &*&
            [fu]up_choices[..m] |-> up_values &*&
            [fd]down_choices[..m] |-> down_values;
        @*/
        if k >= m {
            break;
        }
        // Check the six operation indices before this pair of pointer steps.
        //@ assert 0 <= a && a < n;
        //@ assert 0 <= m + k - a && m + k - a < n;
        //@ assert 0 <= m - 1 - k + d && m - 1 - k + d < n;
        //@ assert 0 <= n - 1 - d && n - 1 - d < n;
        //@ assert 0 <= k && k < n;
        //@ assert 0 <= n - 1 - k && n - 1 - k < n;
        //@ assert 1 <= n - 1 - k;

        //@ trace_bool_choice_open(up_choices, up_values, m, k);
        let up = unsafe { up_choices.add(k).read() };
        //@ assert up == nth(k, up_values);
        //@ trace_bool_choice_close(up_choices, up_values, m, k);
        //@ trace_bool_choice_open(down_choices, down_values, m, k);
        let down = unsafe { down_choices.add(k).read() };
        //@ assert down == nth(k, down_values);
        //@ trace_bool_choice_close(down_choices, down_values, m, k);

        //@ g2_trace_step(m, n, e, k, a, d, up, down);

        //@ mul_mono_l(0, a, s);
        //@ mul_mono_l(a, n, s);
        //@ mul_mono_l(0, m + k - a, s);
        //@ mul_mono_l(m + k - a, n, s);
        //@ mul_mono_l(0, m - 1 - k + d, s);
        //@ mul_mono_l(m - 1 - k + d, n, s);
        //@ mul_mono_l(0, n - 1 - d, s);
        //@ mul_mono_l(n - 1 - d, n, s);
        //@ mul_mono_l(0, k, s);
        //@ mul_mono_l(k, n, s);
        //@ mul_mono_l(0, n - 1 - k, s);
        //@ mul_mono_l(n - 1 - k, n, s);
        //@ mul_mono_l(0, a + (if up { 1 } else { 0 }), s);
        //@ mul_mono_l(a + (if up { 1 } else { 0 }), n, s);
        //@ mul_mono_l(0, m + k - a + (if up { 0 } else { 1 }), s);
        //@ mul_mono_l(m + k - a + (if up { 0 } else { 1 }), n, s);
        //@ mul_mono_l(0, k + 1, s);
        //@ mul_mono_l(k + 1, n, s);

        //@ trace_true_prefix_step(up_values, k);
        //@ trace_true_prefix_step(down_values, k);
        //@ trace_source_forward_step(src as pointer, a, s, up);
        //@ trace_source_forward_step(src as pointer, m + k - a, s, !up);
        //@ trace_destination_forward_step(dst_base as pointer, k, s, true);
        right = unsafe { right.add((!up) as usize) };
        left = unsafe { left.add(up as usize) };
        dst = unsafe { dst.add(1) };

        //@ trace_source_reverse_step(src as pointer, n - 1 - d, s, down);
        //@ trace_source_reverse_step(src as pointer, m - 1 - k + d, s, !down);
        //@ trace_destination_reverse_step(dst_base as pointer, n - 1 - k, s);
        right_rev = right_rev.wrapping_sub(down as usize);
        left_rev = left_rev.wrapping_sub((!down) as usize);
        dst_rev = unsafe { dst_rev.sub(1) };

        a += up as usize;
        d += down as usize;
        k += 1;
    }

    // Here k=m; the terminal left reverse index can be -1. Its numerical
    // address may wrap, so the bridge is source provenance plus modular offset.
    //@ mul_mono_l(0, d, s);
    //@ mul_mono_l(d, n, s);
    //@ mul_mono_l(0, n - d, s);
    //@ mul_mono_l(n - d, n, s);
    //@ trace_source_terminal_step(src as pointer, d - 1, s);
    //@ trace_source_terminal_step(src as pointer, n - 1 - d, s);
    let left_end = left_rev.wrapping_add(1);
    let right_end = right_rev.wrapping_add(1);

    let odd_left_advance = if e == 1 {
        //@ trace_stride_order(a, d, s);
        //@ assert (left < left_end) == (a < d);
        left < left_end
    } else {
        false
    };
    if e == 1 {
        if odd_left_advance {
            //@ assert a + 1 <= d;
            //@ assert a + 1 <= m;
        } else {
            //@ assert d <= a;
            //@ assert 2 * m - a + 1 <= n;
        }
        //@ mul_mono_l(0, a + (if odd_left_advance { 1 } else { 0 }), s);
        //@ mul_mono_l(a + (if odd_left_advance { 1 } else { 0 }), n, s);
        //@ mul_mono_l(0, 2 * m - a + (if odd_left_advance { 0 } else { 1 }), s);
        //@ mul_mono_l(2 * m - a + (if odd_left_advance { 0 } else { 1 }), n, s);
        //@ trace_source_forward_step(src as pointer, a, s, odd_left_advance);
        //@ trace_source_forward_step(src as pointer, 2 * m - a, s, !odd_left_advance);
        left = unsafe { left.add(odd_left_advance as usize) };
        right = unsafe { right.add((!odd_left_advance) as usize) };
    }

    /*@ trace_stride_order(a + (if odd_left_advance { 1 } else { 0 }), d, s); @*/
    /*@ trace_stride_order(2 * m - a + (if e == 1 && !odd_left_advance { 1 } else { 0 }), n - d, s); @*/
    /*@ assert (left == left_end) == (a + (if odd_left_advance { 1 } else { 0 }) == d); @*/
    /*@ assert (right == right_end) == (2 * m - a + (if e == 1 && !odd_left_advance { 1 } else { 0 }) == n - d); @*/
    let residual_guard = left != left_end || right != right_end;
    (
        (( (left, right), (dst, left_rev) ),
         ( (right_rev, dst_rev), (left_end, right_end) )),
        ((a, d), (odd_left_advance, residual_guard)),
    )
}
// CASE_END g2_pointer_trace_projection
