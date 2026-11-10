# RESULT-KANI5116-KF1 — PASS (selected native matrix)
Original T0: coordinator GO before first dispatch, recorded 2026-11-10T21:34:14Z; main 360 + closeout 30 min, no reset.
Successful repair build: a6b5efbc-0553-41e4-b754-0603c41f395f; approved source 10b196f9f21b77e71efac70fd755ef214b958c89.
Cloud SUCCESS; bounded summary COMPLETE / VALIDATED / gate true / expectation met true.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; Kani 0.68.0 / CBMC 6.11.0.
KF1 tooling base: c98d7cee0d509b1633ab61c9a1ae989e286c8e2a; original accepted base 383fd7089550aeabac3ad92366cd7c71e2f237ee.
Patch SHA-256: fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71.
Applied tree: 46f37ae9abe9bb747ec7b7de33212484ed175a1b, equal to fresh preflight and local Kani commit b7314d9bbfbbeae00f9c81e654bf6bf172932037.
Request: kani5116-kf1-repair1-20261111-02; SHA-256 f951412a7c999d2c01310d9a719d1e841bc6fbdfed0dfe1774d2769b4fcc9714.
check-tooling: PASS for pool, all lane paths, six bound blobs, request and patch identities against KF1 base.
Production: 3 macro files +52/-11; tests: 14 new files +429/-0 (9 Rust + 5 golden); no existing golden changed.
ContractFunction retains the original specialization token alongside ItemFn, parsing/emitting ImplItemFn for full method syntax.
Initial and stacked expansions preserve default only on the outer method; signatures, attributes, spans and inline markers remain.
No contract inheritance or resolver/compiler changes. The sole repair added a mandatory PFC harness to the negative requires fixture (+6 lines).

| New fixture | Repair native result / checked behavior |
|---|---|
| specialization_default_fn_5116 | PASS; original ensures+modifies repro through nonspecialized Self |
| specialization_default_clauses | PASS; each clause, both stacked orders, PFC/default stub |
| specialization_default_generic | PASS; FnMut PFC/stub and override's own distinct summary |
| specialization_default_old | PASS; eager scalar snapshot PFC/stub |
| specialization_default_ensures_fail | PASS; Failed Checks: \|result\| *result == 0 |
| specialization_default_requires_fail | PASS; Failed Checks: value != 0 (stub caller) |
| specialization_default_modifies_fail | PASS; assigns FAILURE golden, *var_1 is assignable diagnostic |
| specialization_default_old_fail | PASS; Failed Checks: \|_\| *value == old(*value) |
| specialization_override_no_contract | PASS; error: Failed to check contract: probe has no contract |

Existing 10: 10 PASS / 0 fail — #5135 (1), KT1 neighbors (4), ordinary free/impl/trait/modifies/old+stub (5); no failures to list.
All 19 names ran once; no TIMEOUT/ignored. Every expected diagnostic came from that selector's own child output; positive expected fixtures used --require-success.
Negative expected native PASS means the golden/diagnostic matched the expected failure, not successful Kani exit.
Evidence: only bounded k1g summary/native pages, validated identities/argv/cwd/binary paths/digests; no raw logs or archives.
Repair elapsed 439.366 s (21:51:03.000282082Z–21:58:22.365957Z); Kani/compiletest builds 230/15 s; repair cost $0.1080 (8 billed min).
Build 1 f9143491-2674-408d-8eaf-2a0dfe8adc91 remains FAILURE / TOOL_ERROR: 18/19 PASS, requires fixture lacked PFC harness; no precondition-failure credit for that build.
Build 1 tree a5782891059cd86d4129056d992819ecf25b3945; elapsed 493.318 s; Kani/compiletest 253/16 s; $0.1215 (9 billed min).
KF1 selected-build ledger: 2 builds, **$0.2295 actual / $0 reserved <= $1.50**; historical KT1 $0.3510 unchanged; branch total $0.5805 <= $2.30.
Static validation: 109 Python tooling tests PASS; request/manifest/fresh-pin apply/tree/fixture checks PASS; rustfmt zero diff on 12 Rust files; no local cargo/rustc/Kani/CBMC.
Known ignored/fixme/missing-golden exclusions remain NOT_RUN as declared before Build 1; no selector/expectation weakened or removed.
Not checked: full upstream CI, core safety:: attributes, core-default smoke (KF2). Selected Kani regression evidence does not establish B2/full-proof credit.
Upstream PR description: UPSTREAM-PR-DRAFT.md (8 lines), no publication. KF1 execution complete; submitted for coordinator review, no further dispatch.
