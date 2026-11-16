// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Candidate only, NOT_RUN. Intended flag: -Z uninit-checks.
#![feature(maybe_uninit_array_assume_init)]
use std::mem::MaybeUninit;

#[kani::proof]
fn initialized_array_transmute() {
    let slots = [MaybeUninit::new(1u8), MaybeUninit::new(2u8)];
    let values = unsafe { MaybeUninit::array_assume_init(slots) };
    assert_eq!(values, [1, 2]);
}
