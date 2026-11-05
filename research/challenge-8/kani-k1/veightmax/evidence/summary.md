# K-1 run `veightmax-g1-20261105-02`: PARTIAL

- head `7df3f7d3d68c458185c2f42f72483c13fbe9c161`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `5e6e812216996d281d57aa8bb2626c27b32fed1be71329b2c7cc96261e6161fc`
- run daf1045c-5454-4662-93a7-df16cfd23e00 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 124
- whole run, including compilation: max RSS None KiB, wall None (UNPARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 136 samples, largest sampled sum of RSS 1.87 GiB at 62 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.65 GiB (≤13 GiB), seen 4–80 s, peak sample 62 s
  - `cbmc` 1.48 GiB (≤13 GiB), seen 86–269 s, peak sample 262 s
  - `kani-driver` 0.24 GiB (≤13 GiB), seen 2–268 s, peak sample 94 s
  - `goto-instrument` 0.03 GiB (≤13 GiB), seen 84–182 s, peak sample 182 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 82–82 s, peak sample 82 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–80 s, peak sample 70 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–269 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–268 s, peak sample 2 s
  - `build_script_bu` 0.00 GiB (≤13 GiB), seen 4–4 s, peak sample 4 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–268 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–268 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 1.44 GiB at 260 s
  - simultaneous driver RSS 0.21 GiB at 180 s
  - cbmc PID 22924: 1.48 GiB peak at 262 s; active `T0:allocationcontracts::unstable_network_safety_u8_n32_stubbed`
  - cbmc PID 22895: 1.29 GiB peak at 176 s; active `T0:allocationcontracts::merge_safety_u64_len8_scratch48_src32_dst0`
  - cbmc PID 22857: 0.16 GiB peak at 90 s; active `T0:allocationcontracts::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| allocationcontracts::swap_safety_u8_backing32 | SUCCESS | NOT_RUN |  |  |  |  |
| allocationcontracts::swap_safety_u64_backing32 | SUCCESS | NOT_RUN |  |  |  |  |
| allocationcontracts::unstable_network_safety_u8_n32_stubbed | SUCCESS | UNKNOWN | None |  | None |  |
| allocationcontracts::merge_safety_u64_len8_scratch48_src32_dst0 | SUCCESS | SUCCESS | 86.45552 | 0/228 | 8 | 5/5 |
| allocationcontracts::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed | SUCCESS | SUCCESS | 8.113433 | 0/269 | 9 | 4/4 |
| tailcontracts::insert_tail_safety_u64_backing17_tail1_to7 | SUCCESS | NOT_RUN |  |  |  |  |
| tailcontracts::insert_tail_safety_u64_backing17_tail8_to15 | SUCCESS | NOT_RUN |  |  |  |  |

Inconsistencies:
- final 'Complete - …' line missing

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::allocationcontracts::merge_safety_u64_len8_scratch48_src32_dst0
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::allocationcontracts::sort8_safety_u64_scratch48_src32_dst0_merge_stubbed
