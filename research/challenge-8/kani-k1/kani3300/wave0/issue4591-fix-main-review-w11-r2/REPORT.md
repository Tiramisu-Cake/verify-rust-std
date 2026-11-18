# Independent11 combined review: APPROVE

W11-01 is **CLOSED by independent source review** for this exact candidate.
No blocking finding remains in the repaired fixtures or the transfer to the
approved new main. This approves the combined reviewed delta for root's exact
GO decision. It does not launch CI, create a publication head or publish a PR.

| Binding | Exact value |
| --- | --- |
| Task | 09840da5715c0462ee09256930d8487712beebf3; TASK-KANI-4591-MAIN-PFC-DELTA-W11.md |
| Reviewed g0 package | ad50aaeaabe8b3a84dbf64a88d0214a16f4ee316 |
| Package path | research/challenge-8/kani-k1/kani3300/wave0/issue4591-fix-main-r2 |
| Source | 3a770b5db51ba07acffce3483bde0901e6533f3a |
| Source tree | 7a3d5c05b5d663d515c198b2bfa7c4926ae133ac |
| Source sole parent / approved main | 969f4648980a8e66cd0ca32fd3e714a55ac32cef |
| Main tree | c9a832dc1647c51ac3036429e5f97e73eb717ba7 |
| Main sole parent | faffcee3bca2770c03bd21c3bde89cc8f6f7a14e |
| Prior independent review | 54ea8a918b761dc67213f7f24ae5163b7f463b42 |
| CI-REQUEST.json SHA256 | 50da6854da282d718e28ee93953cd5d27c0bf47b366f538248cd5f461b71fdbe |

All new main/fixed native results, Rust typechecking, compiler, expansion,
Cargo/rustc/rustfmt, Kani/CBMC, fullrunner and CI remain **NOT_RUN**. Approval
is a static review judgment, with Git integrity/replay and bounded synthetic
checks. It supplies neither measured compiler FnDef/MIR evidence nor formal
verification credit. Historical faff intake remains INCONCLUSIVE in its old
scope and supplies no new-main or fixed-candidate native credit.

## W11-01 closure and exact selected-provider reachability

The original finding concerned two harnesses that selected a provider with
PFC but called only an ordinary target containing a copy of the provider body.
That copy retained the ordinary target's function identity and did not make
the selected provider's own FnDef reachable. The prior review and both original
and intermediate r1 packages remain immutable.

The repaired positive harness is
`tests/kani/FunctionContracts/ordinary_stub.rs:173`,
`replacement_contract_target`. Its body now unconditionally calls
`contracted_replacement(0)` before `f(kani::any())`. Both the PFC attribute and
the direct call name the unique local `contracted_replacement` definition;
there is no import, shadow binding, branch or ordinary mapping that redirects
the provider call. This supplies the provider function item in this harness's
own reachable set. Its requires `x < 16` bounds `x + 3`; direct0 returns3 and
satisfies ensures, and the copied PFC Check path also satisfies the contract
throughout the admitted u8 domain.

The repaired negative harness is
`tests/expected/function-contract/ordinary_stub_fail.rs:74`,
`replacement_provider_postcondition`. It selects the new local
`discriminating_replacement`, maps `f` to it, then unconditionally executes:

```rust
discriminating_replacement(0);
f(1);
```

The provider is exactly an identity body with ensures `result == 0`. Direct0
returns0 and passes its postcondition; the copied input1 returns1 and fails
that same postcondition. The provider has no precondition, arithmetic, assume,
early return or recursively selected call to mask the copied failure. The
old `bad_contract` is unchanged and is not called directly by this harness.
The new failure description is unique to this provider and is required in
the semantic `.expected` output. All old expected groups, eleven named failed
harnesses and the two-success/eleven-failure/thirteen-total inventory survive.

This conclusion follows the pinned compiler and macro path, independently
of the author's lexical fixture checker:

1. Each harness starts from its own `MonoItem::Fn(*harness)` in
   `codegen_cprover_gotoc/compiler_interface.rs:442`.
2. `reachability.rs:155-179` inserts each requested function item and visits
   its transformed body. The direct provider call therefore contributes the
   provider item, while the copied call contributes `f` and its nested items.
3. `kani_middle/mod.rs:316-340` derives reachable function IDs from those
   items; `attributes.rs:603-624` still requires the exact selected target ID.
   No reachability guard or diagnostic is weakened. All thirteen PFC harnesses
   in the five fixture files have their own direct selected-target calls,
   including the separately intentional overlap compile-error control.
4. The contract pass retains the requested instance for an explicit selected
   provider; the ordinary `f` instance uses its validated provider source.
   Both repaired paths therefore select the provider's SimpleCheck closures.
   `contracts/check.rs` captures the actual arguments, assumes requires and
   asserts ensures; it does not replace these scalar inputs with arbitrary
   values. Both harness calls occur outside contract clauses.
5. `codegen/contract.rs:32-52` can find the selected provider's actual function
   item and its modifies wrapper. No call in a different harness is credited.

Source resolution and control-flow reasoning close the reported defect.
Actual compiler-generated definition IDs, MIR reachability and native outcomes
still await execution. A missing-closure or unreachable-target compile error
cannot satisfy either repaired semantic fixture's expected output. No compile
error oracle was substituted for either PFC test.

## Original routing, modes and safety

The three-file compiler delta is content-identical to repaired r1. FnStubPass
resets its source state on every invocation, reports a replacement Instance
only after the existing validator accepts its body, and consumes the report
once. Every cache miss initializes the body source from the requested instance.
The cache key, generated loop metadata ownership and all pass ordering remain
the requested function's. Only FunctionWithContractPass changes the Instance
used to interpret the validated copied body.

Ordinary Assert/Original routing uses the provider's attributes and generated
closures, preventing original-target closure lookup on a plain replacement.
An explicit original PFC or verified selection retains the original requested
instance and precedence. Provider PFC/verified selection follows the provider's
Check/Replace modes. RecursiveCheck, generic argument resolution, untouched
dependencies, unstubbed functions, and no-assert-contracts Original mode remain
consistent with the reviewed source. Explicit no-assert PFC and verified modes
remain active. Existing mode selection, closure selection and error behavior
are byte-unchanged.

Signature/constant/trait-bound validation, ordinary transitivity and cycle
handling, bodyless/extern redirection and replacement safety checks are retained.
All later passes still instrument the body with their existing requested
identity. The intentional same-target PFC/verified/ordinary overlap still
produces the original closure diagnostic. It supplies no isolated native
coverage for verified-only overlap and approves no broader conflict policy.

## Transfer to main969f and toolchain/API review

Independent Git checks confirm the source and main trees/sole parents, clean
source worktree and exactly one skipped candidate commit above969f. The new
delta contains exactly three compiler and eight fixture/oracle files.

After removing only Git index blob header lines, oldmain..r1 equals
newmain..candidate byte-for-byte, including hunk coordinates. Likewise,
oldmain..newmain equals r1..candidate. Thus every upstream content hunk survives;
all thirty other upstream changed files have exact new-main blobs. The complete
r1 patch, the new complete patch and independently ordered split patches each
replay from969f to exact tree7a3d5c05. There is no resulting conflict resolution
or extra adaptation. Historical claims about the author's commands are not
treated as independently observed execution history.

The relevant new-main `contracts.rs` change uses `iter().any` for feature
membership. It is preserved separately from the added routing hook. New-main
`attributes.rs` removes AttributeExt/path_matches in favor of Tool/DeriveHelper
segment matching and reads string literals via value_lit/kind.str. That file
is entirely unchanged by the candidate, including selected-target interpretation
and the exact-ID reachability guard. The patch introduces no call to removed
rustc attribute APIs.

The hooks use the existing Instance, FnDef, RigidTy and validation interfaces;
new-main does not change those touched signatures. Accepted type/diagnostic/
intrinsic and loop-contract updates remain in place. Library, workflows,
actions and scripts have exact protected new-main trees. The nightly-2026-11-18
toolchain, dependency pins, driver chrono removal and Cargo.lock are exact
new-main bytes. This is source compatibility assessment, not typechecking.
Fresh read-only ls-remote at 2026-11-18T21:06:55Z still observes exact969f.

## All38 regression oracles

`tests/ORACLE-REVIEW.json` records each current row, attributes, expectation and
source assessment. The eight fixture/oracle files equal r1. Every original
fixture function/attribute/body outside the two repair harnesses is preserved;
the only new helper is the discriminating identity provider. Both repaired
rows have been reassessed independently, rather than inheriting the prior
blocking conclusions.

The safe u8 f/g MRE distinguishes x+1 from x+2 and retains original-precondition
bypass at x=8. Requires-only, ensures-only, recursive, generic, transitive,
multiple-target, uncontracted and unstubbed controls retain their semantic
expectations and safety checks. Verified/PFC negative preconditions/results,
replacement overflow, replacement pre/postconditions and no-assert expected
panic remain meaningful.

The real #4591 body remains verbatim issue source. Its stub permits i32::MAX;
the caller's addition of1 overflows. The required oracle is therefore a failed
caller addition-overflow property. Synthetic output checks reject a fake
success, an overflow only in abs_val, and compile-error output. The original
i32::MIN negation belongs to the replaced body. No successful proof is claimed
for this issue example. Expected counts describe declared harnesses, never
guessed property quotas.

## Full standard push-CI and next authority gate

All27 package files equal the exact delivery blobs; the manifest seals the
other26. All16 native workflow definitions were parsed from exact969f and
compared with the inventory, including complete jobs, matrices, steps,
conditions, concurrency, permissions and native failure/retry behavior.
Independent branch-push event inspection yields:

| Native workflow | Required instances |
| --- | --- |
| kani.yml | regression on macos-15-intel, ubuntu-22.04, ubuntu-24.04, macos-15, ubuntu-24.04-arm; benchcomp-tests; perf; llbc-regression; documentation |
| format-check.yml | format-check; clippy-check |
| deny.yml | audit |

These twelve instances form one full standard push bundle. Stock regression
still runs both kani and expected suites and the rest of its full suites.
Perf timeouts/retry settings, advisory C formatting, Clippy statistics behavior,
Deny and main-only documentation publication retain native settings. There is
no custom workflow, subset, enablement, cron or dispatch change. Upstream PR-only
release/std/benchmark/metadata scope remains deferred under the owner scope.

The eventual full nonskip head is NOT_CREATED. It must be a new same-tree
sibling with exact sole969f parent, with exactly one nonskip commit in969f..final.
Both skipped candidates stay outside that range. Synthetic gate cases accept
the intended sibling and reject tree drift, old base/source/tree, merge or
candidate parents, extra/missing range entries and skip directives. The actual
final-head gate and remote/event/run/checkout receipts remain future work for
the coordinator; a mock match grants no authority or execution evidence.

Exact APPROVE now permits **root's exact GO decision only**. Usercoordinator
alone launches the separately authorized full standard bundle, item1 31/31,
total42/48. The review consumes zero attempts and changes no ledger; references
remain item1 30/31, item2 11/17, total41/48. Owner alone publishes PRs/issues/
comments or pushes existing PR branches. This review issues no root GO and
performs no launch/publication action.

## Validation and delivery

- Independent static/mock checks: **407 PASS**, including three exact patch
  replays, provider-call premises, source invariance, oracle and workflow gates.
- Inspected author validator replay: **237 PASS**, including bounded fixture
  mutations and synthetic final-head rejection cases.
- New native/compiler/typechecking/rustfmt/Kani/CBMC/fullrunner/CI: **NOT_RUN**.
- Candidate/source/package/old review/history edits: none. No subagents, model
  changes, push, PR, issues/comments, raw CI evidence, GCS, ledger, reservations
  or budget mutation occurred. Requested high/FastOFF settings were not changed.

Only this new review directory is delivered and locally committed with
`[skip ci]`. Unrelated pre-existing untracked S3 review work is left untouched.
Inputs and exact source excerpts accompany the report; manifest hashes seal
the review artifacts. If a future semantic candidate changes, original15
prepares a new immutable repair and the same independent11 reviews its delta.
