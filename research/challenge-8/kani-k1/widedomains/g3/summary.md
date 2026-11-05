# K-1 run `widedomains-g3-20261105-01`: COMPLETE

- head `c90719fcab98baeb2a857355effe655755a6baca`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `64bc9e9a17803cf8f7f6fb962df0f2b2000ff52df740618dc9c05cfc76a8642d`
- run 12ded537-de07-422d-b024-35f1d3c6c22b attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5020500 KiB, wall 38:57.10 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1167 samples, largest sampled sum of RSS 5.77 GiB at 627 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 4.79 GiB (≤13 GiB), seen 72–2336 s, peak sample 627 s
  - `kani-compiler` 2.09 GiB (≤13 GiB), seen 2–62 s, peak sample 50 s
  - `kani-driver` 1.57 GiB (≤13 GiB), seen 2–2336 s, peak sample 385 s
  - `goto-cc` 0.08 GiB (≤13 GiB), seen 64–1110 s, peak sample 68 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 70–2095 s, peak sample 1112 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–62 s, peak sample 54 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 848–848 s, peak sample 848 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2337 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–2336 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–2336 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 655–848 s, peak sample 848 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 4.79 GiB at 627 s
  - simultaneous driver RSS 1.56 GiB at 385 s
  - cbmc PID 9400: 4.79 GiB peak at 627 s; active `T0:widedomains::merge_probe_u64_len32_network_backing32`
  - cbmc PID 9331: 4.77 GiB peak at 186 s; active `T0:widedomains::merge_probe_u64_len32_general_scratch48`
  - cbmc PID 9558: 3.81 GiB peak at 1604 s; active `T0:widedomains::insert_tail_probe_u64_backing32_tail15_to19`
  - cbmc PID 9672: 3.78 GiB peak at 2127 s; active `T0:widedomains::insert_tail_probe_u64_backing32_tail1_to4`
  - cbmc PID 9634: 3.78 GiB peak at 1886 s; active `T0:widedomains::insert_tail_probe_u64_backing32_tail5_to9`
  - cbmc PID 9596: 3.78 GiB peak at 1642 s; active `T0:widedomains::insert_tail_probe_u64_backing32_tail10_to14`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| widedomains::insert_tail_probe_u64_backing32_tail1_to4 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_probe_u64_backing32_tail5_to9 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_probe_u64_backing32_tail10_to14 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_probe_u64_backing32_tail15_to19 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insertion_probe_u64_backing32_len1_to16 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insertion_probe_u64_backing32_len17_to20 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::merge_probe_u64_len16_network_backing32 | SUCCESS | SUCCESS | 187.27766 | 0/224 | 8 | 7/7 |
| widedomains::merge_probe_u64_len32_network_backing32 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::unstable_network_safety_u64_n32_all_helpers_stubbed | SUCCESS | SUCCESS | 72.3868 | 0/486 | 17 | 2/2 |
| widedomains::merge_probe_u64_len32_general_scratch48 | SUCCESS | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::merge_probe_u64_len16_network_backing32
- 17 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::unstable_network_safety_u64_n32_all_helpers_stubbed
