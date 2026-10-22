# P1 (overlay admission for `swap_if_less`) — base reproduction, patch not started

`reproduce-base.py VERIFAST_REPO SELECT_COMMIT OUT_DIR` rebuilds, by `git apply`
only, the first two stages of Select's overlay base from `run-o26-refresh.sh`
(@`10e13a41`): 20 manifest patches on `f76012fb` → frozen diff SHA256
`6c4c5a77…`, then 2 refresh patches → `vf_mir_translator.ml` SHA256 `0862e635…`.
Stage 3 (`a1-tool-r17.py reconstruct()` order: strict 3, C4 chain 10, native 3,
zst, dead-code identity, focus scope, lifetime, slice/threshold/selected, R,
signature, reference-own, C, R15 c1/merge-fractions, R16 five, R17 phase, R17 c2)
is reproduced with every pinned base/result SHA checked against Select's current
profile `A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json`: 61 steps, checkpoints
`66e266d3…` (C4 base), `e484d9f9…` (selected), final translator
`b5ea96a19481383a2cbc82fb8f479095d9fdabeecd531b3a2e02cb1b59ba180d` (= Select's
recorded c5 overlay result). Verified locally 2026-10-22. No build or runner execution.

Next (not done): the P1 patch itself, written on that exact translator: admit
exactly one `__vf_callback_unwind_pair` marker in a body named `swap_if_less`
under an explicit opt-in (call line, verified-crate SHA), keeping every
fail-closed check of the callback-unwind overlay (r4/SELECT-REQUESTS.md); hand it
to Select as a reviewed patch candidate, not forked into a Network chain. The
base moves whenever Select's profile moves — rerun this script on the new commit.
