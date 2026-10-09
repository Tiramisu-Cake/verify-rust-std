#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

extern "Rust" {
    fn origin_plain_never(value: u64) -> !;
    //@ req true;
    //@ ens false;
}

pub unsafe fn origin_plain_diverge() -> u64
/*@ req true; @*/ /*@ ens false; @*/ {
    let local = 7_u64;
    unsafe { origin_plain_never(local) } // TARGET: plain diverging extern call
}
