# K-1 run `citrim-g1-20261105-01`: COMPLETE

- head `bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `879ae1c1994099eb19ca2c9d63c7e911efd6b13d781ae020acd0e8f9eb2d2b00`
- run 76b1664d-a0bf-4268-92fc-3b69220d556f attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2993108 KiB, wall 1:20:29 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 2410 samples, largest sampled sum of RSS 3.66 GiB at 3638 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.85 GiB (≤13 GiB), seen 76–4829 s, peak sample 3640 s
  - `kani-driver` 2.13 GiB (≤13 GiB), seen 2–4829 s, peak sample 4829 s
  - `kani-compiler` 1.75 GiB (≤13 GiB), seen 2–66 s, peak sample 52 s
  - `goto-instrument` 0.08 GiB (≤13 GiB), seen 377–4414 s, peak sample 3122 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 66 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 68–4177 s, peak sample 2484 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 72–72 s, peak sample 72 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–4829 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–4829 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 72–72 s, peak sample 72 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–4829 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 2.85 GiB at 3638 s
  - simultaneous driver RSS 2.13 GiB at 4829 s
  - cbmc PID 9834: 2.85 GiB peak at 3640 s; active `T0:network::insert_tail_contract_u64_start1_tail2_to5`
  - cbmc PID 9720: 2.85 GiB peak at 2956 s; active `T0:network::insert_tail_contract_u64_start1_tail9_to10`
  - cbmc PID 9758: 2.85 GiB peak at 3170 s; active `T0:network::insert_tail_contract_u64_start1_tail13`
  - cbmc PID 9796: 2.85 GiB peak at 3391 s; active `T0:network::insert_tail_contract_u64_start1_tail14`
  - cbmc PID 9644: 2.85 GiB peak at 2528 s; active `T0:network::insert_tail_contract_u64_start1_tail6_to8`
  - cbmc PID 9682: 2.85 GiB peak at 2755 s; active `T0:network::insert_tail_contract_u64_start1_tail11_to12`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_direct_u64_n9_ge_ge | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_ge_lt | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_lt_ge | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_lt_lt | SUCCESS | SUCCESS | 298.00433 | 0/416 | 61 | 1/1 |
| merge::stable_direct_u64_n9_ge_ge | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_ge_lt | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_lt_ge | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_lt_lt | SUCCESS | TIMEOUT | None |  | None |  |
| network::dispatch_safety_stable_bytes16_n32 | SUCCESS | SUCCESS | 108.72484 | 0/382 | 9 | 2/2 |
| network::dispatch_safety_stable_unstable_bytes16_n15 | SUCCESS | SUCCESS | 57.527676 | 0/390 | 9 | 3/3 |
| network::dispatch_safety_stable_unstable_bytes16_n16 | SUCCESS | SUCCESS | 63.919994 | 0/390 | 8 | 3/3 |
| network::dispatch_safety_stable_unstable_bytes16_n17 | SUCCESS | SUCCESS | 64.92339 | 0/390 | 8 | 3/3 |
| network::dispatch_safety_stable_unstable_bytes17_n15 | SUCCESS | SUCCESS | 62.401028 | 0/390 | 9 | 3/3 |
| network::dispatch_safety_stable_unstable_bytes17_n16 | SUCCESS | SUCCESS | 70.84245 | 0/390 | 9 | 3/3 |
| network::dispatch_safety_stable_unstable_bytes17_n17 | SUCCESS | SUCCESS | 95.44369 | 0/390 | 9 | 3/3 |
| network::dispatch_safety_unstable_bytes16_n32 | SUCCESS | SUCCESS | 126.870476 | 0/382 | 8 | 2/2 |
| network::insert_tail_contract_u64_start1_tail11_to12 | SUCCESS | SUCCESS | 199.78485 | 0/623 | 44 | 4/4 |
| network::insert_tail_contract_u64_start1_tail13 | SUCCESS | SUCCESS | 231.39142 | 0/623 | 42 | 3/3 |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | SUCCESS | 237.20578 | 0/623 | 40 | 3/3 |
| network::insert_tail_contract_u64_start1_tail2_to5 | SUCCESS | SUCCESS | 210.27011 | 0/623 | 58 | 6/6 |
| network::insert_tail_contract_u64_start1_tail6_to8 | SUCCESS | SUCCESS | 229.83519 | 0/623 | 52 | 5/5 |
| network::insert_tail_contract_u64_start1_tail9_to10 | SUCCESS | SUCCESS | 193.22226 | 0/623 | 48 | 4/4 |
| network::network_safety_unstable_u64_n30 | SUCCESS | SUCCESS | 112.93425 | 0/316 | 12 | 3/3 |
| network::network_safety_unstable_u64_n31 | SUCCESS | SUCCESS | 116.823906 | 0/316 | 12 | 3/3 |
| network::network_safety_unstable_u64_n32 | SUCCESS | SUCCESS | 117.06356 | 0/316 | 12 | 3/3 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- 61 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_direct_u64_n9_lt_lt
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_bytes16_n32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes16_n15
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes16_n16
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes16_n17
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes17_n15
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes17_n16
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_stable_unstable_bytes17_n17
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_unstable_bytes16_n32
- 44 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail11_to12
- 42 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail13
- 40 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail14
- 58 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail2_to5
- 52 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail6_to8
- 48 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail9_to10
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_safety_unstable_u64_n30
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_safety_unstable_u64_n31
- 12 unreachable check(s) in slice::sort::shared::smallsort::verify::network::network_safety_unstable_u64_n32
