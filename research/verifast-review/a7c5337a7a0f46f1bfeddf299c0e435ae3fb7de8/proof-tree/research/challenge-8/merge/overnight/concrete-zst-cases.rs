// SPDX-License-Identifier: Apache-2.0 OR MIT
// Compiler-backed concrete zero-sized pointee probes for W1 wrapping.
// Each operation uses a real `()` or empty user-defined ZST type. No layout
// fact is assumed in a precondition, and none of these arithmetic cases claims
// allocation membership, ownership, initialization, or access permission.

// CASE_BEGIN unit_wrapping_add_const
pub unsafe fn unit_wrapping_add_const(base: *const ()) -> *const ()
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END unit_wrapping_add_const

// CASE_BEGIN unit_wrapping_sub_mut
pub unsafe fn unit_wrapping_sub_mut(base: *mut ()) -> *mut ()
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_sub(1)
}
// CASE_END unit_wrapping_sub_mut

// CASE_BEGIN unit_wrapping_offset_const
pub unsafe fn unit_wrapping_offset_const(base: *const ()) -> *const ()
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_offset(-1)
}
// CASE_END unit_wrapping_offset_const

// CASE_BEGIN unit_terminal_reentry_const
pub unsafe fn unit_terminal_reentry_const(base: *const ()) -> *const ()
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let reverse = base.wrapping_sub(1);
    reverse.wrapping_add(1)
}
// CASE_END unit_terminal_reentry_const

// CASE_BEGIN unit_terminal_reentry_mut
pub unsafe fn unit_terminal_reentry_mut(base: *mut ()) -> *mut ()
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    let reverse = base.wrapping_sub(1);
    reverse.wrapping_add(1)
}
// CASE_END unit_terminal_reentry_mut

// A concrete user-defined ZST checks whether the pinned translator/refiner
// obtains the compiler layout fact for an inhabited empty aggregate too.
// CASE_BEGIN user_zst_wrapping_add_const
struct UserZst;

pub unsafe fn user_zst_wrapping_add_const(base: *const UserZst) -> *const UserZst
/*@
req 0 <= (base as pointer).address &*& (base as pointer).address <= usize::MAX;
@*//*@
ens (result as pointer) == (base as pointer) &*&
    (result as pointer).provenance == (base as pointer).provenance &*&
    (result as pointer).address == (base as pointer).address &*&
    (result as pointer).metadata == (base as pointer).metadata;
@*//*@
on_unwind_ens false;
@*/
{
    base.wrapping_add(1)
}
// CASE_END user_zst_wrapping_add_const
