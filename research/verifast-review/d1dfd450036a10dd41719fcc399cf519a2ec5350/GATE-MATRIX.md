# Standalone slice binding — results

All final results below belong to head095ef553e92deaae063b3684ea3172128e666785 / tree54e80209593942d1381283f71fa916c02fa4ac57, runner/auditor6c663c1d44bc679e0c43635ef5868cf41370141d, Build34c10f8c-c6f9-49b4-a75b-124755f5d219. Full original receipts/archive are retained in evidence/.

| Gate | Result | Evidence / boundary |
| --- | --- | --- |
| Clean-base missing binding | EXPECTED_REJECTION | baseline-missing-binding.stdout: line4 actual exact method has No such function. Baseline semantic src/bin diff against base checked empty before build. |
| Ordinary / empty / MaybeUninit actual calls | PASS | positive stdout: 0 errors,62 statements; positive.ast shows typed data-pointer casts and pointer identities; generated slice ownership/normal/unwind contracts preserved. Empty branch is symbolic and reachable. |
| No invented initialized-T authority | EXPECTED_VC_REJECTION | negative-diagnostic stdout: line8 initialized-u8 points_to missing, after actual as_mut_ptr and opening MU array. No translator/admission/setup refusal. |
| Upstream negative registration | PASS | make-test stdout exact POSIX case accepts only line8 heap-chunk error with EXIT:1; fixture has no should_fail directive or weakened flags. |
| Standard Linux make test, including Rust | PASS | make-test exit0;0 failed processes; elapsed418.76s. New Rust positive/negative appear as PASS in raw suite. Existing suite flags are unchanged. |
| Compiler/std correspondence | REVIEWED | fresh rustc/MIR/std receipts; rustc f7575a9da, slice source efe182d...; actual method self as *mut[T] as *mutT. Exact name/arity/type-first-substitution checks reuse existing as_ptr; no new full-body admission validator. |
| Isolated auditor/registration service tests | PASS (NOT proof) | synthetic data only, incomplete/early/setup failures rejected; source/hash bound receipts retained. |
| Other platforms / optional components | NOT_RUN / штатные skips | No Rocq coqc, Java AST server disabled, assignment models absent. Linux C/C++/Java tests included as configured; no broader platform acceptance. |
| Challenge8 proofs / MDnew integration | NOT_RUN / outside scope | Preserved toolI and ManuallyDrop candidates. No research patches in this net diff. |

First Build424fd00e remains Cloud FAILURE after marked-negative dead-code diagnostic; its positive62/baseline evidence and original raw status are preserved separately. Final proof is fresh, not a reclassification of the first failure.
