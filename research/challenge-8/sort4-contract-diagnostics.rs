// SPDX-License-Identifier: Apache-2.0 OR MIT
// Appended only in a disposable hosted checkout; calls the unchanged std body.
#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_sort4_contract {
    use crate::kani;

    // Element equality avoids an unrelated byte-wise memcmp loop (16/20
    // bytes) while retaining the exact same value assertions and unwind 6.
    fn same_values<const N: usize>(left: &[i32; N], right: &[i32; N]) -> bool {
        let mut i = 0;
        while i < N {
            if left[i] != right[i] {
                return false;
            }
            i += 1;
        }
        true
    }

    fn same_multiset(after: &[i32; 4], before: &[i32; 4]) -> bool {
        let mut i = 0;
        while i < 4 {
            let mut old_count = 0;
            let mut new_count = 0;
            let mut j = 0;
            while j < 4 {
                old_count += (before[j] == before[i]) as usize;
                new_count += (after[j] == before[i]) as usize;
                j += 1;
            }
            if old_count != new_count {
                return false;
            }
            i += 1;
        }
        true
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn negative_coincident_copy_overlap() {
        let mut backing = [0i32, 1, 2, 3];
        let _before = backing;
        let base = backing.as_mut_ptr();
        let mut is_less = |a: &i32, b: &i32| a < b;
        // No references into backing remain live across this call. First copy
        // is source0 -> destination0. No post-UB execution claim is made.
        unsafe { super::sort4_stable(base.cast_const(), base, &mut is_less) };
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn negative_shifted_original_multiset() {
        let mut backing = [0i32, 1, 2, 3, 4];
        let before = [backing[0], backing[1], backing[2], backing[3]];
        let base = backing.as_mut_ptr();
        let mut is_less = |a: &i32, b: &i32| a < b;
        unsafe { super::sort4_stable(base.cast_const(), base.add(1), &mut is_less) };
        let after = [backing[1], backing[2], backing[3], backing[4]];
        assert!(same_values(&after, &[0, 0, 0, 0]), "shifted destination trace");
        assert!(after[0] <= after[1] && after[1] <= after[2] && after[2] <= after[3],
                "shifted output sorted");
        kani::assert(same_multiset(&after, &before), "original multiset preserved");
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn prove_shifted_output_witness() {
        let mut backing = [0i32, 1, 2, 3, 4];
        let before = [backing[0], backing[1], backing[2], backing[3]];
        let base = backing.as_mut_ptr();
        let mut is_less = |a: &i32, b: &i32| a < b;
        unsafe { super::sort4_stable(base.cast_const(), base.add(1), &mut is_less) };
        assert!(same_values(&before, &[0, 1, 2, 3]), "original snapshot");
        assert!(same_values(&backing, &[0, 0, 0, 0, 0]), "shifted backing trace");
        kani::cover(same_values(&backing, &[0, 0, 0, 0, 0]), "shifted all-zero output reached");
    }
}
