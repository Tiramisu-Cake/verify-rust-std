# K-1 run `citrim-g2-20261105-02`: COMPLETE

- head `9cc449ccce74c6b3b8f96554b86308ff39a2b71f`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `7822880947beb888d1a7a3103b2f8e9c2b942269536565ee3363e1884d2d7616`
- run bd623a0c-935a-4bcd-a5c1-5d6f148c6bec attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2359796 KiB, wall 1:13:53 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 2211 samples, largest sampled sum of RSS 3.03 GiB at 3332 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.25 GiB (≤13 GiB), seen 74–4432 s, peak sample 2780 s
  - `kani-compiler` 1.73 GiB (≤13 GiB), seen 2–68 s, peak sample 54 s
  - `kani-driver` 0.71 GiB (≤13 GiB), seen 2–4432 s, peak sample 4428 s
  - `kissat` 0.49 GiB (≤13 GiB), seen 80–4416 s, peak sample 2220 s
  - `goto-instrument` 0.08 GiB (≤13 GiB), seen 375–4012 s, peak sample 2487 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–68 s, peak sample 58 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 70–676 s, peak sample 70 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 1279–2485 s, peak sample 2485 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–4432 s, peak sample 2 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–4434 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–4432 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 2.25 GiB at 2780 s
  - simultaneous driver RSS 0.70 GiB at 4428 s
  - simultaneous solver RSS 0.48 GiB at 2043 s
  - cbmc PID 9656: 2.25 GiB peak at 2780 s; active `T0:network::insert_tail_contract_u64_start1_tail13`
  - cbmc PID 9704: 2.24 GiB peak at 3089 s; active `T0:network::insert_tail_contract_u64_start1_tail14`
  - cbmc PID 9759: 2.21 GiB peak at 3372 s; active `T0:network::insert_tail_contract_u64_start1_tail11_to12`
  - cbmc PID 9808: 2.17 GiB peak at 3699 s; active `T0:network::insert_tail_contract_u64_start1_tail9_to10`
  - cbmc PID 9907: 2.13 GiB peak at 4303 s; active `T0:network::insert_tail_contract_u64_start1_tail6_to8`
  - cbmc PID 9857: 2.07 GiB peak at 3972 s; active `T0:network::insert_tail_contract_u64_start1_tail2_to5`
  - kissat PID 9612: 0.49 GiB peak at 2220 s; active `T0:merge::general_direct_u64_n9_keep0_keep4`
  - kissat PID 9545: 0.49 GiB peak at 1769 s; active `T0:merge::general_direct_u64_n9_swap0_keep4`
  - kissat PID 9461: 0.49 GiB peak at 1015 s; active `T0:merge::general_direct_u64_n9_keep0_swap4`
  - kissat PID 9468: 0.49 GiB peak at 1217 s; active `T0:merge::general_direct_u64_n9_keep0_swap4`
  - kissat PID 9621: 0.49 GiB peak at 2444 s; active `T0:merge::general_direct_u64_n9_keep0_keep4`
  - kissat PID 9615: 0.49 GiB peak at 2296 s; active `T0:merge::general_direct_u64_n9_keep0_keep4`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_direct_u64_n9_keep0_keep4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_keep0_swap4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_swap0_keep4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_direct_u64_n9_swap0_swap4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_keep0_keep4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_keep0_swap4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_swap0_keep4 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::stable_direct_u64_n9_swap0_swap4 | SUCCESS | TIMEOUT | None |  | None |  |
| network::dispatch_safety_unstable_bytes16_n32 | SUCCESS | SUCCESS | 118.51086 | 0/382 | 8 | 2/2 |
| network::insert_tail_contract_u64_start1_tail11_to12 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail13 | SUCCESS | SUCCESS | 299.7872 | 0/602 | 42 | 3/3 |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail2_to5 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail6_to8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail9_to10 | SUCCESS | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::network::dispatch_safety_unstable_bytes16_n32
- 42 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail13
