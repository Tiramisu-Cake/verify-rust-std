# Prepared next-stage native gate — NOT AUTHORIZED / NOT RUN

Request: `RUN-REQUEST.json`; patch: `kani3300-part1-build.patch`; exact selected sources/goldens:
`TEST-MANIFEST.json`. They reproduce the 15 upstream fixtures, with byte-identical final-v2 production.
Pinned Kani baseline: `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Applied tree: `10c032ab8e3c5a38a3fa639c4b0004d61b7c2ffe`.
Patch SHA256: `b30758e575bb0bfabab186d615e8b28871543efb0703028aa721a8622ef28c40`.
Request SHA256: `ad96f7d0ada18cbbfe9345a2a7c06cdfbce0589924fd4255b9d5374fb8ffdaac`.
Existing KT2 tooling baseline: `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`, unchanged by P1.

The existing `kani_k1.py validate` and `prepare-kani` static preflight pass on a fresh detached f046 checkout.
No compile/proof runner was invoked. Index-tree production and all 30 test files equal the upstream candidate.
Default pinned preflight diffstat is 2315 bytes, below 4096; no gate override or path shortening was used.
The static observations/commands are retained in `STATIC-CHECKS.json` and `preflight.json`.

Proposed envelope: standard4, serial native selectors, 150 seconds per selector, 15-minute native work budget,
plus existing 30-minute checkout/build/upload overhead. Reservation `(15 + 30) * $0.0135 = $0.6075`, cap **$0.80**.
P1 spend/reservation: **$0/$0**. No phase, slot, ledger or dispatch authorization is created by this packet.

Next-stage coordinator must authorize the exact committed request/patch and cumulative ledger availability,
install this request as the lane's root `RUN-REQUEST.json`, publish/verify the exact research head and run the existing
coordinator gates. One targeted build is proposed; no automatic repair/retry or resource-profile change.
The historical root lane request remains untouched during P1 to avoid silently arming dispatch.

Acceptance: all 15 native selectors PASS with matching request/patch/tree/tooling identities; positives must
enforce `--require-success`; negatives must match own-output diagnostic and their complete expected golden.
Preserve argument/return, overwrite, both overlap directions, repeat, ZST reset, partial-copy, alias reset,
padding/source-read, clause-PFC and actual user-frame controls. Do not relax goldens to accept OOM/Unsupported.
Read terminal evidence only through the authorized bounded reporting interface; no raw logs/archive fallback.
PFC MU-roundtrip remains excluded and explicitly limited, regardless of this gate's result.
This gate tests final-v2 semantics on f046, not compatibility with the newer main tree or general proof credit.
