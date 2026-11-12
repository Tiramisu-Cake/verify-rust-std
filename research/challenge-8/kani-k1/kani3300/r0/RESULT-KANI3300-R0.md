# KANI3300 R0 — PREPARED / UNVERIFIED
Inventory and guard proposal prepared from pinned source B/R1/R2; R1 first admits flat transfers, R2 refines typed masks/protocol and checks full raw_eq extent. See NOTES.md and GUARD-DESIGN.md for paths, shortcuts and unknowns.
Owner choice required: A preserves direct MU typed masks/legacy equality with complete flat-effect rejection; B retains flat support and keeps release blocked on the provenance/init-state model. Neither selected or implemented. Source types/layouts establish neither runtime identity nor causality; reported audit failures are not new results.
| Proposed control | Expected property (requirements, not measured outcomes) | Status |
|---|---|---|
| Legal direct `MaybeUninit<[T;N]>` typed assignment/arg/return; false-data companion | Legal equality success; companion uninitialized-byte failure, no flat guard | **NOT_RUN** |
| Flat-slot raw copy with unwritten byte, retained raw_eq; holes separately left/right | A Unsupported diagnostic before effect; R2/B corrected model uninitialized-byte failure | **NOT_RUN** |
| Flat N>0/N=0, ZST T, zero/nonzero byte count; fully initialized flat | A Unsupported diagnostic for each; B supported empty/initialized legal equality success, nonempty hole uninitialized-byte failure | **NOT_RUN** |
| Local/global/promoted storage; alias/offset/overwrite and erased views | A flat/unknown origin Unsupported diagnostic; B known legal equality success or hole uninitialized-byte failure; unknown Unsupported | **NOT_RUN** |
| Cross-call arg-only/return-only, pointer effects, Move reset, DST/unresolved/shim | A flat/unresolved Unsupported diagnostic; supported direct/B legal equality success or false-data uninitialized-byte failure; unpaired Unsupported | **NOT_RUN** |
| Guard positive flat / negative direct MU; empty entry, terminator-only, last Assign | Flat exact Unsupported diagnostic retained before effect; direct legal equality success and independent uninitialized-byte failure control | **NOT_RUN** |
| Ordinary array equality: both audited legal harnesses + legal retained raw_eq | Legal equality success required for proposed export; current R2 audit reports failures, cause unknown | **NOT_RUN** |
| Identical controls on B/R1/R2/proposed candidate, including raw copy | B nonempty flat copy Unsupported; R1 raw_eq unchecked (no uninit-failure credit); R2 hole uninitialized-byte failure required; A Unsupported / B-model hole failure; legal equality success required | **NOT_RUN** |
Only these three R0 documents changed; no Kani edits, compiler/tests/CI/Cloud dispatch, cost $0. No execution, actual lowering/MIR binding, causality or proof acceptance claimed. STOP for owner review; no next stage.
