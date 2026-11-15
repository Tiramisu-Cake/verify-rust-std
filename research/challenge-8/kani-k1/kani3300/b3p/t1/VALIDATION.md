# B3 T1 preparation validation

2026-11-15. Kani candidate `1c9940c320f6a6e5c2c84f4068cb99a1c52ee64d`.
Direct parent `0aac16ef62da9e9d5645782d458593e5d78143ba`; all 22 changed paths
are under `.github/`. Six new files (five bundle files and one workflow), all
16 stock workflows removed. Kani source files and Cargo manifests are unchanged.
Author/committer: Tiramisu-Cake <igkharin@gmail.com>; no Co-Authored-By trailer.

Executed locally, without real compiler/verifier/model generation:

```text
python3 -m unittest discover \
  -s /root/verify-rust-std-kani3300-t0/research/challenge-8/kani-k1/kani3300/b3p/t1 \
  -p 'test_*.py'
Ran 24 tests — OK (9 capture/runner, 15 comparison).
```

Capture tests use temporary synthetic bytes/metadata and mocked subprocesses.
One test invokes only the Python capture shim through a temporary PATH symlink,
asserting exit 86 and SAT NOT_RUN. Comparison tests mock goto-instrument and use
GNU diff only on small synthetic text. Neither suite invokes Rust, Cargo, Kani,
CBMC, a solver, or a build. Cases include correct capture, exact harness binding,
partial/missing/null/wrong-type/duplicate evidence, wrong-source binding, original
nonzero exits and timeout exceptions, lock-path and exit validation, A/A precedence,
A/A dumps, metadata-only/insensitive control rejection, backend argv changes,
dump errors/timeouts and GNU diff errors/timeouts.

Static checks passed: Python AST parsing, YAML parsing, single job/ubuntu-24.04/
240-minute cap/always-upload, exactly one remaining workflow, reproducer bytes
equal B's `tests/expected/zst-union-arm/main.rs`, candidate parent A, and Git diff
whitespace checks. These are preparation checks, not an executed CI validation.

Independent static reviewer: Luna High, task `/root/runner_review`, separate
context, no nested delegation. Reviewed runner/shims against actual compiletest
and kani-driver sources, then comparator and final deltas. No confirmed blockers;
final delta approved. Reviewer independently reran capture 9/9 and comparison
15/15 Python tests. Concrete stale test call-count expectations introduced during
streaming-diff implementation were fixed by the comparator owner before final
validation. No unresolved review findings.

No local builds/toolchains, push, CI, PR, issue, dispatch, phase registration,
Cloud evidence download or historical ledger modification occurred. Future
CI results and mandatory positive-control wrapper review remain NOT_RUN/pending.
READY means the CI-only preparation is complete; it does not certify the models.
