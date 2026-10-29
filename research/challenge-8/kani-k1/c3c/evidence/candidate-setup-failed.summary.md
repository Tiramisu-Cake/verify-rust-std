# K-1 run `c3c-matched-candidate`: RUNNER_ERROR

- head `af406030589a1d733709a3376b5b1fa1bb1dfc2e`, Kani `9461e07af7ec929f050aa4192f29363c9be07779`, request sha256 `6373840ff9df3070b1430fd153d47e10a42c718b598a2e2a159e13ccf36eb7e9`
- run dfada6fc-2f83-4c2e-abf5-2ce45c6e3e81 attempt None, image Ubuntu 24.04.5 LTS 4 CPU Intel(R) Xeon(R) CPU @ 2.20GHz, 15.6 GiB (container view; pool per Cloud Build record), build success
- agent `k1-network`, kind `diagnostic`, runner `gcb-e2-standard-4`, per-harness timeout 3 min, harnesses in parallel 3, uninit checks off, controls cfg off
- gate: False; expectation met: False; measurement ok: None; Kani exit None
- whole run, including compilation: max RSS None KiB, wall None (MISSING)
- verify memory cap: MISSING, limit ?, cgroup peak incl. page cache ?, OOM kills None, swap None
- memory peaks MISSING: sampled every ? s, None samples, largest sampled sum of RSS ? at ?; per command (kernel VmHWM; 13 GiB = CircleCI cap, 16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:

| harness | expect | status | time s | failed/total checks | unreachable | covers |
|---|---|---|---|---|---|---|
| merge::merge_contract_u64_n14 | SUCCESS | NOT_RUN |  |  |  |  |
| network::network_correctness_u8_n17 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::merge_contract_u64_n15 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_general_u64_n31 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_noncopy_u64_n31 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_stable_u64_n31 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_general_u64_n32 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_noncopy_u64_n32 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::route_safety_stable_u64_n32 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail7 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail8 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail9 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail10 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail11 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail12 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail13 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail14 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail15 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start6_tail16 | SUCCESS | NOT_RUN |  |  |  |  |
| network::network_correctness_u8_n16 | SUCCESS | NOT_RUN |  |  |  |  |
| network::network_correctness_u64_n8 | SUCCESS | NOT_RUN |  |  |  |  |
| network::network_correctness_u64_n13 | SUCCESS | NOT_RUN |  |  |  |  |
| merge::merge_contract_u64_n16 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insertion_permutation_u64_n12 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail2 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail3 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail4 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail5 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail6 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail7 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail8 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail9 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail10 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail11 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail12 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail13 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail14 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail15 | SUCCESS | NOT_RUN |  |  |  |  |
| network::insert_tail_contract_u64_start1_tail16 | SUCCESS | NOT_RUN |  |  |  |  |
| correct::sorted_permutation_general_u8_n14 | SUCCESS | NOT_RUN |  |  |  |  |
| correct::sorted_permutation_stable_u8_n14 | SUCCESS | NOT_RUN |  |  |  |  |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n31 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n32 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n17 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n16 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::safety_stable_unit_n8 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::permutation_merge_u8_n4 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::sorted_network_prefix_u8_n10 | SUCCESS | NOT_RUN |  |  |  |  |
| assembly::advancement_merge_up_u8_n2 | SUCCESS | NOT_RUN |  |  |  |  |

Tooling SHA-256 at the run commit:
- `.github/workflows/kani.yml` 587cf2116075865fe641bee4da47b96cc22f71ca06433f7cb6f63b3439828577
- `research/challenge-8/kani-k1/gcb/cloudbuild.yaml` 73b61a3573f6d1942007777e6521883fb4ba2731414fecffea80403404762d81
- `research/challenge-8/kani-k1/tools/gcb-k1.sh` c54242159e8beaeec6ffb1d4926e7de62e7b6d5ed23a5a21fbe5c872aa2d59dc
- `research/challenge-8/kani-k1/tools/kani_k1.py` c6236af71fdc13073d63873aafc069de2bbf4b71e50659168632e0a12b6f47d0
- `scripts/run-kani.sh` 28f1b23b692058ff0b807115551554504475f586bde7933fafcf28165da5adc1
- `tool_config/kani-version.toml` f2f2c86a6b480e44223ab43adfce621b30bfc28cf496b4d88fec6caebaa9cdd0

Notes:
- per-command memory peaks MISSING
- verify memory cap MISSING: no reason recorded
- 3 harnesses verified concurrently: times and memory are of the shared run, not single-harness measurements
- Kani log missing: setup or runner failed before verification output
