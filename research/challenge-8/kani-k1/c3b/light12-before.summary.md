# K-1 run `c3b-light12-before`: COMPLETE

- head `05c995e018561500dd4bb8e2f994f1d3521e4a1d`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `a217a552002735b6cdce0e9d07dc9cbeb4743396b080c998a0083080d84eb1c8`
- run 586c0d76-5fcb-454b-9147-7c6c4e6aa0ec attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 1 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1896332 KiB, wall 5:37.19 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 170 samples, largest sampled sum of RSS 2.22 GiB at 48 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `kani-compiler` 1.81 GiB (≤13 GiB), seen 2–62 s, peak sample 48 s
  - `kani-driver` 1.14 GiB (≤13 GiB), seen 0–337 s, peak sample 172 s
  - `cbmc` 0.77 GiB (≤13 GiB), seen 72–337 s, peak sample 186 s
  - `rust-lld` 0.07 GiB (≤13 GiB), seen 6–6 s, peak sample 6 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 68–296 s, peak sample 258 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 0–62 s, peak sample 4 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 64–327 s, peak sample 66 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–337 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–337 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–337 s, peak sample 0 s
  - `cc` 0.00 GiB (≤13 GiB), seen 6–6 s, peak sample 6 s
  - `collect2` 0.00 GiB (≤13 GiB), seen 6–6 s, peak sample 6 s
  - …only the 12 largest commands listed

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::general_stable_sorted_permutation_u8_n0 | SUCCESS | SUCCESS | 0.48391318 | 0/631 | 136 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n1 | SUCCESS | SUCCESS | 0.904023 | 0/631 | 130 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n2 | SUCCESS | SUCCESS | 5.648714 | 0/631 | 113 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n3 | SUCCESS | SUCCESS | 8.084707 | 0/631 | 111 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n4 | SUCCESS | SUCCESS | 18.838312 | 0/631 | 109 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n5 | SUCCESS | SUCCESS | 16.057024 | 0/631 | 107 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n6 | SUCCESS | SUCCESS | 23.7524 | 0/631 | 105 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n7 | SUCCESS | SUCCESS | 29.105669 | 0/631 | 103 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n8 | SUCCESS | SUCCESS | 36.00766 | 0/631 | 99 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n9 | SUCCESS | SUCCESS | 44.435005 | 0/631 | 97 | 2/2 |
| merge::general_stable_sorted_permutation_u8_n10 | SUCCESS | TIMEOUT | None |  | None |  |
| merge::general_stable_sorted_permutation_u64_n0 | SUCCESS | SUCCESS | 0.5325843 | 0/638 | 136 | 2/2 |

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` fb8663df29332899c81c1865583facc5394e6941c484027d896e2cadc0beda04
- `research/challenge-8/kani-k1/tools/kani_k1.py` 1ac896f51b7d1ed1c07a29e8010ffea29ea1c74f2b6e0ece2de10123e1ebf2ef
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 1896332 KiB exceeds the largest sampled command peak 1895444 KiB: a process grew between samples; use the time -v value as the true single-process peak
- 136 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n0
- 130 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n1
- 113 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n2
- 111 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n3
- 109 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n4
- 107 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n5
- 105 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n6
- 103 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n7
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n8
- 97 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n9
- 136 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u64_n0
