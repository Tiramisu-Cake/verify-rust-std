// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// compile-flags: --edition 2021
// kani-flags: -Z uninit-checks --output-format=regular --harness copy_same_source_to_arg1_hole --exact --cbmc-args --object-bits 12

#![feature(custom_mir, core_intrinsics)]
#![allow(internal_features)]

use std::intrinsics::mir::*;
use std::mem::MaybeUninit;

#[inline(never)]
fn read_second(_first: MaybeUninit<u32>, second: MaybeUninit<u32>) -> u32 {
    unsafe { second.assume_init() }
}

#[custom_mir(dialect = "runtime", phase = "optimized")]
fn copy_same_source_to_arg1(source: MaybeUninit<u32>) -> u32 {
    mir! {
        type RET = u32;
        let result: u32;
        {
            Call(result = read_second(Copy(source), Copy(source)), ReturnTo(done), UnwindUnreachable())
        }
        done = {
            RET = Move(result);
            Return()
        }
    }
}

#[kani::proof]
fn copy_same_source_to_arg1_hole() {
    let source = MaybeUninit::<u32>::uninit();
    let _read = copy_same_source_to_arg1(source);
}
