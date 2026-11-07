# Negative controls on the submitted library tree

These runs check that the oracles and contracts of the SmallSort proofs reject what they should. The 13 controls
live behind `cfg(kani_smallsort_controls)`, which CI never sets, so they ran outside GitHub Actions.

## Setup

- Library tree `b2482f4508126b879d1942f9c1c4e0f8bd17cec3`, the same `library/` tree as the submission commit
  [`872d5a4338`](https://github.com/Tiramisu-Cake/verify-rust-std/commit/872d5a43380752786415bc00d2a12ce0e930cb37).
- Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, the pin in `tool_config/kani-version.toml`. The runner uses the
  repository's `scripts/run-kani.sh` and Kani configuration unchanged.
- Google Cloud Build, `e2-standard-4` (4 vCPU, 15.6 GiB, Ubuntu 24.04), one harness at a time, 5-minute per-harness
  timeout, `--cfg kani_smallsort_controls`.
- Build `4da67e0b-a086-459c-8287-f3ae365566dc`: the 13 controls and the two `insertion_sort_shift_left` contract
  proofs. Build `8de198b9-953d-4b19-9eb2-76f90e5a14a4`: harness inventory with the cfg on.

**Acceptance rule:** a control passes only if it is `FAILED` with exactly one failed check, and that check is the
designated one. Any other failed check would count against it.

## Controls

All 13 are `FAILED` with exactly one failed check, and in every case it is the designated check.

| Control (`verify::`) | What it breaks | Failed check (the only one) | Failed / total checks |
|---|---|---|---|
| `fixed_inputs::reject_mutant_swap_u8_n2` | negated copy of `swap_if_less` | `assertion failed: v[0] <= v[1]` @ [fixed_inputs.rs:25](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/fixed_inputs.rs#L25) | 1/80 |
| `merge::profiles::profile_full_value_checker_rejects_payload_change_u8` | payload changed behind the oracle | `full-value checker detects payload corruption` @ [merge/profiles.rs:347](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L347) | 1/378 |
| `forwarding_contracts::rejects_payload_corruption` | payload changed behind the oracle | `full-value checker rejects payload corruption` @ [forwarding_contracts.rs:270](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs#L270) | 1/345 |
| `forwarding_contracts::rejects_always_true` | non-canonical comparator passed to a wrapper | `canonical comparator required` @ [forwarding_contracts.rs:60](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/forwarding_contracts.rs#L60) | 1/588 |
| `merge::profiles::profile_wrong_f_swap_rejected_u8` | wrong comparator at a `swap_if_less` profile consumer | `profile_canonical_comparator::<P>(cmp)` @ [merge/profiles.rs:212](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L212) | 1/247 |
| `merge::profiles::profile_wrong_f_sort4_rejected_u64` | wrong comparator at a `sort4_stable` profile consumer | `profile_canonical_comparator::<P>(cmp)` @ [merge/profiles.rs:237](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L237) | 1/552 |
| `merge::profiles::profile_wrong_f_insert_rejected_u8` | wrong comparator at an `insert_tail` profile consumer | `profile_canonical_comparator::<P>(cmp)` @ [merge/profiles.rs:273](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L273) | 1/605 |
| `merge::profiles::profile_wrong_f_merge_rejected_u8` | wrong comparator at a `bidirectional_merge` profile consumer | `profile_canonical_comparator::<P>(cmp)` @ [merge/profiles.rs:311](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs#L311) | 1/594 |
| `helper_contracts::rejects_swap_outside_backing_u8` | `swap_if_less` called outside the allocation | the `requires` of `swap_if_less` @ [smallsort.rs:409](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort.rs#L409) | 1/137 |
| `helper_contracts::rejects_insert_tail_equal_begin_u64` | `insert_tail` called with `begin == tail` | the `requires` of `insert_tail` @ [smallsort.rs:588](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort.rs#L588) | 1/205 |
| `helper_contracts::rejects_merge_overlapping_dst_u64` | `bidirectional_merge` into an overlapping destination | `merge_contract_regions_disjoint(v.as_ptr(), dst, v.len())` @ [smallsort.rs:859](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort.rs#L859) | 1/235 |
| `helper_contracts::rejects_swap_comparator_writing_outside_frame_u8` | `swap_if_less` contract proof with a comparator that increments a captured counter | write-set check `Check that *var_9 is assignable` @ [helper_contracts.rs:276](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/helper_contracts.rs#L276) | 1/205 |
| `tag_permutation::reject_duplicate_network_u8_n9` | a duplicated tag in the N9 network tag harness | `every input tag occurs exactly once` @ [tag_permutation.rs:55](https://github.com/Tiramisu-Cake/verify-rust-std/blob/872d5a43380752786415bc00d2a12ce0e930cb37/library/core/src/slice/sort/shared/smallsort/verify/tag_permutation.rs#L55) | 1/559 |

For the two `requires` failures at lines 409 and 588, Kani reports the line where the multi-line attribute starts; the
full text of the failed check is the whole `requires` expression.

## Contract proofs of `insertion_sort_shift_left`

The same build ran the two ordinary harnesses that prove the `insertion_sort_shift_left` contract (u64 arrays of
length 2 and 3, every valid offset, arbitrary-answer comparator):

| Harness (`verify::`) | Status | Time, s | Failed / total checks | Covers |
|---|---|---|---|---|
| `helper_contracts::insertion_safety_u64_len2` | SUCCESS | 55.3 | 0/164 | 6/6 |
| `helper_contracts::insertion_safety_u64_len3` | SUCCESS | 63.4 | 0/164 | 6/6 |

In the organizer CI on the submission commit they took 40.4 s and 45.9 s on Ubuntu, and 47.9 s and 55.2 s on macOS.

## Inventory

With `--cfg kani_smallsort_controls`, the compiler reports 248 SmallSort harnesses: the 235 ordinary ones and the
13 controls, with no other names. SHA-256 of the sorted list:
`6d6cd89142e2f8242eb6f1cf6f6b065a11926af2eb16b2939492c59296eb8a61`. Neither build reported a warning from the SmallSort files.

## Raw evidence

- [Build summary with controls](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4562682fe43c6fa9d33a3089665165c7ce9bbfd2/research/challenge-8/kani-k1/insertpfc/g1-evidence/summary.md)
- [Inventory build summary](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4562682fe43c6fa9d33a3089665165c7ce9bbfd2/research/challenge-8/kani-k1/insertpfc/g2-evidence/summary.md)
- [Expected failures](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4562682fe43c6fa9d33a3089665165c7ce9bbfd2/research/challenge-8/kani-k1/insertpfc/controls-expected.json)
- [Sorted cfg-on harness list](https://github.com/Tiramisu-Cake/verify-rust-std/blob/4562682fe43c6fa9d33a3089665165c7ce9bbfd2/research/challenge-8/kani-k1/insertpfc/g2-evidence/compiler-cfg-on-sorted.txt)
