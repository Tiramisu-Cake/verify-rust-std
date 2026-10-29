# K-1 run `c3b-timeout-no-traces6`: PARTIAL

- head `3c1ae08596a281b65fb492cadd370a42cdc9d8f5`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `20ac28bd3445b1989bd2a695ef9a202a3328e1c8672d6d867c2497330af09500`
- run d7c18274-1281-4c8c-95fd-6bc9148102bb attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 124
- whole run, including compilation: max RSS None KiB, wall None (UNPARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1127 samples, largest sampled sum of RSS 3.83 GiB at 1150 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 2.85 GiB (≤13 GiB), seen 82–2255 s, peak sample 1152 s
  - `kani-compiler` 1.71 GiB (≤13 GiB), seen 4–76 s, peak sample 58 s
  - `kani-driver` 1.66 GiB (≤13 GiB), seen 0–2255 s, peak sample 517 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 80–1122 s, peak sample 517 s
  - `goto-cc` 0.03 GiB (≤13 GiB), seen 78–78 s, peak sample 78 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–76 s, peak sample 66 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2257 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–2255 s, peak sample 2 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–2255 s, peak sample 0 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–2257 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 0–2255 s, peak sample 0 s

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | UNKNOWN | None |  | None |  |
| network::insert_tail_contract_u64_start1 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n14 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::general_stable_sorted_permutation_u8_n13 | SUCCESS | SUCCESS | 435.71286 | 0/631 | 89 |  |
| network::network_correctness_u8_n17 | SUCCESS | NOT_RUN |  |  |  |  |

Inconsistencies:
- final 'Complete - …' line missing

Tooling SHA-256 at the run commit:
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` 9d8fea987d2f76f61f830ba0d5beebc03211c0ed2e1076b03c1332905bf0096f
- `research/challenge-8/kani-k1/tools/kani_k1.py` e732269a43cd6f15f68df13d1e28fb8ab593a7e135094113eec2c33522515ed0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- 89 unreachable check(s) in slice::sort::shared::smallsort::verify::merge::general_stable_sorted_permutation_u8_n13
