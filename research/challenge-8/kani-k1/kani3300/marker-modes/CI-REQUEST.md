# Coordinator CI request — preparation only, no dispatch

Marker diagnostics/lookup units are DEFERRED by coordinator decision of 2026-11-13;
see [REQUIRED-STATE.md](REQUIRED-STATE.md). `contract.rs` remains unchanged. No marker
fault injection or required-state design is part of this stage.

Proposed suite: `tests/json-handler/uninit-contract-mode-boundaries`, exactly six roots:

1. replace.rs: replace_transfer — Replace boundary observation.
2. replace.rs: replace_ordinary — Assert legal companion.
3. replace.rs: replace_simple_check — SimpleCheck legal companion.
4. recursive.rs: recursive_check — RecursiveCheck boundary observation.
5. recursive.rs: recursive_ordinary — Assert legal companion with actual bounded recursion.
6. recursive.rs: recursive_simple_check — SimpleCheck legal companion, explicitly unrolled step.

Proposed caps/profile per root: unwind 8; harness timeout 120 s; outer process timeout 180 s
including compilation; b12. Six sequential fresh models. Exact roots and caps require coordinator
approval before dispatch; this document/runner carries no build grant or CI authorization.
`-Z unstable-options` precedes consuming `--cbmc-args --object-bits 12`. Default solver,
slicing, memory/overflow/unwinding/undefined-function/reachability and contract checks remain enabled.

For coordinator execution after approval (OUTPUT must be absent):
`python3 tests/json-handler/uninit-contract-mode-boundaries/run.py --kani KANI --output OUTPUT`

The source runner records argv/source SHA, full export, retained model artifacts, log and full
failure/check/cover observation per root. It requires exact nonempty root selection, completed
outcome, coherent failure sets/counts and mode metadata; build/export/incomplete-result error
makes downstream roots NOT_RUN. Boundary SUCCESS/FAILURE is observed without a guessed golden;
companion failure/path gap fails the collection check. Script PASS is collection plus companions,
not mode/semantic qualification. Verify exported schema with the existing validator as appropriate.

After CI, inspect full per-root inventory and transformed model: bind target/closure mode,
requires/ensures/helper/return, real recursive base/edge/reentry, and lawful prefix. Any unrelated
Unsupported or early frame failure leaves a gap. Full success applies only to that input.
All six Rust verifier runs are currently NOT_RUN and actual bindings BINDING_PENDING.
Python synthetic collector tests and scratchpad rustfmt do not satisfy this gate.

After review/composition with worker14, agree one Quick plus selected new suite. Preserve lawful
user/private writes and mapped P2/postcondition-hole and user outside-write frame negatives.
Do not assume the other branch is green or invent a new Quick count. M3/platform/SmallSort remain
separate gates. No local compiler/verifier/CI, push, raw evidence read or grant reuse occurred.

Inventory detail: JSON export supplies completed outcomes/full failure objects, but successful
check IDs/descriptions are absent (only success counts). Bind those checks and the generated
mode/transfer bodies using retained emitted/property artifacts via the coordinator evidence
workflow; neither metadata nor collector PASS resolves that gap.
