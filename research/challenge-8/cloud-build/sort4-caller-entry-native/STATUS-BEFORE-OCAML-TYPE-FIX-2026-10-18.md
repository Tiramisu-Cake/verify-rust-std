# select/sort4 — OCaml R-only build blocker identified

Owner select-sort4; branch research/night-select-sort4-cloud-2026-10-09.

Reloaded Brief 0.5.1 for Build 7c26b389-1ad9-45c8-9adf-089125476fdb now reports
OCaml `D.Type expects 0 argument(s)` at translator:6681; R-only reference build
exit 2. The prior reporting gap is resolved for selecting a minimal proposal.
Earlier checkpoints, reports, verdicts, pins and ledgers remain unchanged.

Pinned source matches the diagnostic location. Separate one-line proposal adds
`D.generic_arg_kind` type context to the local match result. Source-only patch
application and unchanged-C compatibility PASS; compiler validation UNKNOWN.
Active R/profile/release identities are unchanged: proof/infra e58a75bb,
release ab803728, full R patch91fe9ad4…b6466, exporter c29d0d46…b463ad.

All 26 rows are source-reported NOT_RUN; P1, threshold proofs, own-pair N-false31
lifecycle and final C success are unestablished. Stage order/last completed stage
and Rust-exporter-alone outcome remain UNKNOWN. No formal credit; A1/A2 open.

[Current diagnosis and validation plan](cloud-build/sort4-caller-entry-native/diagnostic-7c26b389-ocaml-type-2026-10-18/REPORT.md),
[Brief](cloud-build/sort4-caller-entry-native/diagnostic-7c26b389-ocaml-type-2026-10-18/brief.md),
[separate proposal](cloud-build/sort4-caller-entry-native/diagnostic-7c26b389-ocaml-type-2026-10-18/PROPOSED-generic-arg-kind-annotation.patch).

Account remains CLOSED: 433/960s charged, 1/1 Build, 527 retired; old accounts
unchanged. No retry, new Build, raw audit or local compilation occurred.
Next: authorize candidate activation and a separate Cloud allowance/window after
review and source-only preparation. No administrative raw audit is required to
select this fix; its compilation and later blockers remain untested.
