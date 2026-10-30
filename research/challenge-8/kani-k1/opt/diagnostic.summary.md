# K-1 run `opt-split-jobs3-20261030`: COMPLETE

- head `ae5aabe3f3e4422a35f861b889ac7436acab4216`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `2c84ed334cb92220d53b4c6981d8ecefff89e079c0b2467faf3720067fece8dc`
- run 64a9829e-1097-4bcf-af34-6e3be5cfdd19 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 3, uninit checks off, controls cfg on
- gate: False; expectation met: False; measurement ok: None; Kani exit 1
- whole run, including compilation: max RSS 8298596 KiB, wall 11:36.19 (PARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 348 samples, largest sampled sum of RSS 14.96 GiB at 588 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:
  - `cbmc` 7.85 GiB (≤13 GiB), seen 70–695 s, peak sample 623 s
  - `kani-compiler` 1.71 GiB (≤13 GiB), seen 2–64 s, peak sample 50 s
  - `kani-driver` 1.45 GiB (≤13 GiB), seen 2–695 s, peak sample 502 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 68–440 s, peak sample 70 s
  - `goto-cc` 0.04 GiB (≤13 GiB), seen 66–502 s, peak sample 66 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–64 s, peak sample 4 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–696 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 2–695 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 2–695 s, peak sample 2 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–696 s, peak sample 2 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 2–695 s, peak sample 2 s
  - simultaneous cbmc RSS 13.70 GiB at 588 s
  - simultaneous driver RSS 1.37 GiB at 695 s
  - cbmc PID 9432: 7.85 GiB peak at 623 s; active `T0:merge::opt_split::stable_contract_u64_n8,T2:merge::opt_split::stable_contract_u64_n6`
  - cbmc PID 9497: 7.74 GiB peak at 580 s; active `T0:merge::opt_split::stable_contract_u64_n8,T1:merge::opt_split::stable_direct_u64_n8,T2:merge::opt_split::stable_contract_u64_n6`
  - cbmc PID 9470: 6.04 GiB peak at 649 s; active `T2:merge::opt_split::stable_contract_u64_n6`
  - cbmc PID 9367: 5.36 GiB peak at 184 s; active `T0:merge::opt_split::general_contract_u64_n6,T1:merge::opt_split::stable_direct_u64_n6,T2:merge::opt_split::general_contract_u64_n8`
  - cbmc PID 9335: 1.86 GiB peak at 377 s; active `T0:merge::opt_split::stable_contract_u64_n8,T1:merge::opt_split::general_direct_u64_n8,T2:merge::opt_split::general_contract_u64_n8`
  - cbmc PID 9394: 1.51 GiB peak at 273 s; active `T0:merge::opt_split::stable_contract_u64_n8,T1:merge::opt_split::general_direct_u64_n8,T2:merge::opt_split::stable_contract_u64_n6`
  - dmesg OOM scan: `[Fri Oct 30 21:05:54 2026] cbmc invoked oom-killer: gfp_mask=0x100dca(GFP_HIGHUSER_MOVABLE|__GFP_ZERO), order=0, oom_score_adj=0 | [Fri Oct 30 21:05:55 2026] oom-kill:constraint=CONSTRAINT_NONE,nodemask=(null),cpuset=011d8c450f953ebeb47bea305175a5adc4bd68af981ba3b7931f61a5547f5264,mems_allowed=0,global_oom,task_memcg=/docker/011d8c450f953ebeb47bea305175a5adc4bd68af981ba3b7931f61a5547f5264,task=cbmc,pid=13054,uid=0 | [Fri Oct 30 21:05:55 2026] Out of memory: Killed process 13054 (cbmc) total-vm:8564840kB, anon-rss:8298408kB, file-rss:4kB, shmem-rss:0kB, UID:0 pgtables:16408kB oom_score_adj:0`

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::opt_split::general_direct_u64_n6 | SUCCESS | SUCCESS | 55.882458 | 0/407 | 66 | 1/1 |
| merge::opt_split::stable_direct_u64_n6 | SUCCESS | SUCCESS | 129.8351 | 0/405 | 66 | 1/1 |
| merge::opt_split::general_contract_u64_n6 | SUCCESS | SUCCESS | 206.39864 | 0/447 | 99 | 1/1 |
| merge::opt_split::stable_contract_u64_n6 | SUCCESS | SUCCESS | 255.93724 | 0/447 | 99 | 1/1 |
| merge::opt_split::general_direct_u64_n8 | SUCCESS | SUCCESS | 244.31534 | 0/407 | 62 | 1/1 |
| merge::opt_split::stable_direct_u64_n8 | SUCCESS | OUT_OF_MEMORY | None |  | None |  |
| merge::opt_split::general_contract_u64_n8 | SUCCESS | SUCCESS | 362.54013 | 0/447 | 95 | 1/1 |
| merge::opt_split::stable_contract_u64_n8 | SUCCESS | OUT_OF_MEMORY | None |  | None |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 2547fc997b057dd41fee896b7c5aac4279a339470992433cb1b46b0145a97812
- `research/challenge-8/kani-k1/tools/kani_k1.py` 55d62136ad9ab71eb5c0fbd470904ecf20b1ecbb8ab34cca1bbdeff9efc8494e
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- time -v max RSS 8298596 KiB exceeds the largest sampled command peak 8236076 KiB: a process grew between samples; use the time -v value as the true single-process peak
- --cfg kani_smallsort_controls on: opt-in control/mutant harnesses compiled, outside the CI set
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_direct_u64_n6
- 66 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::stable_direct_u64_n6
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_contract_u64_n6
- 99 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::stable_contract_u64_n6
- 62 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_direct_u64_n8
- 95 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::opt_split::general_contract_u64_n8
