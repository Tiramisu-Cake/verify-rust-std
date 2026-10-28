# K-1 run `c3b-heavy3-before-j1`: COMPLETE

- head `ff40dd99fb5d1ead04635540e84366800e67a8ed`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `ac4202c089d651efa287d5af60786c10e78c4d5137f1178250818c52972048da`
- run 02b3bd09-26e8-401d-84b5-b33c6d55f759 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 5278436 KiB, wall 15:47.16 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 474 samples, largest sampled sum of RSS 6.57 GiB at 914 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-driver` 5.03 GiB (≤13 GiB), seen 0–946 s, peak sample 284 s
  - `cbmc` 3.49 GiB (≤13 GiB), seen 72–946 s, peak sample 914 s
  - `kani-compiler` 1.66 GiB (≤13 GiB), seen 2–66 s, peak sample 52 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 70–288 s, peak sample 286 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–66 s, peak sample 4 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 68–766 s, peak sample 284 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–946 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–947 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–946 s, peak sample 0 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–947 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 0–946 s, peak sample 0 s

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n13 | SUCCESS | SUCCESS | 476.77588 | 0/442 | 84 | 1/1 |
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS | SUCCESS | 213.54361 | 0/723 | 82 | 2/2 |
| network::mutating_insertion_safety_cell_n11_to12 | SUCCESS | SUCCESS | 180.03354 | 0/195 | 4 | 8/8 |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` fb8663df29332899c81c1865583facc5394e6941c484027d896e2cadc0beda04
- `research/challenge-8/kani-k1/tools/kani_k1.py` 1ac896f51b7d1ed1c07a29e8010ffea29ea1c74f2b6e0ece2de10123e1ebf2ef
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 84 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u64_n13
- 82 unreachable check(s) in slice::sort::shared::smallsort::verify::correct::sorted_permutation_general_stable_u8_n14
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::mutating_insertion_safety_cell_n11_to12
