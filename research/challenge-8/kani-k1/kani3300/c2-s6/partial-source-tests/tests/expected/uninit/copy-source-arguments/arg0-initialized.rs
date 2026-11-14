// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular --harness copy_same_source_to_arg0_initialized --exact --cbmc-args --object-bits 12

#![feature(custom_mir, core_intrinsics)]
#![allow(internal_features)]

use std::intrinsics::mir::*;
use std::mem::MaybeUninit;

#[inline(never)]
fn read_first(first: MaybeUninit<u32>, _second: MaybeUninit<u32>) -> u32 {
    unsafe { first.assume_init() }
}

#[custom_mir(dialect = "runtime", phase = "optimized")]
fn copy_same_source_to_arg0(source: MaybeUninit<u32>) -> u32 {
    mir! {
        type RET = u32;
        let result: u32;
        {
            Call(result = read_first(Copy(source), Copy(source)), ReturnTo(done), UnwindUnreachable())
        }
        done = {
            RET = Move(result);
            Return()
        }
    }
}

#[kani::proof]
fn copy_same_source_to_arg0_initialized() {
    let source = MaybeUninit::<u32>::new(0x1234);
    assert_eq!(copy_same_source_to_arg0(source), 0x1234);
}
