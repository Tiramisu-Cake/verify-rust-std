// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// kani-flags: -Z uninit-checks
// compile-flags: --edition 2021

//! Candidate reduction of U8's first unsupported operation, not executed in U0.

use std::mem::MaybeUninit;

#[kani::proof]
fn scratch_array_layout() {
    let value: u8 = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); 20];
    scratch[0].write(value);
    // SAFETY: the same slot was initialized immediately above.
    let got = unsafe { scratch[0].assume_init() };
    assert_eq!(got, value);
}
