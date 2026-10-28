# K-1 run `coord-final-ubuntu-p4of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `c3c43b1894efafd3e63c1fd6583e00714e76f72fdd96c6732233b5f422468921`
- run 40665992084 attempt 1, image ubuntu24 20261026.354.1, build success
- agent `coordinator`, kind `partition`, runner `ubuntu-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 4567760 KiB, wall 1:32:21 (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 1106 samples, largest sampled sum of RSS 8.83 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 4.20 GiB (≤13 GiB), seen 1042–5537 s
  - `kani-compiler` 4.09 GiB (≤13 GiB), seen 5–972 s
  - `kani-driver` 3.20 GiB (≤13 GiB), seen 5–5537 s
  - `goto-cc` 0.19 GiB (≤13 GiB), seen 321–4380 s
  - `provjobd1003233` 0.13 GiB (≤13 GiB), seen 0–5537 s
  - `Runner.Worker` 0.13 GiB (≤13 GiB), seen 0–5537 s
  - `Runner.Listener` 0.11 GiB (≤13 GiB), seen 0–5537 s

Partition 4/4 (organizers' layout), KANI_JOBS unset (-j): 525 harnesses, 75 of them smallsort kani_k1; statuses {'SUCCESS': 525}; sum of Verification Time 7006.865 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len16 | SUCCESS | 382.33026 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start1_u64 | SUCCESS | 323.3655 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start2_u64 | SUCCESS | 276.94073 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len15 | SUCCESS | 233.34915 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len14 | SUCCESS | 229.24196 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start4_u64 | SUCCESS | 219.63367 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start3_u64 | SUCCESS | 215.2304 |
| ptr::non_null::verify::non_null_check_write_unaligned_i128 | SUCCESS | 207.5255 |
| ptr::non_null::verify::non_null_check_write_unaligned_u128 | SUCCESS | 205.13437 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len16 | SUCCESS | 165.27626 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len13 | SUCCESS | 155.057 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len15 | SUCCESS | 147.18149 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start5_u64 | SUCCESS | 141.2212 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start8_u64 | SUCCESS | 140.05124 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len12 | SUCCESS | 136.494 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 4567760 KiB exceeds the largest sampled command peak 4401936 KiB: a process grew between samples; use the time -v value as the true single-process peak
