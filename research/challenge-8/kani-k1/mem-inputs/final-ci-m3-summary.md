# K-1 run `coord-final-macos-p3of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `b14e576d75605688d2f902aa37a1eb02df8582a098b9fbe2b76087357c3efa5f`
- run 40665992084 attempt 1, image macos26 20261021.0445.8, build success
- agent `coordinator`, kind `partition`, runner `macos-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 2704048 KiB, wall 1765.79s (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 343 samples, largest sampled sum of RSS 11.76 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 2.45 GiB (≤13 GiB), seen 5–1146 s
  - `cbmc` 1.12 GiB (≤13 GiB), seen 1198–1756 s
  - `mds_stores` 0.63 GiB (≤13 GiB), seen 0–1761 s
  - `kani` 0.22 GiB (≤13 GiB), seen 0–1761 s
  - `goto-cc` 0.16 GiB (≤13 GiB), seen 326–1494 s
  - `_goto-cc_` 0.15 GiB (≤13 GiB), seen 490–1494 s
  - `Spotlight` 0.13 GiB (≤13 GiB), seen 0–1761 s
  - `softwareupdated` 0.13 GiB (≤13 GiB), seen 0–1761 s
  - `mds` 0.12 GiB (≤13 GiB), seen 0–1761 s
  - `_cbmc_` 0.11 GiB (≤13 GiB), seen 1219–1364 s
  - `Runner.Worker` 0.10 GiB (≤13 GiB), seen 0–1761 s

Partition 3/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 0 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 735.022 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| num::nonzero::verify::nonzero_check_isqrt_u32 | SUCCESS | 264.8335 |
| num::nonzero::verify::nonzero_check_isqrt_u128_small | SUCCESS | 32.307045 |
| num::nonzero::verify::nonzero_check_isqrt_u128_mid | SUCCESS | 24.707949 |
| num::nonzero::verify::nonzero_check_checked_mul_i128_small | SUCCESS | 18.464905 |
| num::nonzero::verify::check_mul_i128_edge_pos | SUCCESS | 16.29458 |
| num::nonzero::verify::check_mul_i128_edge_neg | SUCCESS | 15.301981 |
| num::nonzero::verify::nonzero_check_saturating_pow_for_i128 | SUCCESS | 13.800305 |
| num::nonzero::verify::nonzero_check_checked_pow_for_i128 | SUCCESS | 13.572238 |
| num::nonzero::verify::check_mul_i128_small | SUCCESS | 10.182786 |
| num::nonzero::verify::check_mul_i128_large_pos | SUCCESS | 9.041688 |
| num::nonzero::verify::nonzero_check_isqrt_u64_small | SUCCESS | 8.996278 |
| num::nonzero::verify::nonzero_check_isqrt_usize_small | SUCCESS | 8.891069 |
| num::nonzero::verify::nonzero_check_isqrt_u128_large | SUCCESS | 8.537045 |
| num::nonzero::verify::check_mul_i128_large_neg | SUCCESS | 7.9262285 |
| num::nonzero::verify::nonzero_check_saturating_pow_for_u128 | SUCCESS | 4.879795 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 2704048 KiB exceeds the largest sampled command peak 2569120 KiB: a process grew between samples; use the time -v value as the true single-process peak
