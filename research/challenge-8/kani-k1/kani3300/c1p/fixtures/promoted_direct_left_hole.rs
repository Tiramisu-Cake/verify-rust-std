// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// RESEARCH DRAFT / NOT_RUN: not activated, compilation and lowering unverified.
// Proposed compile-flags: --edition 2021
// Proposed kani-flags: -Z uninit-checks --output-format=regular

#![feature(core_intrinsics)]
#![allow(internal_features)]

use std::intrinsics::raw_eq;
use std::mem::MaybeUninit;

// Anonymous promotion and Some/None referent bytes are hypotheses until MIR/AllocId
// binding. No mutation of constant storage. MU references are valid before raw_eq.
// Negative: require a reached uninitialized-byte failure on the named operand;
// no earlier UB/Unsupported may substitute. No golden/property ID is assumed.
// Three bytes aim to retain raw_eq through InstSimplify; retention is NOT_RUN.
#[kani::proof]
fn promoted_direct_left_hole() {
    let left: &[MaybeUninit<u8>; 3] = &[
        MaybeUninit::uninit(),
        MaybeUninit::new(7u8),
        MaybeUninit::new(7u8),
    ];
    let right: &[MaybeUninit<u8>; 3] = &[MaybeUninit::new(7u8); 3];
    let _equal = unsafe { raw_eq(left, right) };
}
