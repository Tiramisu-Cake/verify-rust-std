#[repr(align(8))]
pub struct Z;

pub mod aligned {
    use super::Z;

    #[rapx::verify]
    pub unsafe fn copy() {
        let src_value = Z;
        let mut dst_value = Z;
        let src = core::ptr::addr_of!(src_value);
        let dst = core::ptr::addr_of_mut!(dst_value);
        // SAFETY: both zero-byte pointers retain Z's alignment.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}

pub mod source_misaligned {
    use super::Z;

    #[rapx::verify]
    pub unsafe fn copy() {
        let src_value = Z;
        let mut dst_value = Z;
        let src = core::ptr::addr_of!(src_value)
            .cast::<u8>()
            .wrapping_add(1)
            .cast::<Z>();
        let dst = core::ptr::addr_of_mut!(dst_value);
        // Deliberately violates the copy's source alignment requirement.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}

pub mod destination_misaligned {
    use super::Z;

    #[rapx::verify]
    pub unsafe fn copy() {
        let src_value = Z;
        let mut dst_value = Z;
        let src = core::ptr::addr_of!(src_value);
        let dst = core::ptr::addr_of_mut!(dst_value)
            .cast::<u8>()
            .wrapping_add(1)
            .cast::<Z>();
        // Deliberately violates the copy's destination alignment requirement.
        unsafe { core::ptr::copy_nonoverlapping(src, dst, 1) };
    }
}
