# RESULT-KANI5116-KF1 — BUILD 1 FAILED; REPAIR 1 PREPARED
Original T0: coordinator GO before first dispatch, recorded 2026-11-10T21:34:14Z; main 360 + closeout 30 min, no reset.
Build 1: f9143491-2674-408d-8eaf-2a0dfe8adc91; source f0fae09d78f365303beb34ac262ab0e193e8ed2b; Cloud FAILURE / TOOL_ERROR / gate false.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23; Kani 0.68.0 / CBMC 6.11.0.
KF1 tooling base: c98d7cee0d509b1633ab61c9a1ae989e286c8e2a; original accepted base 383fd7089550aeabac3ad92366cd7c71e2f237ee.
Build 1 patch SHA-256: 91ce8329f9cc2e11c4ed77f4e789d10341d6914005710b04e970a3b5f53a571f; applied tree a5782891059cd86d4129056d992819ecf25b3945.
Build 1 request SHA-256: 0d6ec56aafce4e4ffe1f47762bf99fd956e7012d3102087019b0baf7545401f7; check-tooling and all bindings PASS.
Repair patch SHA-256: fd510b8a47ffff2005cc2362af6c25db790d1b579a23c0c990f6d606a983aa71; preflight tree 46f37ae9abe9bb747ec7b7de33212484ed175a1b.
Repair request: kani5116-kf1-repair1-20261111-02; SHA-256 f951412a7c999d2c01310d9a719d1e841bc6fbdfed0dfe1774d2769b4fcc9714; NOT DISPATCHED.
Production: 3 macro files +52/-11; repaired tests: 14 new files +429/-0 (9 Rust + 5 golden).
ContractFunction retains the specialization token alongside ItemFn, parsing/emitting ImplItemFn for full method syntax.
Initial and stacked expansion preserve default only on the outer method; signatures, attributes, spans and inline markers remain.
No inheritance/resolver/compiler change. Repair adds only the missing proof_for_contract harness to the negative requires fixture (+6 lines).

| New fixture | Build 1 native / gate result |
|---|---|
| specialization_default_fn_5116 | PASS / PASS; original default-method repro |
| specialization_default_clauses | PASS / PASS; individual/stacked clauses, default stub |
| specialization_default_generic | PASS / PASS; FnMut PFC/stub and override's own summary |
| specialization_default_old | PASS / PASS; eager scalar snapshot PFC/stub |
| specialization_default_ensures_fail | PASS / PASS; result == 0 assertion fails as expected |
| specialization_default_requires_fail | FAILED / ERROR; missing PFC harness, no precondition-failure credit |
| specialization_default_modifies_fail | PASS / PASS; assigns failure, *var_1 is assignable |
| specialization_default_old_fail | PASS / PASS; stale postcondition fails as expected |
| specialization_override_no_contract | PASS / PASS; override has no contract diagnostic |

Existing 10: 10 PASS / 0 fail — #5135 (1), KT1 neighbors (4), ordinary free/impl/trait/modifies/old+stub (5). No regression.
All 19 requested tests ran once; no TIMEOUT/ignored. Negative expected native PASS does not mean successful Kani exit.
Own requires stderr: missing corresponding #[proof_for_contract] harness; SHA-256 300aedfbb69f202cb4806ac2c06c8a1a03cbc299c9ae413a479ec1d542c8d406.
Bounded native evidence VALIDATED; failed excerpt diagnostic_only, 17 selected/183 omitted; exact source metadata in repair PRE-BUILD.
Build 1 elapsed 493.318 s; Kani/compiletest builds 253/16 s; actual $0.1215, $0 reserved (9 billed min).
Repair reserve $0.7965; KF1 actual + reserve $0.9180 <= $1.50. Historical KT1 cost $0.3510 unchanged.
Repair checks: fresh-pin apply/tree/fixtures, request and unchanged-manifest validation PASS; rustfmt zero diff; tooling unchanged (109 tests previously PASS).
Repair 1 awaits fresh exact-packet GO; no repair result or aggregate acceptance claimed.
Known NOT_RUN exclusions retained in original PRE-BUILD. Not checked: full upstream CI, core safety:: attributes, core-default smoke (KF2).
Upstream description draft: UPSTREAM-PR-DRAFT.md; no publication and no B2/full-proof claim.
