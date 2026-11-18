# W15 — ordinary stub of contracted function: MRE + main confirmation package

ISSUED by owner now, fresh /new15. Verification correctness, not security.
Current pane model/reasoning/tier, Fast OFF; no subagents. STOP only a real blocker
with evidence, not time/volume/context. Compact stage: independent from R5/F4.

Owner grants +1 item1 for MAIN MRE CONFIRMATION ONLY: currently29/30; item2
10/17 after separately granted+3; total39/47. Ledger is owned by coordinator;
never edit/account/reserve it. CI dispatch still requires an exact ready package,
independent14 or11 review and separate coordinator/owner GO. No automatic run.

## Frozen baseline and clean room

Connected GitHub branches/main metadata checked by root this turn:
model-checking/kani main faffcee3bca2770c03bd21c3bde89cc8f6f7a14e,
tree09b828b47c93e90e140e8c41f9048109a2f4a786,
parenta3c8b8610739aab7d2c864bd4021086a5e7c0d94. Freeze this exact baseline,
record source/object hashes, and check relevant current-main drift read-only
before final handoff. Use shared Git objects and own isolated worktrees/namespaces;
never reset/change existing workers' trees, public refs or F4 branch.
Read baseline AGENTS.md and STYLE-UPSTREAM-RULES.md. Clean room unchanged: no
third-party PRs/diffs/patches/code/links in coding materials; use upstream main
source/docs/tests and our own source-derived analysis. No verify-rust-std code,
crate or toolchain dependency, no F4 compiler patch or experimental tool stack.

Own source diagnostic navigation only: g004c61ba50ae4d62caaf87ed84b90e84e958c184f,
kani3300/ch8-s2/r3-closure-diagnostic/SOURCE-TRACE.md and REPORT.md. On old0aac,
FnStubPass replaces the body with g while retaining f's instance; contracts.rs
find_closure/mark_unused searches f's closure names in the replacement body.
S2 had missing __kani_recursion_check_swap_if_less and compiled after removing
contracted ordinary stubs. This supports a mechanism, NOT a native MRE on main
or unique historical unit/body diagnosis. Re-establish source path on exact main.

## Deliver one compact, runnable confirmation packet

1. Minimal standalone dependency-free crate, one ordinary-stub failing harness:
   #[kani::stub(f,g)] calls a small contracted f. Put the smallest needed
   proof_for_contract provider and stub_verified positive control alongside in
   the SAME crate; avoid duplicate crates or large matrix. Use exact selections/
   cfg separation if needed so an ordinary-stub compilation failure cannot
   erase the provider/control observations. Record each invocation/selected
   harness/cfg and why unrelated targets cannot mask it. Main MRE is NOT_RUN.
   Choose distinguishable f/g behavior and meaningful assertions so a successful
   result actually witnesses the intended ordinary substitution, not dead code.
   Explain relation between control validity and the contracts under test.

2. Source analysis: trace ordinary vs verified stub dispatch, pass order, original
   instance/attributes vs selected body, macro-generated closure/debug metadata,
   mark_unused/find_closure for relevant modes on exact current main. Determine
   from source/docs/tests whether ordinary replacement should supersede contract
   instrumentation or is deliberately unsupported and should emit a clear user
   error. Separate documented semantics, source inference, design recommendation,
   and unseen MIR/native behavior. Do not call a missing closure proof of a
   recursion-mode execution or blame old()/generics without evidence.

3. Propose a minimal fix candidate and upstream-style regression in tests/,
   with exact patch/locations, expected main-fail vs fixed-pass (both NOT_RUN).
   Keep confirmation baseline completely STOCK main: fix candidate/patch only
   in separate isolated tree or packet, never mix it into main confirmation.
   Preserve stub_verified/PFC checking, contracts on unstubbed calls, recursive
   contract modes and ordinary noncontract stubs. Do not silently skip missing
   closures for arbitrary functions or weaken proof checks. If support semantics
   is unresolved, report precise alternatives rather than broad compiler rewrite.

4. Prepare CI confirmation NOW, modeled on our wave0/f4-confirm pipeline, but
   minimal slots for this defect. Source compiler is exact STOCK main, fixture
   no dependencies. Reuse established bounded runner/error-path controls and
   exact head/tree/parent/request binding, runtime caps, per-invocation native
   exit/signal/diagnostic and inventory reporting; do not transplant unrelated
   fixture semantics. Build/setup, PFC/verified-control, ordinary reproduction
   must be separately observable even when reproduction has no RESULTS.
   Native build failure is distinct from the intended target compilation error.

   Predeclare per-slot and overall oracles:
   - DEFECT_PRESENT: valid baseline/control invocations plus exact expected
     missing-contract-closure error bound to selected ordinary-stub target on
     stock main. Preserve abort/compiler exit and structured diagnostics.
   - DEFECT_ABSENT: controls valid and ordinary case compiles/runs with expected
     stub semantics; or an explicit documented unsupported-combination diagnostic
     may be a distinct recorded behavior, never silently equated with success.
     State precisely how this affects the defect classification/recommendation.
   - INCONCLUSIVE: setup/build/control failure, unrelated compiler error, missing
     or incomplete evidence, wrong target, timeout/RSS/spawn error. No generic
     nonzero exit counts as reproduction. Keep actual runtime outcomes NOT_RUN.

   Produce one compact result.json artifact with schema, exact source/tool/cfg/
   argv/invocation identities, per-slot status, diagnostic completeness/caps,
   classification/reasons and independently checkable digest/inventory. Capture
   relevant rustc error blocks independently from head/tail preview. Service
   error-path tests via Python/mock fixtures for true/false/partial/timeout/
   missing-control cases. No raw full logs/evidence archives/GCS bypass.

## Output and boundaries

g0 write scope ONLY kani3300/wave0/stub-contract-confirm/: PINS/INPUTS,
source trace, minimal crate and patches, regression/fix proposal, CI-REQUEST
JSON/Markdown + workflow/runner patches, classification/oracle table, compact
schema, bounded static/mock VALIDATION, manifest and HANDOFF READY_FOR_REVIEW.
Source/control trees isolated with exact base/head/tree/parent, patch hashes,
checkout-depth checks. Explain fixture vs stock main compiler binding; label
main/fixed runtime, compile/MIR observations and confirmation all NOT_RUN.
No issue/PR publication or messages to third parties; owner decides later.

No local cargo/rustc/Kani/CBMC/rustfmt/native expansion/verifier/full runner,
CI/rerun/cancel/push/PR/issues/labels/ledger/reservation/budget/source publication.
Python/static/synthetic/mock/Git/read-only upstream checks allowed. Do not edit
R5 packets, sourcebd62, S2 control or any F4 branch/workflow. Stage exact ownpaths,
--only [skip ci], authorTiramisu-Cake <igkharin@gmail.com>. READY fullg0/main/
fixture/control/tree/parent/request/workflow pins and compact findings.
Next independent14/11 review then exact GO-request; never dispatch yourself.
