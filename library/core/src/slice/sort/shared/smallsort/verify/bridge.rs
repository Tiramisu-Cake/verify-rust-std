//! Exact-N3 feasibility smoke: raw merge -> adapter -> checked profile summary.
//! The leaf PFC has no substitutions. A3 uses a separate initialized backing geometry and
//! checks the target's own write set; it does not extend the profile leaf's domain.

#![cfg(kani_smallsort_controls)]

use super::merge::merge_length_body;
use super::merge::specfix::{
    LtU8, Profile, merge_halves_sorted, merge_profile, merge_regions, model_count, model_sorted,
};
use crate::mem::MaybeUninit;
use crate::slice::sort::shared::FreezeMarker;
use crate::slice::sort::shared::smallsort::bidirectional_merge;
use crate::ub_checks::{can_dereference, can_write};
use crate::{kani, ptr};

/// Closed bridge domain: unsupported T/F pairs have no implementation and cannot compile.
trait MergeBridge<F>: Sized {
    unsafe fn merge(v: &[Self], dst: *mut Self, is_less: &mut F);
}

impl MergeBridge<fn(&u8, &u8) -> bool> for u8 {
    unsafe fn merge(v: &[u8], dst: *mut u8, is_less: &mut fn(&u8, &u8) -> bool) {
        // SAFETY: the verified replacement checks all profile requires at this call, including
        // canonical identity of the received value. Do not replace `*is_less` with LtU8::CMP.
        unsafe { merge_profile::<LtU8>(v, dst, *is_less) };
    }
}

unsafe fn adapter<T: FreezeMarker + MergeBridge<F>, F: FnMut(&T, &T) -> bool>(
    v: &[T],
    dst: *mut T,
    is_less: &mut F,
) {
    kani::cover(true, "bridge adapter entered");
    // SAFETY: the sole implementation forwards the original arguments to the checked profile.
    unsafe { T::merge(v, dst, is_less) };
}

// The profile is declared in the earlier `merge` module. This independent leaf executes its
// real body, which calls raw bidirectional_merge::<u8, fn(&u8, &u8) -> bool>.
#[kani::proof_for_contract(merge_profile)]
#[kani::unwind(34)]
fn bridge_leaf_u8_n3() {
    merge_length_body::<LtU8, 3>();
}

/// Proof-owned caller: exact initialized source and a separate uninitialized destination,
/// matching the leaf. The post-oracle reads full u8 values using the unchanged typed probe.
fn caller(v: [u8; 3], cmp: fn(&u8, &u8) -> bool) {
    let mut dst = MaybeUninit::<[u8; 3]>::uninit();
    let dst_ptr = dst.as_mut_ptr() as *mut u8;
    let source_before = v;
    let probe_before = LtU8::probe();
    let count_before = model_count::<LtU8>(v.as_ptr(), 3);
    let mut is_less: fn(&u8, &u8) -> bool = cmp;
    kani::cover(true, "bridge caller raw call reached");
    // SAFETY: exact disjoint regions; the positive harness supplies sorted halves and the
    // canonical function pointer. Negative harnesses violate only their named profile premise.
    unsafe { bidirectional_merge(&v, dst_ptr, &mut is_less) };
    kani::assert(model_sorted::<LtU8>(dst_ptr, 3), "bridge output is key sorted");
    kani::assert(
        count_before == model_count::<LtU8>(dst_ptr, 3),
        "bridge output preserves full values for the same probe",
    );
    kani::assert(v == source_before, "bridge source frame");
    kani::assert(LtU8::probe() == probe_before, "bridge probe frame");
    kani::cover(true, "bridge caller returned");
}

#[kani::proof]
#[kani::stub(bidirectional_merge, adapter)]
#[kani::stub_verified(merge_profile)]
#[kani::unwind(34)]
fn bridge_caller_positive_u8_n3() {
    LtU8::set_probe(kani::any());
    let v: [u8; 3] = kani::any();
    kani::assume((v[1] >> 1) <= (v[2] >> 1));
    caller(v, LtU8::CMP);
}

fn always_true(_: &u8, _: &u8) -> bool {
    true
}

#[kani::proof]
#[kani::stub(bidirectional_merge, adapter)]
#[kani::stub_verified(merge_profile)]
#[kani::unwind(34)]
fn bridge_caller_wrong_f_u8_n3() {
    LtU8::set_probe(kani::any());
    let v: [u8; 3] = kani::any();
    kani::assume((v[1] >> 1) <= (v[2] >> 1));
    caller(v, always_true);
}

#[kani::proof]
#[kani::stub(bidirectional_merge, adapter)]
#[kani::stub_verified(merge_profile)]
#[kani::unwind(34)]
fn bridge_caller_unsorted_u8_n3() {
    LtU8::set_probe(kani::any());
    // Right keys [1, 0] violate sortedness by construction; no sortedness assumption.
    let v: [u8; 3] = [kani::any(), 2, 0];
    caller(v, LtU8::CMP);
}

// A3 target precedes its PFCs. Sentinel is readable/writable but excluded from modifies.
// The body executes raw merge without either substitution. The conditional mutation is the
// only intentional frame violation, inside the target and after a reachable cover.
#[kani::requires(merge_regions::<u8>(v, dst) && merge_halves_sorted::<LtU8>(v))]
#[kani::requires(can_dereference(sentinel as *const u8) && can_write(sentinel))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, 3))]
unsafe fn frame_target(v: &[u8; 3], dst: *mut u8, sentinel: *mut u8, corrupt: bool) {
    let mut is_less: fn(&u8, &u8) -> bool = LtU8::CMP;
    // SAFETY: the profile geometry and pure sorted-halves premise hold on this exact N3.
    unsafe { bidirectional_merge(v, dst, &mut is_less) };
    if corrupt {
        kani::cover(true, "bridge A3 sentinel write reached");
        // SAFETY: valid initialized sentinel in backing[3], outside the permitted dst[0..3).
        // This deliberately violates the target's modifies clause, not Rust memory safety.
        unsafe { *sentinel ^= 1 };
    }
    kani::cover(true, "bridge A3 target returned");
}

fn frame_case(corrupt: bool) {
    LtU8::set_probe(kani::any());
    let input: [u8; 3] = kani::any();
    // Sort only the right pair by construction, using the pure key model, not the callback.
    let (b, c) = if (input[1] >> 1) <= (input[2] >> 1) {
        (input[1], input[2])
    } else {
        (input[2], input[1])
    };
    let source: [u8; 3] = [input[0], b, c];
    let mut backing: [u8; 4] = kani::any();
    let dst = backing.as_mut_ptr();
    // SAFETY: initialized sentinel at byte 3 of the same backing, outside dst bytes 0..3.
    let sentinel = unsafe { dst.add(3) };
    kani::cover(true, "bridge A3 target call reached");
    // SAFETY: separate initialized source3 and backing4, sorted halves 1+2, valid sentinel.
    unsafe { frame_target(&source, dst, sentinel, corrupt) };
}

#[kani::proof_for_contract(frame_target)]
#[kani::unwind(34)]
fn bridge_frame_positive_u8_n3() {
    frame_case(false);
}

#[kani::proof_for_contract(frame_target)]
#[kani::unwind(34)]
fn bridge_frame_negative_u8_n3() {
    frame_case(true);
}
