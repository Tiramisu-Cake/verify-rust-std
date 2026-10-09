// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated return-place entry-death diagnostics for nested Rust tuples.
// Each CASE is checked independently by the existing hosted pointer runner.

pub type TupleLayoutPointerHalf<T> = (
    ((*const T, *const T), (*mut T, *const T)),
    ((*const T, *mut T), (*const T, *const T)),
);

pub type TupleLayoutG2<T> = (
    TupleLayoutPointerHalf<T>,
    ((usize, usize), (bool, bool)),
);

// CASE_BEGIN tuple_layout_unit_entry_baseline
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn tuple_layout_unit_entry_baseline<T>() -> ()
/*@
req true;
@*//*@
ens true;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: baseline proves assertion-false entries are classified at the intended point
    ()
}
// CASE_END tuple_layout_unit_entry_baseline

// CASE_BEGIN tuple_layout_flat_pointer_pair
pub unsafe fn tuple_layout_flat_pointer_pair<T>(
    src: *const T,
    dst: *const T,
) -> (*const T, *const T)
/*@
req true;
@*//*@
ens (result.0) == src &*& (result.1) == dst;
@*//*@
on_unwind_ens false;
@*/
{
    (src, dst)
}
// CASE_END tuple_layout_flat_pointer_pair

// CASE_BEGIN tuple_layout_flat_pointer_pair_false_entry
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn tuple_layout_flat_pointer_pair_false_entry<T>(
    src: *const T,
    dst: *const T,
) -> (*const T, *const T)
/*@
req true;
@*//*@
ens (result.0) == src &*& (result.1) == dst;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: calibrate flat-pair entry reachability
    (src, dst)
}
// CASE_END tuple_layout_flat_pointer_pair_false_entry

// CASE_BEGIN tuple_layout_pointer_pairs
pub unsafe fn tuple_layout_pointer_pairs<T>(
    src: *const T,
    dst: *const T,
) -> ((*const T, *const T), (*const T, *const T))
/*@
req true;
@*//*@
ens ((result.0).0) == src &*& ((result.0).1) == src &*&
    ((result.1).0) == dst &*& ((result.1).1) == src;
@*//*@
on_unwind_ens false;
@*/
{
    ((src, src), (dst, src))
}
// CASE_END tuple_layout_pointer_pairs

// CASE_BEGIN tuple_layout_pointer_pairs_false_entry
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn tuple_layout_pointer_pairs_false_entry<T>(
    src: *const T,
    dst: *const T,
) -> ((*const T, *const T), (*const T, *const T))
/*@
req true;
@*//*@
ens ((result.0).0) == src &*& ((result.0).1) == src &*&
    ((result.1).0) == dst &*& ((result.1).1) == src;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: calibrate paired-pointer entry reachability
    ((src, src), (dst, src))
}
// CASE_END tuple_layout_pointer_pairs_false_entry

// CASE_BEGIN tuple_layout_nested_scalars
pub unsafe fn tuple_layout_nested_scalars() -> ((usize, usize), (bool, bool))
/*@
req true;
@*//*@
ens ((result.0).0) == 11 &*& ((result.0).1) == 13 &*&
    ((result.1).0) == false &*& ((result.1).1) == true;
@*//*@
on_unwind_ens false;
@*/
{
    ((11usize, 13usize), (false, true))
}
// CASE_END tuple_layout_nested_scalars

// CASE_BEGIN tuple_layout_nested_scalars_false_entry
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn tuple_layout_nested_scalars_false_entry() -> ((usize, usize), (bool, bool))
/*@
req true;
@*//*@
ens ((result.0).0) == 11 &*& ((result.0).1) == 13 &*&
    ((result.1).0) == false &*& ((result.1).1) == true;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: calibrate scalar-product entry reachability
    ((11usize, 13usize), (false, true))
}
// CASE_END tuple_layout_nested_scalars_false_entry

// CASE_BEGIN tuple_layout_pointer_half
pub unsafe fn tuple_layout_pointer_half<T>(
    src: *const T,
    dst: *mut T,
) -> TupleLayoutPointerHalf<T>
/*@
req true;
@*//*@
ens (((result.0).0).0) == src &*&
    (((result.0).0).1) == src &*&
    (((result.0).1).0) == dst &*&
    (((result.0).1).1) == src &*&
    (((result.1).0).0) == src &*&
    (((result.1).0).1) == dst &*&
    (((result.1).1).0) == src &*&
    (((result.1).1).1) == src;
@*//*@
on_unwind_ens false;
@*/
{
    (((src, src), (dst, src)), ((src, dst), (src, src)))
}
// CASE_END tuple_layout_pointer_half

// CASE_BEGIN tuple_layout_pointer_half_false_entry
pub unsafe fn tuple_layout_pointer_half_false_entry<T>(
    src: *const T,
    dst: *mut T,
) -> TupleLayoutPointerHalf<T>
/*@
req true;
@*//*@
ens (((result.0).0).0) == src &*&
    (((result.0).0).1) == src &*&
    (((result.0).1).0) == dst &*&
    (((result.0).1).1) == src &*&
    (((result.1).0).0) == src &*&
    (((result.1).0).1) == dst &*&
    (((result.1).1).0) == src &*&
    (((result.1).1).1) == src;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: calibrate eight-pointer entry reachability
    (((src, src), (dst, src)), ((src, dst), (src, src)))
}
// CASE_END tuple_layout_pointer_half_false_entry

// CASE_BEGIN tuple_layout_g2_full
pub unsafe fn tuple_layout_g2_full<T>(
    src: *const T,
    dst: *mut T,
) -> TupleLayoutG2<T>
/*@
req true;
@*//*@
ens ((((result.0).0).0).0) == src &*&
    ((((result.0).0).0).1) == src &*&
    ((((result.0).0).1).0) == dst &*&
    ((((result.0).0).1).1) == src &*&
    ((((result.0).1).0).0) == src &*&
    ((((result.0).1).0).1) == dst &*&
    ((((result.0).1).1).0) == src &*&
    ((((result.0).1).1).1) == src &*&
    (((result.1).0).0) == 0 &*& (((result.1).0).1) == 0 &*&
    (((result.1).1).0) == false &*& (((result.1).1).1) == true;
@*//*@
on_unwind_ens false;
@*/
{
    (
        (((src, src), (dst, src)), ((src, dst), (src, src))),
        ((0usize, 0usize), (false, true)),
    )
}
// CASE_END tuple_layout_g2_full

// CASE_BEGIN tuple_layout_g2_full_false_entry
pub unsafe fn tuple_layout_g2_full_false_entry<T>(
    src: *const T,
    dst: *mut T,
) -> TupleLayoutG2<T>
/*@
req true;
@*//*@
ens ((((result.0).0).0).0) == src &*&
    ((((result.0).0).0).1) == src &*&
    ((((result.0).0).1).0) == dst &*&
    ((((result.0).0).1).1) == src &*&
    ((((result.0).1).0).0) == src &*&
    ((((result.0).1).0).1) == dst &*&
    ((((result.0).1).1).0) == src &*&
    ((((result.0).1).1).1) == src &*&
    (((result.1).0).0) == 0 &*& (((result.1).0).1) == 0 &*&
    (((result.1).1).0) == false &*& (((result.1).1).1) == true;
@*//*@
on_unwind_ens false;
@*/
{
    //@ assert false; // TARGET: calibrate full twelve-leaf entry reachability
    (
        (((src, src), (dst, src)), ((src, dst), (src, src))),
        ((0usize, 0usize), (false, true)),
    )
}
// CASE_END tuple_layout_g2_full_false_entry

// CASE_BEGIN tuple_layout_twelve_quartets
pub unsafe fn tuple_layout_twelve_quartets<T>(src: *const T, dst: *mut T)
    -> ((*const T, *const T, *mut T, *const T),
        (*const T, *mut T, *const T, *const T), (usize, usize, bool, bool))
/*@ req true; @*/
/*@ ens (result.0).0 == src &*& (result.0).1 == src &*&
    (result.0).2 == dst &*& (result.0).3 == src &*&
    (result.1).0 == src &*& (result.1).1 == dst &*&
    (result.1).2 == src &*& (result.1).3 == src &*&
    (result.2).0 == 0 &*& (result.2).1 == 0 &*&
    (result.2).2 == false &*& (result.2).3 == true; @*/
/*@ on_unwind_ens false; @*/
{
    ((src, src, dst, src), (src, dst, src, src), (0, 0, false, true))
}
// CASE_END tuple_layout_twelve_quartets

// CASE_BEGIN tuple_layout_twelve_quartets_false_entry
// EXPECT_ERROR {"stage":"verifast","predicate":"false","line":"TARGET","column_start":16,"column_end":21}
pub unsafe fn tuple_layout_twelve_quartets_false_entry<T>(src: *const T, dst: *mut T)
    -> ((*const T, *const T, *mut T, *const T),
        (*const T, *mut T, *const T, *const T), (usize, usize, bool, bool))
/*@ req true; @*/
/*@ ens (result.0).0 == src &*& (result.0).1 == src &*&
    (result.0).2 == dst &*& (result.0).3 == src &*&
    (result.1).0 == src &*& (result.1).1 == dst &*&
    (result.1).2 == src &*& (result.1).3 == src &*&
    (result.2).0 == 0 &*& (result.2).1 == 0 &*&
    (result.2).2 == false &*& (result.2).3 == true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ assert false; // TARGET: shall reach body for the complete twelve-coordinate stock layout
    ((src, src, dst, src), (src, dst, src, src), (0, 0, false, true))
}
// CASE_END tuple_layout_twelve_quartets_false_entry
