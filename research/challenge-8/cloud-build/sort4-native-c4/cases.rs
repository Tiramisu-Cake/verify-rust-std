// Isolated candidates. Cloud creates one source pair per CASE block.
// The native subsets below preserve the safe signature and native frame.
// No case calls a truncated sort4 summary or supplies raw C1 resources.

// CASE_BEGIN native-before-pointer-positive
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code)]
use std::mem::MaybeUninit;
use std::marker::Freeze;
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}
/*@
lem native_source_typed_identity<T, F>(p: *T, f: *F, t: thread_id_t,
    values: list<T>, comparator: F)
    req type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
    ens type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
{}
@*/
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T], scratch: &mut [MaybeUninit<T>], is_less: &mut F,
) {
    let len = v.len();
    /*@
    if (len >= 8) {
        produce_type_interp::<T>();
        produce_type_interp::<F>();
        assert thread_token(?t);
        assert t == currentThread;
        let native_base = strip_pointer_metadata(v as pointer) as *T;
        let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
        let scratch_len = ptr_len(scratch);
        assert native_base[..len] |-> ?source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> ?mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        assert *is_less |-> ?comparator;
        assert <F>.own(t, comparator);
        array_split::<T>(native_base, 4);
        foreach_split(source_all, own::<T>(t), 4);
        assert native_base[..4] |-> ?first_four;
        native_source_typed_identity::<T, F>(native_base, is_less as *mut F,
            t, first_four, comparator);
        array_join::<T>(native_base);
        foreach_append(take(4, source_all), drop(4, source_all));
        assert native_base[..len] |-> source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        leak type_interp::<T>();
        leak type_interp::<F>();
    }
    @*/
}
// CASE_END native-before-pointer-positive

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
        (len >= 16 ? element_size > 16 : true);
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
        //@ assert len >= 16 ? std::mem::size_of::<T>() > 16 : true;
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
        (len >= 16 ? element_size > 16 : true);
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

// CASE_BEGIN mu-forward
#![allow(dead_code)]
use std::mem::MaybeUninit;
/*@
lem mu_forward<T>(p: *std::mem::MaybeUninit<T>)
    req *p |-> ?old;
    ens *(p as *T) |-?-> old.inner();
{
    std::mem::open_MaybeUninit::<T>(p);
}
@*/
fn small_sort_general_with_scratch() {}
// CASE_END mu-forward

// CASE_BEGIN mu-roundtrip-inner
#![allow(dead_code)]
use std::mem::MaybeUninit;
/*@
lem mu_roundtrip_inner<T>(p: *std::mem::MaybeUninit<T>)
    req *p |-> ?old;
    ens *p |-> ?current &*& current.inner() == old.inner();
{
    std::mem::open_MaybeUninit::<T>(p);
    std::mem::close_MaybeUninit_::<T>(p);
}
@*/
fn small_sort_general_with_scratch() {}
// CASE_END mu-roundtrip-inner

// CASE_BEGIN mu-roundtrip-exact-old
#![allow(dead_code)]
use std::mem::MaybeUninit;
/*@
lem mu_roundtrip_exact_old<T>(p: *std::mem::MaybeUninit<T>)
    req *p |-> ?old;
    ens *p |-> old;
{
    std::mem::open_MaybeUninit::<T>(p);
    std::mem::close_MaybeUninit_::<T>(p);
    assert *p |-> old; // EXACT_OLD_VALUE_RESTORATION_DIAGNOSTIC
}
@*/
fn small_sort_general_with_scratch() {}
// CASE_END mu-roundtrip-exact-old


// CASE_BEGIN native-before-pointer-missing-t
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code)]
use std::mem::MaybeUninit;
use std::marker::Freeze;
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}
/*@
lem native_source_typed_identity<T, F>(p: *T, f: *F, t: thread_id_t,
    values: list<T>, comparator: F)
    req type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
    ens type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
{}
@*/
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T], scratch: &mut [MaybeUninit<T>], is_less: &mut F,
) {
    let len = v.len();
    /*@
    if (len >= 8) {
        produce_type_interp::<F>();
        assert thread_token(?t);
        assert t == currentThread;
        let native_base = strip_pointer_metadata(v as pointer) as *T;
        let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
        let scratch_len = ptr_len(scratch);
        assert native_base[..len] |-> ?source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> ?mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        assert *is_less |-> ?comparator;
        assert <F>.own(t, comparator);
        array_split::<T>(native_base, 4);
        foreach_split(source_all, own::<T>(t), 4);
        assert native_base[..4] |-> ?first_four;
        native_source_typed_identity::<T, F>(native_base, is_less as *mut F,
            t, first_four, comparator);
        array_join::<T>(native_base);
        foreach_append(take(4, source_all), drop(4, source_all));
        assert native_base[..len] |-> source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        leak type_interp::<T>();
        leak type_interp::<F>();
    }
    @*/
}
// CASE_END native-before-pointer-missing-t


// CASE_BEGIN native-before-pointer-missing-f
#![feature(freeze, rustc_attrs, core_intrinsics)]
#![allow(internal_features, dead_code)]
use std::mem::MaybeUninit;
use std::marker::Freeze;
#[unsafe(rustc_allow_lifetime_dependent_specialization)]
pub(crate) trait FreezeMarker {}
impl<T: Freeze> FreezeMarker for T {}
/*@
lem native_source_typed_identity<T, F>(p: *T, f: *F, t: thread_id_t,
    values: list<T>, comparator: F)
    req type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
    ens type_interp::<T>() &*& type_interp::<F>() &*&
        thread_token(t) &*& t == currentThread &*&
        p[..4] |-> values &*& foreach(values, own::<T>(t)) &*&
        *f |-> comparator &*& <F>.own(t, comparator);
{}
@*/
fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(
    v: &mut [T], scratch: &mut [MaybeUninit<T>], is_less: &mut F,
) {
    let len = v.len();
    /*@
    if (len >= 8) {
        produce_type_interp::<T>();
        assert thread_token(?t);
        assert t == currentThread;
        let native_base = strip_pointer_metadata(v as pointer) as *T;
        let mu_base = strip_pointer_metadata(scratch as pointer) as *std::mem::MaybeUninit<T>;
        let scratch_len = ptr_len(scratch);
        assert native_base[..len] |-> ?source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> ?mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        assert *is_less |-> ?comparator;
        assert <F>.own(t, comparator);
        array_split::<T>(native_base, 4);
        foreach_split(source_all, own::<T>(t), 4);
        assert native_base[..4] |-> ?first_four;
        native_source_typed_identity::<T, F>(native_base, is_less as *mut F,
            t, first_four, comparator);
        array_join::<T>(native_base);
        foreach_append(take(4, source_all), drop(4, source_all));
        assert native_base[..len] |-> source_all;
        assert foreach(source_all, own::<T>(t));
        assert mu_base[..scratch_len] |-> mu_all;
        assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));
        leak type_interp::<T>();
        leak type_interp::<F>();
    }
    @*/
}
// CASE_END native-before-pointer-missing-f
