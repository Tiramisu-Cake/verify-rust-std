// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular --harness raw_slice_cross_slot_initialized --exact --cbmc-args --object-bits 12

use std::mem::{self, MaybeUninit};

#[repr(C)]
struct Padded {
    tag: u8,
    value: u32,
}

fn check_layout(slice: &[MaybeUninit<Padded>; 2]) -> usize {
    let value_offset = mem::offset_of!(Padded, value);
    let value_end = value_offset + mem::size_of::<u32>();
    let align = mem::align_of::<Padded>();
    let stride = value_end.div_ceil(align) * align;
    assert_eq!(mem::offset_of!(Padded, tag), 0);
    assert_eq!(value_offset % mem::align_of::<u32>(), 0);
    assert_eq!(mem::align_of::<Padded>(), mem::align_of::<u32>());
    assert_eq!(mem::size_of::<Padded>(), stride);
    assert_eq!(mem::size_of::<MaybeUninit<Padded>>(), stride);
    assert_eq!(mem::size_of_val(slice), 2 * stride);
    value_offset
}

#[kani::proof]
fn raw_slice_cross_slot_initialized() {
    let slots = [
        MaybeUninit::new(Padded { tag: 1, value: 0x5a5a_5a5a }),
        MaybeUninit::new(Padded { tag: 2, value: 0x5a5a_5a5a }),
    ];
    let value_offset = check_layout(&slots);
    let raw_slice = std::ptr::slice_from_raw_parts(slots.as_ptr(), slots.len());
    let borrowed = unsafe { &*raw_slice };
    let second = unsafe { borrowed.get_unchecked(1) };
    let byte = unsafe { second.as_ptr().cast::<u8>().add(value_offset + 3).read() };
    assert_eq!(byte, 0x5a);
}
