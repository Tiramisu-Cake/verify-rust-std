# K-1 run `coord-final-ubuntu-p1of4`: COMPLETE

- head `49f7e73b3817db6e53da3d2cf792c2919e174d4c`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `eec63f33ec2e7338b59bfd98c069b7cd4553f216831ea850bd87706149188fcd`
- run 40665992084 attempt 1, image ubuntu24 20261023.334.3, build success
- agent `coordinator`, kind `partition`, runner `ubuntu-latest`, per-harness timeout 300 min, harnesses in parallel None, uninit checks off, controls cfg off
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 4527588 KiB, wall 39:08.18 (PARSED)
- verify memory cap: not tracked by this lane
- memory peaks PARSED: sampled every 5 s, 469 samples, largest sampled sum of RSS 5.80 GiB; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 4.17 GiB (≤13 GiB), seen 5–1519 s
  - `cbmc` 2.66 GiB (≤13 GiB), seen 1674–2316 s
  - `kani-driver` 0.75 GiB (≤13 GiB), seen 0–2346 s
  - `goto-instrument` 0.33 GiB (≤13 GiB), seen 1674–2341 s
  - `goto-cc` 0.25 GiB (≤13 GiB), seen 411–2346 s
  - `provjobd3748376` 0.14 GiB (≤13 GiB), seen 0–2346 s
  - `Runner.Worker` 0.13 GiB (≤13 GiB), seen 0–2346 s
  - `Runner.Listener` 0.11 GiB (≤13 GiB), seen 0–2346 s

Partition 1/4 (organizers' layout), KANI_JOBS unset (-j): 526 harnesses, 0 of them smallsort kani_k1; statuses {'SUCCESS': 526}; sum of Verification Time 462.254 s (concurrent runs overlap; wall is above)

Slowest 15:

| harness | status | time s |
|---|---|---|
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_left_shift | SUCCESS | 81.86469 |
| ffi::c_str::verify::check_to_str | SUCCESS | 51.812397 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_number_of_digits_decimal_left_shift | SUCCESS | 41.82923 |
| ffi::c_str::verify::check_bytes | SUCCESS | 28.40984 |
| ffi::c_str::verify::check_as_ptr | SUCCESS | 21.678877 |
| ffi::c_str::verify::check_to_bytes_with_nul | SUCCESS | 15.007437 |
| ffi::c_str::verify::check_to_bytes | SUCCESS | 14.098264 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_right_shift | SUCCESS | 9.951418 |
| ffi::c_str::verify::check_is_empty | SUCCESS | 6.1304274 |
| collections::vec_deque::verify::check_vecdeque_swap | SUCCESS | 5.7121696 |
| ffi::c_str::verify::check_count_bytes | SUCCESS | 5.3422 |
| num::verify::widening_mul_u64_mid_edge | SUCCESS | 4.6055017 |
| ffi::c_str::verify::check_from_bytes_until_nul | SUCCESS | 4.039255 |
| num::verify::carrying_mul_u64_mid_edge | SUCCESS | 2.4884882 |
| num::imp::dec2flt::decimal_seq::decimal_seq_verify::check_round | SUCCESS | 2.3178968 |

Tooling SHA-256 at the run commit:
- `.github/workflows/smallsort-kani-k1.yml` b78ad2902b4c498bdcf27ecdf608860d941db1b76249419d3ab2ece11c38cb81
- `research/challenge-8/kani-k1/tools/kani_k1.py` e5198547b3279a6b47708fb7ff0b3c4e39701c5a38f7f9bb8f0b5820fb547e27
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 4527588 KiB exceeds the largest sampled command peak 4374972 KiB: a process grew between samples; use the time -v value as the true single-process peak
