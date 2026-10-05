
// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Bootstrap proofs written for this fork; no competing PR code is imported.

#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_bootstrap {
    use crate::kani;

    #[kani::proof]
    pub fn orders_i32_pair() {
        let before: [i32; 4] = kani::any();
        let mut after = before;
        let mut is_less = |a: &i32, b: &i32| a < b;

        // SAFETY: indices 1 and 2 point to initialized, aligned values in
        // the same live allocation. The comparator does not mutate them.
        unsafe { super::swap_if_less(after.as_mut_ptr(), 1, 2, &mut is_less) };

        assert!(after[1] <= after[2]);
        if before[2] < before[1] {
            assert!(after[1] == before[2] && after[2] == before[1]);
        } else {
            assert!(after[1] == before[1] && after[2] == before[2]);
        }
        assert!(after[0] == before[0] && after[3] == before[3]);

        kani::cover(before[1] < before[2], "already ordered pair is reachable");
        kani::cover(before[1] > before[2], "reversed pair is reachable");
        kani::cover(before[1] == before[2], "equal values are reachable");
    }

    #[kani::proof]
    pub fn preserves_i32_values_for_any_decision() {
        let before: [i32; 4] = kani::any();
        let mut after = before;
        let decision: bool = kani::any();
        let mut comparator = |_: &i32, _: &i32| decision;

        // SAFETY: both positions satisfy swap_if_less's pointer requirements.
        // An arbitrary comparison result need not define a valid ordering;
        // this proof asserts exact value preservation, not sortedness.
        unsafe { super::swap_if_less(after.as_mut_ptr(), 1, 2, &mut comparator) };

        let expected_left = if decision { before[2] } else { before[1] };
        let expected_right = if decision { before[1] } else { before[2] };
        assert!(after[1] == expected_left && after[2] == expected_right);
        assert!(after[0] == before[0] && after[3] == before[3]);

        kani::cover(decision, "swap decision is reachable");
        kani::cover(!decision, "keep decision is reachable");
    }
}
