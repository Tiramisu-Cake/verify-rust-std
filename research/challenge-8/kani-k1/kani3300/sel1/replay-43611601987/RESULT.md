# SEL1 SmallSort replay — run 43611601987 (Kani SEL1 ec85b782a1, uninit ON)

2026-11-14, coordinator. CI overlay `78d2b17d16` (tree bed4a1cffe = worker15 package e59c3527a8) on Gate B′ recipe
`0c1cc8a7d0`, branch `ci/kani3300-sel1-replay-w15`. All six receipts bind `tool_sha` ec85b782a1b7156ad434cfac25403acd4e326dc1.
Std `70ba5befc6` + SEL1 test-only overlay (`6075e7ce17`). object-bits 12, source unwinds, default solver/slicing/checks,
valid-value OFF, controls cfg ON, organizer flags incl. --no-assert-contracts. Verdicts read from per-row stdout.

| Row | Harness | Result |
| --- | --- | --- |
| sort4-closure-on | `helper_contracts::sort4_safety_u64` (PFC `sort4_stable`) | **SUCCESS**, 0 of 753 failed (14 unreachable), 3/3 covers |
| swap-if-less-closure-on | `helper_contracts::swap_safety_u64_backing4` (PFC `swap_if_less`) | **SUCCESS**, 0 of 585 failed (12 unreachable), 6/6 covers |
| raw-legal-on | `replay_uninit_controls::sort4_raw_all_initialized_u64` | **SUCCESS**, 0 of 382 failed, 2/2 covers |
| raw-negative-on | `replay_uninit_controls::sort4_raw_hole_negative_u64` | **intended FAILURE only**: 1 of 382 — `sort4_stable::<u64, …read_less_u64>.safety_check.1`, "Reading from an uninitialized pointer of type `*const u64`", smallsort.rs:751:26 (source[1]); select Unsupported gone |
| merge-raw-closure-on | `helper_contracts_wide::merge_safety_u64_len8_scratch48_src32_dst0` | **SUCCESS**, 0 of 572, 5/5 covers (regression vs B′ C1: 570) |
| merge-profile-closure-on | `replay_gateb_prime::merge_profile_closure_scratch48_u8_n9` | **SUCCESS**, 0 of 1030, 2/2 covers (B′ C1: 1028) |

- No row contains a failed `unsupported_construct`; `select_unpredictable` Unsupported properties: 0 in every row.
  Remaining `unsupported_construct` properties (5–6 per row) all have status SUCCESS (unreached).
- Run4 (C1) → this run: sort4 legal/PFC rows go from "1 select Unsupported" to SUCCESS; the negative keeps exactly
  the intended source[1] read and loses the extra select Unsupported → now a clean single-failure negative.
- Native controls: targeted run 43613912120 on 39a6521bf1 (tests-only follow-up of ec85b782a1): select-unpredictable 29/0.
- Scope: bounded helper evidence for these geometries/targets with closure comparators; not all-SmallSort/all-T,N.
  SEL1 is a separate track outside Part 1 scope A; receipts do not transfer to C2 or a later port.
