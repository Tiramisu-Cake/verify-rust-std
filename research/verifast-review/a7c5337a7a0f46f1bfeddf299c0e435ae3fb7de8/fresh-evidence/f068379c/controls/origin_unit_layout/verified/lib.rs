#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

pub unsafe fn origin_unit_layout()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ assert std::mem::size_of::<()>() == 0; // TARGET: concrete unit size zero
}
