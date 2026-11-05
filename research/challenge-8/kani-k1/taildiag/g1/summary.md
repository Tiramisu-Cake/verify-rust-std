# K-1 run `taildiag-g1-20261105-01`: COMPLETE

- head `1c99acce330d708961571bd593ecc322768f690f`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `ccc22fb30ac75edd682dee2aca2b175fcdc977c23c017a85802d8f0ff3037296`
- run 34500433-bd3d-4784-9a26-aaf0ba3f0492 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 3708104 KiB, wall 23:21.87 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 701 samples, largest sampled sum of RSS 3.98 GiB at 569 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 3.54 GiB (≤13 GiB), seen 70–1399 s, peak sample 92 s
  - `kani-compiler` 1.55 GiB (≤13 GiB), seen 2–64 s, peak sample 48 s
  - `kissat` 0.37 GiB (≤13 GiB), seen 513–621 s, peak sample 539 s
  - `kani-driver` 0.25 GiB (≤13 GiB), seen 2–1399 s, peak sample 411 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 64 s
  - `goto-instrument` 0.02 GiB (≤13 GiB), seen 68–1339 s, peak sample 413 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 66–629 s, peak sample 485 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 806–806 s, peak sample 806 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–1402 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–1399 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–1401 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 3.49 GiB at 92 s
  - simultaneous driver RSS 0.25 GiB at 411 s
  - simultaneous solver RSS 0.36 GiB at 537 s
  - cbmc PID 9332: 3.54 GiB peak at 92 s; active `T0:taildiag::u64_backing17_tail8_to15_value_order`
  - cbmc PID 9563: 3.53 GiB peak at 832 s; active `T0:taildiag::u64_backing17_tail1_to7_value_order`
  - cbmc PID 9484: 3.43 GiB peak at 625 s; active `T0:taildiag::u64_backing17_tail1_to7_kissat`
  - cbmc PID 9525: 3.04 GiB peak at 654 s; active `T0:taildiag::u64_backing17_tail1_to7_cadical`
  - cbmc PID 9370: 3.04 GiB peak at 260 s; active `T0:taildiag::u64_backing17_tail8_to15`
  - cbmc PID 9601: 3.04 GiB peak at 1075 s; active `T0:taildiag::u64_backing17_tail1_to7`
  - kissat PID 9490: 0.37 GiB peak at 539 s; active `T0:taildiag::u64_backing17_tail1_to7_kissat`
  - kissat PID 9491: 0.37 GiB peak at 571 s; active `T0:taildiag::u64_backing17_tail1_to7_kissat`
  - kissat PID 9489: 0.13 GiB peak at 515 s; active `T0:taildiag::u64_backing17_tail1_to7_kissat`
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| taildiag::u64_backing8_tail1_to7 | SUCCESS | SUCCESS | 60.678856 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing12_tail1_to7 | SUCCESS | SUCCESS | 104.20101 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing17_tail1_to7 | SUCCESS | SUCCESS | 182.69366 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing17_tail1_to7_value_order | SUCCESS | TIMEOUT | None |  | None |  |
| taildiag::u64_backing17_tail1_to7_cadical | SUCCESS | SUCCESS | 174.3746 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing17_tail1_to7_kissat | SUCCESS | SUCCESS | 142.5729 | 0/229 | 4 | 5/5 |
| taildiag::u8_backing17_tail1_to7 | SUCCESS | SUCCESS | 38.121933 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing17_tail1_to7_no_explicit_frame | SUCCESS | SUCCESS | 31.25227 | 0/229 | 7 | 5/5 |
| taildiag::u64_backing17_tail8_to15 | SUCCESS | SUCCESS | 177.43237 | 0/229 | 4 | 5/5 |
| taildiag::u64_backing17_tail8_to15_value_order | SUCCESS | SUCCESS | 163.57158 | 0/229 | 4 | 5/5 |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing8_tail1_to7
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing12_tail1_to7
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail1_to7
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail1_to7_cadical
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail1_to7_kissat
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u8_backing17_tail1_to7
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail1_to7_no_explicit_frame
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail8_to15
- 4 unreachable check(s) in slice::sort::shared::smallsort::verify::taildiag::u64_backing17_tail8_to15_value_order
