// Frozen-profile follow-up candidates; Cloud proof pending at publication.
// No new verifier semantics or actual sort4 summary use.

// CASE_BEGIN mu-roundtrip-current-owner
#![allow(dead_code)]
use std::mem::MaybeUninit;
/*@
lem mu_roundtrip_current_owner<T>(p: *std::mem::MaybeUninit<T>, t: thread_id_t)
    req *p |-> ?old &*& <std::mem::MaybeUninit<T>>.own(t, old);
    ens *p |-> ?current &*& <std::mem::MaybeUninit<T>>.own(t, current) &*&
        current.inner() == old.inner();
{
    std::mem::open_MaybeUninit::<T>(p);
    std::mem::close_MaybeUninit_::<T>(p);
    assert *p |-> ?current;
    assert <std::mem::MaybeUninit<T>>.own(t, current);
}
@*/
fn small_sort_general_with_scratch() {}
// CASE_END mu-roundtrip-current-owner

// CASE_BEGIN native-slice-cast-expression
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code)]
use std::mem::MaybeUninit;
use std::marker::Freeze;
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T], scratch: &mut [MaybeUninit<T>], is_less: &mut F,
) {
    let len = v.len();
    let scratch_len = scratch.len();
    // Exact implementation expression from slice/mod.rs:778, receiver renamed.
    // This is a primitive-body component, not binding of actual as_mut_ptr calls.
    let v_base = v as *mut [T] as *mut T;
    let len_div_2 = len / 2;
    let mu_base = scratch as *mut [MaybeUninit<T>] as *mut MaybeUninit<T>;
    let scratch_base = mu_base as *mut T;
    /*@
    assert v_base as pointer == strip_pointer_metadata(v as pointer);
    assert mu_base as pointer == strip_pointer_metadata(scratch as pointer);
    assert scratch_base as pointer == mu_base as pointer;
    assert len_div_2 == len / 2;
    assert thread_token(?t);
    assert t == currentThread;
    assert v_base[..len] |-> ?source_all;
    assert foreach(source_all, own::<T>(t));
    assert mu_base[..scratch_len] |-> ?mu_all;
    assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
    assert *is_less |-> ?comparator;
    assert <F>.own(t, comparator);
    if (len >= 8) {
        array_split::<T>(v_base, 4);
        foreach_split(source_all, own::<T>(t), 4);
        assert v_base[..4] |-> ?first_four;
        assert foreach(first_four, own::<T>(t));
        array_join::<T>(v_base);
        foreach_append(take(4, source_all), drop(4, source_all));
    }
    assert v_base[..len] |-> source_all;
    assert foreach(source_all, own::<T>(t));
    assert mu_base[..scratch_len] |-> mu_all;
    assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
    @*/
}
// CASE_END native-slice-cast-expression


// CASE_BEGIN native-guard-prefix
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code)]
use std::{intrinsics, mem::{MaybeUninit, size_of}};
use std::marker::Freeze;
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}
/*@
lem selected_sort4_guard(len: usize, element_size: usize, scratch_len: usize)
    req len >= 8 &*& !(element_size <= 16 && len >= 16) &*&
        scratch_len >= len + 16;
    ens len >= 4 &*& scratch_len >= 4 &*&
        (len < 16 || element_size > 16);
{}
@*/
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T], scratch: &mut [MaybeUninit<T>], is_less: &mut F,
) {
    let len = v.len();
    if len < 2 {
        return;
    }
    if scratch.len() < len + 16 {
        intrinsics::abort();
    }
    // This guard-only subset contains no pointer, callback, sort8 or sort4 call.
    if const { size_of::<T>() <= 16 } && len >= 16 {
        //@ assert len >= 16;
    } else if len >= 8 {
        //@ selected_sort4_guard(len, std::mem::size_of::<T>(), ptr_len(scratch));
        //@ assert len >= 4;
        //@ assert ptr_len(scratch) >= 4;
        //@ assert len < 16 || std::mem::size_of::<T>() > 16;
    } else {
        //@ assert len < 8;
    }
}
// CASE_END native-guard-prefix


// CASE_BEGIN selected-guard-lemma
#![allow(dead_code)]
/*@
lem selected_sort4_guard(len: usize, element_size: usize, scratch_len: usize)
    req len >= 8 &*& !(element_size <= 16 && len >= 16) &*&
        scratch_len >= len + 16;
    ens len >= 4 &*& scratch_len >= 4 &*&
        (len < 16 || element_size > 16);
{}
lem selected_zst_route_witness()
    req true;
    ens true;
{
    selected_sort4_guard(8, 0, 24);
    assert !(0 <= 16 && 8 >= 16);
    assert !(0 > 0);
}
@*/
fn small_sort_general_with_scratch() {}
// CASE_END selected-guard-lemma
