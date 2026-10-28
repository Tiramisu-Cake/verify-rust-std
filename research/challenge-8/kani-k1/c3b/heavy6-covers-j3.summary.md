# K-1 run `c3b-heavy6-covers-j3`: INCONSISTENT

- head `1b7a1cdac5c45cd732731f5f016a1c4c1bf66c8f`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `15b0645225412a9d6f1900e335478cca7597972391a4a378a48adb3a8dbc9545`
- run 6196139d-3428-4e11-8c70-39dcde7c25d2 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5282304 KiB, wall 22:46.13 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 682 samples, largest sampled sum of RSS 7.39 GiB at 761 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-driver` 5.04 GiB (≤13 GiB), seen 0–1364 s, peak sample 309 s
  - `cbmc` 3.32 GiB (≤13 GiB), seen 68–1364 s, peak sample 773 s
  - `kani-compiler` 1.76 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 66–915 s, peak sample 68 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–64 s, peak sample 4 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1366 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–1364 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1366 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–1364 s, peak sample 0 s
  - …only the 12 largest commands listed

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n13 | SUCCESS | SUCCESS | 449.15265 | 0/442 | 84 | 1/1 |
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS | SUCCESS | 241.70903 | 0/723 | 82 | 2/2 |
| network::mutating_insertion_safety_cell_n11_to12 | SUCCESS | SUCCESS | 118.02896 | 0/195 | 4 | 6/6 |
| network::network_correctness_u64_n14 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n12 | SUCCESS | TIMEOUT | None |  | None |  |

Inconsistencies:
- 2 harness block(s) started on a worker before its previous block ended under kani_jobs > 1: output may be interleaved

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` fb8663df29332899c81c1865583facc5394e6941c484027d896e2cadc0beda04
- `research/challenge-8/kani-k1/tools/kani_k1.py` 1ac896f51b7d1ed1c07a29e8010ffea29ea1c74f2b6e0ece2de10123e1ebf2ef
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 84 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u64_n13
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_stable_u8_n14
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::mutating_insertion_safety_cell_n11_to12
