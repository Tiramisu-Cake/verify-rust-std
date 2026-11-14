# C2-S1 — conflicts and upstream preservation

Three-way common base `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`; ours exact U+B1, theirs exact accepted C1b. No reset/stash, floating rebase, pin movement or old B1 replay. Full path list and blob identities: INPUTS.json.

## Manual conflict map (14 paths)

| Paths under kani-compiler/src/kani_middle/ | Resolution |
| --- | --- |
| points_to/mod.rs | C1b exported AnalysisBodyOverride/BodyProvenance plus the single shared resolver |
| points_to/points_to_analysis.rs | C1b active-call/error/provenance structures and selected-body priority; source fallback and shared resolver use checked_body(tcx, instance) |
| transform/check_uninit/delayed_ub/initial_target_visitor.rs | C1b collector/anonymous targets and explanatory comment; failed resolver remains `.ok()` |
| transform/check_uninit/delayed_ub/instrumentation_visitor.rs | C1b instrumentation; one local unsupported-call owner, no duplicate delayed check |
| transform/check_uninit/delayed_ub/mod.rs | C1b `tcx` visitor constructor, selected override map and Result handling; U checked_body for source targets/entry fallback |
| transform/check_uninit/ptr_uninit/uninit_visitor.rs | C1b protocol/storage behavior, imports incl UintTy; add U TyConstKind and AtomicStore arm; retain common resolver/epilogue and pass tcx |

Eight add/add fixture conflicts under tests/expected/uninit/unresolved-calls/: entry-initialized, entry-partial, erased-pointer, pending-ops, each plain/seeded. Entry inputs take C1b symbolic union values/comments and B1 panic=abort; pending-ops retain B1 panic=abort; erased-pointer takes C1b comment. Single path per fixture, unchanged expected output.

## Clean merges requiring semantic checks

- #5115 `3e095c22a`: AtomicStore is outside check-only group; nonvolatile pre-check retained, setter true after store for both modes; volatile gains no extra pre-read. U codegen store/exchange distinction and atomic controls preserved.
- #5152 `7f89576f8`: `BodyTransformation::body_ref` retains checked_body. Imported immutable-origin collector also uses checked_body; the shared resolver checks actual source MIR through it. In recursion/entry analysis, an already selected RegistrationOverride/DiscardedClosureOverride remains the chosen body; source fallback is lazy. No substitution of source registration panic body for generated trampoline.
- #5093 `2ec6953d9`: U clause-depth helpers are exact; no saturating-method calls or old warnings restored.
- #5154 `0aac16ef6`: all U JSON-handler files and scripts/validate_json_export.py are exact blobs. Three accepted Part1 JSON suites remain additions; S5 conversion is deferred.
- #5138 `28ef0488f`: U workflow matrix retained, including macos-15 and macos-15-intel; no old macos-14 policy or new CI overlay.

Only source lookup plumbing and pinned upstream integrations change accepted production behavior in S1. F5 immutable descriptor coalescing, F6 nested aggregate reset, F7 cache isolation and F8 SEL1 remain unchanged. No goldens were auto-blessed. Mechanical conflict-tool mistakes were caught during full diff inspection and corrected before the committed/reviewed candidate; final targeted diff and exact-blob audits cover complete file contents.
