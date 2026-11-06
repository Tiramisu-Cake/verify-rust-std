# K-1 run `leanhelpers-g1-20261106-01`: COMPLETE

- head `1dff8cf56e8a2115b5b1091882b4f01eb223623c`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `66a7c5cbfac09d0f9468d4ae2680762c97af877d45cb21f6c3c376408b596bb5`
- run ae8d547b-7c77-4312-bff5-fef9e64393fc attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 8 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: True; expectation met: True; measurement ok: None; Kani exit 0
- whole run, including compilation: max RSS 2993992 KiB, wall 6:57.49 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 210 samples, largest sampled sum of RSS 3.01 GiB at 409 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 2.86 GiB (≤13 GiB), seen 76–417 s, peak sample 174 s
  - `kani-compiler` 1.57 GiB (≤13 GiB), seen 2–66 s, peak sample 50 s
  - `kani-driver` 1.12 GiB (≤13 GiB), seen 2–417 s, peak sample 413 s
  - `goto-instrument` 0.08 GiB (≤13 GiB), seen 70–413 s, peak sample 80 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.01 GiB (≤13 GiB), seen 68–68 s, peak sample 68 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–417 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–417 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–417 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–417 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–417 s, peak sample 2 s
  - simultaneous cbmc RSS 2.79 GiB at 216 s
  - simultaneous driver RSS 0.96 GiB at 411 s
  - cbmc PID 8844: 2.86 GiB peak at 174 s; active `T0:network::insert_tail_contract_u64_start1_tail15_to16`
  - cbmc PID 8779: 0.77 GiB peak at 134 s; active `T0:merge::merge_contract_u8_n5`
  - cbmc PID 8871: 0.11 GiB peak at 417 s; active `T0:scratchgeom::stable_u64_min_scratch_n2`
  - cbmc PID 8741: 0.11 GiB peak at 78 s; active `T0:merge::general_stable_direct_u8_n2`
  - cbmc PID 8806: 0.11 GiB peak at 140 s; active `T0:merge::sort4_arbitrary_comparator_u64_n4`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::drop_fallback_drop_count_n2 | SUCCESS | SUCCESS | 0.8586333 | 0/461 | 17 | 2/2 |
| merge::drop_fallback_tag_permutation_n2 | SUCCESS | SUCCESS | 1.1128453 | 0/461 | 16 | 2/2 |
| merge::sort4_arbitrary_comparator_u64_n4 | SUCCESS | SUCCESS | 6.0442863 | 0/165 | 36 | 1/1 |
| merge::general_stable_direct_u8_n2 | SUCCESS | SUCCESS | 4.4072623 | 0/401 | 72 | 2/2 |
| scratchgeom::stable_u64_min_scratch_n2 | SUCCESS | SUCCESS | 3.7573495 | 0/423 | 76 | 2/2 |
| merge::merge_contract_u8_n5 | SUCCESS | SUCCESS | 52.383076 | 0/570 | 64 | 1/1 |
| network::insert_tail_contract_u64_start1_tail15_to16 | SUCCESS | SUCCESS | 263.85718 | 0/622 | 36 | 4/4 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 17 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::drop_fallback_drop_count_n2
- 16 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::drop_fallback_tag_permutation_n2
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::sort4_arbitrary_comparator_u64_n4
- 72 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_direct_u8_n2
- 76 unreachable check(s) in slice::sort::shared::smallsort::verify::scratchgeom::stable_u64_min_scratch_n2
- 64 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::merge_contract_u8_n5
- 36 unreachable check(s) in slice::sort::shared::smallsort::verify::network::insert_tail_contract_u64_start1_tail15_to16
