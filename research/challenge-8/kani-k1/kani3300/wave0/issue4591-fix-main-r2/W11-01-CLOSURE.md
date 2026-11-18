# W11-01 author repair mapping — independent closure pending

Original review54ea8a918b761dc67213f7f24ae5163b7f463b42 reported unreachable
selected providers in two PFC fixtures. Frozen original g0/source are
bdf1bb42189257c9654eb55dfcda11b2f08a0b01 /
a7bca98c91cbfa595bdc2a1bdc6bd4d0a4fa796a.
Repaired r1 g0/source remain 1d7ef5455f2ea790cd98dde9f38565edb59357ea /
e6aa083da3c93f3189039077795cc9a0d67d3a6d. That repair has NOT been independently CLOSED.

Current candidate 3a770b5db51ba07acffce3483bde0901e6533f3a, tree 7a3d5c05b5d663d515c198b2bfa7c4926ae133ac, has exactly
main969f4648980a8e66cd0ca32fd3e714a55ac32cef as sole parent. Its eight fixture/oracle files exactly match
r1; their transfer introduces no further control or semantic change.

| Harness | Direct selected provider | Copied path | Source expectation |
| --- | --- | --- | --- |
| replacement_contract_target | contracted_replacement(0) | f(kani::any()) | Both uses satisfy the provider's Check-mode contract; requires x < 16 bounds x + 3 |
| replacement_provider_postcondition | discriminating_replacement(0) | f(1) | Identity provider ensures result == 0: direct passes, copied fails the intended postcondition |

The direct calls are unconditional standalone statements within each affected
harness. Another harness's call supplies no credit. The negative has a dedicated
provider with no requires or arithmetic: direct0 returns0 and satisfies its
postcondition, copied1 returns1 and violates it. It never adds a directly failing
bad_contract call. Existing bad_contract and all remaining controls/safety
assertions are preserved. The unique expected FAILURE description is
"|result| *result == 0"; all old expected descriptions, named failures and
2 successful / 11 failed / 13 total harness counts remain unchanged.

pfc_fixture_check.py inventories direct lexical target calls per PFC harness,
requires both repaired bodies' exact unconditional call sequence, pins the
identity provider/postcondition, and rejects original unreachable fixtures,
missing/comment-only/dead/cross-harness direct calls, failing direct input,
passing/missing copied input and weakened postcondition. Every other original
fixture function/attribute is compared unchanged. It is a restricted lexical
and Python arithmetic guard, not compiler FnDef binding or MIR proof.
The unsupported overlap compile-error fixture remains a lexical control only.

The new-base transfer preserves the repaired compiler patch content while
retaining every upstream main969f change; see NEWBASE-ANALYSIS.md and
TRANSFER.json. Exact source/provider FnDef reachability and semantic execution
still need independent review and future native validation. No compile-error
oracle replaces either affected semantic fixture. All current-main/fixed native,
compiler/typechecking, expansion, Kani/CBMC, fullrunner and CI remain NOT_RUN.

Next is ONE same independent11 delta review combining W11-01 and new base.
Only that reviewer may independently close the finding. Exact APPROVE then
permits root GO consideration; usercoordinator alone launches the full standard
push bundle after GO, and owner alone publishes PR/issues/comments. No attempt
or accounting is consumed here; reference item1 30/31, item2 11/17, total41/48.
