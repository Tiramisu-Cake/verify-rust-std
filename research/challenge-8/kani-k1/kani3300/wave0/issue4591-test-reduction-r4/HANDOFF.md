# W15 exact test reduction — sealed handoff

READY_FOR_SAME_W11_EXACT_REVIEW. Implemented the owner-accepted review2ed6 COVERAGE-EDITS recipe, reducing 38 declarations to exactly seven harnesses. This is a local source/static package; independent review and native execution remain pending.

- Input g0: `7386fb02477d52a90e468b6b7183a44567497248`.
- Base task g0: `58a74e7436c8214652708bda480f1f9eccd4ad5c`.
- Accepted review g0: `2ed6d7064cd4e30f9337f0d6d288bd70baa41a3b`.
- Source base: `969f4648980a8e66cd0ca32fd3e714a55ac32cef`.
- Candidate: `2dcb2c2d9325d2aa15c21a325cf0c7c320403466`.
- Candidate tree: `b05ea48016f1cb8f20a1e7032394e602929b6e3b`.
- Sole parent: `031fc085cd4373b5fc93a55128d5a69fdbd88df1`.
- Local worktree: `/root/kani-issue4591-test-reduction-r4-w15`.
- Local branch: `work/issue4591-test-reduction-r4-w15`.

Only the six authorized test paths changed: P/A ordinary harness merged exactly; N keeps one honest Original-mode control; F/B keeps one caller-PFC negative with separate provider pre/post witnesses and the exact expected oracle; the overlap pair is deleted. P's ten helpers and three retained controls are byte-exact. The three compiler files, entire compiler/library/workflows/scripts trees, issue4591 repro pair and every tracked path outside the six-path allowlist are unchanged relative to published031. Frozen r3 worktree remains clean at its original local HEAD. Candidate is clean and committed locally with the required identity and [skip ci].

SOURCE.json and INPUTS.json pin identities and committed authority. INVARIANCE.json binds changed paths, protected trees and file hashes. FULL-969f.patch and NARROW-031.patch are full-index source patches. Both replayed in disposable indexes to exactly `b05ea48016f1cb8f20a1e7032394e602929b6e3b`; PATCH-REPLAY.json records base, patch hash and result. Full patch includes the inherited compiler fix relative to base969f; the narrow implementation delta changes tests only. STATIC-CHECKS.json and COVERAGE.md record exact discovery names, attributes/helpers/flags, source arithmetic, single selected caller calls, expected adjacency and source whitespace. These are source checks, not compiler/MIR/proof observations.

Compile/expansion/Kani/CBMC/verifier/compiletest/native formatting/full standard CI: NOT_RUN. No historical native result validates this new candidate, and no B1/B2 or independent proof credit is established. Future native must match both provider failure descriptions and named one-harness totals, and retain the caller-specific overflow oracle.

DELTA-REVIEW11-REQUEST.md is ready for the SAME current W11 context `01a1f366-706c-7321-9286-50c263db0a1e`; it has not been dispatched. No new reviewer context or subagent was created. S4 is independent and untouched. PR text is excluded and owner-controlled; this package contains no PR artifact. No compiler/native tools, CI, push, external writes, raw evidence, ledgers or accounting were used.

MANIFEST.json hashes every other file in this package and excludes itself. The containing g0 commit seals the manifest; its full SHA is supplied in the delivery response, avoiding a circular package self-pin. Package changes alone are not a new CI authorization. After SAME W11 exact review, root/coordinator needs a separate GO; publication/dispatch/accounting remain coordinator-owned. No further action is authorized by this handoff.
