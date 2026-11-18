# Full standard CI request — prepared, not authorized

Candidate source `cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, base
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.

Gates in sequence: committed exact READY_FOR_DELTA_REVIEW14 → same independent reviewer14
approves this plan-only delta and closes F4-R14-1 →
owner's explicit publication command → separate coordinator/owner full-CI GO with budget and
accounting. A GO for this preparation authorizes none of publication, CI or accounting.
Item1 reference remains 27/28, prospective final attempt 28/28; S2 remains ledger4076 unchanged.
No slot or attempt is reserved or consumed here.

Publish the reviewed standalone source to the owner's fork for a future upstream PR against
`model-checking/kani:main`, only on owner command. Read-only recheck upstream main immediately
before publication. The immutable old MAIN-CHECK.json records upstream equal to frozen main at preparation;
the fork's own older main is recorded separately and is an ancestor, not the chosen PR base.
Relevant upstream drift requires explicit handoff; never silently rebase the reviewed source.
All 16 standard workflow blobs must remain byte-identical to the chosen frozen base.

The required source commit has `[skip ci]`. A future authorized publication/CI stage must bind
a same-tree trigger commit without that skip directive to the reviewed source and record both
SHAs/tree plus PR/run/attempt identities. Creating that trigger is outside this stage. Preserve
all standard workflows; add no confirmation-only workflow or custom reduced job matrix.

This delta replaces only the old CI request. Unchanged source patch, regression oracle,
lifecycle/performance assessment, MAIN-CHECK and unpublished PR-DRAFT remain immutable in
package `7485bbb27a72dd463d4a9628c8627689d30e7e56` at `kani3300/wave0/f4-fix/`.

## Required standard PR checks

- `kani.yml`: the complete five-OS regression matrix (macos-15-intel, ubuntu-22.04,
  ubuntu-24.04, macos-15, ubuntu-24.04-arm); benchcomp-tests; full perf; llbc-regression;
  documentation. Regression already includes format/build/unit and all standard suites,
  including script-based-pre where the new test runs. Preserve normal timeouts and retries.
- `format-check.yml`: format-check and clippy-check, with their complete standard steps.
- `deny.yml`: standard Cargo Deny audit.
- `verify-std-check.yml`: both Ubuntu/macOS matrix entries and standard base/head comparison.
  Report baseline or toolchain limitations explicitly rather than relabel a failure as PASS.
- `extra_jobs.yml`: standard auto-label behavior. `bench-pr.yml` has compiler and end-to-end
  benchmark jobs selected by the two Z-*BenchCI labels; both labels apply to this compiler diff
  in `.github/labeler.yml`. Have the authorized owner ensure both jobs actually run through the
  standard label/event path. Automatically added labels alone may not trigger a new run;
  preserve and account for standard event behavior without extra unapproved attempts.

Scheduled, updater and slow-test-only workflows remain present with their native triggers;
they are outside applicable PR checks. Release bundle PR jobs below are required.
Full PR CI means every applicable standard PR check,
including standard conditional benchmark jobs, rather than a hand-picked fast suite.

## Required release.yml PR coverage — 14 instances

Native triggers: pull_request, merge_group, push to main or kani-* tags. Exact job IDs
and matrix values below come from source cab66681; display names are not job IDs.

| Required build job ID | runs-on | platform |
| --- | --- | --- |
| `build_bundle_macos_x86_64` | `macos-15-intel` | `x86_64-apple-darwin` |
| `build_bundle_macos_aarch64` | `macos-15` | `aarch64-apple-darwin` |
| `build_bundle_linux_x86_64` | `ubuntu-22.04` | `x86_64-unknown-linux-gnu` |
| `build_bundle_linux_aarch64` | `ubuntu-24.04-arm` | `aarch64-unknown-linux-gnu` |

Both test jobs need all four builds, preserving native artifact/target routing:

| Required test job ID | Complete matrix.os (five instances each) |
| --- | --- |
| `test-use-local-toolchain` | `macos-15-intel`, `macos-15`, `ubuntu-22.04`, `ubuntu-24.04`, `ubuntu-24.04-arm` |
| `test_bundle` | `macos-15-intel`, `macos-15`, `ubuntu-22.04`, `ubuntu-24.04`, `ubuntu-24.04-arm` |

Four builds + five test_bundle + five test-use-local-toolchain = **14 required PR
build/test instances**. CI-REQUEST.json retains complete matrix include entries,
needs, platform mapping and an explicit 14-instance inventory.

Only `kani_release` has `${{ github.event_name == 'push' && startsWith(github.ref, 'refs/tags/kani-') }}`;
`package_docker` depends on `kani_release`. These two
publication jobs intentionally skip on PR. Their skips do not excuse bundle checks.

## Operational gates for the separate full-CI GO request

- **binding**: Record reviewed source SHA/tree, same-tree trigger SHA/tree, exact final PR branch HEAD SHA/tree, PR number/ref/base SHA/tree, native event, workflow/run/attempt IDs, every required job/matrix and native conclusion. Final PR branch HEAD must be the authorized same-tree trigger with tree 8585336ed35a14fe0fc157a7ca4e0d52075c0e49; a newer HEAD requires rechecking exact candidate/run binding.
- **checkout**: Record actual checkout SHA/tree separately from PR branch HEAD and run head SHA. PR actions/checkout normally uses synthetic merge ref. With unchanged frozen base require merge tree equal reviewed/trigger tree; any delta requires review. Bench reusable jobs explicitly checkout PR head.sha and base.sha; authorized branch-push jobs must checkout exact trigger HEAD. Old confirmation ref gives no candidate evidence.
- **labels_and_event**: Both Z-EndToEndBenchCI and Z-CompilerBenchCI match kani-compiler/**. Owner must establish both labels before an eligible opened/synchronize/reopened/labeled event; GITHUB_TOKEN auto-labeling does not retrigger bench-pr and opening can race labels. Owner chooses authorized choreography/accounting. No label/event action here.
- **benchmarks**: Require end-to-end-bench -> perf-benchcomp and compiler-bench -> compile-timer-short, compile-timer-long on final head versus base. Preserve concurrency cancellations; missing/skipped/cancelled required benchmarks prevent acceptance. Assess warmed-cache clone time/RSS cost; regression requires concrete handoff.
- **native_triggers**: None of the seven applicable workflows has workflow_dispatch. Feature-branch push alone omits full PR std/benchmark/release-bundle coverage. Keep all native triggers, conditions, timeouts, retries and continue-on-error behavior unchanged.
- **native_outcomes**: Retain every applicable matrix conclusion. Missing, skipped, cancelled or red required jobs prevent full-CI acceptance. verify-std head failure remains failure even if conditional base comparison succeeds. extra_jobs auto-label uses trusted base and supplies no candidate build evidence. Documentation publishing skips outside push to main.
- **publication**: Independent reviewer14 approves exact committed plan delta and closes F4-R14-1; owner publication command and separate coordinator full-standard-CI GO/accounting still required. Owner rechecks upstream main; relevant drift requires explicit handoff. Update the future publication copy of old PR-DRAFT Testing only after actual execution, with actual results and at most one full-CI link.
- **scope**: No CI/rerun/cancel/push/PR/publication/labels/events/reservation/ledger/local compiler/verifier/full runner. Item1 remains reference 27/28; last 28/28 unspent. S2r1 GO awaits owner and is outside scope.

The reviewed source subject contains [skip ci]. A separate authorized same-tree
trigger without skip text is necessary. Check skip directives in final PR branch
HEAD and every commit in the pushed range; a non-skipping child alone does not
establish a push run. Record all identities in future_run_binding before credit;
its current NOT_CREATED_OR_RECORDED values authorize no execution.

The seven workflows are kani.yml, format-check.yml, deny.yml, verify-std-check.yml,
extra_jobs.yml, bench-pr.yml and release.yml. All 16 workflow blobs and scripts
remain frozen. No workflow_dispatch or feature-push substitute establishes full PR CI.

## Regression acceptance and evidence

The archived frozen-main results must continue to fail the new oracle as described in
[REGRESSION-ORACLE.md](../f4-fix/REGRESSION-ORACLE.md); fixed execution must pass that oracle, with initialized singleton/paired
SUCCESS, equal semantic inventories, delayed shared-read FAILURE and independent unsafe
FAILURE for both cfg variants. Record any future new-test main execution separately from the
already observed baseline data. Counts are observations; compilation order remains UNKNOWN.
A failed setup/build/test parser is a distinct failure, never an accepted defect reproduction.

Capture exact reviewed source/trigger/PR head/base/tree, all applicable workflow job matrix
identities, native conclusions and new regression outcome through the authorized reporting
interface. Preserve failures/skips/cancellations; missing expected jobs leave full CI incomplete.
Measure or use the standard perf/compiler benchmarks to assess added clone cost; a red or
missing benchmark requires a concrete handoff. No raw/full-log bypass.

This package requests a complete future standard run; actual new compiler/regression/full CI
results are NOT_RUN. The future publication copy of PR-DRAFT.md's Testing paragraph must
be updated after that run with its
actual conclusion and at most one full standard CI run link before an upstream-ready claim.
No PASS wording or link is fabricated now.
