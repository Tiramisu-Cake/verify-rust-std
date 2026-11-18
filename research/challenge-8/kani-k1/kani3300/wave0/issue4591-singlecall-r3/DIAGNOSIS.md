# Native single-call failure: fixture repair r3

The published positive fixture executes the selected PFC check twice in one
execution. The unrun negative fixture has the same defect. The body-source
routing introduced for ordinary stubs makes both calls use the provider's own
generated closures, as intended; the existing DFCC single-call assertion then
rejects the second check. Repair the fixtures by checking a caller whose body
uses the ordinary replacement. Keep the compiler and both guards unchanged.

## Exact scope and evidence

Task `98dde2de28e13381092f20c082ba90f90ce34773`, owner01:00 /new15,
high/FastOFF, no subagents or model changes. Published failed base:
`6fca00af805b5c62b58e3e3f29eef183d6939907`, tree
`7a3d5c05b5d663d515c198b2bfa7c4926ae133ac`, sole parent main
`969f4648980a8e66cd0ca32fd3e714a55ac32cef`. Local repair:
`f82934ca97caaa1270d5279054aa950173868be5`, tree
`2ff34bc99ec3fe63579202c196f0ca288e318919`, sole parent published6f.
SOURCE-PINS.json binds objects, files, patches and protected trees.

Connected metadata confirms Kani run44399789701/attempt1 FAILURE, Format
44399789719 SUCCESS and Deny44399789794 SUCCESS, all push events at published6f.
All twelve jobs are accounted: seven success, one failure, four cancelled.
Job135139352062 regression(ubuntu-24.04) fails step4 Execute Kani regression.
The other Kani jobs benchcomp-tests, perf, documentation and llbc-regression
succeed. Four other OS regression jobs are cancelled. Native null step lists
and skipped steps remain visible in native/CONNECTED-METADATA.json.

Frozen INPUTS separately attributes these details to the coordinator: first
kani suite658pass/1fail; replacement_contract_target fails with supplied text
`Only a single top-level call to function contracted_replacement::{closure} when checking contract`;
reported line146; other harnesses in the same file verified; expected, ui and
script-based-pre suites NOT_RUN; matrix cancellations caused by fail-fast.
The count's unit remains the coordinator's suite counting unit. It supplies
no property quota or complete matrix result. The full diagnostic suffix,
property ID, process exit and native source-span mapping are UNKNOWN.
Run head/tree metadata establishes the run association; an actual per-job
checkout SHA/tree is UNKNOWN. These boundaries are retained in
native/FAILURE-PROJECTION.json. No raw logs or archives were read.

## Source chain and the two guards

Citations below use repository paths and line coordinates at the repair,
unless labeled main969f or published6f. SOURCE-EXCERPTS.json retains the exact
ref/blob/range/text; no compiler, expansion or MIR was executed.

1. `library/kani_macros/src/sysroot/contracts/mod.rs:572-587` generates a PFC
   harness with contract initialization, clause-depth reset and the selected
   target attribute. `bootstrap.rs:39-49,83-104` records and dispatches its
   check, replacement, assert and modifies closures. `check.rs:27-61,122-174`
   assumes requires, asserts ensures and invokes the modifies wrapper containing
   the actual source body. These generated closure definitions retain the
   provider's identity when its body is copied into another requested instance.
2. Exact selected-target reachability is enforced by
   `kani-compiler/src/kani_middle/attributes.rs:590-617`: the selected FnDef's
   def_id must occur in the reachable-functions set. `kani_middle/mod.rs:313-340`
   invokes this check, and compiler_interface.rs performs transformed reachability
   before codegen. Reachability of a copied closure inside `f` alone establishes
   neither reachability of the provider FnDef nor a waiver of this guard.
   This code is byte-identical to main969f and published6f.
3. `transform/stubs.rs:44-77,150-167` resets body_source, resolves the provider
   Instance with the requested generic args, validates its body and reports that
   source only on success. Taking the source consumes the per-body Option.
   `transform/mod.rs:114-124,158-188,233-251` runs FnStubPass before the contract
   pass, keeps the requested Instance as the cache key and runs all passes.
4. `transform/contracts.rs:323-374` preserves explicit PFC/verified selection of
   the requested target; otherwise it selects body_source. `386-427` obtains
   check_fn and replace_fns from the harness. `575-603` chooses Check for the
   selected provider, Replace for verified selections, Assert otherwise, or
   Original under --no-assert-contracts. `670-705` retains the corresponding
   closures. In main969f the body-source selector is absent: an ordinary target
   with a replacement body can instead search for its own missing closures.
   The published fix addresses that mismatch; r3 does not change its routing.
5. `codegen/contract.rs:29-52,110-146` finds the exact selected target in reachable
   items, resolves its check/modifies closure and attaches the assigns contract.
   `kani-driver/src/call_goto_instrument.rs:175-212` supplies --dfcc and
   --enforce-contract with that generated wrapper name.
6. Pinned kani-dependencies selects CBMC6.11.0. Its upstream tag resolves to
   commit `820ff0f555b43fb78e0cd9332e498461bd14244b`.
   `src/goto-instrument/contracts/dynamic-frames/dfcc_swap_and_wrap.cpp`, blob
   `2f57751f7ddeb657e2c80249f503113cbb978e26`, lines110-130 and153-212,
   creates __contract_check_in_progress and __contract_checked_once. Before a
   nonrecursive check it asserts !check_completed, with property class
   single_top_level_call and the exact diagnostic prefix supplied by the
   coordinator. On completion it sets checked_once=true and in_progress=false;
   a later sequential call fails. This is a persistent boolean once tracker,
   rather than a count of distinct syntactic function names. Recursive entry
   has separate handling. inputs/CBMC-GUARD-SOURCE.json retains the compact
   source excerpt; CBMC-SOURCE-PIN.json binds tag, commit and blob. Matching tag
   and immutable-commit fetches returned the same blob. The actual native
   binary identity remains UNKNOWN; configured-release source is not a binary
   attestation.

The clause-depth dispatch in contracts.rs:498-527 sends calls *inside contract
clauses* to Original mode. Both failed harness calls execute in normal harness
code, with depth zero. Their simple arithmetic contracts make no calls to the
selected provider. This dispatch does not exempt either harness call.

## Effective checks on published6f

| Fixture/harness | Source calls in execution order | Effective check wrapper | Guard outcome predicted from source |
| --- | --- | --- | --- |
| positive ordinary_stub.rs / replacement_contract_target | contracted_replacement(0); f(any) with f→contracted_replacement | provider modifies/check closure twice | first passes once guard; second fails |
| negative ordinary_stub_fail.rs / replacement_provider_postcondition | discriminating_replacement(0); f(1) with f→discriminating_replacement | provider modifies/check closure twice | first passes once guard; second fails |

Both direct calls satisfy exact-target reachability. For both copied `f` calls,
the requested f is not check_fn; body_source is the selected provider, so the
contract pass chooses that provider's Check mode. The copied and direct bodies
refer to the same provider-generated closure definitions. They therefore share
the enforced wrapper's once tracker.

For the positive, x=0 gives3 and satisfies its contract, then the completed
tracker remains true. For the negative, direct0 returns0 and satisfies ensures0;
the second call reaches the guard before its intended copied-input1
postcondition failure. Its source arithmetic alone cannot establish the
intended native oracle. The positive failure is native/coordinator evidence;
the negative guard failure is a source prediction because its suite never ran.
Neither is upgraded from static checking to measured MIR or native proof.

Frozen authorad50, review0f4 and GO1a32 remain immutable. Their W11-01 reachability
closure and static APPROVE history did not establish the single-call invariant.
The native failure supersedes the old fixture validity expectation. It does not
establish a new compiler routing defect requiring a guard or pass change.

## Minimal supported composition

Only two .rs fixtures change: 16 insertions, 9 removals. Each gains a contracted
replacement_caller(x) whose body returns f(x). Each harness selects that caller
and invokes it once. The selected exact caller FnDef is genuinely reachable;
its modifies/check wrapper executes once. Its f call copies the provider body,
whose own contract runs in Assert mode because that provider is neither the
PFC selection nor a verified stub in that harness.

Positive lines171-181: caller requires x<16 and ensures result==x+3. The provider
has the same domain/post and body x+3. All16 admitted u8 inputs have results3..18;
the nested ordinary stub supplies behavior across the selected caller's whole
domain, including inputs outside original f's x<8 precondition.

Negative lines66-81: caller ensures result==x and invokes f with input1. The
provider's identity body returns1, so the caller post holds while provider
ensures result==0 fails. It has no precondition, assumption or arithmetic to
mask that failure. A mutation to Original mode or identity ensures would remove
this intended provider failure; the source oracle checks that separation. The
golden still requires the unique ensures0 FAILURE description and the named
replacement_provider_postcondition verification failure.

This changes the former two-sequential-check composition into PFC checking a
caller that uses an ordinary contracted replacement. Separate replacement_provider
and replacement_verified_contract continue to exercise the same provider's PFC
and verified modes. Original f/requires-only/ensures-only/recursive PFC and
verified controls remain unchanged. It does not claim that every possible mixed
provider-PFC alias program is unsupported, or establish a new general conflict
policy. The invalid sequential composition is no longer a semantic regression
test. No compile-error expectation replaces it, and no dummy, unreachable,
clause-depth or mutually-exclusive-call trick is used to satisfy validation.

## Preserved goals and next gate

All38 harness declarations survive; only the two affected harness bodies and
their PFC target attributes change. The other36 harness sources and existing
functions are byte-identical to published6f. PFC-AUDIT.json covers all13 PFC
harnesses, including recursion and the unchanged explicit-original-target
overlap error. All eight fixture/oracle paths remain; all .expected bytes remain
unchanged. The u8 f/g safe ordinary case, outside-precondition behavior,
requires/ensures/both contracts, generic/transitive/uncontracted cases,
replacement safety, no-assert mode and negative pre/post controls survive.
The verbatim issue4591 i32 reproducer retains the real caller-addition overflow
counterexample at i32::MAX. It is not a passing proof expectation.

Three isolated-index patch replays reproduce the candidate tree. Offline
source-shape, guard, mutation, arithmetic, inventory and metadata gate checks
pass, with limitations recorded in tests/VALIDATION.json and VALIDATION.md.
They distinguish published6f from the repair and do not override its native
failure. Compilation, rustfmt, typechecking, expansion/MIR, Kani/CBMC and new
native CI are NOT_RUN. Native results for the repair must be obtained later.

Upstream main read-only recheck still observes969f; remote branch still observes
published6f at the recorded times. No rebase or remote update occurs. All
workflows, actions, scripts, libraries, toolchain and dependency bytes match
reviewed main/base. SAME11 exact delta-review is next. After exact APPROVE,
root prepares GO-request HOLD_FOR_OWNER_EXTRA_ITEM1_GRANT; item1 remains
31/31 EXHAUSTED, potential+1 requires owner morning authorization. Static
approval never authorizes CI. No compiler/CI/push/publication/accounting action
occurred in this task; S3 is independent and untouched.
