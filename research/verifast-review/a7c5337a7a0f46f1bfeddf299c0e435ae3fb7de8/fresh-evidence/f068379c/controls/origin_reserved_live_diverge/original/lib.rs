#![no_std]
#![allow(dead_code)]

// Each case is extracted with this common header and its one delimited body.
// The extern cases intentionally retain their exact reserved symbol spelling.

extern "Rust" {
    fn vf__rust_storage_live(value: u64) -> !;
}
/*@
fn vf__rust_storage_live(value: u64) -> !;
req true;
ens false;
on_unwind_ens false;
@*/

pub unsafe fn origin_reserved_live_diverge() -> u64
/*@ req true; @*/ /*@ ens false; @*/ {
    let local = 7_u64;
    unsafe { vf__rust_storage_live(local) } // TARGET: reserved live diverging extern call
}
