#![no_std]
use core::{mem::ManuallyDrop, ptr};

struct CopyOnDrop<T> {
    src: *const T,
    dst: *mut T,
    len: usize,
}

unsafe fn insertion_onecell<T>(tail: *mut T) {
    unsafe {
        let tmp = ManuallyDrop::new(tail.read());
        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };
        ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, 1);
    }
}
