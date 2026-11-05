# K-1 run `looppin-g1-20261105-01`: COMPLETE

- head `2ed6e9c7da48d61fd362a9f90401486ef25421bc`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `5c3908bef8e08cfa1967cd4b8d1bea82ffd918647c6b777771721a5e3e097caa`
- run f645e709-de9a-4b7a-a61f-69aab36f4f75 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 6227528 KiB, wall 4:16.01 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 129 samples, largest sampled sum of RSS 5.71 GiB at 156 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 5.94 GiB (≤13 GiB), seen 102–254 s, peak sample 210 s
  - `kani-compiler` 1.55 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `goto-instrument` 1.03 GiB (≤13 GiB), seen 70–224 s, peak sample 90 s
  - `kani-driver` 0.09 GiB (≤13 GiB), seen 2–254 s, peak sample 220 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 68–68 s, peak sample 68 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 4 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1plus` 0.01 GiB (≤13 GiB), seen 222–222 s, peak sample 222 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–256 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–254 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 222–222 s, peak sample 222 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–254 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 5.68 GiB at 156 s
  - simultaneous driver RSS 0.09 GiB at 254 s
  - cbmc PID 9291: 5.94 GiB peak at 210 s; active `T0:looppin::outer_loop_u64_symbolic_len_backing5`
  - cbmc PID 9329: 1.24 GiB peak at 236 s; active `T0:looppin::insert_tail_u64_tail1_to4_backing5`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| looppin::calibration_true | SUCCESS | SUCCESS | 0.17787845 | 0/83 | 0 | 3/3 |
| looppin::calibration_false_control | FAILED | FAILED | 0.13606513 | 1/88 | 0 |  |
| looppin::insert_tail_u64_tail1_to4_backing5 | SUCCESS | SUCCESS | 30.317678 | 0/219 | 4 | 4/4 |
| looppin::outer_loop_u64_symbolic_len_backing5 | SUCCESS | SUCCESS | 121.00956 | 0/404 | 4 | 3/3 |

Failed checks of `slice::sort::shared::smallsort::verify::looppin::calibration_false_control`:
- Check invariant after step for loop slice::sort::shared::smallsort::verify::looppin::calibration_false_control.0 @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/looppin.rs:38

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::looppin::insert_tail_u64_tail1_to4_backing5
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::looppin::outer_loop_u64_symbolic_len_backing5
