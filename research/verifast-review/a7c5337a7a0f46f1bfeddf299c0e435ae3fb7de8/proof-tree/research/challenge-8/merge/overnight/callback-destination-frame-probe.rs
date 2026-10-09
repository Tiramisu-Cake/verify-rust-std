// Prepared, unexecuted source-level frame probe. Builds/tests are hosted only.
// merge_up below is copied verbatim from repository SmallSort lines 677-707,
// Git blob 40939f922bcb6fdc7ee0d30427fa861827043827. A future hosted source
// admission must check this copy before treating it as exact-source evidence.
// This does not refute the conditional VF separation contract: the captured
// destination write must itself satisfy the callback's resource obligations.

use std::ptr;

unsafe fn merge_up<T, F: FnMut(&T, &T) -> bool>(
    mut left_src: *const T,
    mut right_src: *const T,
    mut dst: *mut T,
    is_less: &mut F,
) -> (*const T, *const T, *mut T) {
    // This is a branchless merge utility function.
    // The equivalent code with a branch would be:
    //
    // if !is_less(&*right_src, &*left_src) {
    //     ptr::copy_nonoverlapping(left_src, dst, 1);
    //     left_src = left_src.add(1);
    // } else {
    //     ptr::copy_nonoverlapping(right_src, dst, 1);
    //     right_src = right_src.add(1);
    // }
    // dst = dst.add(1);

    // SAFETY: The caller must guarantee that `left_src`, `right_src` are valid
    // to read and `dst` is valid to write, while not aliasing.
    unsafe {
        let is_l = !is_less(&*right_src, &*left_src);
        let src = if is_l { left_src } else { right_src };
        ptr::copy_nonoverlapping(src, dst, 1);
        right_src = right_src.add(!is_l as usize);
        left_src = left_src.add(is_l as usize);
        dst = dst.add(1);
    }

    (left_src, right_src, dst)
}

fn main() {
    let source = [10u32, 20u32];
    let mut output = 0u32;
    let dst = &mut output as *mut u32;
    let mut comparator = |_: &u32, _: &u32| -> bool {
        // A raw write to a separate, initialized output cell before unwind.
        // A callback framed from that cell in VF cannot assume this permission.
        unsafe { dst.write(9) };
        panic!("destination frame probe");
    };
    let outcome = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| unsafe {
        merge_up(source.as_ptr(), source.as_ptr().add(1), dst, &mut comparator)
    }));
    assert!(outcome.is_err());
    assert_eq!(output, 9);
}
