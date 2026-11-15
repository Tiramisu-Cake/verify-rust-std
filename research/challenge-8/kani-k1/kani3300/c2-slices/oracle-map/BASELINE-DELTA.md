# Submitted B1 fixture disposition

U→F adds 364 test source/golden paths and the edge README; no U test removal/modification. B1 already supplies 44 of the 364 paths (22 fixtures). B1→F modifies eight submitted source files and adds twelve unresolved-calls paths (six fixtures). Exact 20 patches are in BASELINE-DELTA.json.

- entry-{initialized,partial}-{plain,seeded}.rs: owner4; runtime-symbolic union instead of ordinary union constants, preserve exact entry u32 SUCCESS/FAILURE plus FnPtr refusal, original goldens unchanged. Baseline fixtures remain mandatory from B1; final source replacement waits for4.
- erased-pointer-{plain,seeded}.rs: owner1 comment correction; actual cast program/golden retained.
- generated-positive-{plain,seeded}.rs: owner1 comment/probe correction; Fn-item/generated body/drop controls retained, original goldens unchanged; comment alone does not prove actual binding.
- item-return-{initialized,uninit}-{plain,seeded}: owner4, paired return/known false vs true; capture-free generated closure shape must be reviewed; no nonzero captured fields.
- tuple-maybe-uninit-{plain,seeded}: owner4, exact tuple-layout Unsupported before direct-shadow Shim guard; this does not qualify that guard.

No B1 source/golden deletion, no rewrite of B1/#5172. Historical S5 legal-pair removal is absent from U→F; it is accounted semantically in SEMANTIC-LINEAGE.json.
