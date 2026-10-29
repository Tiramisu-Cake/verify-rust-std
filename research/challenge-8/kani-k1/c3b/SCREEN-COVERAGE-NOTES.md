# Screen coverage and renamed harnesses

## What the first screen measured

`screen-1of6` is build `45a0dd0c-8f94-49d1-932b-ba5759453cac`, source HEAD
`afea78b3476bdce3b36b7e2e31fad116c129a497`, with a per-harness timeout of 120 seconds. The table below
copies its 16 `TIMEOUT` rows and three `SUCCESS` rows over 90 seconds from `screen-1of6.rows.tsv`.
The right column compares names with the current 395-name source prediction; it does not transfer the
screen's outcome to changed source or to replacement harnesses.

| Harness relative to `verify::` | Screen result | Relation to current 395-name prediction |
|---|---:|---|
| `correct::sorted_permutation_fallback_u64_n13` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `correct::sorted_permutation_fallback_u8_n16` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::fallback_sorted_permutation_u8_n8` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::general_stable_sorted_permutation_u64_n11` | TIMEOUT at 120 s | Removed and replaced by `merge::general_sorted_permutation_u64_n11` and `merge::stable_sorted_permutation_u64_n11`; both replacements are unmeasured. The old timeout is not a result for either replacement. |
| `merge::merge_contract_u64_n14` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::merge_contract_u64_n7` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::merge_contract_u8_n13` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::route_safety_all_routes_n18` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::route_safety_all_routes_n23` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::route_safety_all_routes_n29` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::dispatch_safety_stable_unstable_bytes85_n32` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::dispatch_safety_unstable_u8_n18_31_32` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::insert_tail_contract_u64_start14` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::insert_tail_contract_u64_start9` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::network_correctness_u64_n13` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `network::network_correctness_u64_n8` | TIMEOUT at 120 s | Same name is predicted; current-source run pending. |
| `merge::merge_contract_u8_n6` | SUCCESS, 104.969864 s | Same name is predicted; this is an earlier-source measurement, not a current-source retest. |
| `network::mutating_insertion_safety_cell_n14` | SUCCESS, 96.876656 s | Same name is predicted; this is an earlier-source measurement, not a current-source retest. |
| `network::network_safety_unstable_u64_n18_to21` | SUCCESS, 116.86221 s | Same name is predicted; this is an earlier-source measurement, not a current-source retest. |

## Coverage limits

- The current count of 395 is a source prediction at `7cedf2deb94acbc5d0da281ca4b621fa020162b4`, not a remote `kani list` inventory. The remote inventory count 327 from `84df` covered only the older A+B batches; it does not certify this final source set.
- Three full pending groups of 72, 72, and 71 harnesses (215 total) were not submitted. They have no screen results.
- The helper refactor changed 35 merge models. Those models need remeasurement even where their harness names stayed the same.
- The earlier screen uses a 120-second bound and an earlier source HEAD. Same-name membership in the 395 prediction does not establish current timing or success. Replacement names have no inherited timeout result.
- This is incomplete coverage. It does not establish that every current ordinary harness meets the target or receives full CI admission.

The eight-to-sixteen route split mappings are appended to [`renamed-harnesses.tsv`](renamed-harnesses.tsv); replaced names remain distinct from unmeasured successors.
