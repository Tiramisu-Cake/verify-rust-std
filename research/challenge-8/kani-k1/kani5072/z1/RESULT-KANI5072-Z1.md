# RESULT-KANI5072-Z1 — PRE-BUILD, native NOT_RUN
Task: KANI5072 Z1; owner k1-merge; stage kani5072-z1; Runtime Codex.
Source branch: experiment/kani-k1-kani5072-20261111; exact packet SHA is in PRE-BUILD REVIEW marker.
Kani pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; tooling base c98d7cee0d509b1633ab61c9a1ae989e286c8e2a.
Local Kani commit: 6fba5bf9254f4954dd6dbce6ece8ef159004e905; no Kani push or upstream publication.
Patch SHA-256: 380b22438bbdd115d98aacc81f97a49cce24e9abf77fa176c32067210e8ff238.
Applied tree: f3791c8eb38f92bc331bf8b8c63cda0bc22b9db4; equals local committed tree after fresh-pin apply.
Request: kani5072-z1-main-20261111-01; SHA-256 adbeda538f3c142a3748b1f498c8aae6480e89b1a75e9c104866d61a1d588bdf.
Unconditional src.dereference() caused a spurious memory access for a ZST volatile read.
The fix constructs a typed ZST result, retaining alignment; returning uninhabited ZSTs fail explicitly.
Returning and non-returning ZST loads use the same uninhabited-value SafetyCheck; non-ZST lowering is unchanged.
Null inhabited ZST: positive under the pinned contract; alignment and valid initialized values remain mandatory.
Diffstat: production 1 file +30/-2; tests/goldens 5 new files +90/-0; existing goldens unchanged.

| Selector/group | Native result / expected check |
|---|---|
| load_zst.rs, six harnesses | NOT_RUN; reference/dangling/aligned/null/direct/aggregate, require_success |
| zst_unaligned.rs | NOT_RUN; `src` must be properly aligned |
| zst_uninhabited.rs | NOT_RUN; volatile load of an uninhabited type has undefined behavior |
| Existing load/store/unaligned (3) | NOT_RUN; native PASS required |
| Existing non-ZST misalignment | NOT_RUN; `src` must be properly aligned |
| Existing non-ZST bounds | NOT_RUN; dereference failure: pointer outside object bounds |

Static: request/schema, fresh-pin apply/tree/fixtures/goldens, allowed paths, rustfmt, diff whitespace PASS.
Independent Luna HIGH static review: no remaining blockers; exact identities in INDEPENDENT-REVIEW.md.
Spend: $0 actual/$0 reserved; proposed 35 minutes x $0.0135 = $0.4725 <= $0.50; no Build submitted.
Code-ready candidate; no native subset verified, no B1/B2 proof credit. Full upstream CI and fixme_* NOT_RUN.
Stop boundary: exact-packet coordinator PRE-BUILD review/GO, explicitly required by TASK-KANI5072-Z1.md.
PR draft: UPSTREAM-PR-DRAFT.md; no PR/issue/comment/Actions created.
