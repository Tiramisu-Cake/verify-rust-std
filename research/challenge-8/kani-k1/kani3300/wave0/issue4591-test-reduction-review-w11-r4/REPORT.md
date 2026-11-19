# SAME W11 exact r4 delta review

**APPROVE — no blocking findings.** R1–R4 of review `2ed6d7064cd4e30f9337f0d6d288bd70baa41a3b` are closed for the exact package and source below. R5 is **OWNER_TEXT_EXCLUDED**, superseded by owner13:55 and the supplemental contract at input7386; it is not an outstanding code/test gate. No new PR artifact was produced or external PR file accessed.

- Reviewed g0 package: `2a11df42b94cbdfdb567b0ca8d288b0a9cdfc02c`, `research/challenge-8/kani-k1/kani3300/wave0/issue4591-test-reduction-r4/`.
- Source: `2dcb2c2d9325d2aa15c21a325cf0c7c320403466`.
- Tree: `b05ea48016f1cb8f20a1e7032394e602929b6e3b`.
- Sole parent: `031fc085cd4373b5fc93a55128d5a69fdbd88df1`; full-range base: `969f4648980a8e66cd0ca32fd3e714a55ac32cef`.
- Authority: task at `58a74e7436c8214652708bda480f1f9eccd4ad5c`, mandatory DELTA-REVIEW-W11/INPUTS/ROOT-DECISION at `7386fb02477d52a90e468b6b7183a44567497248`, plus root's exact-bound SAME11 assignment.

The supplied root/author PASS claims were checked independently. All eleven package blobs match the exact committed path set; all ten manifest hashes and byte lengths match. The accepted review and matrix hashes match. Independent disposable-index replays of both committed full-index patches reproduce the exact candidate tree. The candidate and frozen r3 worktrees are clean; no candidate edits occurred. CHECKS.json records these checks and the seven source declarations. INPUTS.json records exact provenance.

## Closure of accepted findings

P = `tests/kani/FunctionContracts/ordinary_stub.rs`; N = `tests/kani/FunctionContracts/ordinary_stub_no_assert.rs`; F = `tests/expected/function-contract/ordinary_stub_fail.rs`; I = `tests/expected/function-contract/ordinary_stub_issue_4591.rs`. All following references are to candidate2dcb source. “PASS/FAIL” denotes intended future verification behavior, not an observed native result.

| Finding | Independently checked closure |
| --- | --- |
| R1 repeated matrix | P:17–34 is byte-exact recipe A, including all six compatible stub attributes and nine assertions. Its ten helper declarations and the three retained controls are byte-exact versus031. P now has four harnesses; the redundant PFC/verified cross-products are gone. Together with N/F/I, exactly the accepted seven names remain. No additional helper or harness was introduced. |
| R2 overlap golden | Both `ordinary_stub_overlap.rs` and `.expected` are deleted. The six-path delta contains both deletions; no substitute internal missing-closure oracle or orphaned overlap expected file remains. Same-target overlap support remains outside this fix. |
| R3 no-assert | N:11–21 retains requires x<4, changes ensures to the actual x+2 body, keeps the exact ordinary harness and its file-wide flag, and removes the other three harnesses. The admitted provider domain0..3 has an honest postcondition; f(8)==10 separately exercises suppression of both original and provider preconditions in Original mode. |
| R4 semantic negative | F:11–29 exactly implements B: provider identity body, requires x<4, ensures0; caller identity post; arbitrary u8 constrained to x<=4; exactly one selected caller call. F.expected:1–11 exactly matches the accepted two adjacent FAILURE-description groups, VERIFICATION FAILED, named failing harness and 0/1/1 summary. Other negative-suite harnesses and unused helpers are removed. |

The delta changes exactly the authorized six paths and nothing else. All three compiler SHA256 values, the entire kani-compiler/library/scripts/workflows trees and issue4591 source/expected pair are unchanged relative to031. All other tracked paths are unchanged by exact Git tree comparison. The earlier compiler assessment therefore carries forward only through byte-exact invariance; no compiler/comment exception is requested. The only new explanatory test comment describes the negative provider's actual contract/body. Headers, license markers, file flags and existing helper comments remain suitable for the code as written.

## Seven retained obligations

| Candidate reference / harness | Distinct obligation and intended observable |
| --- | --- |
| P:17 `ordinary_stub` | PASS: requires-only, ensures-only and both-clause targets use plain g; recursion-tagged target loses original recursion/contracts; generic u8/u16 and equal-input cases use the generic replacement; uncontracted -> requires_only -> g uses the resolved final supplier; untouched contracted_replacement still checks normally. Nine exact results: 10,10,10,10,2,4,5,10,11. |
| P:73 `replacement_provider` | PASS: direct selected provider Check. Its exact FnDef is called once at arbitrary input; requires admits0..15, actual x+3 is3..18 and satisfies its post. This also supplies the required matching PFC target for stub_verified. |
| P:78 `replacement_verified_contract` | PASS: ordinary f's copied provider is selected for verified Replace; input8 satisfies provider requires but violates original f requires. Provider post gives f(8)==11. |
| P:91 `replacement_contract_target` | PASS: selected caller Check executes once; its body calls f once, whose copied provider runs Assert. Caller and provider pre/posts agree on admitted0..15 and actual x+3. |
| N:17 `ordinary_stub_original_mode` | PASS: --no-assert-contracts selects Original processing for the copied contracted provider; concrete f(8)==10 despite the two preconditions. This mode still needs the correct supplier for generated-closure handling. |
| F:23 `replacement_provider_postcondition` | Verification FAIL: admitted x=1 fails provider ensures0; x=4 fails provider requires x<4; x=0 satisfies both. Caller result==x is true on every returning path, with no arithmetic/overflow alternative. Both named description groups and the single failing-harness summary are required. |
| I:22 `check_caller` | Verification FAIL: byte-exact issue4591 repro permits stub result i32::MAX and actual caller +1 overflows. I.expected retains caller.assertion, overflow FAILURE, VERIFICATION FAILED, the named failure and 0/1/1 summary. |

These seven declarations in four Rust files and two expected companions match the accepted matrix; the reduction removes31 declarations without claiming equivalent coverage for every removed baseline cross-product. Generic instance resolution, transitive final-supplier selection, recursion-tagged target shape, default provider assertions, provider Check/Replace, caller composition and Original mode remain represented.

The positive verified-provider result is consistent with the provider's exact postcondition; it does not by itself distinguish every possible havoc implementation from its concrete body. Full recursive Check/Replace, requires-only unconstrained-return havoc, generic contracted providers, extern stubs, modifies and general mixed-alias behavior remain outside this bounded change, as stated in the accepted review. Existing upstream suites are untouched. Deleting the overlap golden does not repair or hide an overlap defect.

## Guard, discovery and oracle checks

P:93–94 selects replacement_caller and calls that exact function once; F:23–28 does likewise on its arbitrary0..4 input. Each caller body has one f(x), and each copied provider is unselected for PFC/verified stubbing in that caller harness, so it uses Assert mode. There is no dummy direct provider call in either caller harness. The direct provider proof is separate at P:73–75. This preserves the repair for exact-target reachability (`kani_middle/attributes.rs:594–615`) and avoids the known sequential-two-Check arrangement. Byte-exact compiler and driver identities preserve the guard mechanism assessed earlier; this review has not established a native CBMC identity or run its once guard. `kani_middle/mod.rs:88–125`'s verified-provider companion requirement is satisfied by the retained direct provider PFC.

For F, failure of requires at4 cannot eliminate the postcondition witness at1, which satisfies requires; the satisfying input0 also remains in the source domain. Replacing provider Assert with Original would remove the required provider failures while leaving the caller post true. A caller-post failure has a different description. A compilation/reachability/DFCC error alone cannot supply the required verification details and named terminal summary. This is source reasoning; actual property reachability and renderer output require future native evidence.

Discovery and oracle behavior inherit exact unchanged sources: `scripts/kani-regression.sh:50–53,94–100` selects kani/kani and expected/expected; `tools/compiletest/src/main.rs:372–382,483–536` recursively discovers these .rs files; `header.rs:150–152` reads their file flags. Positive kani cases require successful invocation (`runtest.rs:250–263`). Expected-mode compares stdout+stderr, permits unsuccessful invocation by default, and links backslash-suffixed fragments to consecutive output lines (`runtest.rs:488–505,535–610`). `kani-driver/src/harness_runner.rs:310–339` renders the named failures/totals. F's two triples bind FAILURE to each required description; its single harness prevents borrowing a provider failure from another harness. I retains the caller-specific triple. There are no added filters, ignore/fixme markers or should_panic controls. These routes were inspected statically; compiletest was not run.

## Evidence limits and next gate

This exact candidate's compilation, expansion, MIR, Kani/CBMC, verifier, compiletest, native formatting and full standard CI are **NOT_RUN**. No current-main native failure or candidate fixed-PASS comparison has been established. A successful regression for F/I means matching intended semantic failures; it does not mean those harnesses verify successfully. No B1/B2 or independent proof credit follows from static arithmetic, source identity, patch replay or this approval.

Historical r3 Kani44461123962 remains FAILURE; Format/Deny successes and job-level regression successes do not validate this new tree. Perf/shutdown/s2n cause remains coordinator-reported with independent attribution UNKNOWN. No full-green, speedup or named-harness observed-pass claim is made. Actual future publication head/ref and CI run are UNKNOWN.

Root may verify this sealed APPROVE packet and prepare a separate full-standard-CI GO request. Approval itself authorizes no native execution, push, publication, dispatch or accounting. A future nonskip same-tree sibling must retain sole parent031 and be bound to the reviewed package under the coordinator's separate authority. R5 owner text is excluded and may change independently. S4P2, historical packets and ledgers are untouched.
