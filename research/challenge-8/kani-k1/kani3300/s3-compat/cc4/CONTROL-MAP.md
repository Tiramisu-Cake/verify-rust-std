# CC4 controls / acceptance

All existing test Rust bytes, strong-oracle inputs/bindings and other goldens
are unchanged. New fixtures live under json-handler/.../cc4 with no new expected
Unsupported golden. Python compares extracted helpers, contracts, bool/MU
predicate, captures, bodies and harness tokens against exact CC3.

| Control | Required interpretation |
| --- | --- |
| Original three recursive.rs roots, separate exact singletons | Retain full independent inventories and root association; classify actual cycles for check/ordinary; SimpleCheck is required legal positive |
| cc4/isolated-bounded.rs :: recursive_simple_check | Only bounded_transfer and its helpers/contracts; source sibling absent; SUCCESS, no failures, both body branches and outer return paths reached |
| cc4/isolated-recursive-ordinary.rs :: recursive_ordinary | Actual recursive_transfer unchanged; obtain selected-body/callsite repeated-key path; fail-closed cycle observation is not release qualification |
| Original whole input / cc4/mixed-reversed.rs, plus reversed singletons | Compare each per-root inventory and mode/body selection; capture actual codegen-unit/starting_items order, never infer order from declarations |
| CC1 self/mutual/capture-free cycles | No crash/partial graph, complete cycle Unsupported; no general recursion credit |
| CC1 diamond_two_inputs / repeated_callee_preserves_hole | Completed DAG/repeated call accepted; distinct-input hole read preserved; exact existing negative check set, no extra failures |
| CC1 independent singleton / roots-cycle-first / roots-acyclic-first | Fresh per-entry active stack, original good-root inventory in both actual orders; common immutable map is not itself corruption |
| Original replace_ordinary / replace_simple_check | Required ordinary Assert/SimpleCheck nonrecursive positives; no bool/ref/layout/Unsupported or other extra failure |
| P1 and all8 strong JSON oracle cases | Preserve previous PASS/exact-negative/no-extra-failure gates on common reviewed composition |
| Two corrected capture fixtures | Exactly one source/model-bound Unsupported each, as EXPECTATION-BOUNDARIES; no capture/PFC credit |
| CC2 slots / CC3 upvars / A3/M1/S3/private frame, left/right holes | Prior invariants and full controls retained; final composition gate, not replaced by diagnostic successes |

All execution/type/model/failure-set/order results for the new candidate are
NOT_RUN. Original CC3 SimpleCheck saved export is SUCCESS but generated-body
cover binding is pending. Isolated-vs-original divergence requires unit/mode/body
investigation. If isolated also cycles, request its actual generated/helper edge.
Unexplained required-positive Unsupported, lost checks, extra FAIL or bad body
selection is STOP/BLOCKED. Runtime depth does not bound the static call walk.
No marker/source-panic fallback, optimistic summary, SCC, new snapshot architecture,
weakened scope, solver policy, arbitrary golden or collector rewrite is included.
Optional upstream flat-recursion reproducer remains NOT_RUN and not requested.
