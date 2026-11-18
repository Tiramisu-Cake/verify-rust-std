# Exact protected comparison and cause

Frozen control `fc29b93b1e333b73e55e2872701c80d9927f3b02`, executed trigger `d92581141b86e0f3b695cb37acc15c265478c9b4`: identical tree `c0368fa64ab474e4f64861aedd75a8f2639b1c29` and sole parent `9e14e033f9ee31522b571c127609dcdff76d230b`. Request/workflow/all payload bytes match. [SOURCE-TRACE.json](SOURCE-TRACE.json) preserves bounded frozen-source spans; [BEFORE-DIFF.json](BEFORE-DIFF.json) contains exact observations, member hashes, JSON pointers and the complete five-observation comparison matrix.

| Binary key | Controller E0/E1.pre/E1.post path | Worker BEFORE/AFTER path | Recorded SHA-256 at all five observations |
|---|---|---|---|
| kani_driver | `tool/target/kani/bin/kani-driver` | `/home/runner/work/kani/kani/tool/target/kani/bin/kani-driver` | `bdff28100fff3b02fc990f7c2d09f9a0edce60fef6d42770a7677e214fcf7846` |
| kani_compiler | `tool/target/kani/bin/kani-compiler` | `/home/runner/work/kani/kani/tool/target/kani/bin/kani-compiler` | `0d42d7487985595ffc608a11a4bea15e158c8eff49c80e1779612f8b1a89c3a4` |
| cbmc | `/usr/bin/cbmc` | `/usr/bin/cbmc` | `a62af25d27425610608221d79c202f993efe1d5a85cece186119bec196382995` |

Both mismatched entries differ **only in `path`**. The guard does not identify a first binary: it compares whole dictionaries. Each snapshot self-comparison succeeds; controller E0/pre/post comparisons succeed; worker BEFORE/AFTER comparison succeeds; every cross controller/worker comparison fails. All five snapshots: required_hashes_present=true, missing_binaries=[], snapshot_completed=true, state=COMPLETE; reported_versions is **present null**, error is **absent**. BEFORE_CHILD versus AFTER_CHILD_SHUTDOWN is outside the compared binaries dictionary and is not the failing field.

Exact observed coordinates inside the verified compact member:

| Observation | Structured member | JSON pointer | Epoch/time |
|---|---|---|---|
| E0 | baseline.json | /binaries | E0 /571.720877061 |
| E1.pre | workers/checker_order_corrupt-lifecycle.json | /pre/binaries | E1.pre /571.946974528 |
| worker BEFORE | groups/s3-checker_order_corrupt/receipt.json | /tool_fingerprints_before | BEFORE_CHILD; separate capture timestamp absent |
| worker AFTER | groups/s3-checker_order_corrupt/receipt.json | /tool_fingerprints_after | AFTER_CHILD_SHUTDOWN; separate capture timestamp absent |
| E1.post | workers/checker_order_corrupt-lifecycle.json | /post/binaries | E1.post /612.842397622 |

The source and authentic record establish the representation chain. Workflow lines93–94 invokes campaign with `--tool tool`. `s3_campaign.run_campaign` preserves that relative tool for controller capture (lines265–298); `s3_snapshots.capture` calls `runner.snapshot_binaries` (lines9–24). `runner.binary_fingerprints` serializes `str(tool / fixed_suffix)` without resolving (lines902–921). Worker invocation explicitly passes `str(tool.resolve())` (`s3_campaign.py:258–263`); worker forwards that absolute argument to `runner._run_group`, which captures BEFORE at `runner.py:1102` and AFTER at1156. The artifact confirms the resulting strings; no installer or filesystem mutation is needed to explain the rejection.

After worker shutdown, `root_outcome` first validates the controller pair, then calls `s3_evidence.protected` (`s3_campaign.py:171–191`). `protected` line48 calls `fingerprints_match(baseline['binaries'], snap)` for BEFORE. `runner.fingerprints_match` validates shape and then returns `before['binaries'] == after['binaries']` (line965). The two path strings make that expression false. It raises **recorded worker binary drift: before**, wrapped as the exact campaign GlobalFailure. This is a proven reader-rejection mechanism, not proof of actual byte drift or independently proven physical path equivalence.

R14-02 changed the comparison scope. On precursor `1dfc267b66abd83d536eb41a17052a4f3d767d2b`, the local finalizer checked COMPLETE workers' request/source, internal binary_identity MATCH and snapshot_errors; it did not compare worker binaries to controller E0 there, and non-COMPLETE handling could bypass observed worker faults. fc29 adds shared all-state protected validation, self-shape validation, direct E0-versus-worker BEFORE and AFTER comparisons, strict recorded-error rejection, and only verified-interruption recovery for genuinely absent AFTER. Portable sealed-root replay calls the same reader. The added cross-observer check exposes a path representation difference that internal worker MATCH cannot detect. `fingerprints_match` itself is unchanged between1dfc andfc29. R14-01's request-derived compile/source provenance passes separately on the authentic artifact.

The relevant mocks omit this shape: `test_s3.py:40–49` returns fixed `/tool/<name>` entries for both controller and worker regardless of input tool path; campaign fixtures use that same binary() for BEFORE/AFTER; SingletonRunnerTests replaces binary_fingerprints, and PortableReplayTests replaces both binary_fingerprints and controller capture. R14-02 tests vary states/errors/absence but retain those identical fixture paths. They exercise writers and guards without exercising relative controller input versus resolved subprocess input. This is the bounded coverage gap; no general compiler audit was performed.

Setup/build receipt has no fingerprints: E0 is the first recorded post-build inventory. Binary size, requested-versus-resolved realpath, readlink/symlink target, inode/device/mtime and independent stat/existence records are absent at every snapshot; they are UNKNOWN, never null measurements. No recorded hash changed; unobserved intermediate bytes and physical object identity remain UNKNOWN. Existing snapshot error fields are absent, not cleared errors. No missing evidence prevents reproducing the exact guard failure. Any stronger physical-identity claim would require a bounded record from the original run containing those measurements; the compact artifact cannot recover measurements never emitted.

No proposed repair is applied. The diagnostic counterfactual in PREFIX-REPLAY changes only path strings in an in-memory copy to isolate this expression; it is not a valid same-file admission or a recommended repair.
