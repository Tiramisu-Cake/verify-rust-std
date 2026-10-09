#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

pub unsafe fn origin_unit_runtime_layout()
/*@ req true; @*/ /*@ ens true; @*/ {
    let runtime_size = core::mem::size_of::<()>();
    //@ assert runtime_size == 0; // TARGET: runtime concrete unit size zero
}
