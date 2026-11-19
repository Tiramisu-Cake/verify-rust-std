# Exact retention and edit contract

All references identify published031 source, not native observations. Abbreviations: **P** = `tests/kani/FunctionContracts/ordinary_stub.rs`; **N** = `tests/kani/FunctionContracts/ordinary_stub_no_assert.rs`; **F** = `tests/expected/function-contract/ordinary_stub_fail.rs`; **I** = `tests/expected/function-contract/ordinary_stub_issue_4591.rs`; **O** = `tests/expected/function-contract/ordinary_stub_overlap.rs`. Numbers are attribute-start line numbers. PASS/FAIL below means the source-intended harness outcome. Expected-mode fixture success can require a failing harness. This table accounts for every one of the 38 current declarations.

## Every current harness

| Source / harness | Current intended oracle | Exact disposition and rationale |
| --- | --- | --- |
| P:17 `provider` | PASS, Check f | REMOVE. Both-clause Check control is `replacement_provider`; no remaining verified use of f needs its own companion. |
| P:22 `verified_control` | PASS, verified f gives x+1 | REMOVE/MERGE mode control into `replacement_verified_contract`, which also exercises an ordinary alias of the selected provider. |
| P:30 `ordinary_stub` | PASS, g gives x+2 | REWRITE/KEEP as shared ordinary harness A below. Include the outside-precondition and multiple-shape assertions. |
| P:38 `ordinary_stub_outside_target_precondition` | PASS, f(8)==10 | MERGE into A's f(8)==10. Shows original requires and ensures are replaced. |
| P:54 `requires_only_provider` | PASS, Check requires-only target | REMOVE. Shape retained in A under ordinary stubbing; standalone Check cross-product is outside this bug. |
| P:59 `requires_only_verified_control` | PASS, valid precondition | REMOVE. Baseline Replace precondition control; selected-provider interaction is retained separately. |
| P:65 `ensures_only_provider` | PASS, Check identity post | REMOVE. Shape retained in A and issue repro; Check selection retained on combined provider. |
| P:70 `ensures_only_verified_control` | PASS, verified identity result | REMOVE. Repeated mode control; `replacement_verified_contract` retains combined-provider post usage. |
| P:76 `multiple_targets` | PASS, two stubs plus unchanged f | MERGE into A's requires_only, ensures_only and untouched contracted_replacement assertions. No claim that a copied body's source persists into an unstubbed function. |
| P:92 `recursive_provider` | PASS, RecursiveCheck | REMOVE. Independent recursive proof machinery; A retains replacement of a recursion-tagged target without recursive execution. |
| P:97 `recursive_verified_control` | PASS, recursive target Replace | REMOVE. Independent recursive verified-stub machinery, not needed to select a plain replacement's metadata. |
| P:103 `recursive_target` | PASS, recursive(8)==10 | MERGE into A unchanged assertion and stub attribute; retains recursion-tagged target shape. |
| P:119 `generic_instances` | PASS at u8/u16 and equal inputs | MERGE all three assertions and generic stub attribute into A. Retains monomorphized source resolution and original precondition bypass. |
| P:131 `uncontracted_target` | PASS, replacement plus untouched f | MERGE into A. Route uncontracted through requires_only to g; call untouched contracted_replacement instead of f. |
| P:138 `transitive_replacement` | PASS, resolved f/requires_only -> g | MERGE chain obligation into A as uncontracted -> requires_only -> g; f -> g remains direct. Checks resolved final body source, with a contracted intermediate. |
| P:152 `replacement_provider` | PASS, direct Check contracted_replacement | KEEP EXACT. Necessary provider companion and selected-target Check control. One direct target call. |
| P:157 `replacement_contract` | PASS, actual contracted provider at input8 | MERGE into `replacement_contract_target`'s admitted inputs0..15, plus A's direct untouched provider call. Caller checks actual return; nested provider Assert checks its conditions. |
| P:164 `replacement_verified_contract` | PASS, provider Replace through ordinary f | KEEP EXACT. Selected-provider verified contract and ordinary-body-source interaction; input8 violates original f precondition and satisfies provider's. |
| P:177 `replacement_contract_target` | PASS, caller Check / provider Assert | KEEP EXACT. Genuine selected caller call once, arbitrary x with assumed x<16, actual provider return x+3. |
| N:17 `ordinary_stub_original_mode` | PASS, concrete result despite disabled contracts | KEEP harness EXACT; REWRITE provider ensures x+3 -> x+2. Distinct Original-mode/body-supplier branch at f(8). |
| N:23 `provider` | PASS, Check f despite no-assert flag | REMOVE. Orthogonal explicit Check override; default-mode Check retained in P. |
| N:28 `verified_control` | PASS, verified f despite no-assert flag | REMOVE. Orthogonal explicit Replace override; default-mode provider Replace retained in P. |
| N:34 `replacement_provider` | Status SUCCESS via should_panic; bad post fails | REMOVE with should_panic. Provider becomes honest; explicit Check under no-assert is not the ordinary-body-source regression. |
| F:15 `provider` | PASS, Check f | REMOVE. Repeated positive provider in expected failure suite; P retains selected provider Check. |
| F:20 `replacement_overflow` | FAIL, g(MAX) overflows | REMOVE. I retains stronger genuine caller-overflow reproducer; ordinary provider safety instrumentation remains an upstream obligation, not separately re-proved here. |
| F:26 `verified_precondition` | FAIL, verified f requires x<8 at8 | REMOVE. Baseline verified precondition enforcement; focused negative retains provider precondition assertion through an ordinary replacement. |
| F:32 `verified_postcondition` | FAIL, client asserts verified f(7)==9 | REMOVE. A false client assertion about a constrained result, not a failing contract postcondition. |
| F:43 `provider_postcondition` | FAIL, bad_contract Check requires x+2 but returns x | REMOVE/MERGE failing provider post into F:77. It is discriminated from caller post there. |
| F:48 `unstubbed_postcondition` | FAIL, unrelated ordinary stub plus bad_contract Assert | REMOVE. Global default assertion baseline; A retains an unchanged contracted function and F:77 retains nested provider Assert. |
| F:54 `unstubbed_precondition` | FAIL, f(8) precondition with unrelated stub | REMOVE. Same unaffected-target baseline; F:77 retains an independently reachable provider-pre failure. |
| F:60 `replacement_postcondition` | FAIL, bad provider post through f | MERGE into F:77; nested provider fails while caller identity post remains true. |
| F:77 `replacement_provider_postcondition` | FAIL, provider ensures0 at input1 | REWRITE/KEEP as B below. Add provider requires x<4; one caller call with arbitrary0..4. Retain distinct pre/post failure witnesses. |
| F:88 `replacement_precondition` | FAIL, restricted_replacement requires x<4 at4 | MERGE precondition into B's discriminating_replacement and x=4 witness; delete restricted_replacement. |
| F:99 `requires_only_provider` | PASS, Check requires-only | REMOVE. Repeated PFC cross-product. No remaining requires_only verified stub needs this companion. |
| F:104 `requires_only_verified_precondition` | FAIL, verified requires-only at8 | REMOVE. Baseline requires-only verified mode, outside this focused reduction. |
| F:110 `requires_only_verified_result` | FAIL, unconstrained verified return asserted==8 | REMOVE. This unique havoc-specific check is not claimed equivalent to a combined-post verified control; no requires-only Replace change is made by this patch. |
| I:22 `check_caller` | FAIL, actual caller +1 can overflow | KEEP source and expected EXACT. Essential issue4591 regression; fixture must pass by finding the named failure. |
| O:17 `overlapping_contract_target` | Compile error, missing f closure | REMOVE with O and its expected. Internal lookup failure is neither a semantic oracle nor supported-overlap proof. |

## A — precise shared ordinary harness

In P, keep the existing helper definitions `f`, `g`, `requires_only`, `ensures_only`, `recursive` (including its recursion attribute), `generic`, `generic_replacement`, `uncontracted`, `contracted_replacement` and `replacement_caller`. Retain all their current signatures, bodies and attributes. Remove the harness declarations indicated above. Replace only `ordinary_stub`'s attributes/body with this recipe:

```rust
#[kani::proof]
#[kani::stub(f, g)]
#[kani::stub(requires_only, g)]
#[kani::stub(ensures_only, g)]
#[kani::stub(recursive, g)]
#[kani::stub(generic, generic_replacement)]
#[kani::stub(uncontracted, requires_only)]
fn ordinary_stub() {
    assert_eq!(f(8), 10);
    assert_eq!(requires_only(8), 10);
    assert_eq!(ensures_only(8), 10);
    assert_eq!(recursive(8), 10);
    assert_eq!(generic(1u8, 2u8), 2);
    assert_eq!(generic(3u16, 4u16), 4);
    assert_eq!(generic(5u8, 5u8), 5);
    assert_eq!(uncontracted(8), 10);
    assert_eq!(contracted_replacement(8), 11);
}
```

These are independent straight-line assertions under compatible stub mappings. Each replaced body is safe on the chosen inputs. The direct f/requires/ensures cases cover all three contract shapes; recursive and generic assert their distinct body/instance shapes; uncontracted exercises the resolved chain through a contracted intermediate; the final call exercises normal contract processing in the same codegen unit. FnStubPass state is reset for each body; source traversal order itself is not asserted. Four positive harnesses remain in P: `ordinary_stub`, `replacement_provider`, `replacement_verified_contract`, `replacement_contract_target`.

## B — precise single semantic-negative harness

In F, retain `f` exactly, `discriminating_replacement`'s identity body and ensures0, `replacement_caller`'s identity post and body f(x), and the named harness `replacement_provider_postcondition`. Add `#[kani::requires(x < 4)]` to discriminating_replacement. Update its comment to: `// The replacement requires x < 4 and returns x with a zero-result postcondition.` Replace the harness body with:

```rust
let x: u8 = kani::any();
kani::assume(x <= 4);
replacement_caller(x);
```

Keep `#[kani::proof_for_contract(replacement_caller)]` and `#[kani::stub(f, discriminating_replacement)]` unchanged. Delete every other F harness and the now-unused helpers `g`, `bad_contract`, `restricted_replacement`, `requires_only`. There is one selected caller call on each execution; provider is Assert, not Check/Replace. Precondition-failing x=4 and admitted postcondition-failing x=1 are different reachable paths, with no arithmetic. x=0 keeps a satisfying execution. Caller result==x is true on every returning path. A suppressed provider Assert would lose the required failures; a caller-post error would have a different description.

Rewrite F's `.expected` to these minimal fragments (backslash adjacency has compiletest meaning):

```text
assertion\
- Status: FAILURE\
- Description: "x < 4"

assertion\
- Status: FAILURE\
- Description: "|result| *result == 0"

VERIFICATION:- FAILED
Verification failed for - replacement_provider_postcondition
Complete - 0 successfully verified harnesses, 1 failures, 1 total.
```

This is an intended oracle, not captured native output. Because there is only one harness in F, file-wide failure fragments cannot be borrowed from a second failing harness. A future native check must establish both failure descriptions and the named summary; compile errors, unreachable checks, coverage errors and DFCC single-top-level-call failures cannot substitute. Preserve the exact human-facing strings unless actual, authorized native evidence requires a reviewed renderer-only adjustment. Do not add `should_panic`, weaken matching to a generic failure or restore unrelated failures.

## N — focused flag-specific control

Keep N's header flags and helpers f/replacement. Change only replacement's ensures to `#[kani::ensures(|result| *result == x + 2)]`. Its body already returns x+2; its requires x<4 is unchanged. Retain `ordinary_stub_original_mode` exactly and remove N's other three harnesses. This honest contract is valid on its admitted inputs; f(8) verifies the concrete result with both preconditions disabled. No false contract or expected-panic provider is required. This is a separate compiletest invocation because `--no-assert-contracts` is file-wide.

## Every expected fixture and file outcome

| Current file | Required edit / intended compiletest oracle |
| --- | --- |
| P (`ordinary_stub.rs`) | Rewrite A, retain three other named harnesses exactly, delete the rest. Default kani mode: four successful harnesses; command exit success. |
| N (`ordinary_stub_no_assert.rs`) | Honest provider and one retained harness. kani mode: one successful harness; command exit success. |
| F (`ordinary_stub_fail.rs`) | B and its retained helpers only. One semantic-failing harness, both provider condition failures. |
| `tests/expected/function-contract/ordinary_stub_fail.expected` | Replace all 32 old lines with B's exact one-harness oracle. Drop all 11 old named-failure list entries except retained replacement_provider_postcondition; add VERIFICATION FAILED; replace 2/11/13 summary with 0/1/1. Keep ensures0 and x<4 failure fragments, remove overflow/x<8/x+2 fragments. |
| I (`ordinary_stub_issue_4591.rs`) | Byte-exact retention. One semantic-failing caller-overflow harness. |
| `tests/expected/function-contract/ordinary_stub_issue_4591.expected` | Byte-exact retention, including caller.assertion, overflow FAILURE, VERIFICATION FAILED, named failure and 0/1/1 summary. |
| O (`ordinary_stub_overlap.rs`) | Delete entire file. No replacement ICE or diagnostic fixture in this task. |
| `tests/expected/function-contract/ordinary_stub_overlap.expected` | Delete entire file; no orphaned expected file. |

## Final coverage and discovery matrix

| Final harness | Unique obligation and intended observable |
| --- | --- |
| P `ordinary_stub` | PASS: original pre/posts replaced for requires/ensures/both; generic u8/u16 and equal input; recursion-tagged target; transitive final supplier; untouched contracted function. Exact results in A. |
| P `replacement_provider` | PASS: direct selected provider FnDef in Check mode; admitted arbitrary x<16 verifies provider x+3. Required provider companion remains (`kani-compiler/src/kani_middle/mod.rs:88–125` checks for a matching PFC target). |
| P `replacement_verified_contract` | PASS: ordinary f uses provider's verified Replace mode and its post at8; original f's requires x<8 is replaced. f(8)==11. |
| P `replacement_contract_target` | PASS: selected caller Check executed once, nested provider Assert, admitted0..15, actual result x+3 and both provider clauses satisfied. |
| N `ordinary_stub_original_mode` | PASS: Original mode on copied contracted provider under no-assert; concrete f(8)==10 despite both preconditions. |
| F `replacement_provider_postcondition` | FAIL at verification: provider pre x<4 at4 and ensures0 at1; caller identity post stays true; named one-harness summary. |
| I `check_caller` | FAIL at verification: original issue caller addition overflows when ordinary stub returns i32::MAX; caller-specific assertion fragment and named one-harness summary. |

Seven harnesses in four Rust files and two expected files (six test artifacts); the original eight artifacts become six because the overlap pair is deleted. The flag-specific invocation and separate original issue source justify the extra files. Count alone is not the acceptance criterion.

`scripts/kani-regression.sh:50–53,94–111` selects kani/kani and expected/expected. `tools/compiletest/src/main.rs:372–382,483–536` recursively discovers .rs in those modes, including every retained file; .expected files are companion oracles, not separate harnesses. `header.rs:150–152` reads file-wide flags. `runtest.rs:250–263` uses process success for these positive kani files; `:488–505,535–610` checks expected-mode stdout+stderr with substring groups, backslash-linked adjacent lines, and no required successful exit by default. `kani-driver/src/harness_runner.rs:310–339` emits the named failure list and totals. No harness filters or ignore/fixme markers are present in the five current Rust files. This discovery was traced in source; compiletest was not executed.

Future W15 acceptance: exact parent031 and frozen compiler hashes, seven names above with matching attributes, no orphaned expected file, no old cross-product/ICE golden, full source diff and preserved protected trees, static review of caller reachability/call count and both negative witnesses, precise reviewed package/manifest. New native evidence and final PR CI URL remain pending separate review/GO; none is authorized by this matrix.
