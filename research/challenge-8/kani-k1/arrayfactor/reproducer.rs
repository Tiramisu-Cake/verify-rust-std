// Local verify-std module fragment: exact D1/D2 controls; see REPRODUCER.md.
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
