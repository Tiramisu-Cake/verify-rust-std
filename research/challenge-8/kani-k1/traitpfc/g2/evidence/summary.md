# K-1 run `traitpfc-g2-20261110-01`: COMPLETE

- head `344daafe1d77694bba095a6c87b3c05f9aeba77b`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `6c9eff4747907fac91b26cb072af33a007d7f7eaa480f25314266b2627099145`
- run fd40d716-e18d-4eb9-ae56-a15cd767147d attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2527508 KiB, wall 7:30.98 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 226 samples, largest sampled sum of RSS 2.93 GiB at 64 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 2.41 GiB (≤13 GiB), seen 4–78 s, peak sample 66 s
  - `cbmc` 0.85 GiB (≤13 GiB), seen 130–449 s, peak sample 389 s
  - `kani-driver` 0.15 GiB (≤13 GiB), seen 2–449 s, peak sample 393 s
  - `goto-cc` 0.12 GiB (≤13 GiB), seen 80–401 s, peak sample 90 s
  - `goto-instrument` 0.11 GiB (≤13 GiB), seen 92–435 s, peak sample 202 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–78 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–451 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–449 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–449 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–451 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–449 s, peak sample 2 s
  - simultaneous cbmc RSS 0.85 GiB at 385 s
  - simultaneous driver RSS 0.12 GiB at 393 s
  - cbmc PID 23191: 0.85 GiB peak at 389 s; active `T0:trait_contracts::stable_ensures_u64_len2`
  - cbmc PID 23153: 0.27 GiB peak at 316 s; active `T0:trait_contracts::unstable_ensures_u64_backing4`
  - cbmc PID 23111: 0.27 GiB peak at 260 s; active `T0:trait_contracts::freeze_ensures_u64_backing4`
  - cbmc PID 22955: 0.26 GiB peak at 168 s; active `T0:forwarding_contracts::unstable_byte_n2`
  - cbmc PID 23264: 0.26 GiB peak at 449 s; active `T0:trait_contracts::freeze_safety_u64_backing4`
  - cbmc PID 22982: 0.11 GiB peak at 186 s; active `T0:scratch_geometry::stable_u64_min_scratch_n2`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| trait_contracts::stable_ensures_u64_len2 | SUCCESS | SUCCESS | 69.51902 | 0/472 | 8 | 5/5 |
| trait_contracts::unstable_ensures_u64_backing4 | SUCCESS | SUCCESS | 20.262255 | 0/559 | 19 | 5/5 |
| trait_contracts::freeze_ensures_u64_backing4 | SUCCESS | SUCCESS | 20.403618 | 0/557 | 21 | 5/5 |
| trait_contracts::verified_forwarding_ensures_u64_backing4 | SUCCESS | SUCCESS | 2.7244892 | 0/627 | 21 | 1/1 |
| trait_contracts::rejects_high_bit_corruption_u64_pair | FAILED | FAILED | 0.19330244 | 1/48 | 1 |  |
| trait_contracts::rejects_verified_forwarding_sorted_u64_backing4 | FAILED | FAILED | 1.8516306 | 1/540 | 21 |  |
| trait_contracts::rejects_reverse_pointer_sorted_u64_backing4 | FAILED | FAILED | 1.9880459 | 1/608 | 21 |  |
| trait_contracts::freeze_safety_u64_backing4 | SUCCESS | SUCCESS | 15.698717 | 0/499 | 21 | 3/3 |
| scratch_geometry::stable_u64_min_scratch_n2 | SUCCESS | SUCCESS | 7.667644 | 0/427 | 76 | 2/2 |
| forwarding_contracts::unstable_byte_n2 | SUCCESS | SUCCESS | 45.22978 | 0/509 | 18 | 7/7 |

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_pair`:
- high-bit corruption preserves full pair @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:175

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_verified_forwarding_sorted_u64_backing4`:
- forwarded output is sorted @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:81

Failed checks of `slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing4`:
- reverse pointer output is sorted @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/trait_contracts.rs:196

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::stable_ensures_u64_len2
- 19 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::unstable_ensures_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_ensures_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::verified_forwarding_ensures_u64_backing4
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_high_bit_corruption_u64_pair
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_verified_forwarding_sorted_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::rejects_reverse_pointer_sorted_u64_backing4
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::trait_contracts::freeze_safety_u64_backing4
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::scratch_geometry::stable_u64_min_scratch_n2
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::forwarding_contracts::unstable_byte_n2
