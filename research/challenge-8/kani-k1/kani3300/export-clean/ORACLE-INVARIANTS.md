# X1 retained oracle invariants

Eight cases retain their exact committed source hashes, root names/lines,
required operations, complete failure identities and useful SUCCESS rows:

| Case | Invariant |
| --- | --- |
| p1 | No failures; exact useful outer ensures SUCCESS. |
| ordinary | No failures; useful generated-body/ensures/harness assertions SUCCESS. |
| pfc | No failures; useful body/ensures/harness and selected out assigns SUCCESS. |
| lawful-modifies | No failures; ensures/result29/out29/outside41 and selected out assigns SUCCESS; reached Unsupported stops downstream. |
| p2 | Two instrumentation checks for one intended ptr::read u8 remain required. This is not a claim of two distinct UB events. Only the exact line14 outer ensures can additionally fail or be UNREACHABLE. |
| postcondition-hole | Same exact read inventory, with only the exact line16 outer ensures consequence. No arbitrary assertion/Unsupported is allowed. |
| frame | Exactly the user outside assigns violation at line22, selected line23 out write SUCCESS. Verifier-private writes cannot substitute. |
| clause | Exactly one bound transmute_neo MaybeUninit<u16> → u16 failure at exact library source/line; no invented second layer. |

Six mode roots retain their operational manifest data:

| Root | Required expectation |
| --- | --- |
| replace_transfer | Completed observation only; Replace remains UNCLAIMED. |
| replace_ordinary | SUCCESS with required return-path covers. |
| replace_simple_check | SUCCESS with required return-path covers. |
| recursive_check | Sole active/failed property is the exact interprocedural-cycle Unsupported diagnostic (with its optional active-path suffix). |
| recursive_ordinary | Same cycle Unsupported expectation. |
| recursive_simple_check | SUCCESS with required return/base/unrolled-edge covers. |

The two recursive negatives retain FAILURE and no companion proof credit.
All mode observations retain `mode_qualification: false`; transformed-body
binding is unestablished. Contract predicates/assumes and recursion semantics
are unchanged. Required covers group by source description/file/line/column,
ignoring generated/original function-copy names. One SATISFIED copy qualifies
the source path even when another is UNREACHABLE. Useful check UNREACHABLE
is not check SUCCESS.

The exact-oracle validator retains schema validation, duplicate JSON keys/IDs,
selection/root/file/line/source-hash binding, exact full failure multiset,
nonterminal/unknown status rejection, counters and complete regular/JSON
crosschecks, flags/backend configuration and current output hashes. All
normalization code is unchanged: only the known checkout prefix is removed;
no generated names, library paths or arbitrary ID fragments are wildcarded.
All existing property adversaries remain. No auto-learning was introduced.
The only removed validator statement required historical artifact/selector/hash
attestation presence; those records now live in research and were not current
property predicates.

Marker diagnostics replacing `unwrap_or_default` remain explicitly DEFERRED
by the coordinator. X1 introduces no production marker guard. Local synthetic
checks are not a Rust proof; all actual Kani results for X1 are NOT_RUN.
