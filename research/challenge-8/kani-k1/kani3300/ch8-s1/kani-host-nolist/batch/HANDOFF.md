# Reviewed grouped S1 control — preparation only

Control `40b5d9cf48900ff1e227e1fbba24cb5b2edbf8d5`, tree `c17af287534589256ea5db86a60763e2832a88f3`, branch `uninit-ci/ch8-s1k-batch-w13`, worktree `/root/kani-ch8-s1k-batch-w13`. Sole parent stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`. S′ `f22f84f316ad8ef6f3fccce86424bad927b09f78` / tree `e0dc89592926571e823797f8618cd6b4a7e11ff6` unchanged. This supersedes per-row control `801c2634cee3f3f39cb20146a1080e016a59e048` under the coordinator's BATCH-NOTE supplement.

All23 row records/oracles/variants/source bindings stay frozen. Five groups retain variant/unwind flags: production34(15),production5(3),production4(3),activation-default34(1),activation-override34(1). Each group uses one `verify-std` invocation, repeated exact selectors, jobs1, harness-timeout600s and one export. Each row's binding and verdict come from its own uniquely named `harnesses[]` entry, independent of export order or group exit.

No global list or separate warm-up remains. Compile+project linking has a900s monitor and bounded receipt in the same process, ending at Kani's initial export marker. Group wall envelope is compile plus sum of row budgets, separately constrained by the unchanged4500s phase/120min job. A phase-cut group without a complete export stays UNKNOWN.

The group RSS cap is min(12GiB,available-2GiB), including finite root cgroup headroom. Samples and logs are explicitly group-scoped. **Per-root RSS remains UNKNOWN**, and no6GiB/root resource credit is asserted. Stock600s timeout covers CBMC processing; full instrumentation wall is not measured as a600s root cap. Export's prior resolved-target/AST binding limitations remain explicit in DESIGN.md.

28 synthetic tests, static exact row/argv/source/payload checks and YAML/actionlint pass. Independent Luna HIGH review: APPROVED_PREPARATION_ONLY, see REVIEW.md and VALIDATION.json. Actual Kani/std compilation/CBMC/proof were not run. All23 proof rows NOT_RUN; proof credit NONE. No push/CI/publication/ledger operations. A separate authorized coordinator stage is needed for publication/dispatch.
