# S3 coordinator request — preparation only

This package grants no dispatch, phase, budget, publication or CI authority.
Exact identities are in INPUTS.json. The worker ran only Git/static checks and
the explicitly allowed rustfmt wrapper. Independent static review is recorded
in REVIEW.md; compile/borrow checking and proof remain NOT_RUN.

1. Apply baseline-tests.patch to exact bf8170b28afb682f8dd55a94199caa247736d8fa;
   verify expected-baseline-tree.txt and all fixture hashes. Run the two negative
   selectors separately. Each must reach its intended read and give false
   VERIFICATION SUCCESSFUL, causing its expected-negative selector to fail.
   Any genuine baseline failure/Unsupported/setup error/UNKNOWN is not credit;
   report NONDISCRIMINATING or UNREPRODUCED and return a bounded revised request.
2. Existing preflight, fmt/build/compiler/typecheck and clippy for the candidate.
   Correct setup errors before retry. Run the two identical negative selectors
   and the reinit companion; verify intended failures with exact source binding,
   failure counts/descriptions and no other Unsupported/frame/validity failure.
   Do not accept only substring FAILED. No cover summaries in the new oracles.
3. Capture actual consumed MIR bindings requested in BASELINE-CANDIDATE.md.
   Review direct bodyful, hook, intrinsic black_box, shim/foreign and resolver
   refusal coverage from RESET-COVERAGE-MAP.md. If any accepted F6 transfer route
   remains unhandled, stop; no docs narrowing. Run reached source/destination
   reset checks with Move, Copy and alias/projection order as applicable.
4. Preserve existing top-level controls: maybe-uninit-call-move,
   maybe-uninit-call-pairing[-unsupported], maybe-uninit-argument-return,
   maybe-uninit-typed-return-padding, part1-composition/move-return-top-level
   and move-return-reinit, transfer-qualification/normal-abort and legal-pair,
   unresolved-calls, ordinary-slots, closure-upvars, cycle, PFC/contract roots,
   and all accepted immutable controls including S2 coalescing fixtures/units.
   Known tuple legal remains a known false positive, not UB detection credit.
   Any change in its failure count requires source review, never auto-blessing.
5. Remaining accepted Quick: kani Uninit/Quantifiers/TailCall; expected
   uninit/quantifier-capture/arbitrary; ui quantifier-safety-checks/
   explicit-tail-calls*; script-based-pre mem-init-reinstrumentation/
   autoharness_explicit_tail_call; JSON contract-oracles and mode-boundaries;
   required trailing stages. Preserve each fixture's flags, including its own
   object-bits12 and normal checks. No blanket check disabling or global override.
6. Run unchanged composition JSON and retain original exit/outcome separately.
   Known S1 isolated ordinary_ensures_legal drift remains S5 debt (c2-s1/DRIFT.md),
   not an all-PASS Quick. No roots/checker/allowlist change or suite removal.
   New lost checks, payload/status changes or unexplained inventory drift stop
   admission; the narrow known-debt classification is not a blanket waiver.

After terminal authorized execution use the established evidence interface.
Report all NOT_RUN/UNKNOWN and keep source reports distinct from independent
credit. Only two distinguishing pairs plus source coverage review authorize
the later narrow docs change. This preparation does not accept S3 or start S4/S5.
