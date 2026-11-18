# Independent F4-A review — APPROVE

Reviewer: **independent11**, issued by owner14:14 in task commit
`fd388552f401d9f72cea6e4b17d0678bdb7e54c1`. This reviewer did not author F4.
Owner explicitly substitutes independent11 for the planning label review14;
this approval names independent11 and requires no author metadata churn.

Reviewed package: `a16ef717e18ca8263e360c24058b13a3ef4d4605`, all 17 committed
files in `f4-uninit-only/` match. Source:
`ca1452227d6ad319f1b9bc1ad33bf618120733eb`, tree
`baedd51d92073ecb2b96991bae7dc562ee8f58a2`, direct parent
`b5a9678fd7c2a0f67c3fcafd90057fc2afaf9b5d`. Source worktree is clean.

**Findings: none.** No blocking source, regression, package or CI-plan finding.
Any subsequent finding goes through the coordinator to original15; repairs
require a new immutable packet and delta review by independent11.

## Source boundary

`compiler_interface.rs:404` uses
`queries.args().ub_check.contains(&ExtraChecks::Uninit)`, exactly the effective
predicate in `check_uninit/delayed_ub/mod.rs:56`. It is independent of the global
pass vector and DumpMirPass. DumpMirPass reads/dumps bodies and returns false.

At `compiler_interface.rs:432`, enabled mode owns a complete transformer clone
for each harness through codegen; disabled mode passes the shared unit
transformer by mutable reference. The conditional local is initialized before
borrowing on its enabled branch; its lifetime spans the codegen call. Every
iteration ends that borrow before reuse of the shared transformer. The shared
template therefore retains the main cache lifetime in disabled mode.

The unchanged derived Clone copies stub/instrumentation pass vectors, the body
cache including modification flags, and both loop metadata maps together. The
restored narrow edits reproduce b5's compiler interface byte for byte. Cache
clearing, cloned global passes, unit metadata and PubFns handling retain their
reviewed lifecycle. The transformation module and pass implementations are
byte invariant from b5. This inherits the prior source assessment in
`cbfd888f274a0666f09af79d98ef4b8b8061f497`; that overall review required CI-plan
changes, closed by `4d79ed98f46d3d89feb25509cffa0704a0398cad`. Neither prior
review is presented as new runtime evidence.

Warming remains conditional on export workers enabling harness ordering.
Enabled copies may repeat local work without warming or on later body discovery.
Compile time, RSS, actual ordering and runtime cache causality remain unmeasured.

## Regression and oracle

The b5 delta changes only the compiler interface and the existing fixture's
`check.py`. Both Rust call paths, padded unsafe fixture, independent padding
control, initialized assertion, Cargo feature, shell/config and expected output
remain byte invariant. No added fixture directory, dependency or check suppression.

The entry point builds fresh arguments for both modes. Enabled mode selects
export-json/ghost-state/uninit-checks; disabled mode selects exactly export-json.
The export feature set is checked for exact equality and duplicates. Cleared
KANIFLAGS/RUSTFLAGS/KANI_LOG, removed encoded/target overrides, distinct targets
and stale-export removal prevent silent cross-mode inheritance. Mocked execution
exercises both cfg paths, delayed/initialized singletons, paired selection and
independent controls in each mode, with exact filters and normal safety checks.

Parser checks bind native exits, complete exports, selection, harnesses, property
counts, partitions, identities and resolved outcomes. Semantic inventories retain
class/semantic ID, status, description, source location and multiplicity while
normalizing numeric suffixes. Enabled unsafe controls must fail at their intended
sites; initialized controls must succeed with the assertion. Disabled ordinary
controls must succeed, retain the initialized assertion and contain no uninit
checks, with singleton/paired inventories matching.

Disabled success is an expectation derived from driver feature forwarding and
fixture layout/accesses: aligned in-bounds accesses, valid integer bit patterns,
discarded delayed read, initialized value 7. It is not an observed baseline.
The unchanged unsafe fixture and ordinary bounds/overflow/unwinding checks remain.
The observed compact frozen-main initialized failure still rejects. Synthetic
fixed envelopes and reconstructed export fields remain explicitly synthetic.

## Identity and CI gates

Independent validation verifies the issued task, committed package, author
manifest, source/tree/parent, source and workflow hashes, all reference hashes,
and committed prior review identities. Exact b5 and full-main patch replays
produce the candidate tree in isolated indexes; the test-only main patch
preserves the frozen compiler. All 16 standard workflows and resource, action,
script, library, dependency and toolchain scope remain unchanged from main.

The plan requests every native push job/matrix in kani.yml, format-check.yml and
deny.yml on a future exact final head, including all five normal regression OS
entries. Native fail-fast, retries, timeouts, C-format continue-on-error and Deny
failure behavior remain intact. Release/std/label-gated bench PR checks remain
explicitly deferred under the owner's policy. Skips and infrastructure/advisory
classifications must be preserved in eventual intake.

The candidate carries [skip ci]. The future final head must be a new no-skip
same-tree sibling with direct parent b5; the entire b5..HEAD pushed range must
contain only that sibling. Independent mocked gate tests accept a valid sibling
and reject 15 invalid candidate/tree/parent/range/skip cases without creating a
commit. The real future head remains NOT_CREATED and its actual gate is pending.

Old run 44274306776 covers b5 only: eight successful jobs, macOS runner NOT_RUN,
Format SUCCESS, Deny native FAILURE/external advisory. It validates neither this
conditional clone nor the revised two-mode test. Candidate PR Testing accurately
states that this revision's compiler/native tests and performance await CI.

## Validation and disposition

`python3 validate_review.py` passes: exact author replay of 15 static/synthetic
groups, 14 mocked orchestration cases, plus the independent identity and final-head
checks. The author validator's package write was intercepted; its reconstructed
report equals the recorded report. Author package bytes, source HEAD/clean state
and real index hash remain unchanged. See VALIDATION.json and AUTHOR-REPLAY.json.

Compiler, Kani/CBMC, native two-mode regression, new main-vs-fix runtime,
performance and new CI: **NOT_RUN**. Proof credit: **NONE**. This is correctness
review with static/synthetic assurance.

Coordinator/root may prepare the exact separate GO-request for the prospective
last item1 bundle 29/29. Current 28/29, item2 provisional 10/14 and total 38/43
remain reference accounting only. Owner retains dispatch, final-head creation,
publication and ledger authority. This approval performs none of those actions.
