//! W3-L2: specialization experiment. Runtime sorting bodies are unchanged.
//! The input snapshot is Copy; `old()` never clones a generic element.

#![allow(dead_code)]

use super::merge::{bm_len, lt_u64, set_probe};
use super::super::{CopyOnDrop, bidirectional_merge};
use crate::{kani, ptr};
use crate::mem::MaybeUninit;

/// Full-width symbolic key; labels are distinct identities in 0..64.
/// Size 16: unstable dispatch chooses general; general uses presort-8 at N>=16,
/// just as for u64. It does not take the <=8-byte network route.
#[repr(C)]
#[derive(Clone, Copy)]
pub(crate) struct Tagged {
    key: u64,
    tag: u64,
}

// Contract stubs havoc the destination's pointees with Arbitrary::any.
// Keep both fields unrestricted: valid labels come from explicit requires.
impl kani::Arbitrary for Tagged {
    fn any() -> Self {
        Self { key: kani::any(), tag: kani::any() }
    }
}

#[derive(Clone, Copy)]
pub(crate) struct K1MergeSnapshot {
    keys: [u64; 64],
    mask: u64,
    count: usize,
    valid: bool,
}

/// No bounds are added to generic runtime functions: a blanket implementation
/// retains the previous arbitrary-probe count, with a Tagged specialization.
pub(crate) trait K1MergePerm: Sized {
    fn k1_snapshot(src: *const Self, len: usize) -> K1MergeSnapshot;
    fn k1_matches(dst: *const Self, len: usize, input: K1MergeSnapshot) -> bool;
    fn k1_uses_tags() -> bool;
}

impl<T> K1MergePerm for T {
    default fn k1_snapshot(src: *const T, len: usize) -> K1MergeSnapshot {
        K1MergeSnapshot {
            keys: [0; 64], mask: 0,
            count: CopyOnDrop::<T>::k1_count_u(src, len), valid: true,
        }
    }

    default fn k1_matches(dst: *const T, len: usize, input: K1MergeSnapshot) -> bool {
        input.count == CopyOnDrop::<T>::k1_count_u(dst, len)
    }

    default fn k1_uses_tags() -> bool { false }
}

impl K1MergePerm for Tagged {
    fn k1_snapshot(src: *const Tagged, len: usize) -> K1MergeSnapshot {
        let mut input = K1MergeSnapshot {
            keys: [0; 64], mask: 0, count: 0, valid: len <= 32,
        };
        for i in 0..len {
            // SAFETY: the caller provides len initialized elements.
            let value = unsafe { *src.add(i) };
            if value.tag >= 64 {
                input.valid = false;
            } else {
                let bit = 1u64 << value.tag;
                input.valid &= input.mask & bit == 0;
                input.mask |= bit;
                input.keys[value.tag as usize] = value.key;
            }
        }
        input
    }

    fn k1_matches(dst: *const Tagged, len: usize, input: K1MergeSnapshot) -> bool {
        if !input.valid { return false; }
        let mut mask = 0u64;
        for i in 0..len {
            // SAFETY: normal return initializes the whole destination region.
            let value = unsafe { *dst.add(i) };
            if value.tag >= 64 { return false; }
            let bit = 1u64 << value.tag;
            if input.mask & bit == 0 || value.key != input.keys[value.tag as usize] {
                return false;
            }
            mask |= bit;
        }
        // Equal region lengths + distinct input labels + mask equality exclude
        // duplicate output labels. The mask is that of this input region.
        mask == input.mask
    }

    fn k1_uses_tags() -> bool { true }
}

impl<T> CopyOnDrop<T> {
    pub(crate) fn k1_merge_snapshot(src: *const T, len: usize) -> K1MergeSnapshot {
        <T as K1MergePerm>::k1_snapshot(src, len)
    }

    pub(crate) fn k1_merge_input_ok(src: *const T, len: usize) -> bool {
        // For ordinary types this is true without reading the probe or input.
        !<T as K1MergePerm>::k1_uses_tags()
            || Self::k1_merge_snapshot(src, len).valid
    }

    pub(crate) fn k1_merge_matches(dst: *const T, len: usize, input: K1MergeSnapshot) -> bool {
        <T as K1MergePerm>::k1_matches(dst, len, input)
    }
}

fn lt_tagged(a: &Tagged, b: &Tagged) -> bool { a.key < b.key }

fn tagged_input<const N: usize>(base: u64) -> [Tagged; N] {
    let keys: [u64; N] = kani::any();
    let mut input = [Tagged { key: 0, tag: 0 }; N];
    for i in 0..N { input[i] = Tagged { key: keys[i], tag: base + i as u64 }; }
    input
}

fn tagged_contract<const N: usize>(base: u64) {
    let input = tagged_input::<N>(base);
    let mut dst = MaybeUninit::<[Tagged; N]>::uninit();
    assert!(<Tagged as K1MergePerm>::k1_uses_tags());
    let mut cmp = lt_tagged;
    // SAFETY: separate, correctly sized destination; proof_for_contract
    // assumes the sorted-half and valid-label requirements of this call.
    unsafe { bidirectional_merge(&input, dst.as_mut_ptr() as *mut Tagged, &mut cmp); }
    kani::cover(true, "Tagged contract: normal return under requires");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(66)]
fn l2_tagged_contract4() { tagged_contract::<4>(8); }

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(66)]
fn l2_tagged_contract8() { tagged_contract::<8>(56); }

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(66)]
fn l2_probe_contract4() {
    assert!(!<u64 as K1MergePerm>::k1_uses_tags());
    bm_len::<u64, _, 4>(lt_u64);
}

/// An independent caller-side oracle: scan input pairs instead of indexing
/// the contract's snapshot. Both sortedness and full key/label identity matter.
fn tagged_oracle<const N: usize>(input: &[Tagged; N], dst: &[Tagged; N]) -> bool {
    let mut input_mask = 0u64;
    let mut output_mask = 0u64;
    for i in 0..N {
        if input[i].tag >= 64 || dst[i].tag >= 64 { return false; }
        input_mask |= 1u64 << input[i].tag;
        output_mask |= 1u64 << dst[i].tag;
        let mut found = false;
        for j in 0..N {
            found |= dst[i].tag == input[j].tag && dst[i].key == input[j].key;
        }
        if !found { return false; }
    }
    input_mask == output_mask
}

fn tagged_stub<const N: usize>(base: u64, mutation: u8) {
    let input = tagged_input::<N>(base);
    let mut cmp = lt_tagged;
    let halves_sorted = CopyOnDrop::<Tagged>::k1_merge_halves_sorted(&input, &&mut cmp);
    kani::assume(halves_sorted);
    kani::cover(halves_sorted, "stub: sorted halves reachable");
    let mut dst = [Tagged { key: 0, tag: 0 }; N];
    // SAFETY: disjoint arrays, sorted halves, unique labels <64.
    unsafe { bidirectional_merge(&input, dst.as_mut_ptr(), &mut cmp); }
    if mutation == 1 { dst[0].key = dst[0].key.wrapping_add(1); }
    if mutation == 2 { dst[0] = dst[1]; }
    kani::cover(true, "stub: before identity assertion");
    assert!(tagged_oracle(&input, &dst));
    for i in 1..N { assert!(dst[i - 1].key <= dst[i].key); }
    kani::cover(true, "stub: normal caller completion");
}

macro_rules! tagged_stub_harness {
    ($name:ident, $n:literal, $base:literal, $mutation:literal) => {
        #[kani::proof]
        #[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
        #[kani::unwind(66)]
        fn $name() { tagged_stub::<$n>($base, $mutation); }
    };
}
tagged_stub_harness!(l2_tagged_stub4, 4, 8, 0);
tagged_stub_harness!(l2_tagged_stub8, 8, 56, 0);
tagged_stub_harness!(l2_stub_mutant_key, 4, 8, 1);
tagged_stub_harness!(l2_stub_mutant_label, 4, 8, 2);

#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(66)]
fn l2_probe_stub4() {
    set_probe::<u64>();
    assert!(!<u64 as K1MergePerm>::k1_uses_tags());
    let input: [u64; 4] = kani::any();
    let mut cmp = lt_u64;
    let halves_sorted = CopyOnDrop::<u64>::k1_merge_halves_sorted(&input, &&mut cmp);
    kani::assume(halves_sorted);
    kani::cover(halves_sorted, "probe stub: sorted halves reachable");
    let before = CopyOnDrop::<u64>::k1_count_u(input.as_ptr(), 4);
    let mut dst = [0u64; 4];
    unsafe { bidirectional_merge(&input, dst.as_mut_ptr(), &mut cmp); }
    assert!(before == CopyOnDrop::<u64>::k1_count_u(dst.as_ptr(), 4));
    kani::cover(true, "probe stub: count retained");
}

// Deliberately bad copies, confined to this verification-only module. Their
// contracts use the very same snapshot/matcher as bidirectional_merge.
macro_rules! identity_mutant {
    ($name:ident, $mutation:literal) => {
        #[kani::requires(input.len() == 4)]
        #[kani::requires(CopyOnDrop::<Tagged>::k1_merge_dst_ok(input, dst))]
        #[kani::requires(CopyOnDrop::<Tagged>::k1_merge_input_ok(input.as_ptr(), input.len()))]
        #[kani::modifies(ptr::slice_from_raw_parts_mut(dst, input.len()))]
        #[kani::ensures(|_| CopyOnDrop::<Tagged>::k1_merge_matches(dst, input.len(), old(CopyOnDrop::<Tagged>::k1_merge_snapshot(input.as_ptr(), input.len()))))]
        unsafe fn $name(input: &[Tagged], dst: *mut Tagged) {
            unsafe {
                ptr::copy_nonoverlapping(input.as_ptr(), dst, input.len());
                if $mutation == 1 { (*dst).key = (*dst).key.wrapping_add(1); }
                if $mutation == 2 { *dst = *dst.add(1); }
            }
        }
    };
}
identity_mutant!(k1_key_mutant, 1);
identity_mutant!(k1_label_mutant, 2);

#[kani::proof_for_contract(k1_key_mutant)]
#[kani::unwind(66)]
fn l2_contract_mutant_key() {
    let input = tagged_input::<4>(8);
    let mut dst = [Tagged { key: 0, tag: 0 }; 4];
    kani::cover(true, "key mutant call reachable");
    unsafe { k1_key_mutant(&input, dst.as_mut_ptr()); }
}

#[kani::proof_for_contract(k1_label_mutant)]
#[kani::unwind(66)]
fn l2_contract_mutant_label() {
    let input = tagged_input::<4>(8);
    let mut dst = [Tagged { key: 0, tag: 0 }; 4];
    kani::cover(true, "label mutant call reachable");
    unsafe { k1_label_mutant(&input, dst.as_mut_ptr()); }
}

#[kani::proof]
#[kani::stub_verified(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(66)]
fn l2_r11_bad_labels() {
    // Sorted keys and valid memory; only label uniqueness is violated.
    let input = [Tagged { key: 0, tag: 8 }; 4];
    let mut dst = [Tagged { key: 0, tag: 0 }; 4];
    let mut cmp = lt_tagged;
    kani::cover(true, "R11 duplicate-label call reachable");
    unsafe { bidirectional_merge(&input, dst.as_mut_ptr(), &mut cmp); }
}
