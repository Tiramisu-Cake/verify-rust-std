# K-1 run `widedomains-g1-20261105-01`: COMPLETE

- head `90fadd7ccf8b5bb32d04401d274a6f492b612897`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `cb5d05e2df44e9ff7969f319cc1f462a8a50ace3e3144b1944f68fc8ccb7a315`
- run f303fd59-fa90-4c25-a50d-8c7ab7146fea attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 6960864 KiB, wall 27:56.84 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 838 samples, largest sampled sum of RSS 6.66 GiB at 210 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 6.64 GiB (≤13 GiB), seen 92–1676 s, peak sample 210 s
  - `kani-driver` 1.99 GiB (≤13 GiB), seen 2–1676 s, peak sample 1598 s
  - `kani-compiler` 1.97 GiB (≤13 GiB), seen 2–66 s, peak sample 54 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 68–1460 s, peak sample 72 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 76–1642 s, peak sample 681 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 469–469 s, peak sample 469 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1677 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1676 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1676 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–1676 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 6.64 GiB at 210 s
  - simultaneous driver RSS 1.49 GiB at 1596 s
  - cbmc PID 9331: 6.64 GiB peak at 210 s; active `T0:widedomains::insert_tail_safety_u64_backing48_tail5_to8`
  - cbmc PID 9369: 6.60 GiB peak at 365 s; active `T0:widedomains::insert_tail_safety_u64_backing48_tail1_to4`
  - cbmc PID 9407: 5.65 GiB peak at 543 s; active `T0:widedomains::insert_tail_safety_u64_backing32_tail17_to19`
  - cbmc PID 9483: 5.65 GiB peak at 944 s; active `T0:widedomains::insert_tail_safety_u64_backing32_tail9_to12`
  - cbmc PID 9559: 5.65 GiB peak at 1345 s; active `T0:widedomains::insert_tail_safety_u64_backing32_tail1_to4`
  - cbmc PID 9445: 5.65 GiB peak at 740 s; active `T0:widedomains::insert_tail_safety_u64_backing32_tail13_to16`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| widedomains::swap_safety_u8_backing32 | SUCCESS | SUCCESS | 33.71013 | 0/234 | 4 | 9/9 |
| widedomains::swap_safety_u64_backing32 | SUCCESS | SUCCESS | 40.420055 | 0/234 | 4 | 9/9 |
| widedomains::unstable_network_safety_u8_n32_stubbed | SUCCESS | SUCCESS | 135.0917 | 0/387 | 12 | 5/5 |
| widedomains::insert_tail_safety_u64_backing32_tail1_to4 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing32_tail5_to8 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing32_tail9_to12 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing32_tail13_to16 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing32_tail17_to19 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing48_tail1_to4 | SUCCESS | TIMEOUT | None |  | None |  |
| widedomains::insert_tail_safety_u64_backing48_tail5_to8 | SUCCESS | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::swap_safety_u8_backing32
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::swap_safety_u64_backing32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::widedomains::unstable_network_safety_u8_n32_stubbed
