# K-1 run `taildiag-g2-20261105-01`: COMPLETE

- head `49420dda0b505d38d9bed8568ce602a4026b4ae4`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `c7652b3bf9c2b8abc8896b894c80c228b619a3087917d55131cdcf19d261fdf7`
- run a5a16595-8c2e-4bf8-80bd-b7627d775ca6 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 2524920 KiB, wall 19:23.62 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 582 samples, largest sampled sum of RSS 2.54 GiB at 1162 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.41 GiB (≤13 GiB), seen 82–1162 s, peak sample 1160 s
  - `kani-compiler` 2.09 GiB (≤13 GiB), seen 2–60 s, peak sample 48 s
  - `kani-driver` 0.12 GiB (≤13 GiB), seen 2–1162 s, peak sample 1162 s
  - `goto-cc` 0.09 GiB (≤13 GiB), seen 62–840 s, peak sample 62 s
  - `goto-instrument` 0.05 GiB (≤13 GiB), seen 66–1098 s, peak sample 66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–60 s, peak sample 52 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 322–322 s, peak sample 322 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1163 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1162 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 322–322 s, peak sample 322 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–1163 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 2.41 GiB at 1160 s
  - simultaneous driver RSS 0.11 GiB at 1162 s
  - cbmc PID 9456: 2.41 GiB peak at 1160 s; active `T0:taildiag::u64_backing17_tail8_to15_no_explicit_frame`
  - cbmc PID 9418: 1.41 GiB peak at 1096 s; active `T0:taildiag::insertion_stubbed_u64_backing17_len1_to4`
  - cbmc PID 9298: 1.39 GiB peak at 320 s; active `T0:taildiag::insertion_stubbed_u64_backing17_len13_to16`
  - cbmc PID 9378: 1.37 GiB peak at 838 s; active `T0:taildiag::insertion_stubbed_u64_backing17_len5_to8`
  - cbmc PID 9338: 1.36 GiB peak at 579 s; active `T0:taildiag::insertion_stubbed_u64_backing17_len9_to12`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| taildiag::u64_backing17_tail8_to15_no_explicit_frame | SUCCESS | SUCCESS | 64.20818 | 0/229 | 7 | 5/5 |
| taildiag::insertion_stubbed_u64_backing17_len1_to4 | SUCCESS | TIMEOUT | None |  | None |  |
| taildiag::insertion_stubbed_u64_backing17_len5_to8 | SUCCESS | TIMEOUT | None |  | None |  |
| taildiag::insertion_stubbed_u64_backing17_len9_to12 | SUCCESS | TIMEOUT | None |  | None |  |
| taildiag::insertion_stubbed_u64_backing17_len13_to16 | SUCCESS | TIMEOUT | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail8_to15_no_explicit_frame
