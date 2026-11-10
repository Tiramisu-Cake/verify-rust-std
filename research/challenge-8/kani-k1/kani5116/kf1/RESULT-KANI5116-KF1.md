# RESULT-KANI5116-KF1 — PREPARED, NOT RUN
No build dispatched; awaiting exact-packet PRE-BUILD coordinator GO. T0 is not started.
Pin: f046b70644e113be0df9c22c2e6ea44a65a57566; nightly-2026-10-23.
KF1 tooling base: c98d7cee0d509b1633ab61c9a1ae989e286c8e2a (authorized cumulative branch-budget patch).
Original accepted tooling: 383fd7089550aeabac3ad92366cd7c71e2f237ee.
Patch SHA-256: 91ce8329f9cc2e11c4ed77f4e789d10341d6914005710b04e970a3b5f53a571f.
Applied tree: a5782891059cd86d4129056d992819ecf25b3945; matches local Kani commit 42dd86287d181210b95717d88605d774a3fcab35.
Request: kani5116-kf1-main-20261111-01; SHA-256 0d6ec56aafce4e4ffe1f47762bf99fd956e7012d3102087019b0baf7545401f7.
Production: 3 macro files, +52/-11 lines; tests: 14 new files, +423/-0 lines (9 Rust + 5 golden).
ContractFunction retains the original specialization token alongside ItemFn, parsed using ImplItemFn.
Initial expansion emits default only on the outer method; stacked expansions serialize the same qualifier.
Signatures, qualifiers, attributes, spans and inline markers are retained; no inheritance or compiler/resolver changes.
Static checks: 109 Python tests PASS; shell/request validation and fresh-pin apply/tree checks PASS; rustfmt zero diff.

| New fixture | Native result / expectation |
|---|---|
| specialization_default_fn_5116 | NOT_RUN / PASS, original repro through nonspecialized Self |
| specialization_default_clauses | NOT_RUN / PASS, individual clauses, both stacked orders, stub |
| specialization_default_generic | NOT_RUN / PASS, FnMut PFC/stub and override's own distinct summary |
| specialization_default_old | NOT_RUN / PASS, eager scalar snapshot PFC/stub |
| specialization_default_ensures_fail | NOT_RUN / native PASS; false result == 0 assertion must fail |
| specialization_default_requires_fail | NOT_RUN / native PASS; value != 0 must fail in stub caller |
| specialization_default_modifies_fail | NOT_RUN / native PASS; assigns property must fail |
| specialization_default_old_fail | NOT_RUN / native PASS; unchanged-value postcondition must fail |
| specialization_override_no_contract | NOT_RUN / native PASS; override has no contract diagnostic |

Existing 10 selectors: NOT_RUN; #5135 (1), KT1 neighbors (4), ordinary free/impl/trait/modifies/old+stub (5).
No failures or proof credit can be assigned before native execution; all 19 expectations are pass.
Known fixme/ignored/missing-golden exclusions are listed in PRE-BUILD before dispatch; none selected.
Build/wall time: NOT_RUN. KF1 cost $0 actual / $0 reserved; proposed Build 1 maximum reserve $0.7965.
Independent KF1 cap $1.50; at most one repair after a new GO and actual-cost check. Historical KT1 cost $0.3510 unchanged.
Not checked: full upstream CI, core safety:: attributes, core-default smoke (KF2); no B2/full-proof claim.
Upstream PR description draft: UPSTREAM-PR-DRAFT.md (8 lines); no publication.
