//! CASE5 diagnostic (`research/challenge-8/kani-k1/TASK-CASEFIVE.md`): the real `swap_if_less`
//! on two arbitrary `[u8; M]` values against the expected conditional move. R0 repeats specfix
//! case5 with its own messages; R1-R7 each change one factor of R0: taken only, not taken only,
//! fn pointer, M = 1, one executable assert, snapshot oracle, reference move without
//! `swap_if_less`. The whole module is opt-in (`kani_smallsort_controls`); every `kani::assert`
//! message is unique to its row. On the pinned Kani a `kani::assert` is assert-assume: later
//! checks and covers only see paths on which every earlier assert held.
//! Not a negative control and not a claimed library or Kani defect.
//! CASE5-2 (`TASK-CASEFIVETWO.md`) appends A1/A2 (plain profile and raw call in the profile
//! fixture), P17/P16/S4 (contract proofs of instrumented twins of the array-model profiles), C1
//! (negative control: a wrong body under the swap profile contract) and D1/D2 (reproducer).

use super::super::network::{KeyB16, KeyB17};
use super::specfix::{
    Profile, Sort4ReadB16, model_count, model_sorted, pair_models, sort4_regions,
    specfix_canonical_comparator, swap_geometry, swap_ordered, swap_profile, swap_transfer,
};
use crate::mem::{ManuallyDrop, MaybeUninit, size_of};
use crate::slice::sort::shared::smallsort::{sort4_stable, swap_if_less};
use crate::{hint, kani, ptr};

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

// G2 (after G1, separate GO): G2B replays the body of `swap_if_less` step by step, G2C keeps only
// the array `==` oracle, G2D runs R0 on `u8` elements. Byte comparisons below avoid array `==`.

/// Byte-wise equality without `PartialEq for [u8; M]`.
fn casefive_bytes_eq<const M: usize>(a: &[u8; M], b: &[u8; M]) -> bool {
    let mut i = 0;
    while i < M {
        if a[i] != b[i] {
            return false;
        }
        i += 1;
    }
    true
}

/// G2B: R0 with the call replaced by the statements of `swap_if_less` (same std calls, same
/// order), each followed by its own assert; the first failing step localizes the divergence.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_g2b_replica_steps_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = y[0] < x[0];
    let base = v.as_mut_ptr();
    // SAFETY: as `swap_if_less` with positions 0 and 1 of one initialized writable array.
    unsafe {
        let v_a = base.add(0);
        let v_b = base.add(1);
        let should_swap = cmp(&*v_b, &*v_a);
        kani::assert(should_swap == taken, "casefive G2B: step 1 decision == taken");
        let v_a_swap = hint::select_unpredictable(should_swap, v_b, v_a);
        let v_b_swap = hint::select_unpredictable(should_swap, v_a, v_b);
        kani::assert(
            v_a_swap == if taken { v_b } else { v_a },
            "casefive G2B: step 2 first select",
        );
        kani::assert(
            v_b_swap == if taken { v_a } else { v_b },
            "casefive G2B: step 3 second select",
        );
        let v_b_swap_tmp = ManuallyDrop::new(ptr::read(v_b_swap));
        kani::assert(
            casefive_bytes_eq(&*v_b_swap_tmp, if taken { &x } else { &y }),
            "casefive G2B: step 4 read of the second selection",
        );
        ptr::copy(v_a_swap, v_a, 1);
        kani::assert(
            casefive_bytes_eq(&*v_a, if taken { &y } else { &x }),
            "casefive G2B: step 5 position 0 after copy",
        );
        ptr::copy_nonoverlapping(&*v_b_swap_tmp, v_b, 1);
        kani::assert(
            casefive_bytes_eq(&*v_b, if taken { &x } else { &y }),
            "casefive G2B: step 6 position 1 after copy_nonoverlapping",
        );
    }
    kani::cover(taken, "casefive G2B: swap taken");
    kani::cover(!taken, "casefive G2B: swap not taken");
}

/// G2C: R0 without the component checks: only the original array `==` oracle. With the move
/// diverging in both branches (G1), a sound `==` must fail here.
#[kani::proof]
#[kani::unwind(140)]
fn casefive_g2c_array_eq_only_bytes17() {
    let x: [u8; 17] = kani::any();
    let y: [u8; 17] = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &[u8; 17], b: &[u8; 17]| a[0] < b[0];
    let taken = y[0] < x[0];
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    kani::cover(taken, "casefive G2C: swap taken");
    kani::cover(!taken, "casefive G2C: swap not taken");
    let ok = if taken { v[0] == y && v[1] == x } else { v[0] == x && v[1] == y };
    kani::assert(ok, "casefive G2C: array == oracle");
}

/// G2D: R0 on `u8` elements (the scalar the P1 network and swap proofs pass on).
#[kani::proof]
#[kani::unwind(140)]
fn casefive_g2d_closure_u8() {
    let x: u8 = kani::any();
    let y: u8 = kani::any();
    let mut v = [x, y];
    let mut cmp = |a: &u8, b: &u8| *a < *b;
    let taken = y < x;
    // SAFETY: distinct initialized writable positions of one array; no probe is involved.
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut cmp) };
    let (want_a, want_b) = if taken { (y, x) } else { (x, y) };
    kani::assert(v[0] == want_a, "casefive G2D: component oracle position 0");
    kani::assert(v[1] == want_b, "casefive G2D: component oracle position 1");
    kani::cover(taken, "casefive G2D: swap taken");
    kani::cover(!taken, "casefive G2D: swap not taken");
}

// CASE5-2: can the array-model profile contract proofs (KeyB17, KeyB16, Sort4ReadB16) be trusted?
// Swap rows use the `swap_contract_fixed` fixture form: `array::from_fn`, `reverse` positions,
// `P::CMP`. The pre-state is snapshot after `v` exists; expectations are checked at positions a
// and b. Covers come before every check; checks are folded into booleans until then.

/// Byte-wise equality of `n` bytes behind two `u8` pointers (no `PartialEq`, no aggregate copy).
///
/// # Safety
/// Both pointers must be readable for `n` initialized bytes.
unsafe fn casefive_buf_eq(p: *const u8, q: *const u8, n: usize) -> bool {
    let mut i = 0;
    while i < n {
        // SAFETY: `i < n`; the caller guarantees `n` readable initialized bytes behind both.
        if unsafe { *p.add(i) != *q.add(i) } {
            return false;
        }
        i += 1;
    }
    true
}

/// A1: the plain profile wrapper `swap_profile::<KeyB17>` (its contract is not the target here)
/// in the PFC fixture; the array `==` oracle and the byte-wise oracle are computed side by side.
#[kani::proof]
#[kani::unwind(180)]
fn casefive_a1_plain_profile_bytes17() {
    let mut v: [[u8; 17]; 2] = crate::array::from_fn(|_| kani::any());
    let pre = v;
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    let taken = (KeyB17::CMP)(&pre[b], &pre[a]);
    // SAFETY: a and b are distinct initialized writable elements of the live exact array; the
    // comparator is the profile's canonical `KeyB17::CMP`.
    unsafe { swap_profile::<KeyB17>(v.as_mut_ptr(), a, b, KeyB17::CMP) };
    let (want_a, want_b) = if taken { (&pre[b], &pre[a]) } else { (&pre[a], &pre[b]) };
    let eq_ok = v[a] == *want_a && v[b] == *want_b;
    let bytes_ok = casefive_bytes_eq(&v[a], want_a) && casefive_bytes_eq(&v[b], want_b);
    kani::cover(true, "casefive A1: reached after the call");
    kani::cover(reverse, "casefive A1: indices 1 and 0");
    kani::cover(!reverse, "casefive A1: indices 0 and 1");
    kani::cover(taken, "casefive A1: swap taken");
    kani::cover(!taken, "casefive A1: swap not taken");
    kani::cover(pre[a][1] != pre[b][1], "casefive A1: payload byte 1 differs");
    kani::cover(!taken && pre[a][1] != pre[b][1], "casefive A1: not taken, payload differs");
    kani::assert(eq_ok == bytes_ok, "casefive A1: array == agrees with the byte-wise oracle");
    kani::assert(bytes_ok, "casefive A1: byte-wise transfer at positions a and b");
}

/// A2: A1 with the raw call `swap_if_less(.., &mut KeyB17::CMP)` (matched raw baseline): the
/// same call `swap_profile` makes, without the wrapper.
#[kani::proof]
#[kani::unwind(180)]
fn casefive_a2_raw_call_bytes17() {
    let mut v: [[u8; 17]; 2] = crate::array::from_fn(|_| kani::any());
    let pre = v;
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    let taken = (KeyB17::CMP)(&pre[b], &pre[a]);
    let mut is_less = KeyB17::CMP;
    // SAFETY: a and b are distinct initialized writable elements of the live exact array.
    unsafe { swap_if_less(v.as_mut_ptr(), a, b, &mut is_less) };
    let (want_a, want_b) = if taken { (&pre[b], &pre[a]) } else { (&pre[a], &pre[b]) };
    let eq_ok = v[a] == *want_a && v[b] == *want_b;
    let bytes_ok = casefive_bytes_eq(&v[a], want_a) && casefive_bytes_eq(&v[b], want_b);
    kani::cover(true, "casefive A2: reached after the call");
    kani::cover(reverse, "casefive A2: indices 1 and 0");
    kani::cover(!reverse, "casefive A2: indices 0 and 1");
    kani::cover(taken, "casefive A2: swap taken");
    kani::cover(!taken, "casefive A2: swap not taken");
    kani::cover(pre[a][1] != pre[b][1], "casefive A2: payload byte 1 differs");
    kani::cover(!taken && pre[a][1] != pre[b][1], "casefive A2: not taken, payload differs");
    kani::assert(eq_ok == bytes_ok, "casefive A2: array == agrees with the byte-wise oracle");
    kani::assert(bytes_ok, "casefive A2: byte-wise transfer at positions a and b");
}

/// Byte capacity of the swap twin's snapshots (`[u8; 16]` and `[u8; 17]` here).
const CASEFIVE_SWAP_CAP: usize = 32;

/// P17/P16 target: `swap_profile` with the same requires/modifies/ensures and the same real
/// `swap_if_less` call, plus independent byte-wise checks inside the target. Only for padding-free
/// `P::Elem` of at most `CASEFIVE_SWAP_CAP` bytes. The pre-state is copied byte by byte into local
/// buffers and, separately, read typed (plain `ptr::read`, no selected pointer).
#[kani::requires(swap_geometry::<P::Elem>(v, a, b))]
#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<P>(v, a, b))]
unsafe fn swap_profile_checked<P: Profile>(
    v: *mut P::Elem,
    a: usize,
    b: usize,
    cmp: fn(&P::Elem, &P::Elem) -> bool,
) {
    let n = size_of::<P::Elem>();
    let size_ok = n <= CASEFIVE_SWAP_CAP;
    let n = if size_ok { n } else { 0 };
    // SAFETY: the requires make a and b distinct readable initialized writable elements of one
    // allocation; the buffers hold `n <= CASEFIVE_SWAP_CAP` bytes; `is_less` is `P::CMP`.
    unsafe {
        let (va, vb) = (v.add(a), v.add(b));
        let mut pre_a = [0u8; CASEFIVE_SWAP_CAP];
        let mut pre_b = [0u8; CASEFIVE_SWAP_CAP];
        let mut i = 0;
        while i < n {
            pre_a[i] = *(va as *const u8).add(i);
            pre_b[i] = *(vb as *const u8).add(i);
            i += 1;
        }
        let typed_a = ManuallyDrop::new(ptr::read(va));
        let typed_b = ManuallyDrop::new(ptr::read(vb));
        let ta = &*typed_a as *const P::Elem as *const u8;
        let tb = &*typed_b as *const P::Elem as *const u8;
        let pre_ok = casefive_buf_eq(pre_a.as_ptr(), va as *const u8, n)
            && casefive_buf_eq(pre_b.as_ptr(), vb as *const u8, n)
            && casefive_buf_eq(pre_a.as_ptr(), ta, n)
            && casefive_buf_eq(pre_b.as_ptr(), tb, n);
        let taken = P::model_less(&P::model(&*typed_b), &P::model(&*typed_a));
        let equal_keys = !taken && !P::model_less(&P::model(&*typed_a), &P::model(&*typed_b));
        let same_value = casefive_buf_eq(pre_a.as_ptr(), pre_b.as_ptr(), n);
        let mut is_less = cmp;
        swap_if_less(v, a, b, &mut is_less);
        kani::cover(true, "casefive swap twin: reached after swap_if_less");
        kani::cover(a > b, "casefive swap twin: indices a > b");
        kani::cover(a < b, "casefive swap twin: indices a < b");
        kani::cover(taken, "casefive swap twin: swap taken");
        kani::cover(!taken && !same_value, "casefive swap twin: not taken, values differ");
        kani::cover(equal_keys && !same_value, "casefive swap twin: equal keys, values differ");
        let (want_a, want_b) =
            if taken { (pre_b.as_ptr(), pre_a.as_ptr()) } else { (pre_a.as_ptr(), pre_b.as_ptr()) };
        let now_a = casefive_buf_eq(want_a, va as *const u8, n);
        let now_b = casefive_buf_eq(want_b, vb as *const u8, n);
        let kept = casefive_buf_eq(pre_a.as_ptr(), ta, n) && casefive_buf_eq(pre_b.as_ptr(), tb, n);
        kani::assert(size_ok, "casefive swap twin: element fits the snapshot buffers");
        kani::assert(pre_ok, "casefive swap twin: byte and typed snapshots match the slots");
        kani::assert(now_a, "casefive swap twin: byte-wise transfer at position a");
        kani::assert(now_b, "casefive swap twin: byte-wise transfer at position b");
        kani::assert(kept, "casefive swap twin: snapshots unchanged by the call");
    }
}

/// `swap_contract_fixed` for the twin: same fixture, target `swap_profile_checked::<P>`.
fn casefive_swap_twin_fixed<P: Profile>()
where
    P::Elem: kani::Arbitrary,
{
    let mut v: [P::Elem; 2] = crate::array::from_fn(|_| kani::any());
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    // SAFETY: a and b are distinct initialized writable elements of the live exact array.
    unsafe { swap_profile_checked::<P>(v.as_mut_ptr(), a, b, P::CMP) };
    kani::cover(true, "casefive swap twin fixture: reached the end");
}

/// P17: contract proof of the instrumented twin for KeyB17.
#[kani::proof_for_contract(swap_profile_checked)]
#[kani::unwind(180)]
fn casefive_p17_checked_contract_bytes17() {
    casefive_swap_twin_fixed::<KeyB17>();
}

/// P16: contract proof of the instrumented twin for KeyB16.
#[kani::proof_for_contract(swap_profile_checked)]
#[kani::unwind(180)]
fn casefive_p16_checked_contract_bytes16() {
    casefive_swap_twin_fixed::<KeyB16>();
}

/// Byte capacity of the sort4 twin's source snapshot (4 x `[u8; 16]` here).
const CASEFIVE_SORT4_CAP: usize = 64;

/// Number of the 4 elements behind `base` (stride `n` bytes) that equal the `n` bytes at `x`.
///
/// # Safety
/// `base` must be readable for `4 * n` initialized bytes and `x` for `n`.
unsafe fn casefive_count4(base: *const u8, n: usize, x: *const u8) -> usize {
    let mut c = 0;
    let mut j = 0;
    while j < 4 {
        // SAFETY: `j < 4`; the caller guarantees the regions.
        if unsafe { casefive_buf_eq(base.add(j * n), x, n) } {
            c += 1;
        }
        j += 1;
    }
    c
}

/// S4 target: `sort4_profile` with the same requires/modifies/ensures and the same real
/// `sort4_stable` call, plus independent byte-wise checks inside the target: every output equals
/// some input byte-wise, byte-wise value counts are kept, keys are ordered. Only for padding-free
/// `P::Elem` with `4 * size <= CASEFIVE_SORT4_CAP`.
#[kani::requires(sort4_regions::<P::Elem>(src, dst))]
#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::modifies(ptr::slice_from_raw_parts_mut(dst, 4))]
#[kani::ensures(|_| model_sorted::<P>(dst, 4))]
#[kani::ensures(|_| model_count::<P>(src, 4) == model_count::<P>(dst, 4))]
unsafe fn sort4_profile_checked<P: Profile>(
    src: *const P::Elem,
    dst: *mut P::Elem,
    cmp: fn(&P::Elem, &P::Elem) -> bool,
) {
    let n = size_of::<P::Elem>();
    let size_ok = 4 * n <= CASEFIVE_SORT4_CAP;
    let n = if size_ok { n } else { 0 };
    // SAFETY: the requires make `src[..4]` readable initialized and `dst[..4]` writable and
    // disjoint; the buffer holds `4 * n <= CASEFIVE_SORT4_CAP` bytes; `is_less` is `P::CMP`.
    unsafe {
        let s = src as *const u8;
        let d = dst as *const u8;
        let mut pre = [0u8; CASEFIVE_SORT4_CAP];
        let mut i = 0;
        while i < 4 * n {
            pre[i] = *s.add(i);
            i += 1;
        }
        let pre_ok = casefive_buf_eq(pre.as_ptr(), s, 4 * n);
        let mut equal_keys_differ = false;
        let mut unsorted = false;
        let mut j = 1;
        while j < 4 {
            let (x, y) = (P::model(&*src.add(j - 1)), P::model(&*src.add(j)));
            unsorted |= P::model_less(&y, &x);
            equal_keys_differ |= !P::model_less(&x, &y)
                && !P::model_less(&y, &x)
                && !casefive_buf_eq(s.add((j - 1) * n), s.add(j * n), n);
            j += 1;
        }
        let mut is_less = cmp;
        sort4_stable(src, dst, &mut is_less);
        kani::cover(true, "casefive sort4 twin: reached after sort4_stable");
        kani::cover(unsorted, "casefive sort4 twin: input out of key order");
        kani::cover(equal_keys_differ, "casefive sort4 twin: adjacent equal keys, values differ");
        let src_kept = casefive_buf_eq(pre.as_ptr(), s, 4 * n);
        let mut each_from_input = true;
        let mut counts_kept = true;
        let mut ordered = true;
        let mut k = 0;
        while k < 4 {
            let out = d.add(k * n);
            let inp = pre.as_ptr().add(k * n);
            each_from_input &= casefive_count4(pre.as_ptr(), n, out) > 0;
            counts_kept &= casefive_count4(d, n, out) == casefive_count4(pre.as_ptr(), n, out);
            counts_kept &= casefive_count4(d, n, inp) == casefive_count4(pre.as_ptr(), n, inp);
            if k > 0 {
                let (x, y) = (P::model(&*dst.add(k - 1)), P::model(&*dst.add(k)));
                ordered &= !P::model_less(&y, &x);
            }
            k += 1;
        }
        kani::assert(size_ok, "casefive sort4 twin: elements fit the snapshot buffer");
        kani::assert(pre_ok, "casefive sort4 twin: byte snapshot matches the source");
        kani::assert(src_kept, "casefive sort4 twin: source bytes unchanged by the call");
        kani::assert(each_from_input, "casefive sort4 twin: every output equals some input");
        kani::assert(counts_kept, "casefive sort4 twin: byte-wise value counts kept");
        kani::assert(ordered, "casefive sort4 twin: output keys ordered");
    }
}

/// S4: contract proof of the instrumented sort4 twin, fixture of `sort4_contract_bytes16_n4`.
#[kani::proof_for_contract(sort4_profile_checked)]
#[kani::unwind(180)]
fn casefive_s4_checked_contract_bytes16() {
    Sort4ReadB16::set_probe(kani::any());
    let v: [[u8; 16]; 4] = kani::any();
    let mut dst = MaybeUninit::<[[u8; 16]; 4]>::uninit();
    // SAFETY: the profile contract is checked by the enclosing proof_for_contract harness.
    unsafe {
        sort4_profile_checked::<Sort4ReadB16>(
            v.as_ptr(),
            dst.as_mut_ptr() as *mut [u8; 16],
            Sort4ReadB16::CMP,
        )
    };
    kani::cover(true, "casefive S4: four-element stable sort returns");
}

/// C1 target: a deliberately wrong body under the unchanged swap profile contract. It writes the
/// old value at b into both positions: no selected pointer, no UB (`[u8; M]` has no destructor).
/// With equal keys and different values only the transfer ensures can fail.
#[kani::requires(swap_geometry::<P::Elem>(v, a, b))]
#[kani::requires(specfix_canonical_comparator::<P>(cmp))]
#[kani::modifies(v.wrapping_add(a), v.wrapping_add(b))]
#[kani::ensures(|_| swap_transfer::<P>(old(pair_models::<P>(v, a, b)), v, a, b))]
#[kani::ensures(|_| swap_ordered::<P>(v, a, b))]
unsafe fn bad_swap_profile<P: Profile>(
    v: *mut P::Elem,
    a: usize,
    b: usize,
    cmp: fn(&P::Elem, &P::Elem) -> bool,
) {
    let _ = cmp;
    // SAFETY: the requires make a and b distinct readable initialized writable elements.
    unsafe {
        let old_b = ManuallyDrop::new(ptr::read(v.add(b)));
        ptr::copy_nonoverlapping(&*old_b, v.add(a), 1);
        ptr::copy_nonoverlapping(&*old_b, v.add(b), 1);
    }
    kani::cover(true, "casefive C1: wrong body returned");
}

/// C1: negative control. Expected FAILED on the transfer ensures only; SUCCESS with the witness
/// cover satisfied would discredit the contract check.
#[kani::proof_for_contract(bad_swap_profile)]
#[kani::unwind(180)]
fn casefive_c1_bad_body_contract_bytes17() {
    let mut v: [[u8; 17]; 2] = crate::array::from_fn(|_| kani::any());
    let reverse: bool = kani::any();
    let (a, b) = if reverse { (1, 0) } else { (0, 1) };
    kani::cover(reverse, "casefive C1: indices 1 and 0");
    kani::cover(!reverse, "casefive C1: indices 0 and 1");
    kani::cover(
        v[a][0] == v[b][0] && v[a][1] != v[b][1],
        "casefive C1: witness equal key, byte 1 differs",
    );
    // SAFETY: a and b are distinct initialized writable elements of the live exact array.
    unsafe { bad_swap_profile::<KeyB17>(v.as_mut_ptr(), a, b, KeyB17::CMP) };
}

/// D1: minimal reproducer candidate: one read through a pointer chosen by `select_unpredictable`
/// over a two-element `[[u8; 1]; 2]` array. One base pointer for both candidates (as in
/// `swap_if_less`), so no second `&mut` reborrow of `v` is involved.
#[kani::proof]
#[kani::unwind(180)]
fn casefive_d1_select_read_bytes1() {
    let x: [u8; 1] = kani::any();
    let y: [u8; 1] = kani::any();
    let mut v = [x, y];
    let c: bool = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: position 1 is in bounds of the two-element array.
    let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
    // SAFETY: `s` points to an initialized element of the live array.
    let got = unsafe { ptr::read(s) };
    kani::cover(c && x[0] != y[0], "casefive D1: first selected, values differ");
    kani::cover(!c && x[0] != y[0], "casefive D1: second selected, values differ");
    kani::assert(got[0] == if c { x[0] } else { y[0] }, "casefive D1: read through the selection");
}

/// D2: D1 on `u8` elements (scalar control).
#[kani::proof]
#[kani::unwind(180)]
fn casefive_d2_select_read_u8() {
    let x: u8 = kani::any();
    let y: u8 = kani::any();
    let mut v = [x, y];
    let c: bool = kani::any();
    let base = v.as_mut_ptr();
    // SAFETY: position 1 is in bounds of the two-element array.
    let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
    // SAFETY: `s` points to an initialized element of the live array.
    let got = unsafe { ptr::read(s) };
    kani::cover(c && x != y, "casefive D2: first selected, values differ");
    kani::cover(!c && x != y, "casefive D2: second selected, values differ");
    kani::assert(got == if c { x } else { y }, "casefive D2: read through the selection");
}
