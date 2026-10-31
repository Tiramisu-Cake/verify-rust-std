//! CASE5 diagnostic (`research/challenge-8/kani-k1/TASK-CASEFIVE.md`): the real `swap_if_less`
//! on two arbitrary `[u8; M]` values against the expected conditional move. R0 repeats specfix
//! case5 with its own messages; R1-R7 each change one factor of R0: taken only, not taken only,
//! fn pointer, M = 1, one executable assert, snapshot oracle, reference move without
//! `swap_if_less`. The whole module is opt-in (`kani_smallsort_controls`); every `kani::assert`
//! message is unique to its row. On the pinned Kani a `kani::assert` is assert-assume: later
//! checks and covers only see paths on which every earlier assert held.
//! Not a negative control and not a claimed library or Kani defect.

use crate::slice::sort::shared::smallsort::swap_if_less;
use crate::{kani, ptr};

/// The case5 order as a named function: key byte 0, the other bytes are payload.
fn case5_key_less_b17(a: &[u8; 17], b: &[u8; 17]) -> bool {
    a[0] < b[0]
}

// R0 (exact copy of specfix case5) and R4 (R0 at M = 1).
macro_rules! casefive_closure_swap {
    ($name:ident, $row:literal, $m:literal) => {
        #[kani::proof]
        #[kani::unwind(140)]
        fn $name() {
            let x: [u8; $m] = kani::any();
            let y: [u8; $m] = kani::any();
            let mut v = [x, y];
            let mut cmp = |a: &[u8; $m], b: &[u8; $m]| a[0] < b[0];
            let taken = y[0] < x[0];
            // SAFETY: distinct initialized writable positions of one array; no probe is involved.
            unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
            let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
            let mut i = 0;
            while i < $m {
                kani::assert(
                    v[0][i] == want_a[i],
                    concat!("casefive ", $row, ": component oracle position 0"),
                );
                kani::assert(
                    v[1][i] == want_b[i],
                    concat!("casefive ", $row, ": component oracle position 1"),
                );
                i += 1;
            }
            kani::cover(taken, concat!("casefive ", $row, ": swap taken"));
            kani::cover(!taken, concat!("casefive ", $row, ": swap not taken"));
            let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
            kani::assert(ok, concat!("casefive ", $row, ": array == oracle"));
        }
    };
}

casefive_closure_swap!(casefive_r0_closure_bytes17, "R0", 17);
casefive_closure_swap!(casefive_r4_closure_bytes1, "R4", 1);

/// R1: R0 restricted to the taken branch before the call. The first cover (after the call, before
/// any assert) shows the branch is reached; the second (R0's cover) that some path passes every
/// component check. The not-taken cover would be unsatisfiable by construction and is omitted.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r1_taken_only_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = y[0] < x[0];
    kani::assume(taken);
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(taken, "casefive R1 taken: reached after the call");
    let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
    let mut i = 0;
    while i < 17 {
        kani::assert(v[0][i] == want_a[i], "casefive R1 taken: component oracle position 0");
        kani::assert(v[1][i] == want_b[i], "casefive R1 taken: component oracle position 1");
        i += 1;
    }
    kani::cover(taken, "casefive R1 taken: every component check held");
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "casefive R1 taken: array == oracle");
}

/// R2: R1 for the not-taken branch (`x[0] <= y[0]`, including equal keys).
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r2_not_taken_only_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = y[0] < x[0];
    kani::assume(!taken);
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(!taken, "casefive R2 not taken: reached after the call");
    let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
    let mut i = 0;
    while i < 17 {
        kani::assert(v[0][i] == want_a[i], "casefive R2 not taken: component oracle position 0");
        kani::assert(v[1][i] == want_b[i], "casefive R2 not taken: component oracle position 1");
        i += 1;
    }
    kani::cover(!taken, "casefive R2 not taken: every component check held");
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "casefive R2 not taken: array == oracle");
}

/// R3: R0 with a function pointer comparator (`F = fn(..) -> bool`, not a function item).
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r3_fn_pointer_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp: fn(&[u8; 17], &[u8; 17]) -> bool = case5_key_less_b17;
    let taken = y[0] < x[0];
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
    let mut i = 0;
    while i < 17 {
        kani::assert(v[0][i] == want_a[i], "casefive R3: component oracle position 0");
        kani::assert(v[1][i] == want_b[i], "casefive R3: component oracle position 1");
        i += 1;
    }
    kani::cover(taken, "casefive R3: swap taken");
    kani::cover(!taken, "casefive R3: swap not taken");
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "casefive R3: array == oracle");
}

/// R5: R0 with the component results folded into booleans (no assert before the covers), then
/// both branch covers, then exactly one executable assert per path, labelled by branch.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r5_single_assert_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = y[0] < x[0];
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    let mut ok_taken = true;
    let mut ok_not_taken = true;
    let mut i = 0;
    while i < 17 {
        ok_taken &= v[0][i] == y[i] && v[1][i] == x[i];
        ok_not_taken &= v[0][i] == x[i] && v[1][i] == y[i];
        i += 1;
    }
    kani::cover(taken, "casefive R5: swap taken");
    kani::cover(!taken, "casefive R5: swap not taken");
    if taken {
        kani::assert(ok_taken, "casefive R5: single oracle [taken]");
    } else {
        kani::assert(ok_not_taken, "casefive R5: single oracle [not taken]");
    }
}

/// R6: R0 with the decision and the expectation taken from a snapshot `pre` of the array.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r6_snapshot_oracle_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let pre = v;
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = pre[1][0] < pre[0][0];
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    let (want_a, want_b) = if taken { (pre[1], pre[0]) } else { (pre[0], pre[1]) };
    let mut i = 0;
    while i < 17 {
        kani::assert(v[0][i] == want_a[i], "casefive R6: component oracle position 0");
        kani::assert(v[1][i] == want_b[i], "casefive R6: component oracle position 1");
        i += 1;
    }
    kani::cover(taken, "casefive R6: swap taken");
    kani::cover(!taken, "casefive R6: swap not taken");
    let ok =
        if taken { v[0] == pre[1] && v[1] == pre[0] } else { v[0] == pre[0] && v[1] == pre[1] };
    kani::assert(ok, "casefive R6: array == oracle");
}

/// R7: reference. R0's fixture and oracle, with `if taken { ptr::swap }` in place of
/// `swap_if_less`: a pass here and a failure in R0 put the difference in the executed move.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_r7_reference_move_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let taken = y[0] < x[0];
    let base = v.as_mut_ptr();
    if taken {
        // SAFETY: two distinct initialized writable elements of one live array.
        unsafe { ptr::swap(base, base.add(1)) };
    }
    let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
    let mut i = 0;
    while i < 17 {
        kani::assert(v[0][i] == want_a[i], "casefive R7: component oracle position 0");
        kani::assert(v[1][i] == want_b[i], "casefive R7: component oracle position 1");
        i += 1;
    }
    kani::cover(taken, "casefive R7: swap taken");
    kani::cover(!taken, "casefive R7: swap not taken");
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "casefive R7: array == oracle");
}
