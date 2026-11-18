# Prepared full native push-CI request

PREPARED_NOT_AUTHORIZED. Reviewed candidate `ca1452227d6ad319f1b9bc1ad33bf618120733eb`, tree `baedd51d92073ecb2b96991bae7dc562ee8f58a2`,
parent `b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`. Compiler and native two-mode/runtime/performance NOT_RUN.

## Identity and publication gate

Independent14 reviews this exact source/tree and package first. Root then prepares
the exact GO-request for one full push-CI bundle, prospective item1 29/29. Owner's
choice A/+1 grants cap29; it supplies no dispatch permission to this task.
Current accounting reference: item1 28/29, item2 provisional10/14, total38/43;
r1S2 accounting and publication remain owner-only. No attempt consumed here.

After review+GO, owner/coordinator creates a new commit using reviewed tree `baedd51d92073ecb2b96991bae7dc562ee8f58a2`
and direct parent `b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`, with a message free of skip directives. It is a sibling
of local skipped candidate `ca1452227d6ad319f1b9bc1ad33bf618120733eb`, never its descendant. Publish only the new
sibling. Never push the skipped candidate or include it in the pushed b5..HEAD
range. No trigger/head is created by this task.

Before publication, run this read-only check against the owner-created full SHA:
`python3 check_push_head.py /root/kani-f4-uninit-only-w15 FUTURE_FINAL_FULL_SHA`.
It checks candidate binding, final tree, exact single parent, entire b5..HEAD
range and skip directives in every range commit. Passing it grants no GO.
Record final SHA/tree/parent, remote head, ref, native push event, run/attempt IDs
and actual checkout identity separately. Any tree change requires review.

## One complete native push bundle

Use the unchanged native branch-push triggers of kani.yml, format-check.yml and
deny.yml on the exact new final head. All native jobs/matrices run under their
original conditions, timeouts, retries and continue-on-error behavior.

| Workflow | Full required native scope |
| --- | --- |
| kani.yml | regression: macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15, ubuntu-24.04-arm; benchcomp-tests; perf; llbc-regression; documentation |
| format-check.yml | format-check (copyright/C/Python) and clippy-check (both native invocations/statistics) |
| deny.yml | audit, frozen cargo-deny action/arguments |

Retain normal macOS entries, including arm64 macos-15. The previous missing runner
is old-head evidence. Regression preserves native fail-fast. Perf retains the
380-minute job timeout, retry@v4 timeout180/max_attempts2 and RUST_TEST_THREADS=1;
these are existing workflow settings, not a new rerun authorization. C formatting
retains continue-on-error=true; Deny retains native failure behavior. Candidate
branch documentation builds; publication obeys the frozen main-only condition.
All16 workflow files, actions, scripts, libraries, dependencies and toolchain
remain byte-identical; SOURCE-PINS.json records every workflow SHA256.

The named regression runs under each normal regression job through the unchanged
compiletest route. Its check.py covers both uninit modes, both cfg call paths,
singleton/paired composition and independent controls with exact features and
normal checks. Preserve actual native evidence, errors, timeouts and NOT_RUN;
old suite-level success supplies no execution result for this revision. Measure
performance only if the new native run supplies measurements; current cost is
UNKNOWN, and enabled copies may recompute bodies discovered after prewarming or
when ordering is disabled.

## Native results and deferred PR work

Retain all required job/matrix conclusions and actual checkout identities when
available. Missing, skipped, cancelled or red required jobs prevent an all-green
or full-matrix PASS claim. Attribute infrastructure failures/external advisories
precisely; an exception or rerun requires owner decision. Keep native Deny FAILURE
separate from its advisory classification. Old kani44274306776 belongs to b5:
8SUCCESS, macos-15 NO_RUNNER/NOT_RUN; FormatSUCCESS, DenyEXTERNAL_ADVISORY.
Owner's old-macOS NO_RERUN remains in effect. No all-green/five-OS claim follows.

Release bundle PR builds/test matrices, verify-std-check, and label-gated
bench-pr comparisons remain deferred to upstream PR by owner. Preserve their
native events, matrix, concurrency and label requirements, including
Z-EndToEndBenchCI/Z-CompilerBenchCI. extra_jobs remains PR metadata. A fork push
covers only the push bundle; it does not complete those PR jobs.

No CI, rerun, cancel, push, PR, labels/events, ledger, reservation or budget action
is performed here. Root maintains the external PR draft independently.
