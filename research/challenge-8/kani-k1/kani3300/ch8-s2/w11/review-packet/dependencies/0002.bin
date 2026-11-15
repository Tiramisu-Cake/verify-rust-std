//! Verification-only full-value model for three exact SmallSort T/F pairs.
//!
//! The generic facade is deliberately unconditional. Inactive pairs read neither
//! elements nor length and make no sorting claim. Contracts must guard with enabled.

use crate::cell::Cell;
use crate::marker::PhantomData;

const CAP: usize = 32;

/// Freeze, non-Copy, no-Drop byte; the whole logical value is its byte.
#[repr(transparent)]
pub(in crate::slice::sort::shared::smallsort) struct NonCopyByte(u8);

impl NonCopyByte {
    pub(in crate::slice::sort::shared::smallsort) const fn new(value: u8) -> Self {
        Self(value)
    }
}

/// A closed, stateless comparator. Its type identifies the exact pure order.
pub(in crate::slice::sort::shared::smallsort) struct KeyLess<T>(PhantomData<fn() -> T>);

impl<T> KeyLess<T> {
    pub(in crate::slice::sort::shared::smallsort) const fn new() -> Self {
        Self(PhantomData)
    }
}

// Only the full logical value is Copy; elements need not be Copy or Freeze.
trait Project {
    fn value(&self) -> u8;
}

impl Project for u8 {
    fn value(&self) -> u8 { *self }
}
impl Project for Cell<u8> {
    fn value(&self) -> u8 { self.get() }
}
impl Project for NonCopyByte {
    fn value(&self) -> u8 { self.0 }
}

macro_rules! key_less {
    ($ty:ty) => {
        impl<'a, 'b> FnOnce<(&'a $ty, &'b $ty)> for KeyLess<$ty> {
            type Output = bool;
            extern "rust-call" fn call_once(self, (a, b): (&'a $ty, &'b $ty)) -> bool {
                a.value() < b.value()
            }
        }
        impl<'a, 'b> FnMut<(&'a $ty, &'b $ty)> for KeyLess<$ty> {
            extern "rust-call" fn call_mut(&mut self, (a, b): (&'a $ty, &'b $ty)) -> bool {
                a.value() < b.value()
            }
        }
    };
}
key_less!(u8);
key_less!(Cell<u8>);
key_less!(NonCopyByte);

/// Owned pre-state: no references to mutable input or uninitialized scratch.
#[derive(Clone, Copy)]
pub(in crate::slice::sort::shared::smallsort) struct Snapshot {
    values: [u8; CAP],
    len: usize,
    valid: bool,
}

impl Snapshot {
    fn invalid() -> Self {
        Self { values: [0; CAP], len: 0, valid: false }
    }
}

fn active_snapshot<T: Project>(values: &[T]) -> Snapshot {
    if values.len() > CAP {
        return Snapshot::invalid();
    }
    let mut result = Snapshot { values: [0; CAP], len: values.len(), valid: true };
    let mut i = 0;
    while i < result.len {
        result.values[i] = values[i].value();
        i += 1;
    }
    result
}

fn active_post<T: Project>(before: Snapshot, values: &[T]) -> bool {
    if !before.valid || before.len > CAP || values.len() > CAP || before.len != values.len() {
        return false;
    }
    let mut i = 1;
    while i < before.len {
        if values[i].value() < values[i - 1].value() {
            return false;
        }
        i += 1;
    }
    // Checking each input value (duplicates may repeat a check) covers the whole
    // multiset: equal input/output lengths leave no room for a novel output value.
    i = 0;
    while i < before.len {
        let query = before.values[i];
        let mut old_count: usize = 0;
        let mut new_count: usize = 0;
        let mut j = 0;
        while j < before.len {
            if before.values[j] == query { old_count += 1; }
            if values[j].value() == query { new_count += 1; }
            j += 1;
        }
        if old_count != new_count {
            return false;
        }
        i += 1;
    }
    true
}

// No trait bounds escape to a generic caller. Only concrete type substitutions
// specialize the default; specialization does not depend on another trait bound.
trait Model<T, F> {
    fn enabled() -> bool;
    fn snapshot(values: &[T]) -> Snapshot;
    fn post(before: Snapshot, values: &[T]) -> bool;
}

impl<T, F> Model<T, F> for () {
    default fn enabled() -> bool { false }
    default fn snapshot(_values: &[T]) -> Snapshot { Snapshot::invalid() }
    default fn post(_before: Snapshot, _values: &[T]) -> bool { true }
}

macro_rules! active_model {
    ($ty:ty) => {
        impl Model<$ty, KeyLess<$ty>> for () {
            fn enabled() -> bool { true }
            fn snapshot(values: &[$ty]) -> Snapshot { active_snapshot(values) }
            fn post(before: Snapshot, values: &[$ty]) -> bool { active_post(before, values) }
        }
    };
}
active_model!(u8);
active_model!(Cell<u8>);
active_model!(NonCopyByte);

pub(in crate::slice::sort::shared::smallsort) fn enabled<T, F>() -> bool {
    <() as Model<T, F>>::enabled()
}
pub(in crate::slice::sort::shared::smallsort) fn snapshot<T, F>(values: &[T]) -> Snapshot {
    <() as Model<T, F>>::snapshot(values)
}
pub(in crate::slice::sort::shared::smallsort) fn post<T, F>(before: Snapshot, values: &[T]) -> bool {
    <() as Model<T, F>>::post(before, values)
}
