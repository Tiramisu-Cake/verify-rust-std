//! U64-TEN-LEAVES: the two real-body leaves a future actual Unstable u64 N10 route would consume.
//! sort9 runs on prefix9 of an exact backing10, then insertion offset9 does one
//! insert_tail(begin0, tail9) over the whole backing10. Leaf-only: no caller is composed here.
//! T=u64, F=U64Cmp, value StrictU64::CMP (reified strict_less::<u64>); no stubs of any kind.

use super::super::{StrictU64, count_matching_values, prefix_unchanged};
use super::{U64Cmp, swap_u64_net9};
use crate::kani;
use crate::slice::sort::shared::smallsort::verify::merge::specfix::{Profile, insert_tail_profile};

/// Pure typed `<` order over the whole backing10; never calls the comparator.
fn sorted10_u64(v: &[u64; 10]) -> bool {
    let mut i = 1;
    while i < 10 {
        if v[i] < v[i - 1] {
            return false;
        }
        i += 1;
    }
    true
}

// Existing swap_u64_net9 target unchanged; its real body calls swap_if_less::<u64, U64Cmp>.
#[kani::proof_for_contract(super::swap_u64_net9)]
#[kani::unwind(25)]
fn u64ten_swap_prefix9_backing10() {
    let mut v: [u64; 10] = kani::any();
    let pre = v;
    let probe: u64 = kani::any();
    let a: usize = kani::any_where(|&i| i < 9);
    let b: usize = kani::any_where(|&i| i < 9 && i != a);
    let cmp: U64Cmp = StrictU64::CMP;
    let taken = pre[b] < pre[a];
    let base = v.as_mut_ptr();
    // SAFETY: base+0 of a full initialized exact backing10; prefix9 holds the distinct pair.
    unsafe { swap_u64_net9(base.add(0), a, b, cmp, probe) };
    let (want_a, want_b) = if taken { (pre[b], pre[a]) } else { (pre[a], pre[b]) };
    kani::assert(v[a] == want_a && v[b] == want_b, "u64ten swap: pair transfer");
    kani::assert(v[a] <= v[b], "u64ten swap: pair ordered");
    kani::assert(
        count_matching_values(&pre[..9], &probe) == count_matching_values(&v[..9], &probe),
        "u64ten swap: active9 count preserved",
    );
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64ten swap: backing10 count preserved",
    );
    let mut i = 0;
    while i < 10 {
        if i != a && i != b {
            kani::assert(v[i] == pre[i], "u64ten swap: cells outside pair unchanged");
        }
        i += 1;
    }
    kani::assert(v[9] == pre[9], "u64ten swap: tail v[9] unchanged");
    let active_hits = count_matching_values(&pre[..9], &probe);
    let whole_hits = count_matching_values(&pre, &probe);
    kani::cover(taken, "u64ten swap: swap taken");
    kani::cover(!taken, "u64ten swap: swap not taken");
    kani::cover(a == 0 && b == 8, "u64ten swap: first to last");
    kani::cover(a == 8 && b == 0, "u64ten swap: last to first");
    kani::cover(a > 0 && a < 8 && b > 0 && b < 8, "u64ten swap: interior pair");
    kani::cover(active_hits > 0, "u64ten swap: probe hits active9");
    kani::cover(active_hits == 0, "u64ten swap: probe misses active9");
    kani::cover(probe == pre[9] && active_hits == 0, "u64ten swap: probe hits only untouched tail");
    kani::cover(
        probe >= (1u64 << 40) && whole_hits > 0,
        "u64ten swap: high-bit probe hits backing10",
    );
}

// Existing insert_tail_profile target, instance StrictU64; its real body calls
// insert_tail::<u64, U64Cmp>. The whole backing10 is the writable region.
#[kani::proof_for_contract(super::super::super::merge::specfix::insert_tail_profile)]
#[kani::unwind(25)]
fn u64ten_insert_strict_u64_begin0_tail9() {
    StrictU64::set_probe(kani::any());
    let probe = StrictU64::probe();
    let mut v: [u64; 10] = kani::any();
    let pre = v;
    let base = v.as_mut_ptr();
    let cmp: U64Cmp = StrictU64::CMP;
    // SAFETY: begin base+0 < tail base+9 in one initialized writable backing10. The sorted
    // prefix9 is the profile's own requires, assumed only by proof_for_contract.
    unsafe { insert_tail_profile::<StrictU64>(base.add(0), base.add(9), cmp) };
    kani::cover(true, "u64ten insert: returned");
    kani::assert(sorted10_u64(&v), "u64ten insert: backing10 sorted");
    kani::assert(
        count_matching_values(&pre, &probe) == count_matching_values(&v, &probe),
        "u64ten insert: backing10 count preserved",
    );
    kani::assert(StrictU64::probe() == probe, "u64ten insert: profile probe unchanged");
    let hits = count_matching_values(&pre, &probe);
    kani::cover(pre[9] < pre[0], "u64ten insert: tail becomes first");
    kani::cover(pre[8] <= pre[9], "u64ten insert: tail stays last");
    kani::cover(pre[0] < pre[9] && pre[9] < pre[8], "u64ten insert: interior insertion");
    kani::cover(pre[9] == pre[4], "u64ten insert: tail ties prefix value");
    kani::cover(!prefix_unchanged(&v, &pre, 0), "u64ten insert: output differs from input");
    kani::cover(hits > 0, "u64ten insert: probe hits backing10");
    kani::cover(hits == 0, "u64ten insert: probe misses backing10");
    kani::cover(probe >= (1u64 << 40) && hits > 0, "u64ten insert: high-bit probe hits backing10");
}

// U64-TEN-CALLER: opt-in child composing the actual u64 N10 route from the leaves above.
mod caller;
