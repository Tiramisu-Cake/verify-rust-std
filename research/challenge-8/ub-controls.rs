// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Isolated controls for measuring Kani's UB detectors; not sorting proofs.

#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_ub_controls {
    use crate::kani;
    use crate::mem::MaybeUninit;
    use crate::ptr;

    static IMMUTABLE_BYTE: u8 = 7;

    #[repr(align(4))]
    struct AlignedBytes([u8; 8]);

    #[kani::proof]
    pub fn positive_initialized_read() {
        let value: i32 = kani::any();
        let read_back = unsafe { ptr::addr_of!(value).read() };
        assert!(read_back == value);
        kani::cover(read_back < 0, "initialized negative scalar is reachable");
        kani::cover(read_back >= 0, "initialized nonnegative scalar is reachable");
    }

    #[kani::proof]
    pub fn positive_valid_bool_pointer_read() {
        let value: bool = kani::any();
        let pointer = &value as *const bool;
        let read_back = unsafe { pointer.read() };
        assert!(read_back == value);
        kani::cover(read_back, "valid true bool is reachable");
        kani::cover(!read_back, "valid false bool is reachable");
    }

    #[kani::proof]
    pub fn negative_uninitialized_i32_read() {
        let slot = MaybeUninit::<i32>::uninit();
        // Expected to fail only when uninitialized-memory instrumentation catches
        // this read. The cover consumes the result so it cannot be dead code.
        let value = unsafe { slot.assume_init() };
        kani::cover(value == 0, "uninitialized i32 read was consumed");
    }

    #[kani::proof]
    pub fn negative_invalid_bool_read() {
        let bytes = [kani::any::<u8>()];
        kani::assume(bytes[0] == 2);
        let pointer = bytes.as_ptr().cast::<bool>();
        let value = unsafe { pointer.read() };
        kani::cover(value, "invalid bool read was consumed");
    }

    #[kani::proof]
    pub fn negative_misaligned_u32_read() {
        let bytes = AlignedBytes([0; 8]);
        let pointer = unsafe { bytes.0.as_ptr().add(1).cast::<u32>() };
        let value = unsafe { pointer.read() };
        kani::cover(value == 0, "misaligned u32 read was consumed");
    }

    #[kani::proof]
    pub fn negative_null_u32_read() {
        let value = unsafe { ptr::null::<u32>().read() };
        kani::cover(value == 0, "null u32 read was consumed");
    }

    #[kani::proof]
    pub fn negative_immutable_static_write() {
        let pointer = ptr::addr_of!(IMMUTABLE_BYTE).cast_mut();
        unsafe { pointer.write(9) };
    }
}
