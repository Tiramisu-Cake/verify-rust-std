// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated admission diagnostics for the G2 trace entry context and tuple return.
// These cases do not replace or weaken g2_pointer_trace_projection.

// CASE_BEGIN trace_generic_entry_domain
pub unsafe fn trace_generic_entry_domain<T>(
    src: *const T,
    dst_base: *mut T,
    n: usize,
    m: usize,
    e: usize,
    up_choices: *const bool,
    down_choices: *const bool,
) -> ()
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
ens m == length(up_values) &*& m == length(down_values) &*&
    [fu]up_choices[..m] |-> up_values &*&
    [fd]down_choices[..m] |-> down_values;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert m == length(up_values);
    //@ assert m == length(down_values);
}
// CASE_END trace_generic_entry_domain

// CASE_BEGIN trace_u32_entry_domain
pub unsafe fn trace_u32_entry_domain(
    src: *const u32,
    dst_base: *mut u32,
    n: usize,
    m: usize,
    e: usize,
    up_choices: *const bool,
    down_choices: *const bool,
) -> ()
/*@
req n == 2 &*& m == 1 &*& e == 0 &*&
    2 <= n &*& 0 < std::mem::size_of::<u32>() &*&
    std::mem::size_of::<u32>() <= usize::MAX &*&
    n * std::mem::size_of::<u32>() <= isize::MAX &*&
    0 < (src as pointer).address &*& 0 < (dst_base as pointer).address &*&
    (src as pointer).address % std::mem::align_of::<u32>() == 0 &*&
    (dst_base as pointer).address % std::mem::align_of::<u32>() == 0 &*&
    (src as pointer).address + n * std::mem::size_of::<u32>() <= usize::MAX &*&
    (dst_base as pointer).address + n * std::mem::size_of::<u32>() <= usize::MAX &*&
    pointer_within_limits(src) == true &*&
    pointer_within_limits(src + n) == true &*&
    pointer_within_limits(dst_base) == true &*&
    pointer_within_limits(dst_base + n) == true &*&
    [?fu]up_choices[..m] |-> ?up_values &*&
    [?fd]down_choices[..m] |-> ?down_values;
@*//*@
ens length(up_values) == 1 &*& length(down_values) == 1 &*&
    [fu]up_choices[..m] |-> up_values &*&
    [fd]down_choices[..m] |-> down_values;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert length(up_values) == 1;
    //@ assert length(down_values) == 1;
}
// CASE_END trace_u32_entry_domain

// CASE_BEGIN trace_nested_tuple_original_domain
pub type G2PointerTrace<T> = (
    (
        ((*const T, *const T), (*mut T, *const T)),
        ((*const T, *mut T), (*const T, *const T)),
    ),
    ((usize, usize), (bool, bool)),
);

pub unsafe fn trace_nested_tuple_original_domain<T>(
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
ens ((((result.0).0).0).0) == src &*&
    ((((result.0).0).0).1) == src &*&
    (((result.0).0).1).0 == dst_base &*&
    (((result.0).0).1).1 == src &*&
    (((result.0).1).0).0 == src &*&
    (((result.0).1).0).1 == dst_base &*&
    (((result.0).1).1).0 == src &*&
    (((result.0).1).1).1 == src &*&
    ((result.1).0).0 == 0 &*& ((result.1).0).1 == 0 &*&
    ((result.1).1).0 == false &*& ((result.1).1).1 == false &*&
    [fu]up_choices[..m] |-> up_values &*&
    [fd]down_choices[..m] |-> down_values;
@*//*@
on_unwind_ens false;
@*/
{
    (
        (((src, src), (dst_base, src)), ((src, dst_base), (src, src))),
        ((0usize, 0usize), (false, false)),
    )
}
// CASE_END trace_nested_tuple_original_domain

// CASE_BEGIN trace_generic_entry_domain_negative
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn trace_generic_entry_domain_negative<T>(
    src: *const T,
    dst_base: *mut T,
    n: usize,
    m: usize,
    e: usize,
    up_choices: *const bool,
    down_choices: *const bool,
) -> ()
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
ens [fu]up_choices[..m] |-> up_values &*&
    [fd]down_choices[..m] |-> down_values;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: negative calibration, only if original entry context is reachable
}
// CASE_END trace_generic_entry_domain_negative
