//! Standalone ARRAYREPRO diagnostics. No proof result is claimed before CI.
//! D1/D2/F2/F5/F7 retain the in-tree function bodies and literal check messages.

#[cfg(kani)]
mod check {
    use std::{hint, ptr};

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

    #[kani::proof]
    #[kani::unwind(180)]
    fn arrayfactor_f2_if_bytes1() {
        let x: [u8; 1] = kani::any();
        let y: [u8; 1] = kani::any();
        let mut v = [x, y];
        let c: bool = kani::any();
        let base = v.as_mut_ptr();
        // SAFETY: position 1 is in bounds of the two-element array.
        let s = if c { base } else { unsafe { base.add(1) } };
        // SAFETY: `s` points to an initialized element of the live array.
        let got = unsafe { ptr::read(s) };
        let value_ok = got[0] == if c { x[0] } else { y[0] };
        kani::cover(c && x[0] != y[0], "arrayfactor F2: first selected, values differ");
        kani::cover(!c && x[0] != y[0], "arrayfactor F2: second selected, values differ");
        kani::assert(value_ok, "arrayfactor F2: read through if selection");
    }

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

    #[kani::proof]
    #[kani::unwind(180)]
    fn arrayfactor_f7_witness_bytes1() {
        let x: [u8; 1] = [1];
        let y: [u8; 1] = [2];
        let mut v = [x, y];
        let c: bool = kani::any();
        let base = v.as_mut_ptr();
        // SAFETY: position 1 is in bounds of the two-element array.
        let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
        // SAFETY: `s` points to an initialized element of the live array.
        let got = unsafe { ptr::read(s) };
        let first_ok = got[0] == x[0];
        let second_ok = got[0] == y[0];
        kani::cover(c && x[0] != y[0], "arrayfactor F7: first selected, values differ");
        kani::cover(!c && x[0] != y[0], "arrayfactor F7: second selected, values differ");
        if c {
            kani::assert(first_ok, "arrayfactor F7: first selected value");
        } else {
            kani::assert(second_ok, "arrayfactor F7: second selected value");
        }
    }

    // W exports a constrained observation as an any input; it is a separate experiment.
    #[kani::proof]
    #[kani::unwind(180)]
    fn arrayrepro_w_observed_bytes1() {
        let x: [u8; 1] = kani::any();
        let y: [u8; 1] = kani::any();
        let mut v = [x, y];
        let c: bool = kani::any();
        let base = v.as_mut_ptr();
        // SAFETY: position 1 is in bounds of the two-element array.
        let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
        // SAFETY: `s` points to an initialized element of the live array.
        let got = unsafe { ptr::read(s) };
        let observed: u8 = kani::any();
        kani::assume(observed == got[0]);
        kani::cover(c && x[0] != y[0], "arrayrepro W: first selected, values differ");
        kani::cover(!c && x[0] != y[0], "arrayrepro W: second selected, values differ");
        kani::assert(got[0] == if c { x[0] } else { y[0] }, "arrayrepro W: read through the selection");
    }

    // One classifying cover per harness makes the terse aggregate unambiguous.
    #[kani::proof]
    #[kani::unwind(180)]
    fn arrayrepro_cover_other_element_bytes1() {
        let x: [u8; 1] = kani::any();
        let y: [u8; 1] = kani::any();
        let mut v = [x, y];
        let c: bool = kani::any();
        let base = v.as_mut_ptr();
        // SAFETY: position 1 is in bounds of the two-element array.
        let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
        // SAFETY: `s` points to an initialized element of the live array.
        let got = unsafe { ptr::read(s) };
        kani::cover(c && x[0] != y[0] && got[0] == y[0], "arrayrepro C-other: first selected, read other element");
        kani::assert(got[0] == if c { x[0] } else { y[0] }, "arrayrepro C-other: read through the selection");
    }

    // One classifying cover per harness makes the terse aggregate unambiguous.
    #[kani::proof]
    #[kani::unwind(180)]
    fn arrayrepro_cover_neither_element_bytes1() {
        let x: [u8; 1] = kani::any();
        let y: [u8; 1] = kani::any();
        let mut v = [x, y];
        let c: bool = kani::any();
        let base = v.as_mut_ptr();
        // SAFETY: position 1 is in bounds of the two-element array.
        let s = hint::select_unpredictable(c, base, unsafe { base.add(1) });
        // SAFETY: `s` points to an initialized element of the live array.
        let got = unsafe { ptr::read(s) };
        kani::cover(c && x[0] != y[0] && got[0] != x[0] && got[0] != y[0], "arrayrepro C-neither: first selected, read neither element");
        kani::assert(got[0] == if c { x[0] } else { y[0] }, "arrayrepro C-neither: read through the selection");
    }
}
