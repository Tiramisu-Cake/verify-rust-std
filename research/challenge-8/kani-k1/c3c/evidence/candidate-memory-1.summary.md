# K-1 run `c3c-memory-candidate-1of2`: COMPLETE

- head `1216fc2884f01af67d6328fd927edce418933af9`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `d4183063d2a63d0316e02001932ea9cfe3b2a813e2ce1c4013824e7fb102f4ae`
- run 5ae76959-e306-4b33-9506-402bc9909768 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2611288 KiB, wall 21:23.49 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 640 samples, largest sampled sum of RSS 5.45 GiB at 567 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.49 GiB (≤13 GiB), seen 76–1283 s, peak sample 682 s
  - `kani-compiler` 1.94 GiB (≤13 GiB), seen 2–64 s, peak sample 54 s
  - `kani-driver` 0.82 GiB (≤13 GiB), seen 2–1283 s, peak sample 1094 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 66–1160 s, peak sample 68 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 72–990 s, peak sample 467 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 62 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1283 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1283 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 382–1160 s, peak sample 382 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1283 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1283 s, peak sample 0 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 4.97 GiB at 543 s
  - simultaneous driver RSS 0.82 GiB at 1094 s
  - cbmc PID 9895: 2.49 GiB peak at 682 s; active `T0:network::network_correctness_u64_n13,T1:merge::merge_contract_u64_n16,T2:network::insert_tail_contract_u64_start6_tail14`
  - cbmc PID 10092: 2.26 GiB peak at 972 s; active `T0:network::network_correctness_u8_n17,T1:merge::merge_contract_u64_n15,T2:network::network_correctness_u8_n16`
  - cbmc PID 9497: 2.19 GiB peak at 374 s; active `T0:network::network_correctness_u64_n8,T1:merge::merge_contract_u64_n14,T2:network::insertion_permutation_u64_n12`
  - cbmc PID 9922: 1.33 GiB peak at 539 s; active `T0:network::network_correctness_u64_n13,T1:merge::merge_contract_u64_n16,T2:merge::route_safety_noncopy_u64_n32`
  - cbmc PID 9951: 1.31 GiB peak at 555 s; active `T0:network::network_correctness_u64_n13,T1:merge::merge_contract_u64_n15,T2:network::network_correctness_u8_n16`
  - cbmc PID 10329: 1.28 GiB peak at 1062 s; active `T0:network::network_correctness_u8_n17,T1:merge::route_safety_noncopy_u64_n31`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u8_n17 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n15 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::route_safety_general_u64_n31 | SUCCESS | SUCCESS | 66.26985 | 0/280 | 5 |  |
| merge::route_safety_noncopy_u64_n31 | SUCCESS | SUCCESS | 105.07332 | 0/527 | 9 |  |
| merge::route_safety_stable_u64_n31 | SUCCESS | SUCCESS | 59.33209 | 0/278 | 5 |  |
| merge::route_safety_general_u64_n32 | SUCCESS | SUCCESS | 61.24718 | 0/280 | 5 |  |
| merge::route_safety_noncopy_u64_n32 | SUCCESS | SUCCESS | 101.15898 | 0/527 | 9 |  |
| merge::route_safety_stable_u64_n32 | SUCCESS | SUCCESS | 63.054222 | 0/278 | 5 |  |
| network::insert_tail_contract_u64_start6_tail7 | SUCCESS | SUCCESS | 13.42738 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail8 | SUCCESS | SUCCESS | 9.509321 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail9 | SUCCESS | SUCCESS | 16.061272 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail10 | SUCCESS | SUCCESS | 17.10515 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail11 | SUCCESS | SUCCESS | 14.197164 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail12 | SUCCESS | SUCCESS | 17.100595 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail13 | SUCCESS | SUCCESS | 25.565466 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail14 | SUCCESS | SUCCESS | 32.047977 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail15 | SUCCESS | SUCCESS | 34.936207 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start6_tail16 | SUCCESS | SUCCESS | 26.340612 | 0/415 | 36 |  |
| network::network_correctness_u8_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n8 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n13 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insert_tail_contract_u64_start1_tail2 | SUCCESS | SUCCESS | 8.977134 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail3 | SUCCESS | SUCCESS | 13.736409 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail4 | SUCCESS | SUCCESS | 14.838967 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail5 | SUCCESS | SUCCESS | 18.371464 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail6 | SUCCESS | SUCCESS | 14.303041 | 0/415 | 36 |  |
| network::insert_tail_contract_u64_start1_tail7 | SUCCESS | SUCCESS | 16.594395 | 0/415 | 36 |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 51e80f4c3b7d6cebb3bca102293379490fa375634ef081e2530b683fe7db152f
- `research/challenge-8/kani-k1/tools/kani_k1.py` eb7c3dda5ac14badf87841b2f185690705bc7617e1c45a302eafbd0a7dced1e1
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 2611288 KiB exceeds the largest sampled command peak 2607828 KiB: a process grew between samples; use the time -v value as the true single-process peak
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_general_u64_n31
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_noncopy_u64_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_stable_u64_n31
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_general_u64_n32
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_noncopy_u64_n32
- 5 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::route_safety_stable_u64_n32
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail7
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail8
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail9
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail10
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail11
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail12
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail13
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail14
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail15
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start6_tail16
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail2
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail3
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail4
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail5
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail6
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail7
