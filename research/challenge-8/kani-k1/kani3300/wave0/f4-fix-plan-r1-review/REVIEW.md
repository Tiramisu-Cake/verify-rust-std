# APPROVE — F4-R14-1 CLOSED

Plan-only delta review of exact package `9743a4a1d073e5c1591a1a20ab4756140241d57e` (nine committed files).
Issued task `task4817b5ddf0c1526432b9c7fa3b16a9ba81a85bb7`; user's coordinator GO 12:06 supersedes the prepared marker.
Current model/Fast unchanged; no subagents.

| Identity | Pin |
| --- | --- |
| New plan package | `9743a4a1d073e5c1591a1a20ab4756140241d57e` |
| Immutable old source package | `7485bbb27a72dd463d4a9628c8627689d30e7e56` |
| Immutable prior review | `cbfd888f274a0666f09af79d98ef4b8b8061f497` |
| Reviewed source | `cab66681c912a3e5ee01a106faaeee5237ca0232` |
| Source tree | `8585336ed35a14fe0fc157a7ca4e0d52075c0e49` |
| Direct parent / frozen main | `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` |
| Base tree | `09b828b47c93e90e140e8c41f9048109a2f4a786` |

## Finding disposition

**F4-R14-1 (P2) CLOSED.** The structured inventory retains the original six PR
workflows and adds release.yml. All seven native event definitions match frozen
source YAML. release.yml has four unconditional actual bundle builds:

| Job ID | Runner | Platform |
| --- | --- | --- |
| build_bundle_macos_x86_64 | macos-15-intel | x86_64-apple-darwin |
| build_bundle_macos_aarch64 | macos-15 | aarch64-apple-darwin |
| build_bundle_linux_x86_64 | ubuntu-22.04 | x86_64-unknown-linux-gnu |
| build_bundle_linux_aarch64 | ubuntu-24.04-arm | aarch64-unknown-linux-gnu |

Both `test_bundle` and `test-use-local-toolchain` require all four builds and keep
all five OS entries: macos-15-intel, macos-15, ubuntu-22.04, ubuntu-24.04 and
ubuntu-24.04-arm. Complete matrix include rows preserve artifact/target routing;
include expansion adds no sixth instance. The explicit required inventory is
4 + 5 + 5 = **14 PR build/test instances**. Only tag-push `kani_release` and its
dependent `package_docker` intentionally skip on PR. Those skips excuse no bundle
build or matrix entry. JSON, prose and metadata diff agree.

Frozen source evidence: release.yml:13 native PR trigger; :25–117 actual builds;
:119–138 local-toolchain matrix; :225–237 bundle matrix; remaining publication
job predicate/dependency checked from YAML. No author workflow was changed.

Submitted static gate replay PASS: all 41 negative cases rejected. Independently
selected 21 omissions (each from an intact plan: seven workflows, four build jobs,
ten individual test OS entries) also fail the submitted plan gate. Input package
matches all nine exact committed files; hashes, recorded validation, metadata diff,
14 old-package files and eight prior-review files match their immutable refs.

## Operational GO prerequisites

The new request carries all execution gates from cbfd; source-level inspection of
native workflows, reusable benchmark checkouts and labeler corroborates them:

- Exact source/tree → same-tree trigger → final PR branch HEAD/tree and base;
  record workflow/event/run/attempt/job identities and recheck any newer HEAD.
- Record actual checkout SHA/tree separately. Default PR checkout uses a merge
  ref; with unchanged frozen base its tree must equal reviewed tree, otherwise
  review that delta. Reusable benchmarks explicitly compare PR head/base SHAs;
  authorized branch-push checks must bind the exact trigger HEAD.
- Both benchmark labels apply to kani-compiler/**. Establish both before an
  eligible native event; GITHUB_TOKEN auto-labeling does not retrigger bench-pr.
  Owner chooses choreography/accounting. Missing, skipped or cancelled required
  perf-benchcomp / compile-timer-short / compile-timer-long prevents acceptance.
- Source subject contains [skip ci]. Future PR HEAD/trigger must have no skip
  directive; inspect every commit in the pushed range before claiming a push run.
- None of seven workflows has workflow_dispatch. Feature-push alone cannot
  establish full PR std/benchmark/release coverage. Retain native conditions,
  retries, timeouts, continue-on-error and every applicable matrix conclusion.
  verify-std head failure remains failure despite a successful base comparison;
  auto-label is trusted-base metadata, and docs publishing may skip outside main.
- Owner rechecks upstream main; relevant drift requires handoff. Exact review
  approval, owner publication command and separate full-CI GO/accounting remain
  distinct. Future Testing text uses actual results and at most one full-CI link.

## Inherited source conclusions and limits

Source `cab66681c912a3e5ee01a106faaeee5237ca0232` / tree `8585336ed35a14fe0fc157a7ca4e0d52075c0e49` / direct parent `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` remains clean and exact.
All nine source/test blobs match old748; all sixteen workflow blobs and complete
.github/scripts trees remain unchanged. Prior cbfd source conclusions carry by
byte invariance. No compiler lifecycle audit, old source validator, regression
orchestration, compiler build or full runner was repeated.

Prior unmeasured warmed-cache clone time/RSS risk remains subject to standard
perf/compiler/e2e benchmarks. Compilation order and runtime cache causality remain
UNKNOWN. Compiler build, fixed/new-test runtime, performance and full standard CI
remain **NOT_RUN**; proof credit **NONE**. APPROVE closes this plan finding only.

Coordinator may now prepare the separate full-standard-CI GO-request on the exact
future PR branch HEAD, prospective final item1 28/28. Reference remains 27/28;
zero attempts consumed/reserved and ledger untouched. S2r1 is outside scope.
Dispatch/publication require separate owner GO. No new blocking finding.
