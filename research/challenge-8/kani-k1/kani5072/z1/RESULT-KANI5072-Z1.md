# RESULT-KANI5072-Z1 — PASS (selected native subset)
Build: 035befd9-379a-4172-9c22-0e6d0e2c8857; source: 39c5682413bfe2a2223382d35119f92776654df9 (exact coordinator GO).
Cloud SUCCESS; bounded summary COMPLETE / VALIDATED / gate true / expectation met true.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; Kani 0.68.0 / CBMC 6.11.0.
Tooling base: c98d7cee0d509b1633ab61c9a1ae989e286c8e2a; check-tooling PASS for pool, lane paths, six bound blobs, request and patch.
Local Kani commit: 6fba5bf9254f4954dd6dbce6ece8ef159004e905; no Kani push or upstream publication.
Patch SHA-256: 380b22438bbdd115d98aacc81f97a49cce24e9abf77fa176c32067210e8ff238.
Applied tree: f3791c8eb38f92bc331bf8b8c63cda0bc22b9db4; matches fresh-pin preflight and local committed tree.
Request: kani5072-z1-main-20261111-01; SHA-256 adbeda538f3c142a3748b1f498c8aae6480e89b1a75e9c104866d61a1d588bdf.
Unconditional src.dereference() caused a spurious memory access for a ZST volatile read.
The fix constructs a typed inhabited-ZST result and retains alignment; uninhabited ZSTs get an explicit SafetyCheck.
Returning and no-return-target paths share that diagnostic; non-ZST lowering remains unchanged.
Null inhabited ZST is positive under the pinned contract; alignment and valid initialized values remain mandatory.
Diffstat: production 1 file +30/-2; tests/goldens 5 new files +90/-0; existing goldens unchanged.

| Selector/group | Native result / checked behavior |
|---|---|
| load_zst.rs (six harnesses) | PASS; reference/dangling/over-aligned/null/direct/aggregate; require_success |
| zst_unaligned.rs | PASS; `src` must be properly aligned |
| zst_uninhabited.rs | PASS; volatile load of an uninhabited type has undefined behavior |
| Existing load.rs / store.rs / unaligned.rs | 3 PASS; ordinary loads/stores and unaligned byte precision |
| Existing volatile_load/unaligned/main.rs | PASS; `src` must be properly aligned |
| Existing unaligned_volatile/out_of_bounds/main.rs | PASS; dereference failure: pointer outside object bounds |

All 8 selectors ran once; no TIMEOUT/ignored; all native compiletest exits 0 and all declared expectations met.
Negative expected-mode PASS matched failing-check goldens and specific own-child-output diagnostics; no unexpected SUCCESS.
Evidence: bounded k1g summary/native pages (0→4→end), status, check-tooling and own budget; identities/argv/cwd/binary digests checked.
Elapsed: 523.746 s, 2026-11-11T02:12:27.724314506Z–02:21:11.469829Z (Cloud status; summary whole-run wall is MISSING).
Kani/compiletest builds: 271/18 s; one Build, $0.1215 actual (9 billed minutes), $0 reserved <= $0.50 cap; no retry.
Static request/apply/tree/fixtures/goldens/rustfmt/whitespace checks PASS; independent Luna HIGH review has no remaining blockers.
Code-ready patch and selected native subset verified; full upstream CI and fixme_* NOT_RUN; no B1/B2/full-proof credit.
Uninit/valid-value instrumentation was off for this subset; no new initialization-check coverage is claimed.
UPSTREAM-PR-DRAFT.md updated; no PR/issue/comment/Actions created. Z1 complete, submitted for coordinator review; no further dispatch.
