# P1 (overlay admission for `swap_if_less`) — base reproduction and patch candidate

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

Patch candidate: `network-swap-if-less-admission.patch` (manifest
`P1-MANIFEST.json`; translator `b5ea96a1…` → `c14d8f8a…`, +50/−1). Admits
exactly one `__vf_callback_unwind_pair` marker in the complete actual
`swap_if_less` under `NETWORK_SWAP_IF_LESS_CALLBACK=1`, the per-crate
`NETWORK_SWAP_IF_LESS_CALL_LINE` (R4/W7 meta `crate_call_line`) and
`NETWORK_SWAP_IF_LESS_SOURCE_SHA256` (the crate's SHA256), on Cloud only, and
refuses the sort4 opt-ins in the same run. All existing fail-closed checks run
first. Independent review GO_WITH_NITS (review-7); **not built** (local builds
forbidden), proof credit 0. Exclusivity is one-directional: the sort4 R15 route
does not itself refuse `NETWORK_*` (harmless, admission is keyed on the body
name); making it mutual would edit Select's route and is left to Select.
It is a request to Select (r4/SELECT-REQUESTS.md P1), not a Network chain. The
base moves whenever Select's profile moves — rerun `reproduce-base.py` (its
endpoint pins then refuse until updated) and re-check the patch.
