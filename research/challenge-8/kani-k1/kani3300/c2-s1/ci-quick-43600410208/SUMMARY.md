# C2-S1 quick CI — run 43600410208 (ba0e5cfedf + CI-only workflow ddd242820b)

- Format check: FAIL — rustfmt wants `.unwrap_or_else(|| { crate::kani_middle::checked_body(tcx, instance).unwrap() })`
  split over 3 lines in `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs:140`.
- Build, clippy -D warnings: PASS.
- kani (Uninit, Quantifiers, TailCall): 24/0. expected (uninit, quantifier-capture, arbitrary): 204/0 (2 ignored).
  ui (quantifier-safety-checks, explicit-tail-calls*): 17/0. script-based-pre (mem-init-reinstrumentation,
  autoharness_explicit_tail_call): 2/0.
- json-handler: 2/1 — uninit-contract-oracles ok, uninit-contract-mode-boundaries ok,
  **uninit-part1-composition FAILED** at `isolated-ordinary_ensures_legal: compare/binding:
  Rejected: lost check, extra check, or status/identity drift`. isolated-immutable_hole_negative and
  isolated-immutable_legal passed binding before it. Oracle artifacts were not uploaded (paths absent).
- `ordinary_ensures_legal.regular.txt`: the full regular output of that isolated run, extracted from the job log.
