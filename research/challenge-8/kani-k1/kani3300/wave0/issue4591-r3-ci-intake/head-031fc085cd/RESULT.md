# #4591 r3 terminal CI intake

READY — **PARTIAL_INFRASTRUCTURE**, with infrastructure cause attributed to the coordinator. Native Kani remains **FAILURE**. Independent failure causality is **UNKNOWN**.

Exact fork head `031fc085cd4373b5fc93a55128d5a69fdbd88df1`, tree `2ff34bc99ec3fe63579202c196f0ca288e318919`, sole parent `6fca00af805b5c62b58e3e3f29eef183d6939907`; retained base `969f4648980a8e66cd0ca32fd3e714a55ac32cef`. All runs are `push`, attempt1, branch `fix/stub-contracted-function`.

| Run | Native result | Jobs |
| --- | --- | --- |
| Kani CI [44461123962](https://github.com/Tiramisu-Cake/kani/actions/runs/44461123962) | FAILURE | 9 |
| Kani Format Check [44461124056](https://github.com/Tiramisu-Cake/kani/actions/runs/44461124056) | SUCCESS | 2 |
| Cargo Deny [44461124017](https://github.com/Tiramisu-Cake/kani/actions/runs/44461124017) | SUCCESS | 1 |

| Native job | Job ID | Conclusion |
| --- | --- | --- |
| llbc-regression | 135347865774 | SUCCESS |
| benchcomp-tests | 135347865966 | SUCCESS |
| regression (ubuntu-24.04-arm) | 135347866005 | SUCCESS |
| regression (ubuntu-24.04) | 135347866072 | SUCCESS |
| regression (macos-15) | 135347866084 | SUCCESS |
| documentation | 135347866089 | SUCCESS |
| regression (macos-15-intel) | 135347866153 | SUCCESS |
| regression (ubuntu-22.04) | 135347866217 | SUCCESS |
| perf | 135347866235 | FAILURE |
| format-check | 135347865898 | SUCCESS |
| clippy-check | 135347866525 | SUCCESS |
| audit | 135347866002 | SUCCESS |

All12 jobs completed on the exact head: 11 SUCCESS and1 FAILURE. Every expected workflow step is present. All runners are assigned; no native job cancellation, skipped job, omitted matrix instance or later run attempt is exposed. The all-attempt job queries return9/2/1 jobs, exactly matching native totals. Full step timestamps, statuses, runner assignments and identities are preserved in CONNECTED-METADATA.json.

The sole failed step is perf job135347866235 step4, `Execute Kani performance tests`. The coordinator reports `runner has received a shutdown signal` during `s2n-quic-core` and attributes it to infrastructure. Both diagnostic and phase remain **COORDINATOR_REPORTED**. The allowed connected check-run summary endpoint is unavailable (HTTP400 INVALID_ARGUMENT), so independent shutdown evidence and causality remain UNKNOWN. No unrelated native failure is exposed, supporting the attributed PARTIAL_INFRASTRUCTURE classification; this does not establish a fully verified infrastructure cause, waive perf or change the native aggregate.

Perf uses the unchanged retry action, max2 attempts,180-minute action timeout and380-minute job timeout. Actual internal retry count is UNKNOWN. Native run attempt1 does not establish the number of action-internal attempts. `Post Checkout Kani` is skipped on perf; `Complete job` is success and does not override its failure. Documentation build succeeds; `Publish Documentation` is skipped under the stock main-branch condition. The C-format step retains `continue-on-error:true` and native conclusion SUCCESS; no separate underlying outcome is exposed. All other step conclusions are SUCCESS.

Historical6f run44399789701/perf135139352074 is SUCCESS in the root-confirmed connected seed. The current delta changes only two regression files; neither fact validates current031 perf, excludes all possible functional causes, establishes a speedup or provides a waiver.

All38 reviewed source-oracle declarations and attributes match exact final source bytes:24 verification-success expectations,11 verification-failure expectations,1 caller-overflow expectation,1 overlap compile-error expectation and1 expected-panic postcondition case. Native summaries expose the five successful `Execute Kani regression` steps. Individual compiletest suites, files, harnesses, properties, exact checkout bytes and actual compiler/MIR/property-input bindings are **UNKNOWN**. Source discovery and script-level success are distinguished in oracle-coverage.json/md. No missing named result is relabeled NOT_RUN.

Both repairs statically select and call replacement_caller once, with nested provider contracts predicted in Assert mode. The negative input1 satisfies the caller identity post while violating the replacement ensures0. These are reviewed source predictions, with no newly observed named diagnostic. The verbatim issue4591 reproducer expects successful compilation followed by an i32MAX+1 caller-overflow counterexample. The unchanged overlap control expects a compile error. Neither expected failure is a verifier PASS. The removed mixed-alias provider-PFC arrangement receives no new coverage credit.

Static checks passed: reviewed final-head gate MATCH; full969f..031 range exactly6f then031; same-tree sibling of reviewedf829; exact2-testfile delta; all36 selected source/workflow/discovery pins; all16 workflow bytes; stock workflow YAML against reviewed inventory; all38 declarations and attributes;14 input references against their pinned commits; refreshed native summaries against the terminal seed. Compiler/driver trees match6f; workflows/actions/scripts/library match969f and6f. These checks provide source/metadata consistency, not formal verification credit.

The old faff main MRE remains historical INCONCLUSIVE/observed error per the pinned task. Previous6f failed the single-call fixture guard, with later suites unrun per coordinator history. No native969f/c25 compile/MIR/property fail/fixed-pass pairing is established. The dispatch-time c25 drift has no changed-path overlap; retain969f base. Release/std/label-gated benchmarks/metadata remain DEFERRED_TO_UPSTREAM_PR.

PR text belongs to the coordinator. This intake contains no PR-DRAFT/style rewrite or external-file write. No source fix, CI/rerun/cancel, push, publication, ledger/accounting operation, raw/full logs, archive, ZIP or GCS access occurred. Only root checking and coordinator factual handoff follow.
