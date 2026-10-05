// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Bounded safety-only experiment for the real insertion_sort_shift_left.

#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_insertion_safety {
    use crate::kani;

    const N: usize = 4;

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn prove_outer_safety_4() {
        let mut backing: [i32; N] = kani::any();
        let len: usize = kani::any();
        let offset: usize = kani::any();
        kani::assume(len >= 1 && len <= N);
        kani::assume(offset >= 1 && offset <= len);

        // The callback returns a fresh unconstrained result on every call.
        // No ordering or sorted-prefix assumptions constrain the input.
        let mut is_less = |_: &i32, _: &i32| kani::any::<bool>();
        super::insertion_sort_shift_left(&mut backing[..len], offset, &mut is_less);

        kani::cover(len == 1, "length one is reachable");
        kani::cover(len == 2, "length two is reachable");
        kani::cover(len == 3, "length three is reachable");
        kani::cover(len == 4, "length four is reachable");
        kani::cover(offset == 1, "first valid offset is reachable");
        kani::cover(offset == len, "one-past-last initial tail is reachable");
        kani::cover(len == 4 && offset == 1, "maximum insertion span is reachable");
    }
}
