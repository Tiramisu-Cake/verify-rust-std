# CHANGES_REQUIRED — exact standalone F4 fix

Issued review task: `TASK-CH8-F4-FIX-REVIEW-W14.md`, task identity
`7b829344c9cdd8c25ec59294bb9015201638a879`. The user's current issuance supersedes
the template's PREPARED_NOT_ISSUED marker. Current model+/fast unchanged; no subagents.

| Input | Exact identity |
| --- | --- |
| g0 package | `7485bbb27a72dd463d4a9628c8627689d30e7e56` |
| Package directory | `kani3300/wave0/f4-fix/` (14 committed files) |
| Kani source | `cab66681c912a3e5ee01a106faaeee5237ca0232` |
| Source tree | `8585336ed35a14fe0fc157a7ca4e0d52075c0e49` |
| Direct parent / frozen main | `faffcee3bca2770c03bd21c3bde89cc8f6f7a14e` |
| Base tree | `09b828b47c93e90e140e8c41f9048109a2f4a786` |
| Source worktree / branch | `/root/kani-f4-fix-w15` / `w15/f4-fix-main` |
| Complete patch SHA256 | `01cb57c32c39d03335e47e74182634f638e3566e93338ca51b29e029c81f5318` |
| Input manifest SHA256 | `72caccd04c0784389f700684c22a7950ed68383599943d85a54408fe6cc5be58` |

One blocking plan finding for **original15**; no source-code finding. No author code
or package edits performed. Compiler build, fixed runtime and full CI remain **NOT_RUN**.

## F4-R14-1 — P2: full-standard-CI plan omits PR release-bundle checks

Locations: `f4-fix/CI-REQUEST.json:17` (`standard_pr_workflows`) and
`f4-fix/CI-REQUEST.md:43` (scheduled/release exclusion).
The JSON lists six PR workflows and omits `release.yml`; the prose treats release
workflows as non-PR triggers. At exact source HEAD, `.github/workflows/release.yml:13`
has `pull_request` and `merge_group` triggers. Its four bundle builds have no PR
exclusion, and `test_bundle` plus `test-use-local-toolchain` each run a five-OS matrix.
These 14 build/test instances are part of full standard PR CI. Only `kani_release`
is tag-push gated; `package_docker` depends on that skipped publication job.

Effect: the requested final attempt could be called complete while required standard
bundle build/installation/toolchain checks are absent. This violates the full-standard
CI acceptance contract even though all workflow files are preserved.

Requested original15 fix: add `release.yml` to CI-REQUEST.json, enumerate the four
builds and both complete test matrices in CI-REQUEST.md, and explicitly distinguish
their required PR execution from intended release/Docker publication skips. Refresh
affected package hashes/metadata and return the exact committed package delta for
review. Preserve the reviewed compiler/tests and all 16 standard workflow files.
Do not run CI/push/PR or alter ledger/accounting to address this finding.

## Isolation, pass state and metadata

`compiler_interface.rs:405` constructs one unit template and `:421` warms its local
transformations through `order_harnesses`. The clone at `:435` precedes the call to
`codegen_items`; only the clone is passed at `:449`. The unit template receives no
harness global-pass writes. A subsequent harness therefore starts with pre-global
local transformations, regardless of which harness ran first. The no-export-worker
path clones an initially empty template and independently fills the harness cache.
`PubFns` retains its single-transformer path.

`transform/mod.rs:85` derives Clone over both owned pass vectors, the owned
`HashMap<Instance, TransformationResult>` and both loop-metadata maps. The existing
trait-object clone machinery clones the concrete passes; `TransformationResult`
already clones its Body and modification flag. Stub maps, contract target/replace
configuration, unused-closure state, Arbitrary-cycle checks, model/helper caches and
loop-pass state travel with the corresponding cached bodies. `group_by_stubs` in
`codegen_units.rs:245` groups by contracts and stub configuration, so cloning the
unit's configuration retains the configuration used to warm those bodies.

`body_ref` drains each pass's generated loop locals/bindings into the two maps as
each body is cached. Clone preserves those Local/Instance identities together with
the body. Cache hits retain the maps; cache misses update the harness copy. The loop
pass resets its per-body scratch state, and delayed instrumentation appends locals
through `MutableBody::new_local`, preserving pre-existing local indices. Codegen
consumers in `overrides/hooks.rs:890` and `codegen/statement.rs:266` query this same
transformer, keeping loop metadata aligned with the body being generated.

`codegen_items:96–145` uses the copy for initial reachability, current-harness global
passes, conditional recollection and `GotocCtx`. `DelayedUbPass::transform` still
discovers targets from checked bodies/current starting items, runs points-to analysis,
and writes delayed-instrumented bodies to the supplied cache. Its enablement,
target discovery and safety checks are unchanged. `clear_codegen_cache()` and
`template_passes.clone()` retain their prior boundaries. Export work owns its symbol
table/metadata after `gcx.split()`; the harness transformer can be dropped safely at
the end of the iteration. No unrelated cache reset or instrumentation disable appears.

## Allocation and performance assessment

The isolation is simple and source-consistent, with a material unmeasured cost:
every harness copies the entire warmed union of bodies, including bodies belonging
to other harnesses. For H harnesses and warmed-cache size U, aggregate copy work can
scale with H×U; each iteration retains the template plus one harness copy. The
existing trait-object clone helper clones each pass through an intermediate box,
adding temporary pass allocations. Export-worker data adds its existing memory cost.

The clone is unconditional, including runs without uninit checking. Without export
workers, or for bodies discovered after warming, local transformations can repeat
between harnesses. Warming is preserved where it exists; sharing of post-warm additions
is lost. No measured time/RSS bound is established. This risk is acceptable for the
requested review-to-full-CI stage, with standard perf and both compiler benchmark
suites required before acceptance. A performance regression needs a concrete handoff.

## Regression and evidence boundaries

The exact observed Rust/Cargo fixture is preserved. The seven probes exercise an
independent unsafe control and singleton/singleton/paired selections for each cfg.
The oracle requires initialized SUCCESS and the successful value assertion, identical
singleton/paired semantic property multisets with multiplicity, and intended unsafe
FAILURE at shared `src/lib.rs:12` and independent `control.rs:16`. Only the final
property ordinal is removed from comparison; no fixed 13/20/37 quota is imposed.
Exit 1 for a paired invocation alone cannot establish the initialized outcome.

All seven retained compact inventories parse with explicitly reconstructed envelope
fields. The main dataset is rejected at `initialized harness failed`; copied-singleton
synthetic expected-fixed inventories pass. Mocked seven-probe orchestration checks
selection, both cfg command routes, target-directory separation and environment
cleanup without invoking native tools. Error-path checks reject partial/missing/null/
wrong-type/NOT_RUN data, wrong partitions or selection, weakened checks, unsupported
failure, wrong unsafe source, unsafe suppression, spawn/timeout/signal/error exits.

The compact producer's discarded native envelopes remain source-attested; this
review does not re-establish their raw integrity. Actual new-test main execution,
fixed build/runtime and performance are NOT_RUN. Cfg names establish call routing;
actual compilation order and runtime cache causality remain UNKNOWN. Proof credit NONE.

## Full standard CI plan: required binding for the coordinator's GO request

CI-REQUEST covers six of seven applicable standard PR workflows. All 16 workflow
blobs, `.github`, scripts, library, toolchain and dependency pins are unchanged from
the frozen base. No confirmation workflow/deletions/research runner enter the source.
The following checks clarify execution of that plan and must accompany its GO request:

| Workflow | Native trigger and required coverage |
| --- | --- |
| `kani.yml` | PR / merge_group / branch push; five regression OS entries, benchcomp-tests, full perf, LLBC and documentation. Regression includes the new script-based test. Preserve standard retries/timeouts; docs publishing step correctly skips outside a push to main. |
| `format-check.yml` | PR / merge_group / branch push; format-check and clippy-check, all standard steps and native continue-on-error behavior. |
| `deny.yml` | PR / merge_group / branch push; audit. |
| `verify-std-check.yml` | PR or reusable call; both Ubuntu/macOS entries. Head failure conditionally runs base comparison. Preserve native head/base outcomes even if the comparison job succeeds. |
| `extra_jobs.yml` | pull_request_target / merge_group; auto-label only. Its checkout uses trusted base context; it supplies no candidate build evidence. |
| `bench-pr.yml` | PR opened/synchronize/reopened/labeled; require both EndToEnd and Compiler labels. Reusable jobs: perf-benchcomp, compile-timer-short and compile-timer-long, comparing PR head SHA with base SHA. |
| `release.yml` — missing from request | PR / merge_group / main-or-tag push; four bundle builds (macOS x86_64/aarch64 and Linux x86_64/aarch64), TestBundle and TestLocalToolchain each on macos-15-intel, macos-15, ubuntu-22.04, ubuntu-24.04 and ubuntu-24.04-arm. All are required on PR. Release and dependent Package Docker publication jobs intentionally skip on PR. |

Both benchmark labels match `kani-compiler/**`. Auto-labeler changes made with
GITHUB_TOKEN do not retrigger `bench-pr`; on PR opening they can arrive after its
label predicates were evaluated. Before the counted full run, the authorized owner
must establish both labels and an eligible native event (for example, one authorized
synchronize after both labels exist, or a manual label event while both are present).
Bench workflow concurrency cancels older runs, so preserve cancellations and bind
the accepted jobs to the final run/head. Label-race skips leave CI incomplete.

The reviewed source subject contains `[skip ci]`. A separately authorized same-tree
trigger without skip text is necessary. Bind reviewed source SHA/tree, trigger SHA,
exact **PR branch HEAD**, PR base and every run/attempt before credit. Push skip
handling must also account for skipped commits in the pushed range; merely adding a
non-skipping child does not by itself establish that a push run will start. The PR
head must have no skip directive. No trigger commit is created by this review.

Standard actions/checkout on a PR normally checks out its synthetic merge ref;
its run head SHA alone does not prove branch-HEAD checkout. Record the actual
checked-out SHA/tree as well as PR head SHA/tree. With unchanged frozen base, verify
that merge tree equals the reviewed/same-tree trigger tree; if it differs, hand off
the exact delta for review before acceptance. The reusable benchmark workflows
explicitly checkout `github.event.pull_request.head.sha` and `base.sha`. Branch-push
checks, if authorized in the run plan, must resolve to the exact trigger HEAD.
No evidence on the old confirmation branch/ref can satisfy these candidate checks.

These seven PR workflows have no workflow_dispatch trigger. A feature-branch push
alone also omits PR std/benchmark/release-bundle coverage. Scheduled, updater and
slow-test-only triggers remain native and are outside applicable PR checks. Retain every applicable matrix
conclusion; missing, skipped or cancelled required jobs prevent full-CI acceptance.
Before publication, owner rechecks upstream main; relevant drift requires explicit
handoff. PR-DRAFT's pending Testing paragraph becomes actual results plus at most
one full-CI link only after execution.

No CI/push/PR/ledger/reservation/message action occurred. Item1 remains the supplied
27/28 reference, with final 28/28 unspent by this review. S2 review e40/accounting is
outside scope. Publication remains solely under an explicit owner command. Return
F4-R14-1 to original15; after the corrected exact package delta is approved, the
coordinator can prepare the separate final full-CI GO request.
