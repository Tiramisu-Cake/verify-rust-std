# W11-01: source repair ready for same11 delta-review

Frozen review: 54ea8a918b761dc67213f7f24ae5163b7f463b42, REPORT.md and HANDOFF.md.
Frozen g0: bdf1bb42189257c9654eb55dfcda11b2f08a0b01.
Frozen source: a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a,
tree 98fae98ce9e783bed0393d35657674da09c3aa31.
Repair source: e6aa083da3c93f3189039077795cc9a0d67d3a6d,
tree 01140856c15e161ff6fc4c1ce460fd4208a298cd,
sole parent faffcee3bca2770c03bd21c3bde89cc8f6f7a14e.

The two selected provider wrappers were absent from their own harness call
graphs. Calling only f after copying a provider body does not make that exact
provider FnDef reachable. The repair adds a genuine standalone direct call
before the copied call in each affected harness.

| Harness | Exact selected target / direct call | Copied call | Source expectation |
| --- | --- | --- | --- |
| replacement_contract_target | contracted_replacement(0) | f(kani::any()) | Both Check-mode uses satisfy provider contract; requires x < 16 bounds x + 3 |
| replacement_provider_postcondition | discriminating_replacement(0) | f(1) | Identity provider ensures result == 0: direct passes, copied fails |

The negative uses a dedicated provider with no requires or arithmetic. It does
not directly call failing bad_contract. Its only direct input returns 0, which
satisfies the postcondition. The copied call returns 1 and violates the same
postcondition. Merely adding a directly failing call would mask the copied-mode
control; this repair rejects that arrangement. The new unique FAILURE property
description is pinned in ordinary_stub_fail.expected. All old descriptions,
named failures and the two-success/eleven-failure summary remain intact.

Only three files differ from frozen source: the two affected .rs fixtures and
their negative .expected file. All other fixture functions/attributes and all
source safety assertions are unchanged. All three compiler files and the whole
kani-compiler tree match frozen source exactly. All16 workflows, scripts,
actions, library and toolchain/dependencies retain frozen main bytes.

pfc_fixture_check.py checks direct selected-target calls per harness, including
other PFC controls. For the repaired bodies it requires unconditional standalone
calls in exact order and both paths. Its synthetic mutations reject missing,
comment-only, dead-branch, cross-harness and failing direct calls, passing or
missing copied calls, a weakened postcondition and both original broken
fixtures. All other original functions and attributes are compared unchanged.
The compile-error overlap fixture remains a lexical inventory control only;
no reachability/proof credit is claimed for its unsupported configuration.

This is source-derived closure offered for the same independent11 reviewer.
Static lexical checks do not establish compiler FnDef binding or MIR reachability.
Compiler, cargo/rustc/rustfmt, expansion, Kani/CBMC, native main/fixed,
fullrunner, CI and publication are NOT_RUN. No semantic/native credit is claimed.

Upstream main drift is recorded in MAIN-CHECK.json. The frozen sole parent is
preserved, and root/coordinator must resolve drift before GO. After same11
delta APPROVE, root alone decides GO; usercoordinator launches full standard
push-CI; owner alone publishes PR/issues/comments. No dispatch or publication
is authorized by READY. Budgets stay item1 30/31, item2 11/17, total41/48.
