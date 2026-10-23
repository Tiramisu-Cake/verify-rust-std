# R22 next-window handoff (no transferred authority)

R22 T0, budget, ledger and window do not transfer. A new assignment must provide its own phase, window and ledger. Client registration for R22 is in `control.py` (`A1_R22_*`). It exports the route marker `SORT4_R20_CALLEE_PHASE_ID` with the R21 literal, because the owner-approved translator patch compares against it, and exports the session phase separately as `SORT4_R22_SESSION_PHASE_ID`. A later phase should reuse that pattern; the static control is `test_route_marker_matches_every_pinned_consumer_literal`.

## Where the actual fractional callee stands (SOURCE_REPORTED, credit 0)

Latest reviewed proof candidate: `dbaf41e612cc7836c58704bd80466e90e21eafa7`.

Tool chain on top of tool `f76012fb`:
- O26 20+2, then branch-selected `78079210`;
- `verifast-r22-fractional-forget-26.10.patch` `219f3dc0`, giving translator `e9a953ca`;
- parser patch `dfdaff60`, giving `rust_parser.ml` `6a866aa5`.

Pins: `FRACTIONAL-FINGERPRINT-INPUT.json` (R22), reconstructed from the Brief read of fingerprint `72a38f11` (`FINGERPRINT-72A38F11-READ.json`).

| Build | Candidate | Outcome |
|---|---|---|
| `71401a80` | `82bb819f` | Parser defect `[1/2] <T>.own` |
| `cfc83426` | `177ef120` | Parser fixed; callee controls fail at intended obligations; unsupported `merge_fractions` deref form |
| `72a38f11` | `363d7752` | Ghost repaired; fingerprint complete |
| `7e23e945` | `dbaf41e6` | Positive reaches function end and fails **only** the leak check: two `MaybeUninit_pointer_own` chunks, the constructor results |

## Next obligations, in order

1. `LEAK-REPAIR-NEXT.md`: bind and consume the two constructor pointer-ownership chunks with checked ghost opens, by exact value. Then:
   - fingerprint-only Build (runner final stage as in `363d7752`);
   - bounded Brief read (walker approach; about 420 requests);
   - patch rows plus any certified ghost text;
   - proof Build.
2. `CONTROL-TARGET-PROPOSAL.json`: pin the seven control targets with review after re-observing them on the repaired positive. The omit-* targets move from the stale R21 final-select equality to the wrapper-select lemma precondition (`lib.rsspec:462/463`).
3. Then the normal/unwind/nested-Drop matrix and acceptance. After that, `BODY-C5-NEXT` (168/191) and P2.

## Parallel (no Cloud)

- **P2:** `NETWORK-P2-RESPONSE.md` + `P2-INTERFACE.json` (NOT_PUBLISHED, planned contract SHA `dc985de2…`) and `MUTABLE-GATE-INVENTORY.md`.
- **`*mut` source writer:** `overnight-helper/prepare-actual-helper-capture-mut.py` is unreviewed and on no route. The owner projection is byte-compatible modulo signature. The nine-body adapters are const-specialized and need a parallel chain.
