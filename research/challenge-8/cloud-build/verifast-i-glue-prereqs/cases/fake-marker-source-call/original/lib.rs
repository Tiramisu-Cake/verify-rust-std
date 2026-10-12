#![no_std]
use core::{mem::ManuallyDrop, ptr};

struct CopyOnDrop {
    src: *const u64,
    dst: *mut u64,
    len: usize,
}

impl Drop for CopyOnDrop {
    fn drop(&mut self) {
        // SAFETY: `src` must contain `len` initialized elements, and dst must
        // be valid to write `len` elements.
        unsafe {
            ptr::copy_nonoverlapping(self.src, self.dst, self.len);
        }
    }
}


unsafe fn natural_onecell(tail: *mut u64)/*@
req thread_token(?t) &*& t == currentThread &*& type_interp::<u64>() &*&
    0 < std::mem::size_of::<u64>() &*&
    std::mem::size_of::<u64>() <= isize::MAX &*&
    tail as usize != 0 &*&
    tail as usize % std::mem::align_of::<u64>() == 0 &*&
    object_pointer_within_limits(tail, std::mem::size_of::<u64>()) == true &*&
    tail as usize <= usize::MAX - std::mem::size_of::<u64>() &*&
    *tail |-> ?held &*& <u64>.own(t, held);
@*//*@
ens thread_token(t) &*& type_interp::<u64>() &*&
    *tail |-> held &*& <u64>.own(t, held);
@*//*@
on_unwind_ens thread_token(t) &*& type_interp::<u64>() &*&
    *tail |-> ?unwound &*& <u64>.own(t, unwound);
@*/ {
    unsafe {
        let tmp = ManuallyDrop::new(tail.read());
        {
        //@ vf__rust_storage_live(0); // NEGATIVE: source annotation cannot mint an internal MIR receipt
        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };
        ptr::copy_nonoverlapping(gap_guard.src, gap_guard.dst, gap_guard.len);
        let _drop_suppressed = ManuallyDrop::new(gap_guard);
        }
    }
}
