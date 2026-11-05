# K-1 run `veightrows-g1-20261105-01`: COMPLETE

- head `01caba2d4d7386759de16ee395518aa866cafbb4`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `e80d8942192e78db648f9e9c8c9471d84783ac6c8891f6be17d8bb40615e62db`
- run aa74ed5a-e1b3-4851-bf9f-094435daf711 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 2522136 KiB, wall 5:34.26 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 168 samples, largest sampled sum of RSS 3.69 GiB at 296 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.41 GiB (≤13 GiB), seen 66–332 s, peak sample 296 s
  - `kani-driver` 2.00 GiB (≤13 GiB), seen 2–332 s, peak sample 170 s
  - `kani-compiler` 1.63 GiB (≤13 GiB), seen 2–62 s, peak sample 48 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–62 s, peak sample 4 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 170–208 s, peak sample 170 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 64–240 s, peak sample 64 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–334 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–332 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–334 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–332 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–332 s, peak sample 2 s
  - simultaneous cbmc RSS 2.41 GiB at 296 s
  - simultaneous driver RSS 1.61 GiB at 168 s
  - cbmc PID 8781: 2.41 GiB peak at 296 s; active `T0:tailcontracts::insert_tail_safety_u64_backing17_tail8_to15`
  - cbmc PID 8819: 2.19 GiB peak at 322 s; active `T0:tailcontracts::insert_tail_safety_u64_backing17_tail1_to7`
  - cbmc PID 8663: 1.48 GiB peak at 122 s; active `T0:allocationcontracts::unstable_network_safety_u8_n32_stubbed`
  - cbmc PID 8703: 0.37 GiB peak at 196 s; active `T0:allocationcontracts::swap_safety_u64_backing32`
  - cbmc PID 8743: 0.30 GiB peak at 236 s; active `T0:allocationcontracts::swap_safety_u8_backing32`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| allocationcontracts::swap_safety_u8_backing32 | SUCCESS | SUCCESS | 31.575 | 0/234 | 4 | 9/9 |
| allocationcontracts::swap_safety_u64_backing32 | SUCCESS | SUCCESS | 35.80377 | 0/234 | 4 | 9/9 |
| allocationcontracts::unstable_network_safety_u8_n32_stubbed | SUCCESS | SUCCESS | 104.319084 | 0/387 | 12 | 5/5 |
| tailcontracts::insert_tail_safety_u64_backing17_tail1_to7 | SUCCESS | SUCCESS | 29.476984 | 0/179 | 4 | 5/5 |
| tailcontracts::insert_tail_safety_u64_backing17_tail8_to15 | SUCCESS | SUCCESS | 61.14256 | 0/179 | 4 | 5/5 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::allocationcontracts::swap_safety_u8_backing32
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::allocationcontracts::swap_safety_u64_backing32
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::allocationcontracts::unstable_network_safety_u8_n32_stubbed
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::tailcontracts::insert_tail_safety_u64_backing17_tail1_to7
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::tailcontracts::insert_tail_safety_u64_backing17_tail8_to15
