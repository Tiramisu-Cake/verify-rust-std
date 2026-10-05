
// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT
// Original fixed-domain experiment; the sorting work calls the real std helpers.

#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_insertion {
    use crate::kani;

    const N: usize = 4;

    fn sorted_prefix(values: &[i32; N], len: usize) -> bool {
        if len > N {
            return false;
        }
        let mut i = 1;
        while i < len {
            if values[i - 1] > values[i] {
                return false;
            }
            i += 1;
        }
        true
    }

    fn count_prefix(values: &[i32; N], len: usize, key: i32) -> usize {
        let mut count = 0;
        let mut i = 0;
        while i < len {
            if values[i] == key {
                count += 1;
            }
            i += 1;
        }
        count
    }

    // Equality of counts for every value present in the old prefix, together
    // with the equal prefix length, characterizes multiset preservation.
    fn same_multiset_prefix(after: &[i32; N], before: &[i32; N], len: usize) -> bool {
        if len > N {
            return false;
        }
        let mut i = 0;
        while i < len {
            let key = before[i];
            if count_prefix(after, len, key) != count_prefix(before, len, key) {
                return false;
            }
            i += 1;
        }
        true
    }

    fn same_suffix(after: &[i32; N], before: &[i32; N], start: usize) -> bool {
        if start > N {
            return false;
        }
        let mut i = start;
        while i < N {
            if after[i] != before[i] {
                return false;
            }
            i += 1;
        }
        true
    }

    // Proof-only monomorphic adapter. It neither replaces nor annotates the
    // generic std function. Its implementation delegates to actual insert_tail.
    // The by-value snapshot and equality precondition express the input state
    // without old() borrow conflicts in this Kani macro expansion.
    #[kani::requires(tail > 0 && tail < N)]
    #[kani::requires(sorted_prefix(values, tail))]
    // Array equality lowers to a 16-byte memcmp in this toolchain. Express the
    // identical condition elementwise so unwind 6 covers the four-cell loop.
    #[kani::requires(same_suffix(values, &before, 0))]
    #[kani::modifies(values)]
    #[kani::ensures(|_| sorted_prefix(values, tail + 1))]
    #[kani::ensures(|_| same_multiset_prefix(values, &before, tail + 1))]
    #[kani::ensures(|_| same_suffix(values, &before, tail + 1))]
    fn insert_one(values: &mut [i32; N], tail: usize, before: [i32; N]) {
        let base = values.as_mut_ptr();
        let mut is_less = |a: &i32, b: &i32| a < b;
        // SAFETY: the live array supplies initialized, aligned elements; the
        // precondition ensures 0 < tail < N within that same allocation.
        unsafe { super::insert_tail(base, base.add(tail), &mut is_less) };
    }

    #[kani::proof_for_contract(insert_one)]
    #[kani::unwind(6)]
    pub fn prove_tail_contract_4() {
        let mut values: [i32; N] = kani::any();
        let tail: usize = kani::any();
        let before = values;
        // proof_for_contract assumes the adapter's preconditions at the call
        // and checks its real implementation against every postcondition.
        insert_one(&mut values, tail, before);
        kani::cover(tail == 1, "two-element insertion is reachable");
        kani::cover(tail == 2, "three-element insertion is reachable");
        kani::cover(tail == 3, "four-element insertion is reachable");
        kani::cover(tail == 3 && before[3] < before[0], "move to beginning is reachable");
        kani::cover(tail == 3 && before[3] >= before[2], "no shift is reachable");
        kani::cover(tail == 3 && before[3] == before[1], "duplicate key is reachable");
    }

    #[kani::proof]
    #[kani::stub_verified(insert_one)]
    #[kani::unwind(6)]
    pub fn prove_composition_4() {
        let before: [i32; N] = kani::any();
        let mut values = before;
        // This experimental caller uses verified summaries for the three
        // insertions. It is not a proof of std's outer pointer loop.
        let first_snapshot = values;
        insert_one(&mut values, 1, first_snapshot);
        let second_snapshot = values;
        insert_one(&mut values, 2, second_snapshot);
        let third_snapshot = values;
        insert_one(&mut values, 3, third_snapshot);
        assert!(sorted_prefix(&values, N));
        assert!(same_multiset_prefix(&values, &before, N));
        kani::cover(before[0] > before[1] && before[1] > before[2] && before[2] > before[3],
                    "reverse ordered input is reachable");
        kani::cover(before[0] == before[1] && before[1] == before[2] && before[2] == before[3],
                    "all equal input is reachable");
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn prove_direct_insertion_4() {
        let before: [i32; N] = kani::any();
        let mut values = before;
        let len: usize = kani::any();
        let offset: usize = kani::any();
        kani::assume(len > 0 && len <= N);
        kani::assume(offset > 0 && offset <= len);
        kani::assume(sorted_prefix(&values, offset));
        let mut is_less = |a: &i32, b: &i32| a < b;
        super::insertion_sort_shift_left(&mut values[..len], offset, &mut is_less);
        assert!(sorted_prefix(&values, len));
        assert!(same_multiset_prefix(&values, &before, len));
        assert!(same_suffix(&values, &before, len));
        kani::cover(len == 1, "length one is reachable");
        kani::cover(len == 2, "length two is reachable");
        kani::cover(len == 3, "length three is reachable");
        kani::cover(len == 4, "length four is reachable");
        kani::cover(offset == len, "already sorted entire slice is reachable");
        kani::cover(len == 4 && offset == 1, "full insertion route is reachable");
        kani::cover(len == 4 && offset == 3, "long presorted prefix is reachable");
    }
}
