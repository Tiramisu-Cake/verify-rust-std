# K-1 run `traitpfc-g3-20261110-02`: COMPLETE

- head `2f1c45e519cc89e1dae532ad0f44243255a514d7`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `b521133c786fa24eb1d38e861a5296eb5da4d31c11c840e1d20120788cd16aa6`
- run 368b93f4-e7ae-4603-bf41-ea3fb6573e3e attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2582352 KiB, wall 16:43.38 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 502 samples, largest sampled sum of RSS 3.01 GiB at 58 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 2.46 GiB (≤13 GiB), seen 4–72 s, peak sample 62 s
  - `cbmc` 1.21 GiB (≤13 GiB), seen 124–1002 s, peak sample 866 s
  - `kani-driver` 0.32 GiB (≤13 GiB), seen 2–1002 s, peak sample 888 s
  - `goto-cc` 0.12 GiB (≤13 GiB), seen 74–651 s, peak sample 86 s
  - `goto-instrument` 0.09 GiB (≤13 GiB), seen 90–890 s, peak sample 230 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–72 s, peak sample 68 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 236–236 s, peak sample 236 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1002 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1003 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1002 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 236–236 s, peak sample 236 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 1.21 GiB at 866 s
  - simultaneous driver RSS 0.30 GiB at 886 s
  - cbmc PID 23454: 1.21 GiB peak at 866 s; active `T0:trait_contracts::stable_sorts_permutation_u64_len3`
  - cbmc PID 23492: 0.86 GiB peak at 998 s; active `T0:trait_contracts::stable_sorts_permutation_u64_len2`
  - cbmc PID 23290: 0.82 GiB peak at 419 s; active `T0:trait_contracts::unstable_sorts_permutation_u64_backing5`
  - cbmc PID 23332: 0.64 GiB peak at 537 s; active `T0:trait_contracts::unstable_sorts_permutation_u64_backing4`
  - cbmc PID 23374: 0.57 GiB peak at 647 s; active `T0:trait_contracts::freeze_sorts_permutation_u64_backing5`
  - cbmc PID 23101: 0.54 GiB peak at 224 s; active `T0:trait_contracts::freeze_frame_function_item_u64_backing5`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| trait_contracts::stable_sorts_permutation_u64_len2 | SUCCESS | SUCCESS | 112.45171 | 0/487 | 16 | 5/5 |
| trait_contracts::stable_sorts_permutation_u64_len3 | SUCCESS | SUCCESS | 169.94554 | 0/503 | 16 | 5/5 |
| trait_contracts::freeze_sorts_permutation_u64_backing4 | SUCCESS | SUCCESS | 28.834583 | 0/582 | 29 | 5/5 |
| trait_contracts::freeze_sorts_permutation_u64_backing5 | SUCCESS | SUCCESS | 68.057304 | 0/638 | 29 | 5/5 |
| trait_contracts::unstable_sorts_permutation_u64_backing4 | SUCCESS | SUCCESS | 82.79854 | 0/714 | 29 | 5/5 |
| trait_contracts::unstable_sorts_permutation_u64_backing5 | SUCCESS | SUCCESS | 128.4587 | 0/770 | 29 | 5/5 |
| trait_contracts::verified_forwarding_sorts_permutation_u64_backing5 | SUCCESS | SUCCESS | 6.1645646 | 0/762 | 29 | 5/5 |
| trait_contracts::rejects_high_bit_corruption_u64_len3 | FAILED | FAILED | 1.9056786 | 1/102 | 12 |  |
| trait_contracts::rejects_changed_multiplicities_u64_len3 | FAILED | FAILED | 0.5499438 | 1/58 | 10 |  |
| trait_contracts::rejects_reverse_pointer_sorted_u64_backing5 | FAILED | FAILED | 2.210697 | 1/633 | 39 |  |
| trait_contracts::rejects_function_item_sorted_u64_backing5 | FAILED | FAILED | 2.0546393 | 1/547 | 21 |  |
| trait_contracts::freeze_frame_function_item_u64_backing5 | SUCCESS | SUCCESS | 35.949974 | 0/492 | 21 | 3/3 |
| scratch_geometry::stable_u64_min_scratch_n2 | SUCCESS | SUCCESS | 3.6611972 | 0/427 | 76 | 2/2 |
| forwarding_contracts::unstable_byte_n2 | SUCCESS | SUCCESS | 31.68138 | 0/509 | 18 | 7/7 |

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_len3`:
- high-bit corruption preserves sorted full values @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:181

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_changed_multiplicities_u64_len3`:
- same set preserves full multiplicities @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:197

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing5`:
- reverse pointer output is sorted @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:220

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_function_item_sorted_u64_backing5`:
- function item output is sorted @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:253

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- time -v max RSS 2582352 KiB exceeds the largest sampled command peak 2582076 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 16 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::stable_sorts_permutation_u64_len2
- 16 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::stable_sorts_permutation_u64_len3
- 29 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_sorts_permutation_u64_backing4
- 29 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_sorts_permutation_u64_backing5
- 29 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::unstable_sorts_permutation_u64_backing4
- 29 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::unstable_sorts_permutation_u64_backing5
- 29 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::verified_forwarding_sorts_permutation_u64_backing5
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_len3
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_changed_multiplicities_u64_len3
- 39 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing5
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_function_item_sorted_u64_backing5
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_frame_function_item_u64_backing5
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::scratch_geometry::stable_u64_min_scratch_n2
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::forwarding_contracts::unstable_byte_n2
