// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// RESEARCH DRAFT / NOT_RUN: not activated, compilation and lowering unverified.
// Proposed compile-flags: --edition 2021
// Proposed kani-flags: -Z uninit-checks --output-format=regular

#![feature(core_intrinsics)]
#![allow(internal_features)]

use std::intrinsics::raw_eq;
use std::mem::MaybeUninit;
use std::ptr;

// Copy T must remain [MaybeUninit<u8>; 3], count=1, not a pointer to one slot.
// Require retained copy/raw_eq, object+offset+extent and last transfer binding.
// Negative: copied unwritten byte at offset 0 must reach the left raw_eq check.
// The other written bytes read 7 first; no early UB/Unsupported may replace it.
// NOT_RUN: expected semantic observable only, no fabricated golden.
#[kani::proof]
fn flat_whole_copy_left_hole() {
    let source: [MaybeUninit<u8>; 3] = [
        MaybeUninit::uninit(),
        MaybeUninit::new(7u8),
        MaybeUninit::new(7u8),
    ];
    let mut destination = [MaybeUninit::new(7u8); 3];
    let other = [MaybeUninit::new(7u8); 3];
    unsafe {
        ptr::copy_nonoverlapping(ptr::addr_of!(source), ptr::addr_of_mut!(destination), 1);
        assert_eq!(destination[1].assume_init(), 7);
        assert_eq!(destination[2].assume_init(), 7);
        let _equal = raw_eq(&destination, &other);
    }
}
