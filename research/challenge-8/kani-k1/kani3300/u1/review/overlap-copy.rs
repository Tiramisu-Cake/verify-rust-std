// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular
// Expected: FAILED in either direction, uninitialized byte; NOT_RUN.
use std::{mem::MaybeUninit, ptr};
#[kani::proof]
fn overlap_copy() {
    let mut slots = [MaybeUninit::new(1u8), MaybeUninit::uninit(), MaybeUninit::new(3)];
    let p = slots.as_mut_ptr();
    unsafe {
        if kani::any() { ptr::copy(p, p.add(1), 2); let _v = slots[2].assume_init(); }
        else { ptr::copy(p.add(1), p, 2); let _v = slots[0].assume_init(); }
    }
}
