// Copyright Kani Contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Candidate only, NOT_RUN. Intended flag: -Z uninit-checks, pinned SEL1.
fn choose(a: &u8, b: &u8) -> bool {
    unsafe {
        std::ptr::read_volatile(a);
        std::ptr::read_volatile(b);
    }
    kani::any()
}

#[inline(never)]
fn invoke<F: FnMut(&u8, &u8) -> bool>(f: &mut F) -> bool {
    f(&1, &2)
}

#[kani::proof]
fn check_function_item() {
    let answer = invoke(&mut choose);
    kani::cover!(answer);
    kani::cover!(!answer);
}

#[kani::proof]
fn check_closure_variant() {
    let mut cmp = |a: &u8, b: &u8| choose(a, b);
    let answer = invoke(&mut cmp);
    kani::cover!(answer);
    kani::cover!(!answer);
}
