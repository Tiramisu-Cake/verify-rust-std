// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// RESEARCH DRAFT / NOT_RUN: not activated, compilation and lowering unverified.
// Proposed compile-flags: --edition 2021
// Proposed kani-flags: -Z uninit-checks --output-format=regular

#![feature(core_intrinsics)]
#![allow(internal_features)]

use std::intrinsics::raw_eq;
use std::mem::MaybeUninit;

#[inline(never)]
fn compare(left: &[MaybeUninit<u8>; 3], right: &[MaybeUninit<u8>; 3]) -> bool {
    unsafe { raw_eq(left, right) }
}

// Anonymous promotion and Some/None referent bytes are hypotheses until MIR/AllocId
// binding. No mutation of constant storage. MU references are valid before raw_eq.
// Legal: require both full-extent checks reached SUCCESS and equality true.
// Three bytes aim to retain raw_eq through InstSimplify; retention is NOT_RUN.
#[kani::proof]
fn promoted_helper_legal() {
    let left: &[MaybeUninit<u8>; 3] = &[MaybeUninit::new(7u8); 3];
    let right: &[MaybeUninit<u8>; 3] = &[MaybeUninit::new(7u8); 3];
    assert!(compare(left, right));
}
