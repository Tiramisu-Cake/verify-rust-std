# Issue5206 codegen_cache — one diagnostic retry

**ROOT AGREE** to exactly one coordinator `--failed` rerun of `Tiramisu-Cake/kani` run **44616139446**, prospective **attempt2**, unchanged head `a65ffdbdccfe5c3620b50c416870f1085a987d30`, tree `3b62ab0119dd49d6ef0dac37774fd4664e6b2535`, parent `0997d11c14cb2da0824efc34e2c4001e53ac0faf`, ref `fix/stub-contract-target-conflict-v2`.

```sh
gh run rerun 44616139446 --failed --repo Tiramisu-Cake/kani
```

Native attempt1 is completed FAILURE: only regression ubuntu22 failed; ubuntu24,ubuntu24-arm,macos15-intel,macos15 were CANCELLED. Docs/perf/LLBC/benchcomp succeeded. Separate Format and Deny succeeded. The requested scope is those five regression instances; do not request fresh successful jobs or separate workflows. GitHub-carried-forward results must keep their original execution timestamps.

Immediately before dispatch, require native latest attempt1 still terminal on this exact head/ref/workflow, the same failed/cancelled set, unchanged source/ref, and no existing attempt2. Coordinator records the ledger row and dispatches once; root does neither. If attempt2 already exists, inspect it instead of rerunning again. Actual new job IDs remain UNKNOWN until dispatch.

The coordinator reports missing `***CACHE STATS***` from codegen_cache despite fixture exit0. Root verified exact fixture/cache/toolchain/workflow Git-object equality with main0997 and comparison cea. Source also shows stats instrumentation is conditional on `debug_assertions`, and printing occurs in TLS cache Drop with CACHE_STATS present. These facts support a bounded diagnostic retry; **they do not prove a flake or establish TLS timing as the cause**. No raw logs or local fixture/compiler execution were used. Individual suite counts and prior per-test pass are coordinator-reported.

No source/test/oracle/environment/profile/flag/cap change, ignored test or relaxed threshold. **No third attempt or automatic retry.** If codegen_cache fails again, assign a bounded worker investigation: compiler binary/build profile/debug_assertions, env propagation, cache initialization/use, TLS-owner termination and output capture, with controlled main/fix comparison as separately authorized. A different failure also needs a new decision. A successful retry does not retroactively establish the first failure's cause.

Attempt1 FAILURE and all CANCELLED records remain immutable in ATTEMPT-1-NATIVE.json; use attempt-specific endpoints for both attempts. Native suite success is distinct from named-harness/property evidence. PR publication/comments remain owner-command only. Ledger accounting belongs to the coordinator; no root reservation/charge/refund/grant or new source changes.
