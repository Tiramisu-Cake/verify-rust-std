# C2-S2 CI — coordinator summary (2026-11-14)

Candidate f96ad419bc + CI-only d86dce7de7, run 43603876627:
- Format check: FAIL — rustfmt reflows two unit-test expressions in immutable_allocations.rs (~:520 `let expected = if … { Err(first.clone()) } else { Ok(()) };` onto one line; ~:550 `registry.register(…).is_ok()` split into a method chain).
- Build, clippy: PASS. `cargo test -p kani-compiler -- immutable_allocations`: 9/0.
- kani 24/0; expected 208/0 (2 ignored) incl. all 4 immutable-descriptor-coalescing controls ok; ui 17/0; script 2/0.
- json: oracles ok, mode-boundaries ok, composition FAIL at isolated-ordinary_ensures_legal compare/binding (same stop point as S1 drift; not re-classified).

Baseline 69b13711e + baseline-controls.patch (tree 208e5f1945) + CI-only ac5613f652, run 43603880264:
- expected immutable-descriptor-coalescing: **4/4 ok** on the old code.

=> The four real-source controls are NONDISCRIMINATING: the old registry does not hit the fatal on these programs.
   F5 as a real-source failure is not reproduced; only the unit-level register() matrix shows the behaviour change.
