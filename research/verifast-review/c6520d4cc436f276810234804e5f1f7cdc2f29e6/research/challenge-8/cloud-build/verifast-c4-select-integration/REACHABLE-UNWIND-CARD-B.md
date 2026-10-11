# Selector reachable-unwind admission mutant card B

2026-10-10. This design implements only the independently reviewed normalized-call-record path. It does not alter MIR serialization, verifier semantics, source, posts, or the consumer call graph.

## Fixed target and order of checks

Run only in the exact nine-body selector producer with the R3 frame and frame-shadow profile enabled, wrapper input-relation/nine-body admission active, exact `verified/lib.rs` source SHA `7ec86f52b362f7f8b2ed26e3fa108212eb3d6288820bab9c6db3fa37bf8cabe0`, original complete decoded unit/body hashes, exact source/MIR inputs, and the exact body order placing `select_unpredictable` at unit index 7. The opt-in is `SORT4_SELECTOR_REACHABLE_UNWIND_MUTANT=1`, default off; unknown values reject. It is mutually exclusive with C4 first-select semantic controls and TYPE/MOVE/EDGE admission mutants.

After the original unit/body admission hashes pass, derive one normalized record for every `Call` terminator in the admitted body-7 Reader. Each record preserves the actual block index, full source location, normal target, and normalized unwind action/cleanup target. Require exactly one record at source line 194 in `verified/lib.rs`, with original `Unreachable` action and unchanged source/body identity.

## Single permitted mutation and production fold

Change only that record's unwind action from `Unreachable` to `Cleanup(38)`. Preserve its source location, block identity, normal successor, every other call record, and the decoded Reader. Print old/new call-edge fingerprints and the complete call-record count before running the normal predecessor fold. Both ordinary admission and mutant admission use the same production fold over the normalized records. With the R3 frame profile, the expected shared-cleanup predecessor count changes from 18 to 19; the unchanged inventory check must then reject with `owner shared cleanup predecessor inventory` before any function proof header.

The mutant is valid only if the log proves (1) original source, unit, and all-nine-body hashes passed; (2) body index 7 and line-194 call were uniquely selected from the actual Reader; (3) the record changed only `Unreachable -> Cleanup(38)`; (4) normal target and every other normalized edge stayed equal; and (5) the same fold observed 18 then 19 and the unchanged admission predicate emitted its ordinary inventory refusal. A hand-computed count, synthetic failure, changed expected count, or counting the original Reader instead of the mutated records is inconclusive.

## Boundaries

This default-off control is an admission negative only. It neither modifies the Cap'n Proto Reader nor changes the AST/tool input accepted by a successful run. It must not change cleanup behavior, call summaries, contract posts, frame resources, source hashes, or kernel checks. It requires a fresh Cloud run on the exact effective tool; no local compilation or proof run is authorized.
