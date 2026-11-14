# Independent static review — C2-S1

Candidate: `ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c`  
Tree: `0fe7f51c1017656ae141f7d223ac737a930d7265`  
Parent/B1: `6fe484b30043b3696b5f1ccc4bea0e42891ad012`  
Upstream U: `0aac16ef62da9e9d5645782d458593e5d78143ba`  
Accepted C1b: `3f2c12f46e9e32899e8d84e89c65cb6483ba685a`

## Findings

No actionable S1 integration defect found in the inspected source and fixture diffs.

- `uninit_visitor.rs` removes `AtomicStore` from the check-only arm. Its explicit arm checks operand 0 only when the volatile const argument is false, then emits `Set { value: true, position: After }` in both cases (lines 591–608). This matches the #5115 behavior.
- Source-body access sites in the integration use `checked_body`: the immutable allocation collector, points-to call resolver, delayed target/entry analysis, and `BodyTransformation::body_ref`. Delayed analysis separately builds immutable overrides from `transformer.body_ref`; registration overrides retain the `RunContract` trampoline and origin, while discarded closures retain their unreachable selected body (`delayed_ub/mod.rs:98–123, 140–145`). Points-to recursion prefers those selected snapshots over source MIR (`points_to_analysis.rs:617–630`).
- Cycle handling is per entry root: `run_points_to_analysis` creates a fresh `ActiveCalls`, nested analyses latch an error, stop adding effects, unwind as `Err`, and failed child/root results are not joined (`points_to_analysis.rs:211–231, 275–279, 694–709`; `delayed_ub/mod.rs:125–150`). The failed root receives an Unsupported check after ordinary instrumentation (`delayed_ub/mod.rs:195–213`).
- The rejected-call visitor invokes `super_terminator` before resolver failure, so already collected operand checks/loads remain ahead of the Unsupported operation (`uninit_visitor.rs:509–517`). The B1 plain/seeded fixture pairs remain present; the integration adjusts the affected entry fixtures to use runtime symbolic union bytes and adds Item-return controls.
- The candidate retains the upstream `macos-15` platform matrix. `scripts/validate_json_export.py` and every `tests/json-handler` file tracked by U have Git blobs identical to U in the candidate. The three accepted C1b JSON-handler suites are additional carried files; they are not changes to upstream #5154 files. The #5093 saturating-helper change is present in the upstream base and was not reverted by the integration.

## Limits / status

Review was static only. No compiler, formatter, tests, Kani, CBMC, Miri, or CI was run; all such results remain **NOT_RUN**. Rust type checking and runtime semantics therefore remain unverified. The review packet’s `candidate.diff`, `integration.diff`, and `changed-paths.txt` SHA-256 values match its metadata; the spec hash matches `1965568203eba0ae88925a13d0fde26c3429ba402b099efb9f9df281919cf336`. The packet generator’s size/baseline limitation remains applicable; this is not automated packet-check or proof credit.

S1 CI request remains outstanding: fmt/build/clippy; targeted Uninit, expected, UI, and script checks; AtomicStore/volatile and explicit-tail-call controls; B1 plain/seeded pending-operation controls; contract override/cycle controls; then Linux Quick with the existing heavy 12-bit fixture settings. F5–F8 repairs were not reviewed or performed.
