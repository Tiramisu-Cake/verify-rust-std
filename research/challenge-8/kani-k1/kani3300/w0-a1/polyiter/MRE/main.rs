// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular
// Static proposal only: all four harnesses are NOT_RUN.

#![no_std]

use core::mem::{ManuallyDrop, MaybeUninit};

// A local product type, without array::IntoIter or any std source overlay.
#[repr(C)]
struct PolymorphicIter<DATA> {
    start: usize,
    end: usize,
    data: DATA,
}

impl PolymorphicIter<[MaybeUninit<usize>; 2]> {
    // Safety: both slots in the declared live range 0..2 must be initialized.
    // The negative intentionally violates this and then performs a concrete read.
    #[inline(never)]
    unsafe fn new_unchecked(data: [MaybeUninit<usize>; 2]) -> Self {
        Self { start: 0, end: 2, data }
    }
}

#[kani::proof]
fn struct_uninitialized_negative() {
    let data = [MaybeUninit::new(7usize), MaybeUninit::uninit()];
    let iter = unsafe { PolymorphicIter::new_unchecked(data) };
    assert_eq!(iter.start, 0);
    assert_eq!(iter.end, 2);
    // Slot 1 has never been initialized: the desired post-fix failure is UB.
    assert_eq!(unsafe { iter.data[1].as_ptr().read() }, 9);
}

#[kani::proof]
fn struct_initialized_companion() {
    let data = [MaybeUninit::new(7usize), MaybeUninit::new(9usize)];
    let iter = unsafe { PolymorphicIter::new_unchecked(data) };
    assert_eq!(iter.start, 0);
    assert_eq!(iter.end, 2);
    assert_eq!(unsafe { iter.data[1].as_ptr().read() }, 9);
}

#[kani::proof]
fn manually_drop_uninitialized_negative() {
    let data = [MaybeUninit::new(7usize), MaybeUninit::uninit()];
    let iter = ManuallyDrop::new(unsafe { PolymorphicIter::new_unchecked(data) });
    assert_eq!(iter.start, 0);
    assert_eq!(iter.end, 2);
    assert_eq!(unsafe { iter.data[1].as_ptr().read() }, 9);
}

#[kani::proof]
fn manually_drop_initialized_companion() {
    let data = [MaybeUninit::new(7usize), MaybeUninit::new(9usize)];
    let iter = ManuallyDrop::new(unsafe { PolymorphicIter::new_unchecked(data) });
    assert_eq!(iter.start, 0);
    assert_eq!(iter.end, 2);
    assert_eq!(unsafe { iter.data[1].as_ptr().read() }, 9);
}
