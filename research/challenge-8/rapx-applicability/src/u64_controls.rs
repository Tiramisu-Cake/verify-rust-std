pub mod aligned {
    #[rapx::verify]
    pub unsafe fn copy() {
        let src_value = [0_u64; 1];
        let mut dst_value = [0_u64; 1];
        let src = core::ptr::addr_of!(src_value).cast::<u64>();
        let dst = core::ptr::addr_of_mut!(dst_value).cast::<u64>();
        // SAFETY: separate one-element initialized source and writable destination.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}

pub mod source_misaligned {
    #[rapx::verify]
    pub unsafe fn copy() {
        let src_storage = [0_u64; 2];
        let mut dst_storage = [0_u64; 2];
        let src = core::ptr::addr_of!(src_storage)
            .cast::<u8>()
            .wrapping_add(1)
            .cast::<u64>();
        let dst = core::ptr::addr_of_mut!(dst_storage).cast::<u64>();
        // Deliberately violates only source alignment; both 8-byte ranges fit distinct 16-byte objects.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}

pub mod destination_misaligned {
    #[rapx::verify]
    pub unsafe fn copy() {
        let src_storage = [0_u64; 2];
        let mut dst_storage = [0_u64; 2];
        let src = core::ptr::addr_of!(src_storage).cast::<u64>();
        let dst = core::ptr::addr_of_mut!(dst_storage)
            .cast::<u8>()
            .wrapping_add(1)
            .cast::<u64>();
        // Deliberately violates only destination alignment; both 8-byte ranges fit distinct 16-byte objects.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}
