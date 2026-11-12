# R6 complementary pair inside Hbuf

Stage only: worker15 prepares two reviewed direct R1 children; Cloud$0, dispatch0. Hcopy/GLUE stay exact R1. No third variant, production repair, automatic next stage or new baseline run. Both candidates are NOT_RELEASE_CANDIDATE.

The planner reports R5-01 bcc1a2af3f/run43268005490: 145 properties, 11639 symex steps, VCC476→182, 846480 variables/51218835 clauses, ConvertSSA8.5s, reached solver. R5-02 899ffb5f26/run43268011610: 150 properties, 9971 steps, VCC569→120, >6.68GiB killed before size print. These are coordinator-reported outcomes, without independently observed retained paths/failures/phase bindings. They motivate a cut inside Hbuf, not global independence or a semantic PASS. Prior R1/V01/R4 runs are reused, never rerun or rewritten. Selection-only V01 was insufficient; selection+reset is a different joint cut.

1. R6-01/P1: R1 Hrepr + U Hepoch. This drops mandatory return selection and epoch invalidation together; normal matched consumption, live scalar capture and marked membership remain. Active/stale buffer can survive initialize. False transfer, mandatory return and epoch guarantees are diagnostically lost. Legal PASS cannot establish acceptance.
2. R6-02/P1: U Hrepr + R1 Hepoch. Mandatory return0 and explicit epoch None are restored on unmarked Option pointer representation. Saved pointer can outlive a source return slot. Store/consume/reset writes can fail frame, Unsupported or invalid-source paths; None does not repair private membership. No R4-A extension or new assumptions.

Only coordinator may perform sequential build/inventory→admitted solver, same P1 bytes/root/settings, timeout300s/watchdog>6GiB. Build failure means solver NOT_RUN. Cutoff means INCOMPLETE. Partial/no-match/capped inventories stay UNKNOWN, and early failure may change obligations. Model size/ConvertSSA/SAT-entry and semantic failure inventory are separate dimensions.

| Observed conversion after real build and binding | Next interval for a separate coordinator handoff |
| --- | --- |
| Only R6-01 converts | Joint Hepoch selection/reset, never single selection by inference |
| Only R6-02 converts | Hrepr/lifetime/private membership; placement versus pointer capture still coupled |
| Both or neither convert | Check interactions, changed paths and reset/type adapter against known endpoints |

No monotonicity premise. First inspect retained source guard, reset location and normal continuation, pointer-vs-ID load, marked/unmarked writes and DFCC targets. Early frame/Unsupported/invalid-source loss means numerical relief is not automatically a causal fix. Parser/job success is not semantic success; conversion alone gives no B1/B2 or independent proof credit. P2/M3/full matrix/heavy M2 selectors remain HELD. Stop after two reviewed candidates and handoff.
