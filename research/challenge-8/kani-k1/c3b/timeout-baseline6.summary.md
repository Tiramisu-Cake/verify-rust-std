# K-1 run `c3b-timeout-baseline6`: PARTIAL

- head `84dfc4b58e48c758001b7af383e9d7e84dc84250`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `4be6fe159a5615507305fc6998cab4f77b7e402e2acccdb9b0f651327bdfa691`
- run bc9ee7b8-a3e8-43e4-8aa7-2f91c175b2de attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 10 min, harnesses in parallel 1, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit 124
- whole run, including compilation: max RSS None KiB, wall None (UNPARSED)
- verify memory cap: MACHINE (no cgroup cap; the machine's memory 15.63 GiB is the limit), swap off
- memory peaks PARSED: sampled every 2 s, 1045 samples, largest sampled sum of RSS 4.02 GiB at 1249 s; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner):
  - `cbmc` 2.85 GiB (≤13 GiB), seen 90–2091 s, peak sample 1249 s
  - `kani-driver` 1.94 GiB (≤13 GiB), seen 2–2091 s, peak sample 603 s
  - `kani-compiler` 1.72 GiB (≤13 GiB), seen 2–84 s, peak sample 66 s
  - `goto-instrument` 0.04 GiB (≤13 GiB), seen 88–1814 s, peak sample 605 s
  - `cargo` 0.03 GiB (≤13 GiB), seen 2–84 s, peak sample 84 s
  - `goto-cc` 0.02 GiB (≤13 GiB), seen 86–1209 s, peak sample 1209 s
  - `bash` 0.00 GiB (≤13 GiB), seen 0–2091 s, peak sample 0 s
  - `run-kani.sh` 0.00 GiB (≤13 GiB), seen 0–2091 s, peak sample 2 s
  - `gcc` 0.00 GiB (≤13 GiB), seen 86–86 s, peak sample 86 s
  - `tee` 0.00 GiB (≤13 GiB), seen 0–2091 s, peak sample 0 s
  - `time` 0.00 GiB (≤13 GiB), seen 0–2091 s, peak sample 0 s
  - `timeout` 0.00 GiB (≤13 GiB), seen 0–2091 s, peak sample 0 s

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n16 | SUCCESS | TIMEOUT | None |  | None |  |
| network::insertion_permutation_u64_n12 | SUCCESS | UNKNOWN | None |  | None |  |
| network::insert_tail_contract_u64_start1 | SUCCESS | TIMEOUT | None |  | None |  |
| network::network_correctness_u64_n14 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::general_stable_sorted_permutation_u8_n13 | SUCCESS | SUCCESS | 513.55634 | 0/631 | 89 | 2/2 |
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
