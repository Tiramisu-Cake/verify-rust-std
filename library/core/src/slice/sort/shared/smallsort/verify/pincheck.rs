//! PINCHECK (`research/challenge-8/kani-k1/TASK-PINCHECK.md`): opt-in fixtures re-run on the
//! current Kani pin. The whole module is compiled only with `cfg(kani_smallsort_controls)`; it is
//! not part of the ordinary suite and claims no library property.
//! CASE5 rows, copied unchanged: D1 and D2 from CASE5-2 (`merge/casefive.rs`, d558b986c6) and
//! F5 from the standalone array-select reproduction (42ead2dba6, re-indented only). Uninit pilot
//! (run with `-Z uninit-checks`): a calibration pair that differs only in how `slot` is built,
//! and SPECDIAG's `raw_uninit_read_sensitivity` (4da5ec554a), copied unchanged.

use crate::mem::MaybeUninit;
use crate::{hint, kani, ptr};

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

/// F5: D1 with symbolic distinct indices for the two candidates (passing variant of D1 in the
/// standalone array-select reproduction).
#[kani::proof]
#[kani::unwind(180)]
fn arrayfactor_f5_symbolic_indices_bytes1() {
    let x: [u8; 1] = kani::any();
    let y: [u8; 1] = kani::any();
    let mut v = [x, y];
    let c: bool = kani::any();
    let r: bool = kani::any();
    let (i, j) = if r { (1, 0) } else { (0, 1) };
    let base = v.as_mut_ptr();
    // SAFETY: i and j are distinct in-bounds indices of the two-element array.
    let s = hint::select_unpredictable(c, unsafe { base.add(i) }, unsafe { base.add(j) });
    // SAFETY: `s` points to an initialized element of the live array.
    let got = unsafe { ptr::read(s) };
    let value_ok = got[0] == if c { [x, y][i][0] } else { [x, y][j][0] };
    kani::cover(c && x[0] != y[0], "arrayfactor F5: first selected, values differ");
    kani::cover(!c && x[0] != y[0], "arrayfactor F5: second selected, values differ");
    kani::cover(r && x[0] != y[0], "arrayfactor F5: indices 1 and 0, values differ");
    kani::cover(!r && x[0] != y[0], "arrayfactor F5: indices 0 and 1, values differ");
    kani::assert(value_ok, "arrayfactor F5: read through symbolic indices");
}

/// Uninit-check calibration: both rows read through this function; only the construction of
/// `slot` differs.
fn pincheck_read_slot(slot: MaybeUninit<u8>) -> u8 {
    // SAFETY: intentionally unchecked; the uninitialized calibration row violates it on purpose.
    unsafe { slot.assume_init() }
}

/// Calibration, failing half: reads a `MaybeUninit<u8>` that was never written.
#[kani::proof]
fn pincheck_calibration_uninit_read_u8() {
    let slot = MaybeUninit::<u8>::uninit();
    kani::cover(true, "pincheck calibration uninit: read reached");
    let value = pincheck_read_slot(slot);
    kani::cover(value == 0, "pincheck calibration uninit: read value zero");
    kani::cover(value != 0, "pincheck calibration uninit: read value nonzero");
}

/// Calibration, passing half: the same read of a `MaybeUninit<u8>` written with an arbitrary byte.
#[kani::proof]
fn pincheck_calibration_init_read_u8() {
    let x: u8 = kani::any();
    let slot = MaybeUninit::<u8>::new(x);
    kani::cover(true, "pincheck calibration init: read reached");
    let value = pincheck_read_slot(slot);
    kani::assert(value == x, "pincheck calibration init: read returns the written byte");
    kani::cover(value == 0, "pincheck calibration init: read value zero");
    kani::cover(value != 0, "pincheck calibration init: read value nonzero");
}

/// SPECDIAG row 17: a volatile read of an uninitialized `MaybeUninit<u8>` through `as_ptr`.
#[kani::proof]
fn raw_uninit_read_sensitivity() {
    let slot = MaybeUninit::<u8>::uninit();
    kani::cover(true, "specdiag raw uninitialized before volatile read");
    // SAFETY: intentionally violated, with dependent observations retaining the actual read.
    let value = unsafe { ptr::read_volatile(slot.as_ptr()) };
    kani::cover(value == 0, "specdiag raw uninitialized read value zero");
    kani::cover(value != 0, "specdiag raw uninitialized read value nonzero");
}
