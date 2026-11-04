# RESULT NEWPINCAL — Part 1 v7 on Kani cd355b0b: rows 4/4 as expected; inventory 202 (cfg-off), not 210
Build `998c68c4-76bc-44ff-96d7-7d73b1f39ad7` (k1-standard4, 11:17:48–12:03:51Z, Cloud Build SUCCESS), head `937765c281`
(GO), library tree `32ce0c62f6` = TRIMPART, Kani `cd355b0bccd3…` / nightly-2026-10-22 from the tree, request
`newpincal-diag-inv-ctl-4rows-20261104` sha256 9d8b8b11…0f34. check-tooling vs eccc31f43b rc 0 (pool, lane files,
6 bound SHA-256). Lane gate True, expectation met True, `Complete - 2 successfully verified, 2 failures, 4 total`.
Compile with `--cfg kani_smallsort_controls` OK; no `[-]> .*smallsort` warning. Own $0.6345 ≤ $1.00; project
used $93.6465 / $98.96, reserved 0. One Build, no retry, no repair. Evidence in `newpincal/` (g1.*).
## Inventory
202 names, complete (3 pages, `names_sha256` b721d93c… recomputed from pages), byte-equal as a set to TRIMPART
`ordinary-expected.txt` (202); 0 of the 8 `controls-expected.txt` names. Task gate "exactly 210" **not met** (fact,
no fix). Lane cause (unchanged): for diagnostic + `inventory: true` gcb-k1.sh runs `kani list` (l.134) before exporting
controls RUSTFLAGS (l.166; kind `inventory` exports first, l.105–107), so this is the cfg-off (CI) list.
## Rows (controls on, jobs 1, uninit off; cbmc peak 0.32 GiB, whole run 1.60 GiB max RSS)
| # | Root | Status | VT s new | VT s old pin | Checks | Covers | Failed check (description @ location) |
|---|---|---|---:|---|---|---|---|
| 1 | network::swap_contract_four_positions_u8 | SUCCESS | 12.8 | 15.4 (predecessor `swap_profile_four_positions_u8`, RESULT-SPECFIX) | 0/322, 4 unr. | 5/5 | — |
| 2 | network::dispatch_safety_stable_u8_n0_1_2_7_8 | SUCCESS | 11.6 | none in RESULT | 0/380, 10 unr. | 6/6 | — |
| 3 | assembly::reject_mutant_swap_u8_n2 | FAILED = exp. | 0.4 | none in RESULT | 1/80, 6 unr. | 1/1 | `assertion failed: v[0] <= v[1]` @ assembly.rs:25 |
| 4 | merge::specfix::specfix_wrong_f_swap_rejected_u8 | FAILED = exp. | 0.2 | 0.1 (RESULT-PONECLEAN G1) | 1/243, 10 unr. | 1/1 | `specfix_canonical_comparator::<P>(cmp)` @ specfix.rs:216 |
## Conclusions for the full CI run on the new pin
- The whole Part 1 v7 tree (ordinary + controls cfg) compiles on cd355b0b / nightly-2026-10-22 with no smallsort
  warning, and the cfg-off listing gives exactly the 202 ordinary roots: the CI set is intact.
- Contracts (`proof_for_contract`, `stub_verified`, stubs) and default checks behave as before on the 4 rows;
  failed-check descriptions keep the old format (`assertion failed: <expr>`, requires expression), so the
  existing expect_check texts carry over. Times: row 1 12.8 vs 15.4 s (predecessor), row 4 0.2 vs 0.1 s.
- Four light rows say nothing about the heavy roots (old TIMEOUT-margin and multi-GiB ones): their time/RSS on
  the new pin still need the full matrix. A cfg-on 210 inventory needs kind `inventory` with `controls: true`.
  Not checked: the other 6 controls, uninit checks, kani_jobs 2 (organizers' layout).

NEWPINCAL ЗАВЕРШЁН
