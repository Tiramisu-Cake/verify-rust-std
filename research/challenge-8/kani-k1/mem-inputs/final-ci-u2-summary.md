# K-1 run `coord-final-ubuntu-p2of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `d84971acc8295ccae775fd923f5fb753d0ba6ba8637229a029b82078cdad863a`
- run 40665992084 attempt 2, image ubuntu24 20261023.334.3, build success
- agent `coordinator`, kind `partition`, runner `ubuntu-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 10605204 KiB, wall 2:46:56 (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 1998 samples, largest sampled sum of RSS 15.25 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-driver` 9.84 GiB (≤13 GiB), seen 5–10013 s
  - `cbmc` 6.52 GiB (≤13 GiB), seen 1373–9998 s
  - `kani-compiler` 4.12 GiB (≤13 GiB), seen 5–1308 s
  - `goto-instrument` 1.80 GiB (≤13 GiB), seen 1373–8956 s
  - `goto-cc` 0.26 GiB (≤13 GiB), seen 391–8850 s
  - `provjobd2650030` 0.15 GiB (≤13 GiB), seen 0–10013 s
  - `Runner.Worker` 0.14 GiB (≤13 GiB), seen 0–10013 s
  - `Runner.Listener` 0.11 GiB (≤13 GiB), seen 0–10013 s

Partition 2/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 280 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 15759.731 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n14 | SUCCESS | 569.408 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_perm_u64_n12 | SUCCESS | 482.4512 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u8_n17 | SUCCESS | 399.94034 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len12 | SUCCESS | 308.49472 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n13 | SUCCESS | 297.58383 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len16 | SUCCESS | 265.4925 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n8 | SUCCESS | 256.51022 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u8_n16 | SUCCESS | 205.09145 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len11 | SUCCESS | 201.92398 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u8_len13 | SUCCESS | 193.5112 |
| slice::sort::shared::smallsort::kani_k1::merge::w2night_fallback_u8_len8 | SUCCESS | 181.90096 |
| slice::sort::shared::smallsort::kani_k1::correct::l2_fallback_u64_n16 | SUCCESS | 179.51419 |
| slice::sort::shared::smallsort::kani_k1::merge::w2_a_all_len32_safety | SUCCESS | 178.50594 |
| slice::sort::shared::smallsort::kani_k1::merge::w2night_drop_upper16_perm | SUCCESS | 178.47914 |
| slice::sort::shared::smallsort::kani_k1::correct::l2_gs_u8_n15 | SUCCESS | 173.5884 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 10605204 KiB exceeds the largest sampled command peak 10319864 KiB: a process grew between samples; use the time -v value as the true single-process peak
