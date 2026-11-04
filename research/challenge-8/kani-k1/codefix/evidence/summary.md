# K-1 run `codefix-v8-20261104-02`: COMPLETE

- head `63bbd6d309b8063a515dae5be1a082e7e6836992`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `c8b6de28b7cca912b4aa6729c172d765e4de6cbdeb31586eea6a688d66347cb3`
- run 6bc006d2-eff0-406e-92a5-06c934e5e97f attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 15 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1736192 KiB, wall 1:34.17 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 49 samples, largest sampled sum of RSS 1.77 GiB at 60 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.66 GiB (≤13 GiB), seen 4–78 s, peak sample 60 s
  - `cbmc` 0.14 GiB (≤13 GiB), seen 86–92 s, peak sample 90 s
  - `kani-driver` 0.10 GiB (≤13 GiB), seen 2–92 s, peak sample 92 s
  - `goto-cc` 0.07 GiB (≤13 GiB), seen 80–82 s, peak sample 80 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 4–78 s, peak sample 78 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 84–84 s, peak sample 84 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–94 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–92 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–94 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–94 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–94 s, peak sample 2 s
  - simultaneous cbmc RSS 0.14 GiB at 90 s
  - simultaneous driver RSS 0.10 GiB at 92 s
  - cbmc PID 23280: 0.14 GiB peak at 90 s; active `T0:network::unstable_freeze_noncopy_bytes86_fallback_n2`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| network::swap_same_position_u8 | SUCCESS | SUCCESS | 0.28875694 | 0/69 | 4 | 2/2 |
| network::unstable_freeze_noncopy_bytes86_fallback_n2 | SUCCESS | SUCCESS | 8.783918 | 0/544 | 21 | 3/3 |
| assembly::reject_mutant_swap_u8_n2 | FAILED | FAILED | 0.5040002 | 1/80 | 6 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::assembly::reject_mutant_swap_u8_n2`:
- assertion failed: v[0] <= v[1] @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/assembly.rs:25

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::network::swap_same_position_u8
- 21 unreachable check(s) in slice::sort::shared::smallsort::verify::network::unstable_freeze_noncopy_bytes86_fallback_n2
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::reject_mutant_swap_u8_n2
