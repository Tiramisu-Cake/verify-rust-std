# K-1 run `tidydocs-g1-20261106-01`: COMPLETE

- head `0c472366d38e807a70561cc378c28601f237c007`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `b35b328679111b715eeb0195c3686ff384cef8ea3e92c647dacce6157cc7bbce`
- run 479cf06d-7189-4bba-bd72-285bbd1e329d attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 5 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1706152 KiB, wall 2:13.56 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 68 samples, largest sampled sum of RSS 1.81 GiB at 50 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.63 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `cbmc` 0.83 GiB (≤13 GiB), seen 68–132 s, peak sample 102 s
  - `kani-driver` 0.11 GiB (≤13 GiB), seen 2–132 s, peak sample 126 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 70–126 s, peak sample 72 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 56 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 66–66 s, peak sample 66 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–133 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–132 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–132 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–133 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–132 s, peak sample 2 s
  - simultaneous cbmc RSS 0.83 GiB at 102 s
  - simultaneous driver RSS 0.08 GiB at 126 s
  - cbmc PID 8714: 0.83 GiB peak at 102 s; active `T0:realcontracts::sort4_safety_u64`
  - cbmc PID 8783: 0.28 GiB peak at 132 s; active `T0:realcontracts::unstable_network_safety_u8_n9_stubbed`
  - cbmc PID 8754: 0.26 GiB peak at 124 s; active `T0:realcontracts::swap_safety_u8_backing9`
  - cbmc PID 8676: 0.02 GiB peak at 68 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| realcontracts::rejects_swap_comparator_writing_outside_frame_u8 | FAILED | FAILED | 1.8466973 | 1/205 | 4 |  |
| realcontracts::swap_safety_u8_backing9 | SUCCESS | SUCCESS | 17.311901 | 0/219 | 4 | 6/6 |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | SUCCESS | 7.0849905 | 0/387 | 18 | 1/1 |
| realcontracts::sort4_safety_u64 | SUCCESS | SUCCESS | 32.77827 | 0/293 | 6 | 3/3 |

Failed checks of `slice::sort::shared::smallsort::verify::realcontracts::rejects_swap_comparator_writing_outside_frame_u8`:
- Check that *var_9 is assignable @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/realcontracts.rs:360

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::rejects_swap_comparator_writing_outside_frame_u8
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::swap_safety_u8_backing9
- 18 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::unstable_network_safety_u8_n9_stubbed
- 6 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::sort4_safety_u64
