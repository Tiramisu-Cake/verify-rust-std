//! Concrete stable scratch geometries with the parent's full-value probe and key order.

use super::{
    CopyOnDrop, MaybeUninit, SMALL_SORT_GENERAL_SCRATCH_LEN, bidirectional_merge, kani, lt_u8, ptr,
    set_value_probe,
};

// SAFETY: callers supply exactly eight initialized bytes at `base`.
unsafe fn initialized_span_matches(base: *const u8, input: &[u8; 8]) -> bool {
    let view = unsafe { crate::slice::from_raw_parts(base, 8) };
    let mut equal = true;
    for i in 0..8 {
        equal &= view[i] == input[i];
    }
    equal
}

// SAFETY: source and destination each contain eight initialized bytes after the real call.
// Fresh views are formed here, after any deliberate mutation and its source borrow has ended.
unsafe fn check_same8(input: &[u8; 8], source: *const u8, dst: *const u8) {
    let mut cmp = lt_u8;
    let cmp = &mut cmp;
    assert!(CopyOnDrop::<u8>::is_sorted_unrolled(dst, 8, &cmp), "GEOM16_SORTED");
    assert!(
        CopyOnDrop::<u8>::probe_count_unrolled(input.as_ptr(), 8)
            == CopyOnDrop::<u8>::probe_count_unrolled(dst, 8),
        "GEOM16_FULL_VALUE_COUNT"
    );
    assert!(unsafe { initialized_span_matches(source, input) }, "GEOM16_SOURCE_FRAME");
}

// SAFETY: the protected left half contains eight initialized bytes.
unsafe fn check_left_half(left: *const u8, input: &[u8; 8]) {
    assert!(unsafe { initialized_span_matches(left, input) }, "GEOM16_LEFT_HALF_FRAME");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn final16_stable_scratch48_actual_pfc() {
    set_value_probe::<u8>();
    let input: [u8; 16] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let source = scratch.as_mut_ptr().cast::<u8>();
    let mut dst: [u8; 16] = kani::any();
    let mut cmp = lt_u8;
    // SAFETY: only scratch[0..16] is initialized; dst is a separate initialized array.
    // The actual contract supplies the sorted-halves precondition under PFC.
    unsafe {
        ptr::copy_nonoverlapping(input.as_ptr(), source, 16);
        bidirectional_merge(crate::slice::from_raw_parts(source, 16), dst.as_mut_ptr(), &mut cmp);
    }
    kani::cover(true, "GEOM16_FINAL16_PFC_COMPLETE");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn same16to0_stable_scratch48_actual_pfc() {
    set_value_probe::<u8>();
    let input: [u8; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let base = scratch.as_mut_ptr().cast::<u8>();
    let mut cmp = lt_u8;
    // SAFETY: source[16..24] and dst[0..8] share base but are disjoint and in bounds.
    // Only source is initialized before the call; PFC supplies sorted halves.
    unsafe {
        let source = base.add(16);
        ptr::copy_nonoverlapping(input.as_ptr(), source, 8);
        bidirectional_merge(crate::slice::from_raw_parts(source, 8), base, &mut cmp);
    }
    kani::cover(true, "GEOM16_SAME16TO0_PFC_COMPLETE");
}

#[kani::proof_for_contract(crate::slice::sort::shared::smallsort::bidirectional_merge)]
#[kani::unwind(34)]
fn same24to8_stable_scratch48_actual_pfc() {
    set_value_probe::<u8>();
    let input: [u8; 8] = kani::any();
    let left: [u8; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let base = scratch.as_mut_ptr().cast::<u8>();
    let mut cmp = lt_u8;
    // SAFETY: only left[0..8] and source[24..32] are initialized before the call.
    // Dst[8..16] is disjoint from both within the same scratch object.
    unsafe {
        let source = base.add(24);
        ptr::copy_nonoverlapping(left.as_ptr(), base, 8);
        ptr::copy_nonoverlapping(input.as_ptr(), source, 8);
        bidirectional_merge(crate::slice::from_raw_parts(source, 8), base.add(8), &mut cmp);
        check_left_half(base, &left);
    }
    kani::cover(true, "GEOM16_SAME24TO8_PFC_COMPLETE");
}

// Each monomorphization includes only its own post-call mutation and cover.
fn same16to0_plain(after_call: impl FnOnce(*mut u8)) {
    set_value_probe::<u8>();
    let input: [u8; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let base = scratch.as_mut_ptr().cast::<u8>();
    let mut cmp = lt_u8;
    // SAFETY: only source[16..24] is initialized. Dst[0..8] is writable and disjoint.
    unsafe {
        let source = base.add(16);
        ptr::copy_nonoverlapping(input.as_ptr(), source, 8);
        {
            let view = crate::slice::from_raw_parts(source, 8);
            let cmp_ref = &mut cmp;
            kani::assume(CopyOnDrop::<u8>::merge_inputs_are_sorted(view, &cmp_ref));
            bidirectional_merge(view, base, cmp_ref);
        }
        // The shared source view has ended before any raw mutation or fresh checker view.
        after_call(base);
        check_same8(&input, source, base);
    }
}

fn same24to8_plain(after_call: impl FnOnce(*mut u8)) {
    set_value_probe::<u8>();
    let input: [u8; 8] = kani::any();
    let left: [u8; 8] = kani::any();
    let mut scratch = [MaybeUninit::<u8>::uninit(); SMALL_SORT_GENERAL_SCRATCH_LEN];
    let base = scratch.as_mut_ptr().cast::<u8>();
    let mut cmp = lt_u8;
    // SAFETY: source[24..32] and protected left[0..8] are initialized, dst[8..16] is not.
    // All three spans are disjoint within base's single scratch allocation.
    unsafe {
        let source = base.add(24);
        let dst = base.add(8);
        ptr::copy_nonoverlapping(left.as_ptr(), base, 8);
        ptr::copy_nonoverlapping(input.as_ptr(), source, 8);
        {
            let view = crate::slice::from_raw_parts(source, 8);
            let cmp_ref = &mut cmp;
            kani::assume(CopyOnDrop::<u8>::merge_inputs_are_sorted(view, &cmp_ref));
            bidirectional_merge(view, dst, cmp_ref);
        }
        after_call(base);
        check_same8(&input, source, dst);
        check_left_half(base, &left);
    }
}

#[kani::proof]
#[kani::unwind(34)]
fn same16to0_checker_positive() {
    same16to0_plain(|_| {});
    kani::cover(true, "GEOM16_SAME16TO0_CHECKER_COMPLETE");
}

#[kani::proof]
#[kani::unwind(34)]
fn same16to0_value_corruption_control() {
    same16to0_plain(|base| {
        kani::cover(true, "GEOM16_SAME16TO0_VALUE_BEFORE_MUTATION");
        // SAFETY: dst slot0 was initialized by the completed real merge.
        unsafe { *base ^= 1 };
    });
}

#[kani::proof]
#[kani::unwind(34)]
fn same16to0_source_frame_control() {
    same16to0_plain(|base| {
        kani::cover(true, "GEOM16_SAME16TO0_SOURCE_BEFORE_MUTATION");
        // SAFETY: source slot16 is initialized and its shared call view has ended.
        unsafe { *base.add(16) ^= 1 };
    });
}

#[kani::proof]
#[kani::unwind(34)]
fn same24to8_value_corruption_control() {
    same24to8_plain(|base| {
        kani::cover(true, "GEOM16_SAME24TO8_VALUE_BEFORE_MUTATION");
        // SAFETY: dst slot8 was initialized by the completed real merge.
        unsafe { *base.add(8) ^= 1 };
    });
}

#[kani::proof]
#[kani::unwind(34)]
fn same24to8_left_frame_control() {
    same24to8_plain(|base| {
        kani::cover(true, "GEOM16_SAME24TO8_LEFT_BEFORE_MUTATION");
        // SAFETY: protected left slot0 is initialized and outside source and dst.
        unsafe { *base ^= 1 };
    });
}
