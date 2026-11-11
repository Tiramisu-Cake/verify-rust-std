# K-1 run `kani3300-cmp4-clean-20261111-01`: COMPLETE

- head `9730eb7286d50bfd956b1180b1211927595283aa`, Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, request sha256 `9ab5f113371d3d360ae7592e42bee058d7c1b4a936b93a128dc7a26afc4ca6a3`
- run a7061950-0ce5-4776-8d65-fdd686526dd1 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-merge`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 1, uninit checks on, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 1635708 KiB, wall 1:13.01 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 38 samples, largest sampled sum of RSS 1.77 GiB at 54 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `kani-compiler` 1.56 GiB (≤13 GiB), seen 2–70 s, peak sample 54 s
  - `rust-lld` 0.06 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–70 s, peak sample 2 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cbmc` 0.02 GiB (≤13 GiB), seen 72–72 s, peak sample 72 s
  - `kani-driver` 0.01 GiB (≤13 GiB), seen 2–72 s, peak sample 72 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–73 s, peak sample 2 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–72 s, peak sample 2 s
  - `cc` 0.00 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `collect2` 0.00 GiB (≤13 GiB), seen 2–2 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–72 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–73 s, peak sample 0 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 0.02 GiB at 72 s
  - simultaneous driver RSS 0.01 GiB at 72 s
  - cbmc PID 8715: 0.02 GiB peak at 72 s; active ``
  - dmesg OOM scan: `none_seen`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| uninit_probe::cmp3_index_range_len | SUCCESS | SUCCESS | 0.09110829 | 0/20 | 0 | 1/1 |
| uninit_probe::cmp4_index_range_len_runtime | SUCCESS | SUCCESS | 0.10221386 | 0/26 | 0 | 1/1 |
| uninit_probe::cmp3_manually_drop_unsized_len | SUCCESS | FAILED | 0.14265065 | 1/27 | 1 | 0/2 |
| uninit_probe::pincheck_calibration_uninit_read_u8 | FAILED | FAILED | 0.4404721 | 1/31 | 3 | 3/3 |

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::cmp3_manually_drop_unsized_len`:
- Checking memory initialization of type [mem::maybe_uninit::MaybeUninit<usize>; 2] is not supported. Cannot determine layout for a type that contains union of type mem::maybe_uninit::MaybeUninit<usize> as a field. @ /workspace/src/library/core/src/array/iter/iter_inner.rs:48

Failed checks of `slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8`:
- Transmuting between types of incompatible layouts. @ /workspace/src/library/core/src/mem/mod.rs:1283

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` d51f9c59823339dfd211e0e1226e6a372f4816d2ef6c86a68cce2676dc796215
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 60af9d2e9f2d704ed66e6201cfc990662e000d860a230967ab64ec0e20801897
- `research/challenge-8/kani-k1/tools/kani_k1.py` 2a1b6d7a20af9b3c0296d9dc435cb7f12585ce16e27add45f10b9902e35fee23
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 7dca0aa5bf9467c6c4fb4323dabc12254f6372f5f01af096420583bc2b5c9ca3

Notes:
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- -Z uninit-checks on: not in the organizers' CI flags, evidence outside CI
- 1 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::cmp3_manually_drop_unsized_len
- 3 unreachable check(s) in slice::sort::shared::smallsort::verify::uninit_probe::pincheck_calibration_uninit_read_u8
