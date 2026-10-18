# select/sort4 — unused_mut fix candidate, Cloud NOT_RUN

Owner select-sort4; branch research/night-select-sort4-cloud-2026-10-09.
Initial checkpoint/HEAD d2444867 matched remote; no fresher commits found.

Updated Brief for57ea65a3-475e-4370-810c-19ad36803174 now corroborates R-only
native reference build exit2: unused_mut exporter843:17 and906:60 under
#![deny(warnings)]. All26 rows source-reported NOT_RUN. The prior insufficient
Brief diagnosis is resolved for choosing this fix; old reports/checkpoints stay
unchanged. P1/N-false31/formal verification were not established.

New R candidate removes only the two approved mut tokens. Exact43-patch baseline,
R/C source/hash and frozen semantic checks PASS; exporter c29d0d46…b463ad.
New profile/authorization binding and recipe retain the same26-row matrix.
10 dispatcher checks +4 same-Build reuse tests PASS, independent Luna High review
finds no source blocker. Compilation/extraction/verification only Cloud; new
candidate remains NOT_RUN pending published closure/config preflight and Build.

New phase SORT4-A1-UNUSED-MUT-FIX-CLOUD-2026-10-18; T008:37:29Z,
main10:37:29Z, absolute11:07:29Z,960s/max1 Build900s. Old330/960 with630 retired
and earlier accounts remain closed; no carry. Canonical C protocol ID stays old;
new authorization ID is separately pinned/enforced without translator changes.

[Session](cloud-build/sort4-caller-entry-native/A1-UNUSED-MUT-FIX-2026-10-18.md),
[source checks](cloud-build/sort4-caller-entry-native/A1-UNUSED-MUT-SOURCE-CHECK-2026-10-18.json),
[review](cloud-build/sort4-caller-entry-native/A1-UNUSED-MUT-REVIEW-2026-10-18.md).
Previous STATUS preserved in dated snapshot. All pre-existing local policy edits
preserved. Full A1/A2 NOT ACHIEVED, index15%, profile UNACCEPTED; actual
small_sort→helper, A2/ZST, C5/copies and sort8 remain outside this task.
