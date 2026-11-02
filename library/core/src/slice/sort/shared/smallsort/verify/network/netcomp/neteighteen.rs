//! NET18-LEAVES: independent real-body leaves for the Unstable u8 N18 network geometry.
//! T = u8, F = U8Cmp, value StrictU8::CMP. Existing targets and contracts are unchanged; these
//! fixtures only place them on the N18 backings. No stubs: each target runs its real helper.
//! Not a caller/composition proof: future N18 call sites are not bound here.

use super::super::{StrictU8, count_matching_values};
use super::{U8Cmp, swap_net9};
use crate::kani;
use crate::mem::MaybeUninit;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{Profile, merge_profile};

// Unrestricted backing18 and independent probe; active9 = global OFF..OFF + 9; OFF is 0 or 9.
fn swap_leaf18<const OFF: usize>() {
    let mut v: [u8; 18] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let a: usize = kani::any_where(|&i| i < 9);
    let b: usize = kani::any_where(|&i| i < 9 && i != a);
    let (ga, gb) = (OFF + a, OFF + b);
    let cmp: U8Cmp = StrictU8::CMP;
    let taken = pre[gb] < pre[ga];
    // SAFETY: initialized backing18, base + OFF with OFF + 9 <= 18, distinct local indices < 9.
    unsafe { swap_net9(v.as_mut_ptr().add(OFF), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[gb], pre[ga]) } else { (pre[ga], pre[gb]) };
    kani::assert(v[ga] == want_a && v[gb] == want_b, "net18 swap leaf: pair transfer");
    kani::assert(v[ga] <= v[gb], "net18 swap leaf: pair ordered");
    let active_pre = count_matching_values(&pre[OFF..OFF + 9], &probe);
    kani::assert(
        active_pre == count_matching_values(&v[OFF..OFF + 9], &probe),
        "net18 swap leaf: active9 count preserved",
    );
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "net18 swap leaf: backing18 count preserved",
    );
    let mut i = 0;
    while i < 18 {
        if i != ga && i != gb {
            kani::assert(
                v[i] == pre[i],
                "net18 swap leaf: backing18 values outside pair unchanged",
            );
        }
        i += 1;
    }
    kani::cover(taken, "net18 swap leaf: swap taken");
    kani::cover(!taken, "net18 swap leaf: swap not taken");
    kani::cover(a == 0 && b == 8, "net18 swap leaf: first to last");
    kani::cover(a == 8 && b == 0, "net18 swap leaf: last to first");
    kani::cover(a > 0 && a < 8 && b > 0 && b < 8, "net18 swap leaf: interior pair");
    kani::cover(active_pre > 0, "net18 swap leaf: probe hits active9");
    kani::cover(active_pre == 0, "net18 swap leaf: probe misses active9");
}

#[kani::proof_for_contract(super::swap_net9)]
#[kani::unwind(25)]
fn net18_swap_left_backing18() {
    swap_leaf18::<0>();
}

#[kani::proof_for_contract(super::swap_net9)]
#[kani::unwind(25)]
fn net18_swap_right_backing18() {
    swap_leaf18::<9>();
}

// Canonical StrictU8 merge of source18 into prefix18 of a separate uninitialized scratch32.
// Sorted halves9 come only from the target's requires; the tail 18..32 is never read.
#[kani::proof_for_contract(super::super::super::merge::specfix::merge_profile)]
#[kani::unwind(34)]
fn net18_merge_strict_scratch32() {
    StrictU8::set_probe(kani::any());
    let probe = StrictU8::probe();
    let src: [u8; 18] = kani::any();
    let pre = src;
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let dst = scratch.as_mut_ptr() as *mut u8;
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: initialized source18, separate scratch32 written at offset 0 for 18 elements.
    unsafe { merge_profile::<StrictU8>(&src, dst, cmp) };
    kani::cover(true, "net18 merge: returned");
    kani::assert(StrictU8::probe() == probe, "net18 merge: probe unchanged");
    let mut i = 0;
    while i < 18 {
        kani::assert(src[i] == pre[i], "net18 merge: source18 unchanged");
        i += 1;
    }
    // SAFETY: a normal return wrote the whole prefix18; only that prefix is viewed.
    let out = unsafe { crate::slice::from_raw_parts(dst as *const u8, 18) };
    let mut i = 1;
    while i < 18 {
        kani::assert(!(out[i] < out[i - 1]), "net18 merge: destination prefix18 sorted");
        i += 1;
    }
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(out, &probe),
        "net18 merge: source18/prefix18 full-value count preserved",
    );
    kani::cover(src[0] < src[9], "net18 merge: left first");
    kani::cover(src[9] < src[0], "net18 merge: right first");
    kani::cover(src[0] == src[9], "net18 merge: equal first values");
    kani::cover(count_matching_values(&pre, &probe) > 0, "net18 merge: probe hits source18");
    kani::cover(count_matching_values(&pre, &probe) == 0, "net18 merge: probe misses source18");
}
