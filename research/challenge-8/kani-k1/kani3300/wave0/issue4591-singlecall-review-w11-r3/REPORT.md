# SAME11 r3 delta review

Verdict: **APPROVE**. No blocking findings for the exact delivered package
`5162af47e12611de4102ba20b0135b17c1d79d7d` and candidate
`f82934ca97caaa1270d5279054aa950173868be5`, tree
`2ff34bc99ec3fe63579202c196f0ca288e318919`, sole parent
`6fca00af805b5c62b58e3e3f29eef183d6939907`.

This is the new independent W11 static delta verdict requested by owner01:23
/new11 under task `98dde2de28e13381092f20c082ba90f90ce34773`. The current agent
performed it directly; no subagents, model changes or Fast change were used.
It neither reissues the old review nor establishes repaired native PASS.

## Failure diagnosis and guard separation

The committed compact connected metadata projection accounts for twelve jobs:
seven success, one failure, four cancelled. Kani run44399789701 failed at
published6f; Format44399789719 and Deny44399789794 succeeded. Regression
ubuntu-24.04 job135139352062 failed at Execute Kani regression, step4.
The other four regression OS instances were cancelled. The first-suite
658pass/1fail, named positive failure, supplied single-top-level-call diagnostic,
other same-file harness results and fail-fast/NOT_RUN explanation are explicitly
coordinator-reported in the task INPUTS, rather than independently observed
per-harness verifier evidence. This review used those committed projections;
it did not query raw/full logs or claim a fresh native observation.

Exact selected-FnDef reachability and legal enforced-call multiplicity are
distinct constraints. At the pinned candidate, which preserves the compiler
from6f:

- `kani-compiler/src/kani_middle/attributes.rs:594` checks the selected target
  def_id against the reachable-function set. `kani_middle/mod.rs:313` and
  `codegen_cprover_gotoc/compiler_interface.rs:98` apply this to transformed
  reachable items. Copying provider closures into f alone does not supply the
  provider's exact FnDef.
- `kani_middle/transform/stubs.rs:47` copies the validated replacement body and
  records its resolved Instance. `transform/mod.rs:114` orders FnStubPass before
  FunctionWithContractPass; `:158` retains the requested cache key and hands on
  body_source. `contracts.rs:323` preserves explicitly selected requested
  targets and otherwise uses body_source. `:575` chooses Check, Replace, Assert,
  Original in that order. This body-source routing is the retained #4591 fix.
- `library/kani_macros/src/sysroot/contracts/bootstrap.rs:39` creates closures
  under their provider definition; copying the body preserves those referenced
  closure identities. `contracts/check.rs:27` assumes requires and asserts
  ensures around the actual body wrapper. `contracts/assert.rs:69` asserts
  provider pre/postconditions around its actual body. No expansion/MIR was run.
- `codegen_cprover_gotoc/codegen/contract.rs:29` resolves the selected exact
  function's check/modifies closure. `kani-driver/src/call_goto_instrument.rs:175`
  supplies DFCC/enforce-contract for that wrapper.
- The packaged configured CBMC6.11.0 source excerpt, attributed to commit
  `820ff0f555b43fb78e0cd9332e498461bd14244b`, blob
  `2f57751f7ddeb657e2c80249f503113cbb978e26`,
  `dfcc_swap_and_wrap.cpp:153-212`, uses persistent check_completed. Its
  single_top_level_call assertion checks !check_completed, and completion sets
  it true. A second sequential entry fails. Recursive in-progress entry is a
  separate path. This is source analysis of the configured release, not an
  attestation of the native executable. Its actual binary identity is UNKNOWN.

Both failed baseline harnesses directly reach the selected provider and then
reach the same provider wrapper through f's copied body:

| Published6f harness | Direct Check | Copied-body Check | Boundary |
| --- | --- | --- | --- |
| replacement_contract_target | contracted_replacement(0), result3 | f(any), body_source contracted_replacement | Named native failure reported by coordinator |
| replacement_provider_postcondition | discriminating_replacement(0), result0 | f(1), body_source discriminating_replacement | Expected suite NOT_RUN; second guard failure is a source prediction |

Both direct input0 calls meet their posts, then leave the once flag completed.
The negative's desired input1 ensures0 failure therefore cannot be credited
from the old arrangement. Clause-depth dispatch does not rescue either case:
these are normal body/harness calls at depth zero; their arithmetic clauses do
not call the selected function. Removing direct0 loses exact provider FnDef
reachability; retaining both calls violates the existing once guard. The
diagnosis supports a fixture repair, with both compiler and guards preserved.

## Supported repair and semantic oracles

The two changed fixture harnesses now select replacement_caller and execute it
once. That exact FnDef is genuinely called and its checked body returns f(x).
The caller is neither an ordinary-stub target nor a dummy reachability call.
Its selected Check wrapper runs once. Nested f copies the provider body; that
provider is neither selected for PFC nor stub_verified in these harnesses, so
its own conditions run in Assert mode. Clause brackets surround predicate
evaluation, not the whole caller body; the nested call stays on this path.

| Repair case | Caller Check | Nested provider Assert | Semantic distinction |
| --- | --- | --- | --- |
| Positive ordinary_stub.rs:171-181 | requires x<16, ensures result==x+3; one arbitrary-u8 call | contracted_replacement requires x<16, body x+3, ensures x+3 | All16 admitted inputs give3..18 without overflow, including8..15 outside original f's precondition |
| Negative ordinary_stub_fail.rs:66-81 | no requires, identity ensures; one input1 call | discriminating_replacement returns x, ensures0 | Result1 satisfies caller post and violates provider post; no precondition, assumption or overflow masks it |

Provider Original-mode or identity-post mutations remove the intended negative
failure while leaving the caller post true. Thus a generic compilation error
or single-call rejection cannot substitute for the required semantic oracle.
All golden bytes remain identical. In particular the negative expected output
requires the ensures0 FAILURE description, the named harness failure and the
existing 2success/11failure/13total harness summary. Compiletest's unchanged
`tools/compiletest/src/runtest.rs:488-565` matches expected output fragments.
That matcher is not a property-to-harness binding proof: future compact native
evidence should retain the actual named outcome and intended failure detail.

## Coverage retained and limits

All38 harness declarations and all existing non-harness function definitions
remain. Only the two affected harness declarations change; the other36 are
byte-identical. Each fixture adds its own replacement_caller. All13 PFC
harnesses were revisited, including the unchanged recursive and overlap cases.
The independent declaration inventory is in tests/REVIEW-CHECKS.json; the
per-harness mapping is in COVERAGE.md.

The repair replaces sequential provider-PFC direct+copied calls with
ordinary-provider Assert inside caller PFC. Separate positive
replacement_provider and replacement_verified_contract retain provider Check
and Replace coverage. This does not establish provider Check through every
ordinary alias shape, support a sole copied call without exact target
reachability, or define a universal mixed-alias conflict policy. Existing
explicit-original-target PFC+verified+ordinary overlap remains a separate
compile-error control. It supplies no semantic proof credit. Recursion and
overlap are outside the straight-line call model; their source is unchanged.

Ordinary safe-u8 f/g, outside-target-precondition behavior, requires-only,
ensures-only, both-clause, same-function PFC and verified controls, generic,
transitive, uncontracted, recursive, replacement safety, negative pre/post,
and no-assert behavior are preserved. The issue4591 i32 caller reproducer is
verbatim: replacement may return i32::MAX, and actual caller addition +1
overflows. Its expected result remains a real caller counterexample.

## Identity, replay and future publication boundary

Independent checks match all38 package files to delivery5162 and all37 manifest
seals, all44 frozen input references, exact source/tree/parent/clean status,
source excerpts and file pins. Only two fixtures differ from6f, with16 added
and9 removed lines. Whole compiler/driver trees equal6f. Whole .github,
scripts and library trees equal reviewed main969f and6f; toolchain/dependency
and every workflow byte match. Three actual replays in a private temporary
Git object store/index reproduce tree2ff34b: repair from6f, full patch from969f,
and compiler+regression patches from969f. Source worktree remains clean.

Fresh offline YAML parsing agrees with the inventory and complete CI job
request: five regression OS instances, four other Kani jobs, two Format jobs,
one Deny job. All native steps, conditions, default fail-fast, timeouts,
retries and stock fifteen-suite regression route remain. PR-triggered scope
stays deferred. No custom CI/F4 route is introduced.

The local candidate contains [skip ci] and must stay unpublished. A future
nonskip commit must be a same-tree sibling with sole6fparent. Its complete
969f..final range must be exactly old nonskip6f plus the new nonskip repair,
excluding skipped candidatef829. That ancestry permits fast-forward from6f.
The reviewed gate checks the entire range and rejects skipped ancestors,
wrong/merge parents, changed trees and omitted/extra commits. Metadata mutation
tests pass; actual invocations reject both localf829 and old6f. A matching
future final head has NOT_CREATED status and has no actual acceptance receipt.
Recorded remote/main observations are time-bound; recheck them immediately
before any separately authorized launch, returning drift to root.

## Validation and disposition

Independent checks:330 PASS. Author validation replay:141 PASS. All three
independent patch replays produce the reviewed tree. The reviewer checker was
adjusted before sealing to the excerpt representation (joined lines omitting
the final LF; optional blob metadata on fixture excerpts). Those checker
development issues do not change any input or weaken comparison of source
content. Source diff whitespace checks pass.

No compiler/Cargo/rustc/rustfmt/expansion/MIR/Kani/CBMC/verifier/full runner or
native CI ran. Bounded lexical models, arithmetic calculations and metadata
mocks are static evidence, not B1/B2 proof or binary/source binding. Native
repair is NOT_RUN. The old native failure, frozen static approvals and all
historical records remain intact. No complete-green claim is made.

APPROVE prepares only the root request
HOLD_FOR_OWNER_EXTRA_ITEM1_GRANT. Current owner override is item1 31/31 EXHAUSTED,
item2 11/17, total42/48, superseding frozen12/17,total43/48 references without
editing them. Potential owner morning+1 is NOT_GRANTED. No CI/push authority,
repeat, refund, reservation, charge or accounting mutation follows. The owner
grant and separate coordinator launch remain mandatory; PR publication is
owner-only. S3 stays independent. Authorized review work is complete.
