# S1-06 offline acceptance — run 43889560779

**Result: acceptance pending; proof credit NONE.** This is a replayable offline classification from the pinned request and the 14 compact structured JSON artifacts. It did not inspect stdout/stderr previews or raw logs, and did not relax the current fail-closed location rule.

## Inventory and admissible observations

- 14 groups / 35 harness rows: 4 groups have complete file/line inventory; 10 groups failed intake with missing sites. Eighteen property records are retained without usable file/line coordinates, across 18 rows; each is `class=unreachable`, `status=SUCCESS`, description `unreachable code`. Their structured `location_display` begins `library/core/src/lib.rs:0:0` and names a helper specialization. There are two distinct property IDs (u8: 14 rows; NonCopyByte: 4 rows). No missing coordinate was inferred from a property count, function name, ordinal, or neighboring site.
- Qualification is `UNKNOWN` for all 26 rows in failed/incomplete groups, including the 8 individually coordinate-complete rows in `light-controls-u34`; this separate group-completeness gate is recorded for every affected row. The other 9 rows, from four complete groups, remain structured source observations only. All 35 row acceptance states remain `PENDING`.
- 27 rows report positive source verdicts without failed properties. Eight expected-negative rows match the predeclared sole failure by exact ID, class, status, source file/line, and pinned source or variant patch. These are source-reported structured observations, not independent proof results.
- All 113 required cover messages bind to unique `SATISFIED` property IDs. SAT supports reachability observations only. Of 127 required success messages, 13 bind through a unique source assertion site to a successful placeholder assertion; the rest remain pending.
- Exact inventory reconciliation distinguishes 1,276 `class=unreachable,status=SUCCESS` properties from 413 check properties with `status=UNREACHABLE` and 2 covers with `status=UNREACHABLE`. These statuses are not interchangeable. The stock role is confirmed: pinned Kani compiler `statement.rs:513` generates `PropertyClass::Unreachable` for MIR `Unreachable`; that identifies a guard assertion, not a failed check. The 413+2 records still need role/applicability analysis against post/frame/relation obligations; helper or function names do not grant an exemption.

## Remaining gates

No row is independently accepted. Besides 18 row-level coordinate gates, the 10 failed groups have a separate group-intake completeness gate and `binary_after=UNKNOWN_AFTER_RUN_STOPPED`, affecting 26 rows. Unreachable-status role and post/frame/relation applicability remain pending on 31 rows; full qualified target/contract-wrapper binding remains pending on 22 PFC rows; required success-message binding remains pending where exact property links are not unique. Same-run companion checks retain their own source verdict, row/group completeness, and after-run fingerprint gates. Proof credit remains NONE for all 35 rows.

The missing `unreachable`-class records are successful stock MIR-`Unreachable` guard assertions; they are not failures and do not create a failed obligation by class alone. Any counterfactual location exception is **NOT_APPLIED** and remains a coordinator policy decision. Source coordinates also do not independently establish AST/MIR/parser-input binding.

The per-group/per-row detail and replay are in [ACCEPT.json](ACCEPT.json) and [intake.py](intake.py). No historical receipts or ledgers were changed.
