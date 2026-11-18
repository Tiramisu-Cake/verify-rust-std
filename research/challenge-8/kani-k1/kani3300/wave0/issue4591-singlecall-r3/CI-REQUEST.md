# Full standard push CI: prepared, held

HOLD_FOR_SAME11_THEN_OWNER_EXTRA_ITEM1_GRANT. CI-REQUEST.json binds the complete
native configuration to repair f82934ca97caaa1270d5279054aa950173868be5, tree
2ff34bc99ec3fe63579202c196f0ca288e318919, sole published6f parent. All16 workflow
definitions are freshly parsed from main969f in WORKFLOW-INVENTORY.json and
their bytes match main, published6f and candidate. All actions/scripts/library/
toolchain/dependency bytes remain unchanged. No F4 or custom workflow enters.

The next gate is SAME11 exact delta-APPROVE of this committed package and source
tree. Root then prepares a GO-request with status
HOLD_FOR_OWNER_EXTRA_ITEM1_GRANT. Item1 is31/31 EXHAUSTED. Only the owner's
explicit morning+1 can supply capacity; no repeat, refund, reservation, charge
or grant is made here. Item2 12/17 and total43/48 are task references, untouched.
Static review and a metadata gate do not authorize dispatch. A separate
authorized usercoordinator command is required after the owner grant and exact
GO/final-head gates. PR/issues/comments remain owner-only.

## Future final head and fast-forward

The future nonskip head has not been created. It must have exactly candidate
tree2ff34b and exactly published6f as sole parent. It is a sibling of the local
skipped repair, not its child. The full969f..final range must consist of exactly
the already-published nonskip6f followed by the new nonskip repair. No skipped
candidate belongs in that range. Normal branch advancement from6f is therefore
fast-forward; no force push or rebase is part of this request.

Use the read-only gate only after the actual final SHA exists:

```text
python3 -B check_push_head.py /root/kani-issue4591-singlecall-r3-w15 FINAL_FULL_SHA
```

Require exit0, MATCH and empty errors; record the actual SHA/tree/sole parent
and complete nonskip range. Metadata mocks provide no final-head receipt.
Recheck upstream main and actual remote branch immediately before any
separately authorized launch. Recorded read-only observations are main969f and
remote fix/stub-contracted-function=published6f. Drift returns to root;
no automatic rebase or open-PR branch update is authorized.

## Complete unchanged branch-push bundle

| Workflow | Required native jobs |
| --- | --- |
| kani.yml | regression on macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15, ubuntu-24.04-arm; benchcomp-tests; perf; llbc-regression; documentation |
| format-check.yml | format-check with copyright/C/Python checks; clippy-check with both native Clippy invocations and statistics |
| deny.yml | audit with unchanged cargo-deny action/arguments |

All12 job instances, native steps, conditions, matrices, timeout settings and
native retries are included. Regression retains native default fail-fast and
the stock scripts/kani-regression.sh route through all15 suites, plus native
build/unit-test and subsequent checks. The added fixtures participate in stock
kani/expected suites; targeted outcomes do not replace full matrix evidence.
Perf keeps timeout380min, retry timeout180/max_attempts2 and RUST_TEST_THREADS=1.
C formatting keeps its native continue-on-error and Clippy statistics its
native result handling. Documentation publication remains main-only. No
workflow_dispatch, cron enablement, custom research CI or subset launch is
requested. No outside automatic rerun is authorized.

## Receipts and deferred PR scope

Record native push event/ref, exact remote head, three workflow IDs/attempts,
every native job/matrix/step conclusion and actual checkout SHA/tree if exposed.
A successful checkout step alone supplies no checkout identity. Seek named
positive and negative repair outcomes and intended failure descriptions in
explicitly allowed compact evidence; absent details remain UNKNOWN. Preserve
suite-only evidence, failure/cancellation/skipped/NOT_RUN separately, with
current advisory/infrastructure/performance evidence. A fail-fast partial
matrix cannot establish all-green. The published6f native failure stays failed;
the new repair remains NOT_RUN until executed. Old F4 classifications and old
faff INCONCLUSIVE evidence supply no repaired-head credit.

release.yml native PR bundle builds/tests and matrices, verify-std-check.yml
native ubuntu22/macOS15 jobs, bench-pr.yml label-gated comparisons and
extra_jobs.yml PR metadata remain deferred to the upstream PR under unchanged
events/conditions. Release publication is tag-only. Native benchmark labels,
concurrency and reusable workflows remain unchanged. This package neither
publishes a PR nor applies labels or changes event scope.
