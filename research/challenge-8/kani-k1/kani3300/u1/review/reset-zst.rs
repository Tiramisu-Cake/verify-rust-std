// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular
// Expected: ZST allowed, then FAILED/uninit u64 after reset; NOT_RUN.
use std::{mem::MaybeUninit, ptr};
#[kani::proof]
fn reset_after_zst() {
    let empty = [MaybeUninit::<()>::uninit(); 3];
    unsafe { empty[2].assume_init(); }
    let mut slot = MaybeUninit::new(9u64);
    unsafe { ptr::addr_of_mut!(slot).write(MaybeUninit::uninit()); }
    let _value = unsafe { slot.assume_init() };
}
