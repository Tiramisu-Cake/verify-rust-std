# macOS autoharness summary (mac-autoharness-4)

**evidence_integrity True**, job_success True; problems []

manual_review_required False: []

exit `0`; Complete `{'success': 1943, 'failures': 0, 'total': 1943}`; blocks 1943 {'SUCCESS': 1943}; log sha256 `3ee6859f12215879204fb378e9050baa00a2cca50e945fcdc2bf5cfee9125912`

SmallSort: expected 197, rows 197, SUCCESS 197; missing 0, extra 0, duplicate 0

Other std non-SUCCESS (first 50): []

## Candidate groups (threshold 300.0 s)

- **m9**: ADMIT — general_direct_u64_n9=ok (206.4186 s), stable_direct_u64_n9=ok (150.79286 s)
- **start1**: ADMIT — insert_tail_contract_u64_start1_tail2_to8=ok (129.35028 s), insert_tail_contract_u64_start1_tail9_to12=ok (164.58257 s), insert_tail_contract_u64_start1_tail13_to16=ok (150.86093 s)
- **u8n9**: ADMIT — general_direct_u8_n9=ok (107.94101 s), stable_direct_nonconst_u8_n9=ok (116.053055 s)
- **s68const**: ADMIT — stable_direct_u64_n6=ok (16.735832 s), stable_direct_u64_n7=ok (34.495747 s), stable_direct_u64_n8=ok (72.24256 s)
- **btwoconst**: ADMIT — general_stable_direct_u64_n2=ok (7.2296124 s)
- **bthreeconst**: ADMIT — general_stable_direct_u64_n3=ok (7.3330836 s)
- **bfourconst**: ADMIT — general_stable_direct_u64_n4=ok (14.163651 s)
- **bfiveconst**: ADMIT — general_stable_direct_u64_n5=ok (23.7052 s)
- **retncten**: ADMIT — network_correctness_u8_n10=ok (10.671785 s)
- **retnceleven**: ADMIT — network_correctness_u8_n11=ok (12.229633 s)
- **retnctwelve**: ADMIT — network_correctness_u8_n12=ok (26.403095 s)
- **retipeleven**: ADMIT — insertion_permutation_u8_n11=ok (3.1916876 s)
- **retrsthree**: ADMIT — route_safety_all_routes_n3=ok (4.6356034 s)
- **retrsfour**: ADMIT — route_safety_all_routes_n4=ok (5.299818 s)
- **retrsfive**: ADMIT — route_safety_all_routes_n5=ok (8.369385 s)
- **retrssix**: ADMIT — route_safety_all_routes_n6=ok (11.411331 s)
- **retrsseven**: ADMIT — route_safety_all_routes_n7=ok (12.68377 s)

## Top 25 SmallSort VT (no VT first)

| harness | status | VT s | checks | unreachable | covers |
|---|---|---:|---|---:|---|
| merge::general_direct_u64_n9 | SUCCESS | 206.4186 | 0/407 | 61 | 1/1 |
| network::network_safety_unstable_u64_n30_to32 | SUCCESS | 201.16989 | 0/312 | 12 | 5/5 |
| network::dispatch_safety_stable_unstable_bytes17_n32 | SUCCESS | 181.9748 | 0/386 | 9 | 3/3 |
| network::network_safety_unstable_u64_n0_to17 | SUCCESS | 167.32686 | 0/312 | 18 | 19/19 |
| network::insert_tail_contract_u64_start1_tail9_to12 | SUCCESS | 164.58257 | 0/428 | 36 | 6/6 |
| network::dispatch_safety_stable_unstable_bytes17_n15_16_17 | SUCCESS | 164.18866 | 0/396 | 9 | 7/7 |
| network::dispatch_safety_stable_unstable_bytes16_n32 | SUCCESS | 163.21169 | 0/386 | 8 | 3/3 |
| network::insert_tail_contract_u64_start1_tail13_to16 | SUCCESS | 150.86093 | 0/428 | 36 | 6/6 |
| merge::stable_direct_u64_n9 | SUCCESS | 150.79286 | 0/405 | 61 | 1/1 |
| network::dispatch_safety_unstable_u8_n18_31_32 | SUCCESS | 146.60172 | 0/390 | 12 | 4/4 |
| network::dispatch_safety_stable_unstable_bytes16_n15_16_17 | SUCCESS | 146.04642 | 0/396 | 8 | 7/7 |
| merge::merge_contract_u8_n9 | SUCCESS | 133.80951 | 0/435 | 94 | 1/1 |
| network::insert_tail_contract_u64_start1_tail2_to8 | SUCCESS | 129.35028 | 0/428 | 36 | 9/9 |
| merge::merge_contract_u64_n8 | SUCCESS | 121.592 | 0/442 | 94 | 1/1 |
| merge::stable_direct_nonconst_u8_n9 | SUCCESS | 116.053055 | 0/398 | 63 | 1/1 |
| types::sorted_permutation_traits_stable_fallback_cell_u8_n8 | SUCCESS | 111.073074 | 0/414 | 4 | 4/4 |
| types::sorted_permutation_traits_unstable_fallback_cell_u8_n8 | SUCCESS | 109.7731 | 0/414 | 4 | 4/4 |
| merge::general_direct_u8_n9 | SUCCESS | 107.94101 | 0/400 | 63 | 1/1 |
| merge::merge_scratch48_contract_u8_n9 | SUCCESS | 106.0886 | 0/440 | 95 | 2/2 |
| network::dispatch_safety_stable_unstable_bytes85_n32 | SUCCESS | 105.9418 | 0/386 | 9 | 3/3 |
| merge::merge_contract_u8_n8 | SUCCESS | 102.64488 | 0/435 | 96 | 1/1 |
| network::mutating_route_safety_cell_n13_to16 | SUCCESS | 98.52521 | 0/189 | 4 | 10/10 |
| network::dispatch_safety_stable_unstable_bytes85_n15_16_17 | SUCCESS | 95.73365 | 0/396 | 9 | 7/7 |
| network::dispatch_safety_stable_u8_n31_32 | SUCCESS | 93.2798 | 0/387 | 9 | 3/3 |
| network::dispatch_safety_stable_unstable_drop_u8_n32 | SUCCESS | 93.16745 | 0/373 | 5 | 3/3 |
