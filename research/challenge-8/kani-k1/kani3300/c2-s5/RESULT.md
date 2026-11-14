# S5 — READY 6d2e9ae621310605eda4b0c9572d34d9a7ff948d

Source branch fix/kani-3300-c2-s5, parent 3b382c812a1b8541946e6dc732cf04497ebcf995, final tree 6a8f2b2e11780445451640eaba8b6a7076686896.
Author Tiramisu-Cake <igkharin@gmail.com>, set through git -c. Source worktree clean.
Research remains uncommitted in g0; no source push or CI dispatch.

All21 old semantic case/root rows are closed before deletion and represented by22
one-harness expected fixtures:8 strong,7 mode (including explicit false-return partition),
7 composition. Exactly3 named JSON suites (29 old files) removed; legal-pair split into
ordinary/PFC selectors. Remaining upstream JSON suites, validator/schema/matcher/driver,
compiler/runtime/pins, S4 units and independent existing controls unchanged.

Counts: strong p2/postcondition-hole3, Replace2 from supplied exact-base run43630584079;
composition from current S4 capture43621476331. Historical Replace5→2 explained by
current own-slot initialization and nonzero closure-layout mechanisms, not invented
new observations; payload-read failures remain and support stays UNCLAIMED.
False-return companion N0 is source-justified, new native execution NOT_RUN.

Independent Luna High static review completed; copied map-text finding corrected and
all22 goldens reconciled. Requested rustfmt wrapper, staged diff whitespace check,
22-file discovery/flags/negative-cover/map/hash audit,4 sensitivity patch apply checks
and source-full.patch exact-tree reconstruction PASS. No local builds/compiler/verifier,
native compiletest, push or CI. New fixtures/sensitivity observed verdicts/exits NOT_RUN.

Four independent CI-only/test-only sensitivity patches plus exact candidate/hash/selector
manifest are outside export. Normal cases must pass in coordinator CI first; native
compiletest mutation detection remains required. Linux Quick follows targeted/regression
controls. Three-platform full Gate A remains after S6/freeze; S6 was not started.

Per-root expected does not establish mixed-inventory equality. Exported end-to-end
mixed regression coverage decreases; unchanged F7+6/2 structural units and source-reported
S4 baseline6/18 mismatch/candidate18/18 EXACT_MATCH research remain the stated basis.
See MIXED-ISOLATION-DISPOSITION/REVIEW for this explicit coordinator acceptance item.
