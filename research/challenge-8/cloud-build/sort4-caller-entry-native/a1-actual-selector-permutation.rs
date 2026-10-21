#![no_std]
#![allow(dead_code)]

/*@
lem selector_permutation(
    c1: bool, c2: bool, c3: bool, c4: bool, c5: bool,
    ia: usize, ib: usize, ic: usize, id: usize,
    imin: usize, imax: usize, iul: usize, iur: usize,
    ilo: usize, ihi: usize)
    req
        ((c1 && ia == 1) || (!c1 && ia == 0)) &*&
        ((c1 && ib == 0) || (!c1 && ib == 1)) &*&
        ((c2 && ic == 3) || (!c2 && ic == 2)) &*&
        ((c2 && id == 2) || (!c2 && id == 3)) &*&
        ((c3 && imin == ic) || (!c3 && imin == ia)) &*&
        ((c4 && imax == ib) || (!c4 && imax == id)) &*&
        ((c3 && iul == ia) || (!c3 && c4 && iul == ic) || (!c3 && !c4 && iul == ib)) &*&
        ((c4 && iur == id) || (!c4 && c3 && iur == ib) || (!c4 && !c3 && iur == ic)) &*&
        ((c5 && ilo == iur) || (!c5 && ilo == iul)) &*&
        ((c5 && ihi == iul) || (!c5 && ihi == iur));
    ens
        0 <= imin &*& imin <= 3 &*&
        0 <= ilo &*& ilo <= 3 &*&
        0 <= ihi &*& ihi <= 3 &*&
        0 <= imax &*& imax <= 3 &*&
        imin != ilo &*& imin != ihi &*& imin != imax &*&
        ilo != ihi &*& ilo != imax &*& ihi != imax;
{
if (c1) {
    if (c2) {
        if (c3) {
            if (c4) {
                if (c5) {
                    assert imin == 3;
                    assert ilo == 2;
                    assert ihi == 1;
                    assert imax == 0;
                } else {
                    assert imin == 3;
                    assert ilo == 1;
                    assert ihi == 2;
                    assert imax == 0;
                }
            } else {
                if (c5) {
                    assert imin == 3;
                    assert ilo == 0;
                    assert ihi == 1;
                    assert imax == 2;
                } else {
                    assert imin == 3;
                    assert ilo == 1;
                    assert ihi == 0;
                    assert imax == 2;
                }
            }
        } else {
            if (c4) {
                if (c5) {
                    assert imin == 1;
                    assert ilo == 2;
                    assert ihi == 3;
                    assert imax == 0;
                } else {
                    assert imin == 1;
                    assert ilo == 3;
                    assert ihi == 2;
                    assert imax == 0;
                }
            } else {
                if (c5) {
                    assert imin == 1;
                    assert ilo == 3;
                    assert ihi == 0;
                    assert imax == 2;
                } else {
                    assert imin == 1;
                    assert ilo == 0;
                    assert ihi == 3;
                    assert imax == 2;
                }
            }
        }
    } else {
        if (c3) {
            if (c4) {
                if (c5) {
                    assert imin == 2;
                    assert ilo == 3;
                    assert ihi == 1;
                    assert imax == 0;
                } else {
                    assert imin == 2;
                    assert ilo == 1;
                    assert ihi == 3;
                    assert imax == 0;
                }
            } else {
                if (c5) {
                    assert imin == 2;
                    assert ilo == 0;
                    assert ihi == 1;
                    assert imax == 3;
                } else {
                    assert imin == 2;
                    assert ilo == 1;
                    assert ihi == 0;
                    assert imax == 3;
                }
            }
        } else {
            if (c4) {
                if (c5) {
                    assert imin == 1;
                    assert ilo == 3;
                    assert ihi == 2;
                    assert imax == 0;
                } else {
                    assert imin == 1;
                    assert ilo == 2;
                    assert ihi == 3;
                    assert imax == 0;
                }
            } else {
                if (c5) {
                    assert imin == 1;
                    assert ilo == 2;
                    assert ihi == 0;
                    assert imax == 3;
                } else {
                    assert imin == 1;
                    assert ilo == 0;
                    assert ihi == 2;
                    assert imax == 3;
                }
            }
        }
    }
} else {
    if (c2) {
        if (c3) {
            if (c4) {
                if (c5) {
                    assert imin == 3;
                    assert ilo == 2;
                    assert ihi == 0;
                    assert imax == 1;
                } else {
                    assert imin == 3;
                    assert ilo == 0;
                    assert ihi == 2;
                    assert imax == 1;
                }
            } else {
                if (c5) {
                    assert imin == 3;
                    assert ilo == 1;
                    assert ihi == 0;
                    assert imax == 2;
                } else {
                    assert imin == 3;
                    assert ilo == 0;
                    assert ihi == 1;
                    assert imax == 2;
                }
            }
        } else {
            if (c4) {
                if (c5) {
                    assert imin == 0;
                    assert ilo == 2;
                    assert ihi == 3;
                    assert imax == 1;
                } else {
                    assert imin == 0;
                    assert ilo == 3;
                    assert ihi == 2;
                    assert imax == 1;
                }
            } else {
                if (c5) {
                    assert imin == 0;
                    assert ilo == 3;
                    assert ihi == 1;
                    assert imax == 2;
                } else {
                    assert imin == 0;
                    assert ilo == 1;
                    assert ihi == 3;
                    assert imax == 2;
                }
            }
        }
    } else {
        if (c3) {
            if (c4) {
                if (c5) {
                    assert imin == 2;
                    assert ilo == 3;
                    assert ihi == 0;
                    assert imax == 1;
                } else {
                    assert imin == 2;
                    assert ilo == 0;
                    assert ihi == 3;
                    assert imax == 1;
                }
            } else {
                if (c5) {
                    assert imin == 2;
                    assert ilo == 1;
                    assert ihi == 0;
                    assert imax == 3;
                } else {
                    assert imin == 2;
                    assert ilo == 0;
                    assert ihi == 1;
                    assert imax == 3;
                }
            }
        } else {
            if (c4) {
                if (c5) {
                    assert imin == 0;
                    assert ilo == 3;
                    assert ihi == 2;
                    assert imax == 1;
                } else {
                    assert imin == 0;
                    assert ilo == 2;
                    assert ihi == 3;
                    assert imax == 1;
                }
            } else {
                if (c5) {
                    assert imin == 0;
                    assert ilo == 2;
                    assert ihi == 1;
                    assert imax == 3;
                } else {
                    assert imin == 0;
                    assert ilo == 1;
                    assert ihi == 2;
                    assert imax == 3;
                }
            }
        }
    }
}
    // Each of the 32 explicit selector cases has the four distinct output
    // constants 0, 1, 2, and 3; the contract also states every output bound.
}

lem selector_wrong_minimum_post_negative(
    c1: bool, c2: bool, c3: bool, c4: bool, c5: bool,
    ia: usize, ib: usize, ic: usize, id: usize,
    imin: usize, imax: usize, iul: usize, iur: usize,
    ilo: usize, ihi: usize)
    req
        ((c1 && ia == 1) || (!c1 && ia == 0)) &*&
        ((c1 && ib == 0) || (!c1 && ib == 1)) &*&
        ((c2 && ic == 3) || (!c2 && ic == 2)) &*&
        ((c2 && id == 2) || (!c2 && id == 3)) &*&
        ((c3 && imin == ic) || (!c3 && imin == ia)) &*&
        ((c4 && imax == ib) || (!c4 && imax == id)) &*&
        ((c3 && iul == ia) || (!c3 && c4 && iul == ic) || (!c3 && !c4 && iul == ib)) &*&
        ((c4 && iur == id) || (!c4 && c3 && iur == ib) || (!c4 && !c3 && iur == ic)) &*&
        ((c5 && ilo == iur) || (!c5 && ilo == iul)) &*&
        ((c5 && ihi == iul) || (!c5 && ihi == iur));
    ens imin == 4;
{
    selector_permutation(c1, c2, c3, c4, c5,
        ia, ib, ic, id, imin, imax, iul, iur, ilo, ihi);
    // Expected negative: the selector lemma establishes imin <= 3, so this
    // deliberately incorrect selected-index postcondition must fail.
    assert imin == 4;
}
@*/

// Generic target anchor only; it adds no comparator, ownership, layout, or
// element-size assumption to the selector lemma.
#[allow(dead_code)]
pub fn r15_selector_permutation_type_anchor<T>(base: *const T) {
    let _ = base;
}
