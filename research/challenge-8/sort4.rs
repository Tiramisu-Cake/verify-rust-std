// Copyright Challenge 8 contributors
// SPDX-License-Identifier: Apache-2.0 OR MIT

// Appended to the real smallsort.rs by run-sort4.sh in a disposable hosted
// checkout. These harnesses call the actual generic sort4_stable body.
#[cfg(kani)]
#[unstable(feature = "kani", issue = "none")]
pub mod challenge8_sort4 {
    use crate::kani;

    const N: usize = 4;

    fn sorted(values: &[i32; N]) -> bool {
        let mut i = 1;
        while i < N {
            if values[i - 1] > values[i] {
                return false;
            }
            i += 1;
        }
        true
    }

    fn count(values: &[i32; N], key: i32) -> usize {
        let mut count = 0;
        let mut i = 0;
        while i < N {
            if values[i] == key {
                count += 1;
            }
            i += 1;
        }
        count
    }

    // Counting every old value (and preserving the fixed length) proves the
    // exact multiset, including duplicate values; a sum would lose information.
    fn same_multiset(after: &[i32; N], before: &[i32; N]) -> bool {
        let mut i = 0;
        while i < N {
            if count(after, before[i]) != count(before, before[i]) {
                return false;
            }
            i += 1;
        }
        true
    }

    fn same_values(left: &[i32; N], right: &[i32; N]) -> bool {
        let mut i = 0;
        while i < N {
            if left[i] != right[i] {
                return false;
            }
            i += 1;
        }
        true
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn prove_sort4_values() {
        let src: [i32; N] = kani::any();
        let before = src;
        let mut dst: [i32; N] = [0; N];
        let mut is_less = |a: &i32, b: &i32| a < b;

        // The two independently declared initialized arrays give four live
        // readable source cells and four initialized writable destination
        // cells. Their Rust array storage is disjoint; only Copy i32 values are
        // exercised by this functional claim.
        unsafe { super::sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut is_less) };

        assert!(sorted(&dst));
        assert!(same_multiset(&dst, &before));
        assert!(same_values(&src, &before));

        kani::cover(
            before[0] < before[1]
                && before[1] < before[2]
                && before[2] < before[3],
            "strictly ascending input",
        );
        kani::cover(
            before[0] > before[1]
                && before[1] > before[2]
                && before[2] > before[3],
            "strictly reverse input",
        );
        kani::cover(
            before[0] == before[1]
                && before[1] == before[2]
                && before[2] == before[3],
            "all keys equal",
        );
        kani::cover(
            before[0] == before[2] && before[0] != before[1],
            "mixed duplicate keys",
        );
        kani::cover(
            before[0] == i32::MIN && before[3] == i32::MAX,
            "both signed extremes present",
        );

        // These strict relative-order patterns force the four possible c3/c4
        // outcomes after the first two input pairs are ordered. They retain
        // unrestricted i32 values and do not encode a finite key domain.
        kani::cover(
            before[0] < before[1]
                && before[1] < before[2]
                && before[2] < before[3],
            "c3=false and c4=false pattern",
        );
        kani::cover(
            before[0] < before[2]
                && before[2] < before[3]
                && before[3] < before[1],
            "c3=false and c4=true pattern",
        );
        kani::cover(
            before[2] < before[0]
                && before[0] < before[1]
                && before[1] < before[3],
            "c3=true and c4=false pattern",
        );
        kani::cover(
            before[2] < before[0]
                && before[0] < before[3]
                && before[3] < before[1],
            "c3=true and c4=true pattern",
        );
        kani::cover(before[1] < before[0], "first pair inversion");
        kani::cover(before[3] < before[2], "second pair inversion");
        kani::cover(
            before[0] < before[2]
                && before[2] < before[1]
                && before[1] < before[3],
            "unknown pair requires final exchange",
        );
    }

    #[repr(C)]
    #[derive(Clone, Copy)]
    struct Tagged {
        key: i32,
        original_id: u8,
    }

    fn same_item(left: Tagged, right: Tagged) -> bool {
        left.key == right.key && left.original_id == right.original_id
    }

    fn count_item(values: &[Tagged; N], item: Tagged) -> usize {
        let mut count = 0;
        let mut i = 0;
        while i < N {
            if same_item(values[i], item) {
                count += 1;
            }
            i += 1;
        }
        count
    }

    fn same_items(after: &[Tagged; N], before: &[Tagged; N]) -> bool {
        let mut i = 0;
        while i < N {
            if count_item(after, before[i]) != 1 {
                return false;
            }
            i += 1;
        }
        true
    }

    fn sorted_and_stable(values: &[Tagged; N]) -> bool {
        let mut i = 1;
        while i < N {
            if values[i - 1].key > values[i].key {
                return false;
            }
            if values[i - 1].key == values[i].key
                && values[i - 1].original_id >= values[i].original_id
            {
                return false;
            }
            i += 1;
        }
        true
    }

    fn same_tagged_values(left: &[Tagged; N], right: &[Tagged; N]) -> bool {
        let mut i = 0;
        while i < N {
            if !same_item(left[i], right[i]) {
                return false;
            }
            i += 1;
        }
        true
    }

    #[kani::proof]
    #[kani::unwind(6)]
    pub fn prove_sort4_stability() {
        let keys: [i32; N] = kani::any();
        let src = [
            Tagged { key: keys[0], original_id: 0 },
            Tagged { key: keys[1], original_id: 1 },
            Tagged { key: keys[2], original_id: 2 },
            Tagged { key: keys[3], original_id: 3 },
        ];
        let before = src;
        let mut dst = [
            Tagged { key: 0, original_id: 0 },
            Tagged { key: 0, original_id: 0 },
            Tagged { key: 0, original_id: 0 },
            Tagged { key: 0, original_id: 0 },
        ];
        let mut is_less = |a: &Tagged, b: &Tagged| a.key < b.key;

        // The comparator observes keys only. IDs distinguish equal-key input
        // occurrences and are not consulted by sorting decisions.
        unsafe { super::sort4_stable(src.as_ptr(), dst.as_mut_ptr(), &mut is_less) };

        assert!(sorted_and_stable(&dst));
        assert!(same_items(&dst, &before));
        assert!(same_tagged_values(&src, &before));

        kani::cover(
            keys[0] == keys[1] && keys[1] == keys[2] && keys[2] == keys[3],
            "all tagged keys equal",
        );
        kani::cover(
            keys[0] == keys[2] && keys[0] != keys[1],
            "tagged mixed duplicate keys",
        );
        kani::cover(
            keys[0] == i32::MIN && keys[3] == i32::MAX,
            "tagged signed extremes present",
        );
        kani::cover(
            keys[0] < keys[1]
                && keys[1] < keys[2]
                && keys[2] < keys[3],
            "tagged strictly ascending keys",
        );
        kani::cover(
            keys[0] > keys[1]
                && keys[1] > keys[2]
                && keys[2] > keys[3],
            "tagged strictly reverse keys",
        );
        kani::cover(
            keys[0] < keys[2]
                && keys[2] < keys[1]
                && keys[1] < keys[3],
            "tagged unknown pair requires final exchange",
        );
    }
}
