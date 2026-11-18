# F4 — GO-request for full standard PR CI

READY_FOR_OWNER_GO, conditional on final head/event binding. Independent plan-delta
review `4d79ed98f46d3d89feb25509cffa0704a0398cad`: **APPROVE, F4-R14-1 CLOSED**.
No CI or publication authorization is implied.

Candidate Kani `cab66681c912a3e5ee01a106faaeee5237ca0232`, tree
`8585336ed35a14fe0fc157a7ca4e0d52075c0e49`, parent/main
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`. Source package
`7485bbb27a72dd463d4a9628c8627689d30e7e56`, source review
`cbfd888f274a0666f09af79d98ef4b8b8061f497`; code unchanged during plan repair.
Corrected CI plan `9743a4a1d073e5c1591a1a20ab4756140241d57e`;
exact structured requirements/hashes and future identity slots are in GO-REQUEST.json.
Coordinator checked 9 committed plan files, 7 committed review files and all review
manifest input/output hashes. Author 41 and reviewer 21 negative cases were rejected
per the committed review. This closes plan completeness only; prior static source
conclusions are inherited by byte invariance, with no repeated source audit.

Request: the last item1 full standard PR CI attempt **28/28**, on the exact final PR
branch head. Owner publication command and separate CI/accounting GO are outstanding.
No source/push/PR/label/event/CI/reservation/ledger actions are performed here.

Required native workflows: `kani.yml`, `format-check.yml`, `deny.yml`,
`verify-std-check.yml`, `extra_jobs.yml`, `bench-pr.yml`, **`release.yml`**.
Keep every native candidate job/matrix, including five regression OSes, full performance,
LLBC/docs, format/clippy/audit and std head/base outcomes. `extra_jobs` is trusted-base
labeling only and contributes no candidate build evidence. Both benchmark labels
`Z-EndToEndBenchCI` and `Z-CompilerBenchCI` are required: end-to-end perf-benchcomp
and both compile-timer-short/long comparisons on the final PR head versus base.

`release.yml` requires **14 PR instances**: build_bundle_macos_x86_64,
build_bundle_macos_aarch64, build_bundle_linux_x86_64, build_bundle_linux_aarch64;
then both `test_bundle` and `test-use-local-toolchain` on macos-15-intel, macos-15,
ubuntu-22.04, ubuntu-24.04, ubuntu-24.04-arm. Native tag-only `kani_release` and
dependent `package_docker` skips are expected on a PR. Artifact routing and build
needs remain unchanged; full inventory is pinned in the JSON request/approved plan.

Before dispatch, owner rechecks main drift and creates/records a same-tree final
PR trigger/head without skip directives; the reviewed source commit has `[skip ci]`.
Inspect the complete pushed range too. No final trigger, PR number or run exists in
this request. Record exact head/base SHA/tree, native event and every run/attempt;
record actual checkout SHA/tree separately from run head and PR head. Synthetic PR
merge checkout must have the reviewed tree, or its delta needs review. Benchmarks
bind actual PR head/base; old confirmation refs give no candidate build evidence.
Relevant base drift requires explicit handoff; no silent rebase or source changes.

None of these seven workflows has workflow_dispatch. Feature push alone cannot
cover the required PR suite. Both benchmark labels must exist for an eligible native
event: GITHUB_TOKEN auto-labeling does not retrigger bench-pr, and PR-open can race
labels. Owner chooses authorized event choreography/accounting. Preserve native
conditions, timeouts, continue-on-error behavior, concurrency and all conclusions;
no automatic reruns, hidden events or additional attempts are authorized.

Missing/skipped/cancelled/red required jobs prevent full-CI acceptance. A green std
base comparison cannot erase a failing head. Require actual fixed-head regression
PASS with valid unsafe controls, and assess clone-time/RSS cost with full performance
and both compiler benchmarks. Main confirmation run44177926794/intake06ff67af4a
established DEFECT_PRESENT in the compact fixture; both cfg variants do not establish
actual compilation order or runtime cache causality. Fixed runtime/full CI remain
**NOT_RUN**. Update future PR Testing only after actual evidence, at most one full-CI
link; no upstream-ready claim yet.

Accounting is reference-only: ledger4076fb01d5, item1 **27/28**, item2 **10/14**,
total **37/42**. This request consumes/reserves nothing. S2 repeat/accounting remains
separate, owner-only (GO-request1ce52e417e).
