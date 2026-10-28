//! Comparator shared by bounded stable unit-ZST harnesses.
//!
//! Sized values use observable volatile reads. ZSTs use ordinary reads to avoid the verifier's
//! volatile-ZST limitation; this helper does not check uninitialized reads.

use crate::mem::ManuallyDrop;
use crate::{kani, ptr};

pub(super) fn zst_aware_less<T>(a: &T, b: &T) -> bool {
    // SAFETY: callers supply initialized readable references. ManuallyDrop prevents destruction
    // of read copies; for a ZST the reference is non-null and aligned and no bytes are accessed.
    unsafe {
        if crate::mem::size_of::<T>() != 0 {
            let _left = ManuallyDrop::new(ptr::read_volatile(a));
            let _right = ManuallyDrop::new(ptr::read_volatile(b));
        } else {
            let _left = ManuallyDrop::new(ptr::read(a));
            let _right = ManuallyDrop::new(ptr::read(b));
        }
    }
    kani::any()
}
