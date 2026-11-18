# Full standard CI request — prepared, not authorized

Candidate source `cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, base
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.

Gates in sequence: committed exact READY → independent review14 of source/package and
lifecycle/performance tradeoff → concrete findings resolved and candidate identity reviewed →
owner's explicit publication command → separate coordinator/owner full-CI GO with budget and
accounting. A GO for this preparation authorizes none of publication, CI or accounting.
Item1 reference remains 27/28, prospective final attempt 28/28; S2 remains ledger4076 unchanged.
No slot or attempt is reserved or consumed here.

Publish the reviewed standalone source to the owner's fork for a future upstream PR against
`model-checking/kani:main`, only on owner command. Read-only recheck upstream main immediately
before publication. MAIN-CHECK.json records upstream equal to frozen main at preparation;
the fork's own older main is recorded separately and is an ancestor, not the chosen PR base.
Relevant upstream drift requires explicit handoff; never silently rebase the reviewed source.
All 16 standard workflow blobs must remain byte-identical to the chosen frozen base.

The required source commit has `[skip ci]`. A future authorized publication/CI stage must bind
a same-tree trigger commit without that skip directive to the reviewed source and record both
SHAs/tree plus PR/run/attempt identities. Creating that trigger is outside this stage. Preserve
all standard workflows; add no confirmation-only workflow or custom reduced job matrix.

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

Scheduled, release and dependency-update workflows remain present with their native triggers;
this request does not dispatch them. Full PR CI means every applicable standard PR check,
including standard conditional benchmark jobs, rather than a hand-picked fast suite.

## Regression acceptance and evidence

The archived frozen-main results must continue to fail the new oracle as described in
REGRESSION-ORACLE.md; fixed execution must pass that oracle, with initialized singleton/paired
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
results are NOT_RUN. PR-DRAFT.md's Testing paragraph must be updated after that run with its
actual conclusion and at most one full standard CI run link before an upstream-ready claim.
No PASS wording or link is fabricated now.
