# K-1 run `c3b-heavy6-before-j3`: INCONSISTENT

- head `16202a68d9ce42d6ceae6a66cd2c6aa6da5ae350`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `75c700acff56c75b552dd7c39535fd7ad10bfa20cb335517baf8d442b1db87d4`
- run 311f6aa7-0e7c-4e0b-828f-eed3d3b68e56 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 5280116 KiB, wall 20:42.57 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 621 samples, largest sampled sum of RSS 9.58 GiB at 834 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-driver` 5.04 GiB (≤13 GiB), seen 0–1241 s, peak sample 359 s
  - `cbmc` 3.49 GiB (≤13 GiB), seen 70–1239 s, peak sample 836 s
  - `kani-compiler` 1.65 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 68–674 s, peak sample 70 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 68–68 s, peak sample 68 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–66 s, peak sample 66 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–1241 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1242 s, peak sample 0 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1242 s, peak sample 0 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 70–70 s, peak sample 70 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–1241 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 0–1241 s, peak sample 0 s

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n13 | SUCCESS | SUCCESS | 566.6999 | 0/442 | 84 | 1/1 |
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS | SUCCESS | 289.35147 | 0/723 | 82 | 2/2 |
| network::mutating_insertion_safety_cell_n11_to12 | SUCCESS | SUCCESS | 210.40353 | 0/195 | 4 | 8/8 |
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
