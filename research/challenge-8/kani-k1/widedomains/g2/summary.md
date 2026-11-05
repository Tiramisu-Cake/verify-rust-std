# K-1 run `widedomains-g2-20261105-01`: COMPLETE

- head `4fbe77cf46cd416fb6140a54bf6c9ffb78479d3c`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `688168c844c7620715a3461e8826a836dd5347994a23b21d58d619e712646a80`
- run 100bfc31-d211-4e7a-be52-fc6e72ab7d69 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 4113984 KiB, wall 24:45.44 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 742 samples, largest sampled sum of RSS 5.44 GiB at 1335 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 3.92 GiB (≤13 GiB), seen 72–1484 s, peak sample 806 s
  - `kani-driver` 2.42 GiB (≤13 GiB), seen 2–1484 s, peak sample 310 s
  - `kani-compiler` 1.97 GiB (≤13 GiB), seen 2–66 s, peak sample 52 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 80–1303 s, peak sample 355 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 4 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 68–70 s, peak sample 70 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1485 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1484 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1484 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1485 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1484 s, peak sample 2 s
  - simultaneous cbmc RSS 3.89 GiB at 1335 s
  - simultaneous driver RSS 2.22 GiB at 308 s
  - cbmc PID 9545: 3.92 GiB peak at 806 s; active `T0:widedomains::insert_tail_initialized_u64_backing32_tail15_to19`
  - cbmc PID 9621: 3.92 GiB peak at 1153 s; active `T0:widedomains::insert_tail_initialized_u64_backing32_tail5_to9`
  - cbmc PID 9583: 3.92 GiB peak at 970 s; active `T0:widedomains::insert_tail_initialized_u64_backing32_tail10_to14`
  - cbmc PID 9659: 3.92 GiB peak at 1335 s; active `T0:widedomains::insert_tail_initialized_u64_backing32_tail1_to4`
  - cbmc PID 9387: 1.42 GiB peak at 252 s; active `T0:widedomains::unstable_network_safety_u64_n32_swap_insertion_stubbed`
  - cbmc PID 9358: 1.29 GiB peak at 158 s; active `T0:widedomains::merge_safety_u64_len8_scratch48_src32_dst0`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| widedomains::insert_tail_initialized_u64_backing32_tail1_to4 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_initialized_u64_backing32_tail5_to9 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_initialized_u64_backing32_tail10_to14 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_initialized_u64_backing32_tail15_to19 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insertion_stubbed_u64_backing32_len1_to16 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insertion_stubbed_u64_backing32_len17_to20 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::swap_safety_u64_backing32_tail_comparator | SUCCESS | SUCCESS | 39.150494 | 0/224 | 4 | 9/9 |
| widedomains::unstable_network_safety_u64_n32_swap_insertion_stubbed | SUCCESS | SUCCESS | 146.68248 | 0/474 | 12 | 5/5 |
| widedomains::merge_safety_u64_len8_scratch48_src32_dst0 | SUCCESS | SUCCESS | 80.85085 | 0/228 | 8 | 5/5 |
| widedomains::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | SUCCESS | SUCCESS | 7.120541 | 0/269 | 9 | 4/4 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::swap_safety_u64_backing32_tail_comparator
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::unstable_network_safety_u64_n32_swap_insertion_stubbed
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::merge_safety_u64_len8_scratch48_src32_dst0
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed
