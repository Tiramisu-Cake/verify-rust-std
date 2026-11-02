//! DIRECTFOUR: direct merge4 baseline for the MERGESTEP composed fixture. The existing
//! merge_profile<StrictU8> contract is checked on the real bidirectional_merge and the real
//! merge_up/merge_down: no stub or stub_verified annotation, no adapter, step summary or ledger.
//! Fixture, call and post-return oracle are those of `mergestep_composed_merge4_u8`. T = u8,
//! F = U8Cmp, value StrictU8::CMP; source18[..4] into a separate scratch32 at offset 0.

use super::{ACTIVE4, StrictU8, U8Cmp, check_merge4, count_matching_values, register};
use crate::kani;
use crate::mem::MaybeUninit;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::merge_profile;

#[kani::proof_for_contract(super::super::super::super::merge::specfix::merge_profile)]
#[kani::unwind(34)]
fn directfour_merge4_u8() {
    StrictU8::set_probe(kani::any());
    let probe = StrictU8::probe();
    let src: [u8; 18] = kani::any();
    let pre = src;
    let mut scratch = MaybeUninit::<[u8; 32]>::uninit();
    let dst = scratch.as_mut_ptr() as *mut u8;
    // Readonly context for the unchanged parent post-check only; nothing in this target reads it.
    register(&src, dst, probe, false, false);
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: initialized source18 prefix4, separate scratch32 written at offset 0 for 4 cells.
    unsafe { merge_profile::<StrictU8>(&src[..ACTIVE4], dst, cmp) };
    kani::cover(true, "directfour merge4: returned");
    check_merge4(&src, &pre, dst, probe, (false, false));
    kani::cover(src[0] < src[2], "directfour merge4: left first");
    kani::cover(src[2] < src[0], "directfour merge4: right first");
    kani::cover(src[0] == src[2], "directfour merge4: equal first values");
    let hits = count_matching_values(&pre[..ACTIVE4], &probe);
    kani::cover(hits > 0, "directfour merge4: probe hits source prefix4");
    kani::cover(hits == 0, "directfour merge4: probe misses source prefix4");
}
