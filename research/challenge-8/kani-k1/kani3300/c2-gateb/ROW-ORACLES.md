# C2 row oracles (unchanged bounded Gate B′)

Common selector prefix: slice::sort::shared::smallsort::verify. Exact argv/environment: CI-REQUEST.json.

| ID | Selector suffix | PFC target / unwind | Required C2 result |
| --- | --- | --- | --- |
| merge-raw-closure-on | helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0 | bidirectional_merge / 34 | SUCCESS; 0 failures and Unsupported; covers 5/5; useful body/frame checks reached |
| merge-profile-closure-on | replay_gateb_prime::merge_profile_closure_scratch48_u8_n9 | concrete merge_profile_closure_u8 / 34 | SUCCESS; 0 failures and Unsupported; ensures reached; covers 2/2, both scratch backings |
| sort4-closure-on | helper_contracts::sort4_safety_u64 | sort4_stable / 16 | BOUNDARY; exactly one select_unpredictable failure in hint.rs; 0 comparator/layout/uninit/frame failures |

Profile: closure comparators, same PFC targets, uninit ON, object-bits 12, cfg controls ON, valid-value OFF, normal solver/slicing/default checks, organizer flags including --no-assert-contracts. Geometry/harnesses/contracts/comparators are byte-identical to C1 std overlay. Profile companion is concrete test-only, not proof of generic fn-pointer merge_profile<P>.
C1 run 43600834435 comparison: raw 570 checks (16 unreachable), covers 5/5; profile 1028 (68 unreachable), covers 2/2; sort4 758 with exactly one select_unpredictable failure at hint.rs:871. Totals need not equal; explain every useful check/ensures/cover loss and compare semantics/reachability. Unsupported properties marked SUCCESS/unreached are not failures; retain their full inventory.
Sort4 SUCCESS requires explicit coordinator review of selected body/reachability and is not automatic acceptance. New merge failure is BLOCKED with exact obstacle; no source or contract relaxation. All receipt.outcome=UNKNOWN require explicit coordinator review. No whole-SmallSort, unbounded, or independent B2 proof credit.
