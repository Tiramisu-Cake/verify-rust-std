# Historical stage0 dependency review — superseded by accepted variant C

Stage0 was a static dependency/test-map assessment at `d1dbc70afd`. The findings below were not runtime outcomes. Variant C was accepted by the coordinator at `4fef62ad67`; update worker15 maps and Quick plan accordingly. This file preserves what the earlier review found and records how the accepted decision resolves the plan-level stop without claiming that tests ran.

| Historical question | Static finding (not a run) | Accepted variant C disposition |
|---|---|---|
| Head1 integration qualification | The complete ordinary cycle/DAG/root-order fixtures use MU; ordinary-slots payload/padding need STORAGE4 and positive includes storage plus ordinary/PFC closures needing5. ActiveCalls9 uses synthetic keys. FunctionContracts alone does not establish selected contract MIR or ordinary entry seeding. | Head1 is `NO_REGRESSION`, not integration-qualified. Preserve full baseline uninit/delayed-UB, inherited B1 controls, all kani FunctionContracts, full expected function-contract, ActiveCalls9 and common Quick. Keep owner1 obligations pending: listed traversal/ordinary-entry fixtures at4; positive/capture/contract fixtures at5. No test filtering or weakened golden. |
| Head3 nested layout qualification | Nested Pat/enum and raw-eq-uninit full fixtures perform local MU storage assignment/move; u8 mixed/promoted raw_eq alone does not qualify these offsets. | Source ownership stays3; run whole fixtures at4 and preserve nested qualification as pending until exact cumulative head4 results. |
| Head4 marked-model controls | Both controls return ordinary Byte union via Arbitrary::any. Earlier source map placed the constant branch at6. | Corrected source-map assigns the exact five-line `B1--F:19:009` part +420/count5 (F420..424) to STORAGE4. Both marked-model controls run at4. Canonical hunk and part hashes are recorded in ORACLE-MAP.json. |
| Head4 PFC modifies companion | `generated-modifies-no-shadow` uses a captured contract environment; other hook controls do not imply that fixture is runnable at4. | Keep `generated-modifies-no-shadow` at5; all other hook controls, including marked-model pair, qualify at4. |

## Limits and provenance

No MIR extraction or new runtime observation is claimed. Exact source coordinates establish the static source-map assignment only; they do not independently prove AST/MIR binding or causality. U/B1/F remain fixed, and F is unchanged. This decision updates test scheduling and metadata, not production semantics.

## Preserved golden-precision boundary

The earlier exactness audit found 134 of182 shipped F goldens are literal-only without an exact property-N anchor;48 have exact N. This is a precision limit, not a plan failure. Preserve literal constraints byte-for-byte and do not invent counts. These are historical static identities; no runtime verdict is implied.
