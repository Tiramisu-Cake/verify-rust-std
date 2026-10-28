# K-1 run `coord-final-macos-p1of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `5075d682fc8ce247c0a1e35c7be341b1337764bb080bb11cccbcccbc82252d9c`
- run 40665992084 attempt 1, image macos26 20261021.0445.8, build success
- agent `coordinator`, kind `partition`, runner `macos-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 3436688 KiB, wall 2264.17s (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 436 samples, largest sampled sum of RSS 12.17 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 3.06 GiB (≤13 GiB), seen 1764–2250 s
  - `kani-compiler` 2.63 GiB (≤13 GiB), seen 5–1607 s
  - `mds_stores` 0.69 GiB (≤13 GiB), seen 0–2260 s
  - `kani` 0.69 GiB (≤13 GiB), seen 0–2260 s
  - `goto-cc` 0.23 GiB (≤13 GiB), seen 590–2255 s
  - `_goto-cc_` 0.22 GiB (≤13 GiB), seen 663–2198 s
  - `goto-instrument` 0.21 GiB (≤13 GiB), seen 1769–2245 s
  - `Spotlight` 0.13 GiB (≤13 GiB), seen 0–2260 s
  - `softwareupdated` 0.12 GiB (≤13 GiB), seen 0–2260 s
  - `contactsd` 0.10 GiB (≤13 GiB), seen 0–2260 s
  - `corespotlightd` 0.10 GiB (≤13 GiB), seen 0–2260 s
  - `spindump` 0.10 GiB (≤13 GiB), seen 0–2260 s
  - …only the 12 largest commands listed

Partition 1/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 0 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 415.365 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_left_shift | SUCCESS | 83.627014 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_number_of_digits_decimal_left_shift | SUCCESS | 51.07428 |
| ffi::c_str::verify::check_to_str | SUCCESS | 35.924248 |
| ffi::c_str::verify::check_bytes | SUCCESS | 15.786216 |
| ffi::c_str::verify::check_as_ptr | SUCCESS | 13.015955 |
| ffi::c_str::verify::check_to_bytes | SUCCESS | 10.218892 |
| ffi::c_str::verify::check_to_bytes_with_nul | SUCCESS | 9.545578 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_right_shift | SUCCESS | 8.880648 |
| collections::vec_deque::verify::check_vecdeque_swap | SUCCESS | 6.4338665 |
| ffi::c_str::verify::check_is_empty | SUCCESS | 4.741039 |
| num::verify::widening_mul_u64_mid_edge | SUCCESS | 4.62365 |
| ffi::c_str::verify::check_count_bytes | SUCCESS | 3.8776863 |
| num::verify::carrying_mul_u64_mid_edge | SUCCESS | 3.0366855 |
| ffi::c_str::verify::check_from_bytes_until_nul | SUCCESS | 2.6507807 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_round | SUCCESS | 2.482444 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 3436688 KiB exceeds the largest sampled command peak 3213104 KiB: a process grew between samples; use the time -v value as the true single-process peak
