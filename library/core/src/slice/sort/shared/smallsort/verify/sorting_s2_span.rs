//! Opt-in DIAGNOSTIC_ASSUMED spec predicates; no qualified semantic leaves.
//! Active only for u8/default KeyLess. Inactive specialization never reads storage.
use super::sorting_model::{self, KeyLess, Snapshot};
use crate::slice;
trait Span<T, F> {
    fn active() -> bool;
    fn capture(p: *const T, n: usize) -> Snapshot;
    fn post(s: Snapshot, p: *const T, n: usize) -> bool;
    fn ordered(p: *const T, n: usize) -> bool;
}
impl<T, F> Span<T, F> for () {
    default fn active() -> bool { false }
    default fn capture(_p: *const T, _n: usize) -> Snapshot {
        sorting_model::snapshot::<u8, ()>(&[])
    }
    default fn post(_s: Snapshot, _p: *const T, _n: usize) -> bool { true }
    default fn ordered(_p: *const T, _n: usize) -> bool { true }
}
impl Span<u8, KeyLess<u8>> for () {
    fn active() -> bool { true }
    fn capture(p: *const u8, n: usize) -> Snapshot {
        if n > 32 { return sorting_model::snapshot::<u8, ()>(&[]); }
        if n == 0 { return sorting_model::snapshot::<u8, KeyLess<u8>>(&[]); }
        // SAFETY: requires establishes initialized readable n-span before spec read.
        unsafe { sorting_model::snapshot::<u8, KeyLess<u8>>(slice::from_raw_parts(p, n)) }
    }
    fn post(s: Snapshot, p: *const u8, n: usize) -> bool {
        if n > 32 { return false; }
        if n == 0 { return sorting_model::post::<u8, KeyLess<u8>>(s, &[]); }
        unsafe { sorting_model::post::<u8, KeyLess<u8>>(s, slice::from_raw_parts(p, n)) }
    }
    fn ordered(p: *const u8, n: usize) -> bool {
        if n > 32 { return false; }
        let mut i = 1;
        while i < n {
            if unsafe { *p.add(i) < *p.add(i - 1) } { return false; }
            i += 1;
        }
        true
    }
}
pub(in crate::slice::sort::shared::smallsort) fn active<T, F>() -> bool {
    <() as Span<T,F>>::active()
}
pub(in crate::slice::sort::shared::smallsort) fn capture<T, F>(p: *const T,n: usize) -> Snapshot {
    <() as Span<T,F>>::capture(p,n)
}
pub(in crate::slice::sort::shared::smallsort) fn post<T, F>(s: Snapshot,p: *const T,n: usize) -> bool {
    <() as Span<T,F>>::post(s,p,n)
}
pub(in crate::slice::sort::shared::smallsort) fn ordered<T, F>(p: *const T,n: usize) -> bool {
    <() as Span<T,F>>::ordered(p,n)
}
