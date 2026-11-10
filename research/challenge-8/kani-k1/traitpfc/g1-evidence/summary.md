# K-1 run `traitpfc-g1-20261110-01`: COMPLETE

- head `ac1a18c84f39ed9c5ce3ecf95bf7b84e67908e3f`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `1370f5eb029023967b38644f579d221677123b63938e987114d8dde27afe9c5e`
- run e77f402e-95bf-400b-994e-a86fe57bd72c attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2503552 KiB, wall 5:14.48 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 158 samples, largest sampled sum of RSS 3.04 GiB at 56 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 2.39 GiB (≤13 GiB), seen 2–68 s, peak sample 56 s
  - `cbmc` 0.82 GiB (≤13 GiB), seen 112–312 s, peak sample 312 s
  - `kani-driver` 0.14 GiB (≤13 GiB), seen 2–312 s, peak sample 150 s
  - `goto-cc` 0.12 GiB (≤13 GiB), seen 70–78 s, peak sample 72 s
  - `goto-instrument` 0.06 GiB (≤13 GiB), seen 80–250 s, peak sample 80 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 60 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–314 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–312 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–312 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–314 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–312 s, peak sample 2 s
  - simultaneous cbmc RSS 0.82 GiB at 312 s
  - simultaneous driver RSS 0.11 GiB at 232 s
  - cbmc PID 8965: 0.82 GiB peak at 312 s; active `T0:trait_contracts::stable_safety_u64_len2`
  - cbmc PID 8887: 0.27 GiB peak at 232 s; active `T0:trait_contracts::freeze_safety_u64_backing4`
  - cbmc PID 8725: 0.26 GiB peak at 140 s; active `T0:forwarding_contracts::unstable_byte_n2`
  - cbmc PID 8927: 0.24 GiB peak at 246 s; active `T0:trait_contracts::unstable_safety_u64_len2`
  - cbmc PID 8752: 0.11 GiB peak at 148 s; active `T0:scratch_geometry::stable_u64_min_scratch_n2`
  - cbmc PID 8845: 0.05 GiB peak at 166 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| trait_contracts::stable_safety_u64_len2 | SUCCESS | SUCCESS | 61.873463 | 0/371 | 8 | 3/3 |
| trait_contracts::unstable_safety_u64_len2 | SUCCESS | SUCCESS | 8.339401 | 0/409 | 19 | 3/3 |
| trait_contracts::freeze_safety_u64_backing4 | SUCCESS | SUCCESS | 16.11834 | 0/446 | 21 | 3/3 |
| trait_contracts::real_forwarding_sorts_u64_backing4 | SUCCESS | SUCCESS | 1.5168791 | 0/375 | 18 |  |
| trait_contracts::verified_forwarding_frame_u64_backing4 | SUCCESS | SUCCESS | 1.5670406 | 0/473 | 21 |  |
| trait_contracts::rejects_verified_forwarding_sorted_u64_backing4 | FAILED | FAILED | 1.6120687 | 1/488 | 21 |  |
| scratch_geometry::stable_u64_min_scratch_n2 | SUCCESS | SUCCESS | 3.794201 | 0/427 | 76 | 2/2 |
| forwarding_contracts::unstable_byte_n2 | SUCCESS | SUCCESS | 31.778137 | 0/509 | 18 | 7/7 |

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_verified_forwarding_sorted_u64_backing4`:
- forwarded output is sorted @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:81

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- time -v max RSS 2503552 KiB exceeds the largest sampled command peak 2502960 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::stable_safety_u64_len2
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::unstable_safety_u64_len2
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_safety_u64_backing4
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::real_forwarding_sorts_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::verified_forwarding_frame_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_verified_forwarding_sorted_u64_backing4
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::scratch_geometry::stable_u64_min_scratch_n2
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::forwarding_contracts::unstable_byte_n2
