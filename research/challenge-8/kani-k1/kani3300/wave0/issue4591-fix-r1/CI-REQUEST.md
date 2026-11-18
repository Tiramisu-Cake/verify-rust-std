# One full standard push-CI bundle, prepared only

PREPARED_NOT_AUTHORIZED. `SOURCE-PINS.json` binds the skipped local candidate
and stock main. `CI-REQUEST.json` contains the exact native jobs and settings;
`WORKFLOW-INVENTORY.json` derives all workflow events, jobs, steps and matrices
from the actual pinned main. Native results, including fixed regression
results, are NOT_RUN.

The sequence is exact committed READY → same11 delta-review → root drift decision and exact
GO-request → separate usercoordinator full standard push-CI command. Owner's
+1 item1 grants preparation/capacity, not dispatch. Reference ledger
`df7a140991`: item1 30/31, item2 11/17, total41/48. A future authorized bundle
would reach item1 31/31 and total42/48; this task consumes zero attempts and
does not write accounting or reservations. PR publication needs an owner
command independently of CI preparation.

## Final publication head

After review and GO, the usercoordinator creates a new nonskip commit with
exactly the candidate tree and exactly stock main as its single parent.
It is a sibling of the local `[skip ci]` candidate. Its exact SHA is
NOT_CREATED and must be recorded before publication. The entire main..final
range must contain that single nonskip sibling; the skipped candidate must
remain outside the pushed range. Any tree or parent change requires renewed
review and GO binding. No final commit is created or pushed by this task.

Use the read-only gate on the owner-created final full SHA:

```text
python3 check_push_head.py /root/kani-issue4591-fix-r1-w15 FINAL_FULL_SHA
```

It checks the candidate tree/parent, final full SHA/tree/single parent, complete
range and skip directives in every range commit. A metadata match supplies no
authorization. Record the final head, remote branch head, event/ref, native
run IDs/attempts and actual checkout SHA/tree separately. A successful checkout
step alone is insufficient to infer the checked-out identity.

## Unchanged native branch-push scope

| Workflow | All native jobs / matrices |
| --- | --- |
| `kani.yml` | `regression` on macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15 and ubuntu-24.04-arm; `benchcomp-tests`; `perf`; `llbc-regression`; `documentation` |
| `format-check.yml` | `format-check`: copyright/C/Python checks; `clippy-check`: both native Clippy invocations and statistics |
| `deny.yml` | `audit`, unchanged cargo-deny action, arguments and native failure behavior |

All twelve native job instances belong to the single full standard push bundle
on the exact eventual PR branch head. Regression keeps native default fail-fast
and every OS entry. The added tests run through the stock `kani` and `expected`
compiletest suites in `scripts/kani-regression.sh`. They do not replace the full
regression suite. No custom research workflow, altered triggers, subset-only
bundle, disabled checks or cron enablement is included.

Perf retains its 380-minute job timeout, retry@v4 timeout180/max_attempts2 and
RUST_TEST_THREADS=1. C formatting keeps continue-on-error=true; Clippy statistics
keeps its native `|| true`; Deny retains its native conclusion. Documentation
builds on the branch; its publish step remains main-only. Every workflow,
action, script, library, toolchain and dependency file remains byte-identical
to pinned main; hashes and protected Git trees are in SOURCE-PINS.json.

Retain native SUCCESS/FAILURE/CANCELLED/SKIPPED/NOT_RUN and infrastructure or
advisory classifications separately. Missing, red or unexecuted required jobs
prevent an all-green/full-matrix claim. Any exception, retry beyond native
workflow behavior or rerun needs owner classification/command. No old run
supplies fixed-head credit. New named-regression evidence should be retained
when exposed; suite-level success must remain distinguishable. Runtime and
performance values remain UNKNOWN until measured by that native run.

## Deferred upstream PR scope

Following the owner's F4 scope, the native `release.yml` bundle build/test
jobs and matrices, `verify-std-check.yml` (ubuntu-22.04/macos-15), label-gated
`bench-pr.yml` comparisons and `extra_jobs.yml` metadata run on the upstream PR
under their unchanged events/conditions. They are not supplied by a fork PR or
this branch-push bundle. Release publication stays tag-only. Benchmark labels
Z-EndToEndBenchCI/Z-CompilerBenchCI, native concurrency and reusable workflows
remain unchanged. This task neither publishes a PR nor applies labels/events.

## Frozen-base drift gate

MAIN-CHECK.json observes upstream main
969f4648980a8e66cd0ca32fd3e714a55ac32cef instead of the required frozen parent
faffcee3bca2770c03bd21c3bde89cc8f6f7a14e. This package preserves the mandated
sole parent. Root/coordinator must resolve that drift before GO; the prepared
head gate checks frozen source/tree metadata only and grants no authorization.
The usercoordinator launches CI, and owner alone publishes PR/issues/comments.
