# K-1 run `coord-final-macos-p4of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `9d290c347a8aed7efc8f50dc845ebb0b182ffce715cc74149b070dc241f61155`
- run 40665992084 attempt 1, image macos26 20261013.0424.1, build success
- agent `coordinator`, kind `partition`, runner `macos-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 3018752 KiB, wall 4539.48s (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 880 samples, largest sampled sum of RSS 12.04 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 2.65 GiB (≤13 GiB), seen 5–963 s
  - `cbmc` 2.28 GiB (≤13 GiB), seen 1014–4535 s
  - `kani` 1.60 GiB (≤13 GiB), seen 0–4535 s
  - `mds_stores` 0.96 GiB (≤13 GiB), seen 0–4535 s
  - `goto-cc` 0.16 GiB (≤13 GiB), seen 278–4484 s
  - `Spotlight` 0.15 GiB (≤13 GiB), seen 0–4535 s
  - `_goto-cc_` 0.12 GiB (≤13 GiB), seen 283–3734 s
  - `corespotlightd` 0.12 GiB (≤13 GiB), seen 0–4535 s
  - `contactsd` 0.11 GiB (≤13 GiB), seen 0–4535 s
  - `Runner.Worker` 0.10 GiB (≤13 GiB), seen 0–4535 s

Partition 4/4 (organizers' layout), KANI_JOBS unset (-j): 523 harnesses, 75 of them smallsort kani_k1; statuses {'SUCCESS': 523}; sum of Verification Time 9233.45 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len16 | SUCCESS | 510.78152 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len15 | SUCCESS | 398.2396 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start2_u64 | SUCCESS | 365.01385 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start1_u64 | SUCCESS | 334.0896 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len14 | SUCCESS | 318.5184 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start3_u64 | SUCCESS | 315.7525 |
| slice::sort::shared::smallsort::kani_k1::network::w2night_k8r_start4_u64 | SUCCESS | 294.5164 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len16 | SUCCESS | 276.4071 |
| ptr::non_null::verify::non_null_check_write_unaligned_i128 | SUCCESS | 237.62868 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len13 | SUCCESS | 228.78693 |
| ptr::non_null::verify::non_null_check_write_unaligned_u128 | SUCCESS | 223.7279 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len15 | SUCCESS | 210.10257 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len14 | SUCCESS | 207.94559 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u64_len12 | SUCCESS | 189.58003 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_bm_u8_len13 | SUCCESS | 177.7124 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 3018752 KiB exceeds the largest sampled command peak 2778576 KiB: a process grew between samples; use the time -v value as the true single-process peak
