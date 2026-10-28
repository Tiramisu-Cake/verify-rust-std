# K-1 run `coord-final-macos-p2of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `1285e83a786110f69200a26616dac730a423df7ac8b4af9eab95f5c5c31aa841`
- run 40665992084 attempt 1, image macos26 20261021.0445.8, build success
- agent `coordinator`, kind `partition`, runner `macos-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 4082512 KiB, wall 11038.39s (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 2107 samples, largest sampled sum of RSS 11.57 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani` 3.85 GiB (≤13 GiB), seen 0–11037 s
  - `cbmc` 2.68 GiB (≤13 GiB), seen 1552–11016 s
  - `kani-compiler` 2.12 GiB (≤13 GiB), seen 10–1464 s
  - `goto-instrument` 1.84 GiB (≤13 GiB), seen 1552–10487 s
  - `_cbmc_` 1.37 GiB (≤13 GiB), seen 1583–7970 s
  - `mds_stores` 0.63 GiB (≤13 GiB), seen 0–11037 s
  - `_kani-compiler_` 0.29 GiB (≤13 GiB), seen 0–5 s
  - `goto-cc` 0.24 GiB (≤13 GiB), seen 590–10575 s
  - `_goto-cc_` 0.22 GiB (≤13 GiB), seen 611–9171 s
  - `softwareupdated` 0.12 GiB (≤13 GiB), seen 0–11037 s
  - `contactsd` 0.12 GiB (≤13 GiB), seen 0–11037 s
  - `Spotlight` 0.11 GiB (≤13 GiB), seen 0–11037 s
  - …only the 12 largest commands listed

Partition 2/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 280 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 26969.049 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_perm_u64_n12 | SUCCESS | 1266.1135 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n14 | SUCCESS | 924.1855 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u8_len13 | SUCCESS | 720.36957 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u8_n17 | SUCCESS | 682.7469 |
| slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_mid | SUCCESS | 567.3438 |
| slice::sort::shared::smallsort::kani_k1::network::w2_k16_a16_mid | SUCCESS | 522.2749 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u8_len12 | SUCCESS | 445.49902 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len12 | SUCCESS | 387.72577 |
| slice::sort::shared::smallsort::kani_k1::correct::l2_fallback_u64_n16 | SUCCESS | 386.0225 |
| slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_n32 | SUCCESS | 363.1275 |
| slice::sort::shared::smallsort::kani_k1::merge::w2p2_gs_u64_len11 | SUCCESS | 358.12033 |
| slice::sort::shared::smallsort::kani_k1::merge::w2_a_all_len32_safety | SUCCESS | 338.92224 |
| slice::sort::shared::smallsort::kani_k1::network::w2_k16_a17_n31 | SUCCESS | 315.97186 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n8 | SUCCESS | 315.82455 |
| slice::sort::shared::smallsort::kani_k1::network::w2p2_k10_u64_n13 | SUCCESS | 308.655 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 4082512 KiB exceeds the largest sampled command peak 4032752 KiB: a process grew between samples; use the time -v value as the true single-process peak
