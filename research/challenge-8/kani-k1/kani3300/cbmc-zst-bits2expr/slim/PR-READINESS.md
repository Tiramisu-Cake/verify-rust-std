# Preparation complete; upstream readiness pending

The clean source contains one bug fix, one regression directory and three relocated unit cases. PR draft uses the exact BASE, final reproducer, template checklist verbatim, disclosure and the kani#5085 reference without a closing directive. Version/argv/verbatim invariant and both Testing sentences remain pending until one matched final baseline invocation and complete final CI. No older measurements are carried forward. No issue is prepared or published.

Required gate: baseline5/5 exact array invariant, fix5/5 profile PASS with one descriptor/no skips, Make4/4 and CMake4/4 exact cases with assertions, formatter18.1.8 empty diff, cpplint and diff checks. Any missing solver/build error/cap/signal/unrelated baseline failure/skip/empty selection stops the package; no profile exclusions or relaxed checks.

Separate Kani B3 handoff (code unchanged here): before a separate Kani PR, update codegen/typ.rs around1319–1324 at 6e9e782024 to say “CBMC's bits2expr constant reconstruction rejects zero-width array elements in this nonzero-width padded struct.” Retain rustc-layout/recursive-arm explanation. Keep the workaround and leave #5085 open; runtime Kani replay, release/pin updates and upstream actions are outside this task.

No compiler/build/verifier or final formatter was run locally. Preparation does not mean upstream-ready; push/CI and publication belong to the coordinator/owner.
