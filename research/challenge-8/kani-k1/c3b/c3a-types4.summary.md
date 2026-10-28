# K-1 run `c3a-types-priority1-01`: COMPLETE

- head `8003d40abe12b3cfdc48729f060fd0a3214e6be6`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `d1ee7c01098203a17b3b0e8ed19e69155e6bbe408fd7bf5968312468b49bab0b`
- run 2f10637a-a1d4-420f-ab5c-7eae9ecb8d97 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `measurement`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: False; Kani exit 1
- whole run, including compilation: max RSS 2263336 KiB, wall 18:37.15 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 559 samples, largest sampled sum of RSS 2.41 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-driver` 2.16 GiB (≤13 GiB), seen 0–1116 s
  - `kani-compiler` 1.73 GiB (≤13 GiB), seen 2–64 s
  - `cbmc` 1.43 GiB (≤13 GiB), seen 68–1114 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 711–765 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 66–66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–64 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1117 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–1116 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–1116 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 0–1116 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1117 s

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| types::sorted_permutation_traits_fallback_cell_u8_n0_to2 | SUCCESS | SUCCESS | 40.57603 | 0/573 | 20 | 14/18 |
| types::sorted_permutation_traits_fallback_cell_u8_n7_to9 | SUCCESS | TIMEOUT | None |  | None |  |
| types::sorted_permutation_traits_general_drop_u8_n0_to2 | SUCCESS | SUCCESS | 53.581898 | 0/739 | 24 | 14/18 |
| types::sorted_permutation_traits_general_drop_u8_n7_to9 | SUCCESS | SUCCESS | 349.6911 | 0/738 | 6 | 18/18 |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 5f2f37f55022d92e365b4453ad3a6e1748fc9bb18f879142d74ef5104922cb87
- `research/challenge-8/kani-k1/tools/kani_k1.py` 11c1d129ea913d2948f5ed80ebf6bf62e129d1ed845c0365db68b79026eff7e8
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 20 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_fallback_cell_u8_n0_to2
- 24 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_general_drop_u8_n0_to2
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::types::sorted_permutation_traits_general_drop_u8_n7_to9
