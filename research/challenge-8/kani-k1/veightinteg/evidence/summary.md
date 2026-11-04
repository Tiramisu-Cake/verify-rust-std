# K-1 run `veightinteg-g1-20261105-02`: COMPLETE

- head `91aeee2c62c3fc1e665fa7a44a5787c8283e54ab`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `67856fbccfcd68a923830ff8fcac6393a245a6a23b1628b4df64c4a31239df81`
- run 03d45e6a-0553-414e-83ea-6f6c9ce87778 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 1897304 KiB, wall 7:48.51 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 235 samples, largest sampled sum of RSS 2.05 GiB at 58 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.81 GiB (≤13 GiB), seen 2–76 s, peak sample 58 s
  - `cbmc` 1.24 GiB (≤13 GiB), seen 84–467 s, peak sample 262 s
  - `kani-driver` 0.51 GiB (≤13 GiB), seen 2–467 s, peak sample 108 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 78–363 s, peak sample 80 s
  - `rust-lld` 0.05 GiB (≤13 GiB), seen 4–4 s, peak sample 4 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 82–461 s, peak sample 379 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–76 s, peak sample 64 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–468 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–467 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–468 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–467 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 1.18 GiB at 262 s
  - simultaneous driver RSS 0.42 GiB at 415 s
  - cbmc PID 23638: 1.24 GiB peak at 262 s; active `T0:realcontracts::insert_tail_safety_u64_tail1_to4_backing5`
  - cbmc PID 23600: 0.83 GiB peak at 242 s; active `T0:realcontracts::sort4_safety_u64`
  - cbmc PID 23524: 0.71 GiB peak at 170 s; active `T0:realcontracts::merge_safety_u64_len4`
  - cbmc PID 23432: 0.45 GiB peak at 98 s; active `T0:permtags::network_u8_n13`
  - cbmc PID 23562: 0.43 GiB peak at 208 s; active `T0:realcontracts::merge_safety_u64_len2`
  - cbmc PID 23747: 0.42 GiB peak at 351 s; active `T0:realcontracts::unstable_network_safety_u8_n13_stubbed`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| permtags::network_u8_n13 | SUCCESS | SUCCESS | 24.318867 | 0/559 | 18 | 1/1 |
| permtags::network_u8_n9 | SUCCESS | SUCCESS | 14.063343 | 0/559 | 18 | 1/1 |
| permtags::tag_types_preserve_source_routes | SUCCESS | SUCCESS | 0.06044549 | 0/14 | 1 | 1/1 |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | SUCCESS | 38.1495 | 0/219 | 4 | 7/7 |
| realcontracts::merge_safety_u64_len2 | SUCCESS | SUCCESS | 31.429583 | 0/284 | 8 | 4/4 |
| realcontracts::merge_safety_u64_len4 | SUCCESS | SUCCESS | 45.406685 | 0/284 | 8 | 4/4 |
| realcontracts::sort4_safety_u64 | SUCCESS | SUCCESS | 35.744152 | 0/293 | 6 | 3/3 |
| realcontracts::swap_safety_bytes17_backing4 | SUCCESS | SUCCESS | 33.57819 | 0/402 | 9 | 6/6 |
| realcontracts::swap_safety_u64_backing4 | SUCCESS | SUCCESS | 20.581472 | 0/229 | 4 | 6/6 |
| realcontracts::swap_safety_u8_backing13 | SUCCESS | SUCCESS | 19.395584 | 0/219 | 4 | 6/6 |
| realcontracts::swap_safety_u8_backing4 | SUCCESS | SUCCESS | 19.17471 | 0/229 | 4 | 6/6 |
| realcontracts::swap_safety_u8_backing9 | SUCCESS | SUCCESS | 18.622524 | 0/219 | 4 | 6/6 |
| realcontracts::unstable_network_safety_u8_n13_stubbed | SUCCESS | SUCCESS | 18.837992 | 0/387 | 18 | 1/1 |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | SUCCESS | 8.316227 | 0/387 | 18 | 1/1 |
| scratchgeom::stable_u64_min_scratch_n2 | SUCCESS | SUCCESS | 5.838726 | 0/423 | 76 | 2/2 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- time -v max RSS 1897304 KiB exceeds the largest sampled command peak 1896988 KiB: a process grew between samples; use the time -v value as the true single-process peak
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::permtags::network_u8_n13
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::permtags::network_u8_n9
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::permtags::tag_types_preserve_source_routes
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::insert_tail_safety_u64_tail1_to4_backing5
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::merge_safety_u64_len2
- 8 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::merge_safety_u64_len4
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::sort4_safety_u64
- 9 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_bytes17_backing4
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_u64_backing4
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_u8_backing13
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_u8_backing4
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_u8_backing9
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::unstable_network_safety_u8_n13_stubbed
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::unstable_network_safety_u8_n9_stubbed
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::scratchgeom::stable_u64_min_scratch_n2
