# Independent N5 R7 review

**Decision: GO for the reviewed candidate and its exact N5 `swap-size` stage admission.** This is a code/admission review only; it grants no proof acceptance or credit.

## Reviewed identities

- Baseline: `920dd8a50dcab9b7dd698af9be7d261d7754563c`
- Candidate: `ed3bedb8802ed3ef5b38b5b3250d7691c426dd4d` (tree `1b264acd49b9b6ddc47d64849ab7b28cde84c972`)
- Spec SHA-256: `cb70925bb9724e5371599f1460c6c7c2636eb4326c3b073479b221ee5e32dbae`
- Review packet SHA-256: `d54dad578bc9210bcea921c7d541c18854ca33933ed10f26123be7638427705d`
- Diff SHA-256: `598e8b730472813f1abb43ac300cad145c08a9d12e8fa0606fe10cf48141c3b6`

The packet identity check returned `PACKET_VALID_NOT_REVIEWED`; review covers the committed diff and its declared dependency snapshots.

## Findings

No blocking soundness, source-preservation, recipe-closure, or stage-admission findings.

The runner checks the pinned provider/profile before extraction, pins the unchanged extractor and live source bytes/blob, validates the exact ghost contract and byte-for-byte ghost stripping, and requires the pinned stock tool, compiler, target, and LP64 identities. It records and checks verifier/refiner argv, cwd, timeout, exits, logs and hashes; snapshots proof and tool inputs around execution; retains exceptions, timeouts, partial logs, malformed receipts and `NOT_RUN`; and runs refinement after verifier failure. Acceptance is fail-closed on source/stage/target mismatches and the emitted audit keeps `accepted` and `proof_credit` false.

The N5 client admits `swap-size` only under the new pinned R7 profile and exact recipe closure, with the 810-second stage and 1185-second Build envelope. The historical N4 profile/stage set remains pinned; the new stage is registered only for N5. The shell wrapper retains setup and runner exits and refuses incomplete, malformed, wrong-stage/lane, or credit-bearing runner audits. No change touches the source blob, stock tool, shared coordinator, transport, or IAM.

## Checks and limits

- `smallsort-session review check`: packet valid; exact candidate/spec match; no proof credit.
- Synthetic tests: 30 passed across N13 client, R7 wrapper and R7 runner suites.
- `bash -n`, Python AST/JSON parsing and `git diff --check` passed.
- No source extractor, compiler, VeriFast, refiner, Cloud Build, or raw evidence was run or inspected. The R7 execution and theorem therefore remain UNRUN; this review does not establish component acceptance.
- The worktree contains the authorized live N5 ledger/checkpoint/status updates and order evidence. I did not alter them or run final static closure against their older committed ledger snapshot; that known metadata mismatch is not a candidate semantic finding.
