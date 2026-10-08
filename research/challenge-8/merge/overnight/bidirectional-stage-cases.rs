// SPDX-License-Identifier: Apache-2.0 OR MIT
// Checked option-stage facts. No memory or ownership resources are produced.
/*@
fix bidirectional_unwind_options<T>(dst0: option<T>, dst1: option<T>, partial0: option<T>, partial1: option<T>) -> bool {
    match partial0 {
        none => partial0 == dst0 && partial1 == dst1,
        some(written0) => partial1 == dst1 || match partial1 {
            none => false,
            some(written1) => true
        }
    }
}

lem bidirectional_stage_unchanged<T>(dst0: option<T>, dst1: option<T>)
    req true;
    ens bidirectional_unwind_options::<T>(dst0, dst1, dst0, dst1) == true;
{
    match dst0 {
        none => { assert bidirectional_unwind_options::<T>(dst0, dst1, dst0, dst1) == true; }
        some(old0) => { assert bidirectional_unwind_options::<T>(dst0, dst1, dst0, dst1) == true; }
    }
}

lem bidirectional_stage_first<T>(dst0: option<T>, dst1: option<T>, written0: T)
    req true;
    ens bidirectional_unwind_options::<T>(dst0, dst1, some(written0), dst1) == true;
{
    assert bidirectional_unwind_options::<T>(dst0, dst1, some(written0), dst1) == true;
}

lem bidirectional_stage_full<T>(dst0: option<T>, dst1: option<T>, written0: T, written1: T)
    req true;
    ens bidirectional_unwind_options::<T>(dst0, dst1, some(written0), some(written1)) == true;
{
    assert bidirectional_unwind_options::<T>(dst0, dst1, some(written0), some(written1)) == true;
}
@*/

// CASE_BEGIN bidirectional_stage_frame
pub unsafe fn bidirectional_stage_frame(dst0: *mut u32, dst1: *mut u32)
/*@ req *dst0 |-?-> ?old0 &*& *dst1 |-?-> ?old1; @*/
/*@ ens *dst0 |-?-> old0 &*& *dst1 |-?-> old1 &*&
    bidirectional_unwind_options::<u32>(old0, old1, old0, old1) == true &*&
    bidirectional_unwind_options::<u32>(old0, old1, some(7), old1) == true &*&
    bidirectional_unwind_options::<u32>(old0, old1, some(7), some(9)) == true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ bidirectional_stage_unchanged::<u32>(old0, old1);
    //@ bidirectional_stage_first::<u32>(old0, old1, 7);
    //@ bidirectional_stage_full::<u32>(old0, old1, 7, 9);
}
// CASE_END bidirectional_stage_frame

// CASE_BEGIN bidirectional_stage_wrong_suffix_negative
pub unsafe fn bidirectional_stage_wrong_suffix_negative()
/*@ req true; @*/
/*@ ens true; @*/
/*@ on_unwind_ens false; @*/
{
    //@ assert bidirectional_unwind_options::<u32>(none, none, none, some(7)) == true; // TARGET: suffix write without the first write is not an admitted panic stage
}
// CASE_END bidirectional_stage_wrong_suffix_negative
