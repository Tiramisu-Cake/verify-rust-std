// Final independent components; no tool semantics changes.

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
    if len < 2 {
        return;
    }
    let scratch_len = scratch.len();
    // Exact implementation expression from slice/mod.rs:778, receiver renamed.
    // This is a primitive-body component, not binding of actual as_mut_ptr calls.
    let v_base = v as *mut [T] as *mut T;
    let len_div_2 = len / 2;
    let mu_base = scratch as *mut [MaybeUninit<T>] as *mut MaybeUninit<T>;
    let scratch_base = mu_base as *mut T;
    /*@
    assert (v_base as pointer) == strip_pointer_metadata(v as pointer);
    assert (mu_base as pointer) == strip_pointer_metadata(scratch as pointer);
    assert (scratch_base as pointer) == (mu_base as pointer);
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

// CASE_BEGIN native-early-return-resources
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
    if len < 2 {
        return;
    }
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
// CASE_END native-early-return-resources

// CASE_BEGIN checked-add-overflow-reproducer
#![allow(dead_code)]
fn small_sort_general_with_scratch(len: usize) {
    let _need = len + 16;
}
// CASE_END checked-add-overflow-reproducer
