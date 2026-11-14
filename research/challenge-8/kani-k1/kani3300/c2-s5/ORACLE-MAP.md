# S5 ORACLE-MAP — STOP before deletion

Machine-readable source/JSON pointers, operations, selectors, required property descriptions/statuses,
current S4 counts and per-row status are in ORACLE-MAP.json (21 roots/cases).
This is the first preparation result, not a completed replacement map.

Two missing evidence classes block destructive migration:

- Strong `/cases/4` (p2) and `/cases/5` (postcondition-hole): two mandatory instrumentation failures of one read,
  `*const u8` and `u8`; the exact outer ensures may be FAILURE or UNREACHABLE under the old oracle.
  The old checker accepts that specific consequence; it does not establish a single total N.
  New goldens must select exactly 2 or exactly 3 after current-output confirmation, never accept both.
- Mode `/roots/0` replace_transfer: UNCLAIMED observation accepts either completed SUCCESS or FAILURE.
  S4's “mode ok” therefore does not determine verdict, exact N, failed kinds or useful reached checks.
  Historical five failures include capture/layout defects subsequently changed; importing them is invalid.

Composition counts were read from current S4 candidate per-root capture summaries, not C1b:
immutable_legal0, immutable_hole_negative2, ordinary_ensures_legal0, pfc_legal0,
pfc_negative3 (two reads plus exact ensures41 consequence), cycle_root1,
unrelated_legal_after_cycle0. Paths moved into single-root files still need native CI validation.

All existing controls and three suites remain intact. No fixture is declared a replacement.
Source-to-GOTO causal binding, portability on three hosts, and native candidate/sensitivity results remain NOT_RUN.
