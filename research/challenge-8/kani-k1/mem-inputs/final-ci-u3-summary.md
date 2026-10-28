# K-1 run `coord-final-ubuntu-p3of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `185beba64111d3b0eed5eab7ac603079cd3e62ef274dfd6c32be862c0abcb3ad`
- run 40665992084 attempt 1, image ubuntu24 20261026.354.1, build success
- agent `coordinator`, kind `partition`, runner `ubuntu-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 4609456 KiB, wall 26:25.28 (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 317 samples, largest sampled sum of RSS 5.01 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 4.12 GiB (≤13 GiB), seen 5–1082 s
  - `cbmc` 0.65 GiB (≤13 GiB), seen 1117–1568 s
  - `kani-driver` 0.16 GiB (≤13 GiB), seen 5–1583 s
  - `goto-cc` 0.15 GiB (≤13 GiB), seen 291–1197 s
  - `Runner.Worker` 0.14 GiB (≤13 GiB), seen 0–1583 s
  - `provjobd2317857` 0.13 GiB (≤13 GiB), seen 0–1583 s
  - `Runner.Listener` 0.10 GiB (≤13 GiB), seen 0–1583 s

Partition 3/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 0 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 608.258 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| num::nonzero::verify::nonzero_check_isqrt_u32 | SUCCESS | 227.37154 |
| num::nonzero::verify::nonzero_check_isqrt_u128_small | SUCCESS | 28.767822 |
| num::nonzero::verify::nonzero_check_isqrt_u128_mid | SUCCESS | 25.573708 |
| num::nonzero::verify::nonzero_check_checked_mul_i128_small | SUCCESS | 20.768482 |
| num::nonzero::verify::check_mul_i128_edge_pos | SUCCESS | 16.929348 |
| num::nonzero::verify::nonzero_check_saturating_pow_for_i128 | SUCCESS | 16.827253 |
| num::nonzero::verify::nonzero_check_checked_pow_for_i128 | SUCCESS | 13.510285 |
| num::nonzero::verify::check_mul_i128_edge_neg | SUCCESS | 12.556159 |
| num::nonzero::verify::check_mul_i128_small | SUCCESS | 10.299725 |
| num::nonzero::verify::nonzero_check_isqrt_u128_large | SUCCESS | 8.653394 |
| num::nonzero::verify::check_mul_i128_large_neg | SUCCESS | 8.079029 |
| num::nonzero::verify::check_mul_i128_large_pos | SUCCESS | 7.5345764 |
| num::nonzero::verify::nonzero_check_isqrt_u64_small | SUCCESS | 7.502709 |
| num::nonzero::verify::nonzero_check_isqrt_usize_small | SUCCESS | 7.4848423 |
| num::nonzero::verify::nonzero_check_checked_pow_for_u128 | SUCCESS | 4.133054 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 4609456 KiB exceeds the largest sampled command peak 4320088 KiB: a process grew between samples; use the time -v value as the true single-process peak
