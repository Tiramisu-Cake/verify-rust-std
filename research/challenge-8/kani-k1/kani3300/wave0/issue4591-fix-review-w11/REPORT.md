# Independent11 review: REQUEST_CHANGES

Exact package `bdf1bb42189257c9654eb55dfcda11b2f08a0b01`, source
`a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a`, tree
`98fae98ce9e783bed0393d35657674da09c3aa31`, sole parent/main
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`.
Task: `TASK-KANI-4591-REVIEW-W11.md`, issued against task commit
`7afd3d52d959a246df4e968e9cc8a66f029fbedf`.

One blocking finding prevents APPROVE and the root GO-request. Source and
package pins match. The routing change has no additional source-level finding
from this review. Native main/fixed tests, compiler, rustfmt, Kani and CI remain
**NOT_RUN**. This is a static review, not proof or typechecking credit.

## W11-01 — High: two PFC fixtures cannot reach their selected target

Affected candidate locations:

- `tests/kani/FunctionContracts/ordinary_stub.rs:171`, harness
  `replacement_contract_target` (declaration at line 173).
- `tests/expected/function-contract/ordinary_stub_fail.rs:66`, harness
  `replacement_provider_postcondition` (declaration at line 68).

Both select a provider using `proof_for_contract(provider)` and map
`stub(f, provider)`, then call only `f`. Their selected providers are respectively
`contracted_replacement` and `bad_contract`. The copied body and its contract
closures do not make the provider's function definition reachable:

1. `BodyTransformation::body_ref` retains the requested `f` cache identity while
   copying the provider body. Its new `body_source` is passed to the contract
   pass; it adds no call edge to the provider wrapper.
2. `reachability.rs:142-179` inserts the requested `MonoItem::Fn(f)` and visits
   the transformed body. Provider closures and nested registration functions
   have their own definition IDs. The simple provider bodies here contain
   arithmetic/identity operations, with no call back to their provider wrapper.
   Macro generation in `library/kani_macros/src/sysroot/contracts/check.rs`
   embeds the original statements in the modifies closure.
3. `kani_middle/mod.rs:313-340` constructs the reachable-function set from
   `instance.def.def_id()`. `attributes.rs:583-600` requires the exact selected
   PFC target ID in that set and emits the diagnostic:
   `The function specified in the proof_for_contract attribute ... is not reachable from the harness ...`
   (the actual diagnostic places backticks around the attribute and names).
   It then aborts before verification.
4. `compiler_interface.rs:420-450` starts each harness from its own single
   `MonoItem::Fn(*harness)`. A direct provider call in another harness in the
   same file supplies no reachability credit here. The shared transformer cache
   also supplies no additional starting item. `codegen/contract.rs:32-52`
   separately expects the selected provider function item for contract setup.

Consequently the positive file cannot deliver its expected all-successful
inventory. The negative file cannot deliver its expected two successful and
eleven failed verification outcomes: compilation fails first. Its `.expected`
requires semantic verification results, so the compilation error fails that
test too. These are source-derived predictions; no native execution occurred.

The author's static validator passes because it checks fixture inventories and
expected-output strings without checking this reachability invariant. This
review reproduces that validator success and records the additional finding;
neither result overrides the other.

Repair belongs to **original15**. Keep this reviewed delivery immutable and
produce a new immutable repair package with updated pins, patches, oracle,
validation, manifest and handoff. Make each PFC target genuinely reachable in
its own harness while preserving a meaningful test of copied-provider mode.
For the positive case a direct call to the valid provider can establish that
reachability alongside the call through `f`. For the negative case, merely
adding a directly failing `bad_contract(0)` can mask the behavior under test;
use a provider/input arrangement where the direct target call passes and the
copied call exposes the intended postcondition failure, or an equivalently
discriminating oracle. Preserve original precondition-bypass assertions and
replacement safety checks. Do not remove the target-reachability guard or
substitute a compile-error expectation for these semantic controls. Return the
repair to the same independent11 reviewer for delta-review before root GO.

## Routing and contract modes

The compiler diff is confined to three files, with 36 inserted and two removed
lines. `FnStubPass` resets `body_source` on each invocation and reports the
resolved replacement `Instance` only after `FnStubValidator::validate` returns
a body. `take_body_source` consumes it immediately. Each cache miss starts
from the requested instance, so failed/inactive mappings and unrelated bodies
cannot inherit a previous replacement.

Only `FunctionWithContractPass` overrides `transform_instance`. Its ordinary
Assert/Original cases use the validated body's source. Plain providers thus
avoid original contract closure lookup; contracted providers select their own
attributes, generated closures and mode. Generic arguments come from the
existing `Instance::resolve` path. All remaining passes receive the requested
instance and copied body; safety instrumentation and loop metadata ownership
retain their order and identity. No closure error is suppressed.

Explicit original PFC or `stub_verified` selection retains the requested
instance. Unstubbed functions and closures likewise retain their identity.
`contract_mode`, `mark_unused`, closure lookup and mode-setting code are
unchanged. Recursive PFC retains RecursiveCheck; verified calls retain Replace;
`--no-assert-contracts` retains Original for ordinary dependencies and explicit
Check/Replace for selected targets. Contracted providers selected by verified
stubbing use their own Replace mode. PFC selection of a provider is subject to
the separate reachability requirement described in W11-01.

The explicit same-target PFC/verified/ordinary combination deliberately keeps
main's original-target closure-error behavior and PFC precedence. Its new
compile-error fixture matches that scope. Verified-only same-target overlap is
preserved by the source guard but has no separate new native result or isolated
new fixture. No generalized conflict policy is approved by this review.

`group_by_stubs` separates contract usages and ordinary mappings;
`apply_transitivity`, duplicate/cycle errors, signature compatibility,
bodyless/extern redirection, constant validation and trait-bound validation
remain byte-unchanged. Multiple targets and transitive mappings still resolve
before body transformation. Generic, recursive, uncontracted and unstubbed
dependency controls are present. Their outcomes remain predictions.

## Regression oracle assessment

All 38 harness rows were inspected; per-row conclusions are in
`tests/ORACLE-REVIEW.json`. The two rows in W11-01 have incorrect expected
execution stages and block both containing files. Other per-harness semantic
expectations are supported by source inspection, subject to whole-file
compilation and future native validation.

The safe f/g MRE distinguishes `x+1` from `x+2`, stays in the u8 range, and calls
`f(8)` to distinguish bypass of the original precondition/postcondition.
Requires-only/ensures-only/both, original PFC/verified controls, and
`--no-assert-contracts` have corresponding fixtures. The no-assert replacement's
incorrect postcondition is checked separately with PFC and `should_panic`.

Negative controls pin named failures for replacement overflow, verified
preconditions/results, PFC postconditions, unstubbed pre/postconditions and
replacement pre/postconditions. The requires-only verified result is
unconstrained without ensures, so its asserted exact return has a genuine
counterexample. Expected counts refer to explicit harnesses, not property
quotas. Compiletest matches each expected substring group independently and
requires lines joined by backslashes to be adjacent. Synthetic checks confirm
that missing-closure compilation output cannot satisfy the two semantic
expected-output files.

The #4591 Rust body matches the retained issue code block. Its ordinary
replacement admits `i32::MAX`, then `caller` adds one. A failing **caller
addition** overflow property is the correct oracle. The `caller.assertion`
substring permits native property suffixes while excluding a failure solely in
`abs_val`. A synthetic successful or unrelated-overflow result is rejected.
The original `i32::MIN` negation belongs to the body being replaced. The package
correctly avoids claiming this example verifies successfully after the fix.

The historical run44380273557 intake is separately retained as INCONCLUSIVE,
with its observed original missing-closure error and successful controls. It
provides no new-main, fixed-head or formal-proof credit. Its files were checked
by the author-validator replay without changing their classifications.

## Exact isolation, provenance and standard push-CI preparation

Independent checks confirm all 21 package files equal their blobs at the exact
delivery commit; the author manifest seals the other 20 files. The source is
clean and its only commit above exact main is the pinned skipped candidate.
The changed set is exactly three compiler and eight test files. Main's
tree/parent, changed-file hashes/blobs, protected workflows/actions/scripts/
library trees, dependencies and toolchain are consistent. Patch replay from
main reproduces the exact candidate tree. Read-only `ls-remote` rechecks main
without drift. No F4/unpublished compiler change occurs in the delta.

The package declares stock main, own trace and only the authorized issue #4591
and its two comments as coding inputs. This review used those retained inputs
and local pinned source; it consulted no unrelated external PR/diff. Historical
authoring provenance is an author declaration, not independently reconstructed
history. STYLE and PR draft were reviewed: disclosure, license, Resolves #4591,
concrete failure/expected fix and pending native testing are present. A future
publication must replace pending testing only with actual standard-run evidence.

All 16 workflow inventories match actual pinned YAML. Independent event
inspection derives exactly these non-main branch-push workflows and 12 native
instances:

| Workflow | Complete jobs/matrices |
| --- | --- |
| kani.yml | regression on macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15, ubuntu-24.04-arm; benchcomp-tests; perf; llbc-regression; documentation |
| format-check.yml | format-check; clippy-check |
| deny.yml | audit |

All job definitions match, including conditions, permissions, fail-fast defaults,
native retry/timeouts and advisory settings. Both regression suites run through
stock `scripts/kani-regression.sh`; no subset replaces the full bundle. Release,
verify-std, benchmark and metadata PR events remain deferred to the owner-defined
upstream PR scope. No custom workflow, changed trigger or cron enablement exists.

The final nonskip head is **NOT_CREATED**. Its required relationship is a
same-tree sibling of the local skipped candidate, sole parent exact main,
with exactly one nonskip commit in the entire main..final range. The candidate
must stay outside that range. Synthetic/adversarial checks cover skip directives,
tree drift, wrong/merge parents, extra commits and an empty range. A metadata
match grants no publication authorization. Actual final SHA, branch/ref, remote
head, native run IDs/attempts, every job/matrix conclusion and checkout SHA/tree
remain future receipts, never inferred from a successful checkout step.

These CI preparations are structurally consistent but **not ready for GO while
W11-01 remains open**. Budget reference remains item1 30/31, item2 11/17,
total41/48. Review consumed zero CI attempts and changed no accounting. A future
authorized full bundle would be item1 31/31, total42/48; preparation is not
dispatch authority. CI and PR publication retain their separate owner gates.

## Validation and authority boundary

- Independent static checks: 112 passed, with W11-01 explicitly recorded.
- Inspected author's `python3 -B validate.py` replay: 137 static/mock checks
  passed, including split/full patch replay into temporary Git indexes.
- Every new main/fixed native result: NOT_RUN. Compiler/typechecking, Cargo,
  rustfmt, Kani/CBMC, fullrunner and CI: NOT_RUN.
- No source/test edits, subagents, model-setting changes, push, PR, issue/comment,
  CI, ledger/reservation/budget action or raw evidence access occurred.

Own review files are the only delivery changes. Inputs, exact source excerpts,
static results, oracle review and manifest accompany this report. Original15
repairs the finding; independent11 reviews the immutable delta. Root GO-request
is withheld until exact APPROVE, and execution/publication remain with the
separately authorized coordinator/owner.
