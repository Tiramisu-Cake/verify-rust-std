//! S2 proposal: exact full-byte transfer for the actual swap_if_less contract.
//! Register under kani_smallsort_sorting only after integration of the attrs in
//! the W11 S2 INTERFACE. This module does not attach a contract by itself.
//! Only u8/KeyLess<u8> is active here; S1's other pairs are not swap-qualified.

use super::sorting_model::KeyLess;

#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct PairSnapshot {
    a: u8,
    b: u8,
    valid: bool,
}

impl PairSnapshot {
    fn invalid() -> Self { Self { a: 0, b: 0, valid: false } }
}

trait SwapModel<T, F> {
    fn enabled() -> bool;
    fn capture(base: *const T, a: usize, b: usize) -> PairSnapshot;
    fn post(pre: PairSnapshot, base: *const T, a: usize, b: usize) -> bool;
}

impl<T, F> SwapModel<T, F> for () {
    default fn enabled() -> bool { false }
    default fn capture(_base: *const T, _a: usize, _b: usize) -> PairSnapshot {
        PairSnapshot::invalid()
    }
    default fn post(_pre: PairSnapshot, _base: *const T, _a: usize, _b: usize) -> bool {
        true
    }
}

impl SwapModel<u8, KeyLess<u8>> for () {
    fn enabled() -> bool { true }
    fn capture(base: *const u8, a: usize, b: usize) -> PairSnapshot {
        // SAFETY: the actual callee's existing requires establish both initialized,
        // readable positions, nonwrapping offsets and a common allocation first.
        unsafe { PairSnapshot { a: *base.add(a), b: *base.add(b), valid: true } }
    }
    fn post(pre: PairSnapshot, base: *const u8, a: usize, b: usize) -> bool {
        if !pre.valid { return false; }
        let now = <() as SwapModel<u8, KeyLess<u8>>>::capture(base, a, b);
        if pre.b < pre.a {
            now.a == pre.b && now.b == pre.a
        } else {
            now.a == pre.a && now.b == pre.b
        }
    }
}

/// Unconditional generic facade; no new T/F bounds on the actual helper.
pub(in crate::slice::sort::shared::smallsort) fn enabled<T, F>() -> bool {
    <() as SwapModel<T, F>>::enabled()
}

/// Spec-only read: active callers must establish the actual swap requires first.
/// Inactive calls do not inspect pointers, indices or pointed-to bytes.
pub(in crate::slice::sort::shared::smallsort) fn capture<T, F>(
    base: *const T, a: usize, b: usize,
) -> PairSnapshot {
    <() as SwapModel<T, F>>::capture(base, a, b)
}

/// Exact conditional transfer implies pair order and preservation of both full
/// bytes, including equal positions. The actual modifies clause supplies frame.
pub(in crate::slice::sort::shared::smallsort) fn post<T, F>(
    pre: PairSnapshot, base: *const T, a: usize, b: usize,
) -> bool {
    <() as SwapModel<T, F>>::post(pre, base, a, b)
}
