# Original15 — localized W11-01 PFC fixture repair (ISSUED /new15)

Owner23:38 explicitly requested fresh15. Read frozen review
54ea8a918b761dc67213f7f24ae5163b7f463b42 at
kani3300/wave0/issue4591-fix-review-w11/REPORT.md and HANDOFF.md.
Original g0 bdf1bb42189257c9654eb55dfcda11b2f08a0b01 and source
a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a/tree98fae98ce9e783bed0393d35657674da09c3aa31
remain immutable; sole main parent faffcee3bca2770c03bd21c3bde89cc8f6f7a14e.
Current high/FastOFF, no subagents/model changes; STOP only real blocker.

W11-01: replacement_contract_target (ordinary_stub.rs:171) and
replacement_provider_postcondition (ordinary_stub_fail.rs:66) select PFC providers
but call only ordinary-substituted f. Exact provider FnDef is unreachable;
compiler reachability rejects the file before semantic verification. The
review independently found no additional compiler-routing blocker.

Repair ONLY fixtures/necessary test oracles and package bindings. Make each PFC
provider genuinely reachable IN ITS OWN harness alongside the copied call.
Positive: valid direct provider and copied f call. Negative: directly called
provider must pass for its direct input, while the copied body call exposes the
intended postcondition failure. Existing bad_contract fails every input; simply
adding a failing direct call would mask copied-provider mode and is forbidden.
Use a discriminating dedicated provider/input arrangement or equivalent oracle;
preserve existing negative controls and source safety assertions. Do not weaken
reachability guard, switch to compile-error oracle, remove test, or alter the
compiler routing without a new concrete finding returned to root. Add a narrow
static regression for per-harness exact selected-target reachability plus
copied-path-negative/direct-path-positive discrimination; it is not MIR proof.

Create new isolated same-main-parent candidate (sibling, not child of skipped
candidate) and immutable g0 output kani3300/wave0/issue4591-fix-r1/. Preserve all
old packages/reviews/native NOT_RUN and source analysis. Rebind exact full
main/source/tree/parent/test/patch/CI request/oracle/manifest pins; regression
fixtures may change, compiler three-file bytes MUST remain reviewed a7b bytes.
All16 standard workflows/scripts/actions unchanged. One full native push-CI
bundle on a future nonskip same-tree sibling/sole main parent, no custom CI,
no enable/cron/dispatch. Night root+usercoordinator decide work/GO; only owner
publishes PR/issue/comments or pushes open PR branches. Native main/fixed NOT_RUN.

Meaningful targeted static/mock checks, both patch replays, source/standard-CI
invariance and actual final object provenance. No cargo/rustc/rustfmt/Kani/CBMC/
expansion/compiler/verifier/fullrunner/CI/push/PR/issues/ledger/reservation/budget.
Budget30/31 item1,11/17 item2,total41/48 unchanged. Ownpaths commit --only [skip ci]
Tiramisu-Cake <igkharin@gmail.com>. READY fullg0/source/tree/parent/patch/test/CI
pins plus W11-01 closure explanation, then SAME11 delta-review -> root GO only.
