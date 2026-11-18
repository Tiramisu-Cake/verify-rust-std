# Source trace and scope

W15/new15, Fast OFF, no subagents. Task input is g0
`0396e88e1557104fd081587cc453f6cd22bcfbe1`. `SOURCE-PINS.json` binds the
isolated source worktree, stock main, candidate, trees, single parent, patches,
test files and protected paths. Main is
`faffcee3bca2770c03bd21c3bde89cc8f6f7a14e`; its tree is
`09b828b47c93e90e140e8c41f9048109a2f4a786` and parent is
`a3c8b8610739aab7d2c864bd4021086a5e7c0d94`.

Original coding inputs were that exact main and our own source trace, plus the owner
clean-room exception for issue #4591 and its two comments. `ISSUE-4591.json`
retains those public inputs. The maintainer's comment is
https://github.com/model-checking/kani/issues/4591#issuecomment-4946988101.
No unrelated third-party PR, patch or implementation was consulted. The
isolated branch has a single direct child of stock main; F4 and unpublished
tool stacks are absent. F4's requested CI scope was consulted only as an
owner-provided process precedent; its implementation was not a coding input.

## Failure path on stock main

1. `codegen_units::group_by_stubs` groups harnesses by ordinary stub maps and
   contract usages, then applies ordinary stub transitivity. Unit validation
   checks signature compatibility. Duplicate mappings and cycles retain their
   current diagnostics in `stubbing/annotations.rs` and `codegen_units.rs`.
2. `BodyTransformation::body_ref` loads and caches a body under the requested
   original `Instance`. The configured pass order is automatic harness,
   automatic arbitrary, `FnStubPass`, `ExternFnStubPass`,
   `FunctionWithContractPass`, `AnyModifiesPass`, intrinsic/loop passes, and
   enabled safety instrumentation. Stubbing passes execute before instrumenting
   passes, preserving the current grouping in `add_pass`.
3. `FnStubPass` filters to ordinary mappings with bodies at both ends, resolves
   the replacement with the actual generic arguments and runs
   `FnStubValidator::validate`, including constant and trait-bound validation.
   A successful result supplies the replacement's checked monomorphized body.
4. Main passes the original instance to every later pass. A contracted original
   therefore selects its original contract mode even though its body has been
   replaced. `mark_unused` searches that replacement body for the original
   recursion/check/replace/assert closure names. `find_closure` aborts on the
   missing original recursion closure, before native verification can start.

## Change

`FnStubPass` emits the resolved body source through `take_body_source` only
after successful validation and body replacement. It resets that state on each
invocation, and the caller consumes it immediately. `body_ref` initializes the
source to the requested instance for each cache miss, retains the original
cache key, and still runs every configured pass. There is no guard based on a
name, a unit containing some stub, or missing closure metadata.

The default `transform_instance` keeps the requested instance. The contract
pass overrides it to use the resolved source for ordinary replacements. A plain
replacement thus has no original contract closure lookup, precondition or
postcondition instrumentation. A contracted replacement selects and processes
its own contract, using its own closure definitions and the current harness's
contract mode. Its closure pruning remains checked by `find_closure`.

All other passes continue to receive the original instance and replaced body,
exactly as on main. `ExternFnStubPass`, `AnyModifiesPass`, intrinsic and loop
transforms, enabled validity/uninitialized-memory checks and generated-loop
bindings retain their ordering and original cache ownership. Replacement
overflow remains a verification failure. No missing-closure diagnostic was
removed, downgraded or globally suppressed.

## Modes and overlapping configurations

| Requested body / selected mode | Contract pass instance |
| --- | --- |
| Unchanged body, Assert / Original / Check / Replace | Original, as on main |
| Successful ordinary replacement, original in Assert / Original | Resolved replacement source |
| Original explicitly selected by PFC (simple or recursive) | Original target |
| Original explicitly selected by `stub_verified` | Original target |
| Replacement itself has a contract | Replacement, with its own Assert / Original / Check / Replace mode |

Same-function PFC and verified harnesses in separate codegen units keep the
original bodies/contracts. Ordinary and verified stubs of different functions
can coexist. When a provider is itself the target of PFC or `stub_verified`, its
contract mode also applies to its body copied into an ordinary target; direct
and copied uses select the same provider closure mode. The tests include both
provider-target overlaps, including a failing provider postcondition.

An ordinary stub of the very same target explicitly selected by PFC or
`stub_verified` retains main's unsupported/error path. In particular, the
combined overlap regression still searches for the original `f` closure and
fails compilation. The guard preserves both explicit modes, and their current
PFC-over-Replace precedence. This package does not decide whether that separate
configuration should check the original, check a replacement against the
original specification, or reject the combination with a new diagnostic. It
must not gain original-proof credit through a plain replacement. Supporting
that combination would require an explicit policy decision; it is outside the
ordinary Assert/Original case fixed here. No new diagnostic or contract
precedence policy is introduced.

Transitive ordinary mappings still resolve in `apply_transitivity`. Generic
resolution, validation failure, bodyless/extern call redirection, duplicate and
cycle handling are unchanged. An invalid or inactive ordinary replacement
leaves the body source as the original. Closures retain their original
cache identities and the contract pass's normal unused-closure handling.

These are source-level conclusions. Compilation, expansion, Kani verification
and new native main/fix results are NOT_RUN.

## W11-01 fixture-only delta

The compiler/source analysis above is retained from the frozen delivery. All
three compiler file blobs and the entire kani-compiler tree match reviewed
`a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a`; fix.patch is byte-identical too.
The r1 candidate is a new sibling with sole parent frozen main, carrying that
reviewed compiler change and only the fixture/oracle repair described in
W11-01-CLOSURE.md. Frozen g0 and review packages are unchanged.

Each repaired harness now directly calls its exact selected provider before
calling ordinary-stubbed f. The positive provider call at input 0 satisfies its
own pre/postconditions. The dedicated negative provider returns x with ensures
result == 0: direct input 0 passes, copied input 1 fails. Existing bad_contract
and every other fixture function/control are unchanged. This supplies a lexical
call edge in each harness; exact compiler FnDef/MIR reachability and native
verification remain NOT_RUN. See pfc_fixture_check.py for the restricted static
regression and rejected mutations.

MAIN-CHECK.json records upstream drift to
`969f4648980a8e66cd0ca32fd3e714a55ac32cef`. The specified main parent remains
frozen. No rebase or GO is inferred; root/coordinator must resolve drift before
CI/publication. Only the usercoordinator may launch the authorized full standard
push-CI bundle; only the owner publishes PR/issues/comments.
