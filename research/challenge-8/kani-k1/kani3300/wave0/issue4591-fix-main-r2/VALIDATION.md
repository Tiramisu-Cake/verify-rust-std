# Static/mock validation and exact transfer checks

Run python3 -B validate.py. VALIDATION.json records executed checks and their
assurance limits. The checker verifies the actual clean source commit/tree,
sole new-main parent, one-commit range, author/skip message, exact three compiler
and eight test paths, patch and protected-file/tree hashes. The split regression
patch plus compiler patch and the whole patch replay independently through
temporary Git indexes to the exact candidate tree.

TRANSFER.json pins clean application of the old repaired full patch to the new
base without conflicts or adaptations. Normalized candidate diffs are identical
and normalized old-main..new-main equals old-r1..new-source. Normalization removes
only index blob-ID header lines and retains every path, hunk coordinate and
content line. Range-diff is checked against actual git objects. All31 upstream
path identities are validated, including preserved new attributes API,
contracts feature-flag expression, nightly-2026-11-18 toolchain, chrono removal
and Cargo.lock. All eight test/oracle files match repaired r1 byte-for-byte.
All16 standard workflows and every native job/matrix are validated against the
new approved main, together with scripts/actions/library/dependency invariance.

The unchanged pfc_fixture_check.py inventories 13 lexical PFC harness target
calls and performs sixteen narrow checks/mutations for direct/copy input
separation and every other original function/attribute. The two affected
harnesses retain the direct-provider-PASS/copied-provider-FAIL source oracle.
No AST/FnDef/MIR reachability or native result is established by lexical checks.

Synthetic publication checks accept exact new-main/same-tree nonskip metadata
and reject skipped candidate/main, abbreviated SHA, wrong/merge/old-base/old-source
parents, old r1 tree, tree drift, empty/extra ranges, skipped ancestors and skip
directives. Actual read-only CLI calls reject new candidate, new main, old r1
candidate and an abbreviated SHA. No future publication object is created.

Original package/review and repaired r1 package are compared with frozen commit
objects; the historical source analysis is carried verbatim. Fresh main lookup
matches approved969f with no further drift. Old faff intake stays INCONCLUSIVE
and provides no new-main or fixed-candidate credit. W11-01 is pending independent
closure; ONE combined same11 delta-review and root GO are still pending.
Compiler/cargo/rustc/rustfmt, expansion, Kani/CBMC, verifier/fullrunner, all new
native tests, CI, push/PR/issues, ledger/reservations/budget remain NOT_RUN.
