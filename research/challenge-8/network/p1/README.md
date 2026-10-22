# P1 (overlay admission for `swap_if_less`) — base reproduction, patch not started

`reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR` rebuilds, by `git apply`
only, the first two stages of Select's overlay base from `run-o26-refresh.sh`
(@`10e13a41`): 20 manifest patches on `f76012fb` → frozen diff SHA256
`6c4c5a77…`, then 2 refresh patches → `vf_mir_translator.ml` SHA256 `0862e635…`.
Stage 3a (strict 3 + C4 chain 10 + native 3 from `a1-tool-r17.py reconstruct()`)
reaches the caller manifest's `c4_base_translator_sha256` `66e266d3…` (38 patches).
Verified locally 2026-10-22 (every checkpoint matches). No build or runner execution.

Next (not done): rest of stage 3 — the A1 overlay order of
`sort4-caller-entry-native/a1-tool-r17.py reconstruct()` (strict, c4, legacy,
native-signature, lifetime, c1/c2 recovery, scope/referent overlays), checked
against the profile's `r_before`/`r_after`/`c_before`/`c_after` translator SHAs.
Only on that exact translator can the P1 patch be written; it must keep every
fail-closed check of the callback-unwind overlay (r4/SELECT-REQUESTS.md) and be
handed to Select as a reviewed patch candidate, not forked into a Network chain.
