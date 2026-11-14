# S2 follow-up CI — coordinator (2026-11-14)

Baseline: 69b13711e + baseline-controls.patch + baseline-new-controls.patch (commit 16db0764e3, tree 0178f8e21d — superset of the
requested 74dd51d27e: also carries the first four controls) + CI-only d187f8398c, run 43606850975:
- immutable-descriptor-coalescing: 4 ok (direct/nested-first[-volatile], NONDISCRIMINATING as before),
  **2 FAILED**: aggregate-constant-initializer, const-fn-initializer — kani-compiler exit 101,
  `error: conflicting immutable descriptors: symbol …::AllocId(10, …), requested AllocId(0, …)`.

Candidate bf8170b28 + CI-only 52bb00546c, run 43606854394: SUCCESS —
format check PASS, build PASS, clippy PASS, `cargo test -p kani-compiler -- immutable_allocations` 9/0,
expected `immutable` filter 19/0 (all 6 coalescing controls + immutable-masks, contract-immutable-masks, part1-edges immutable-*).

=> F5 reproduced on real source (two discriminating controls) and fixed by the candidate. S2 accepted at bf8170b28.
Full uninit Quick for S2 head: last full run 43603876627 on f96ad419bc (only fmt + 2 test files differ since).
