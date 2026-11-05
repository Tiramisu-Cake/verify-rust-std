# K-1 run `loopreal-g1-repair1-20261105-01`: COMPLETE

- head `dc0d792f74c437966aff93c734d43fcedc4dc7a7`, Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`, request sha256 `92b07d04e7bf08dcfaba93c0b92601236e3ce9cf987b00b34e181797ffe0ff22`
- run 8400bb9d-f0f3-43fe-b47e-df5b4a4aae67 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 4 min, harnesses in parallel 1, uninit checks off, valid-value checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 15601676 KiB, wall 40:18.76 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1207 samples, largest sampled sum of RSS 14.94 GiB at 455 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 14.78 GiB (≤16 GB), seen 84–2417 s, peak sample 455 s
  - `kani-compiler` 2.14 GiB (≤13 GiB), seen 2–66 s, peak sample 54 s
  - `goto-instrument` 1.74 GiB (≤13 GiB), seen 76–2403 s, peak sample 2113 s
  - `kani-driver` 0.21 GiB (≤13 GiB), seen 2–2417 s, peak sample 182 s
  - `goto-cc` 0.08 GiB (≤13 GiB), seen 68–2385 s, peak sample 737 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–66 s, peak sample 58 s
  - `python3` 0.02 GiB (≤13 GiB), seen 0–0 s, peak sample 0 s
  - `cc1` 0.01 GiB (≤13 GiB), seen 334–334 s, peak sample 334 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2418 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–2417 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 74–334 s, peak sample 74 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–2417 s, peak sample 2 s
  - …only the 12 largest commands listed
  - simultaneous cbmc RSS 14.78 GiB at 455 s
  - simultaneous driver RSS 0.20 GiB at 182 s
  - cbmc PID 9465: 14.78 GiB peak at 455 s; active `T0:loopreal::outer_loop_u64_backing128`
  - cbmc PID 9385: 12.48 GiB peak at 180 s; active `T0:assembly::safety_stable_unit_n32`
  - cbmc PID 9543: 10.74 GiB peak at 921 s; active `T0:loopreal::outer_loop_u64_backing32`
  - cbmc PID 9621: 6.09 GiB peak at 1493 s; active `T0:loopreal::outer_loop_u64_backing8`
  - cbmc PID 9425: 5.72 GiB peak at 304 s; active `T0:loopreal::outer_loop_false_invariant_backing8`
  - cbmc PID 9503: 4.01 GiB peak at 735 s; active `T0:loopreal::insert_tail_u64_backing128`
  - dmesg OOM scan: `[Thu Nov  5 08:51:23 2026] python3 invoked oom-killer: gfp_mask=0x100cca(GFP_HIGHUSER_MOVABLE), order=0, oom_score_adj=0 | [Thu Nov  5 08:51:24 2026] oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),cpuset=169faf178d6018d96ae09d66d1ee12ff55446dde86b6d81716fcf1bf459cfdbd,mems_allowed=0,global_oom,task_memcg=/docker/169faf178d6018d96ae09d66d1ee12ff55446dde86b6d81716fcf1bf459cfdbd,task=cbmc,pid=13044,uid=0 | [Thu Nov  5 08:51:25 2026] Out of memory: Killed process 13044 (cbmc) total-vm:16493104kB, anon-rss:15601500kB, file-rss:0kB, shmem-rss:0kB, UID:0 pgtables:31108kB oom_score_adj:0`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| loopreal::insert_tail_u64_backing8 | SUCCESS | TIMEOUT | None |  | None |  |
| loopreal::outer_loop_u64_backing8 | SUCCESS | SUCCESS | 151.6557 | 0/609 | 7 | 4/4 |
| loopreal::insert_tail_u64_backing32 | SUCCESS | TIMEOUT | None |  | None |  |
| loopreal::outer_loop_u64_backing32 | SUCCESS | TIMEOUT | None |  | None |  |
| loopreal::insert_tail_u64_backing128 | SUCCESS | TIMEOUT | None |  | None |  |
| loopreal::outer_loop_u64_backing128 | SUCCESS | OUT_OF_MEMORY | None |  | None |  |
| loopreal::outer_loop_false_invariant_backing8 | FAILED | FAILED | 88.192055 | 1/636 | 7 |  |
| realcontracts::insert_tail_safety_u64_tail1_to4_backing5 | SUCCESS | TIMEOUT | None |  | None |  |
| network::unstable_freeze_noncopy_bytes86_fallback_n2 | SUCCESS | TIMEOUT | None |  | None |  |
| realcontracts::unstable_network_safety_u8_n9_stubbed | SUCCESS | SUCCESS | 13.157118 | 0/775 | 23 | 1/1 |
| assembly::safety_stable_unit_n16 | SUCCESS | SUCCESS | 6.4619365 | 0/514 | 10 | 1/1 |
| assembly::safety_stable_unit_n32 | SUCCESS | SUCCESS | 92.49891 | 0/514 | 10 | 1/1 |

Failed checks of `slice::sort::shared::smallsort::verify::loopreal::outer_loop_false_invariant_backing8`:
- Check invariant after step for loop slice::sort::shared::smallsort::verify::loopreal::insertion_sort_shift_left_false::<u64, for<'a, 'b> fn(&'a u64, &'b u64) -> bool {slice::sort::shared::smallsort::verify::loopreal::reading_less_u64}>.0 @ /workspace/src/library/core/src/slice/sort/shared/smallsort/verify/loopreal.rs:115

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` ee09ed6a89e51f7ba00034176b8a2cc2eccbcab5f9400a6d96ef8248fcd35028
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 8048ff98998b7d30f4701483378f067a069a948222d4894fa8a4b1bd69b18963
- `research/challenge-8/kani-k1/tools/kani_k1.py` 8e2a15c98ccd9dba3fc7d412768cb76ddb8c78b12143ff224c9359097a9e46e7
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` 40ee88392e3e1b0af82611394f9a30df259e22cad6a623bded49ba1a0adb954c

Notes:
- time -v max RSS 15601676 KiB exceeds the largest sampled command peak 15503184 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::loopreal::outer_loop_u64_backing8
- 7 unreachable check(s) in slice::sort::shared::smallsort::verify::loopreal::outer_loop_false_invariant_backing8
- 23 unreachable check(s) in slice::sort::shared::smallsort::verify::realcontracts::unstable_network_safety_u8_n9_stubbed
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n16
- 10 unreachable check(s) in slice::sort::shared::smallsort::verify::assembly::safety_stable_unit_n32
