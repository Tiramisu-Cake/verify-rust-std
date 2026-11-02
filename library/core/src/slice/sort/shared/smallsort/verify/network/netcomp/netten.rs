//! NETTEN leaves: the two real-body leaves a future actual Unstable u8 N10 route would consume.
//! sort9 runs on prefix9 of an exact backing10, then insertion offset9 does one
//! insert_tail(begin0, tail9) over the whole backing10. Leaf-only: no caller is composed here.
//! T=u8, F=U8Cmp, value StrictU8::CMP (reified strict_less::<u8>); no stubs of any kind.

use super::super::{StrictU8, count_matching_values, prefix_unchanged};
use super::{U8Cmp, swap_net9};
use crate::kani;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{Profile, insert_tail_profile};

/// Pure typed `<` order over the whole backing10; never calls the comparator.
fn sorted10(v: &[u8; 10]) -> bool {
    let mut i = 1;
    while i < 10 {
        if v[i] < v[i - 1] {
            return false;
        }
        i += 1;
    }
    true
}

// Existing swap_net9 target unchanged; its real body calls swap_if_less::<u8, U8Cmp>.
#[kani::proof_for_contract(super::swap_net9)]
#[kani::unwind(25)]
fn netten_swap_prefix9_backing10() {
    let mut v: [u8; 10] = kani::any();
    let pre = v;
    let probe: u8 = kani::any();
    let a: usize = kani::any_where(|&i| i < 9);
    let b: usize = kani::any_where(|&i| i < 9 && i != a);
    let cmp: U8Cmp = StrictU8::CMP;
    let taken = pre[b] < pre[a];
    let base = v.as_mut_ptr();
    // SAFETY: base+0 of a full initialized exact backing10; prefix9 holds the distinct pair.
    unsafe { swap_net9(base.add(0), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "netten swap: pair transfer");
    kani::assert(v[a] <= v[b], "netten swap: pair ordered");
    kani::assert(
        count_matching_values(&pre[..9], &probe) == count_matching_values(&v[..9], &probe),
        "netten swap: active9 count preserved",
    );
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netten swap: backing10 count preserved",
    );
    let mut i = 0;
    while i < 10 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "netten swap: cells outside pair unchanged");
        }
        i += 1;
    }
    kani::assert(v[9] == pre[9], "netten swap: tail v[9] unchanged");
    let active_hits = count_matching_values(&pre[..9], &probe);
    kani::cover(taken, "netten swap: swap taken");
    kani::cover(!taken, "netten swap: swap not taken");
    kani::cover(a == 0 && b == 8, "netten swap: first to last");
    kani::cover(a == 8 && b == 0, "netten swap: last to first");
    kani::cover(a > 0 && a < 8 && b > 0 && b < 8, "netten swap: interior pair");
    kani::cover(active_hits > 0, "netten swap: probe hits active9");
    kani::cover(active_hits == 0, "netten swap: probe misses active9");
    kani::cover(probe == pre[9] && active_hits == 0, "netten swap: probe hits only untouched tail");
}

// Existing insert_tail_profile target, instance StrictU8; its real body calls
// insert_tail::<u8, U8Cmp>. The whole backing10 is the writable region.
#[kani::proof_for_contract(super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn netten_insert_strict_u8_begin0_tail9() {
    StrictU8::set_probe(kani::any());
    let probe = StrictU8::probe();
    let mut v: [u8; 10] = kani::any();
    let pre = v;
    let pre_tail = pre[9];
    let base = v.as_mut_ptr();
    let cmp: U8Cmp = StrictU8::CMP;
    // SAFETY: begin base+0 < tail base+9 in one initialized writable backing10. The sorted
    // prefix9 is the profile's own requires, assumed only by proof_for_contract.
    unsafe { insert_tail_profile::<StrictU8>(base.add(0), base.add(9), cmp) };
    kani::cover(true, "netten insert: returned");
    kani::assert(sorted10(&v), "netten insert: backing10 sorted");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "netten insert: backing10 count preserved",
    );
    kani::assert(StrictU8::probe() == probe, "netten insert: profile probe unchanged");
    let hits = count_matching_values(&pre, &probe);
    kani::cover(pre_tail < pre[0], "netten insert: tail becomes first");
    kani::cover(pre[8] <= pre_tail, "netten insert: tail stays last");
    kani::cover(pre[0] < pre_tail && pre_tail < pre[8], "netten insert: interior insertion");
    kani::cover(pre_tail == pre[4], "netten insert: tail ties prefix value");
    kani::cover(!prefix_unchanged(&v, &pre, 0), "netten insert: output differs from input");
    kani::cover(hits > 0, "netten insert: probe hits backing10");
    kani::cover(hits == 0, "netten insert: probe misses backing10");
}

// NETTEN-CALLER: opt-in child composing the actual N10 route from the leaves above.
mod caller;
