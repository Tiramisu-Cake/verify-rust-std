# Network Cloud readiness — PREPARED_NOT_REGISTERED

Task `network-bootstrap-2026-10-22-n1`, budget 0. Nothing here is registered,
deployed or executed: no coordinator/`active.json`/`requests` change, no
client of Select/Merge/VeriFast touched, no Build. Files live outside
`cloud-build/`, so neither `smallsort-session` nor any watcher picks them up.
Execution of any step below needs a separate owner decision.

## Contents

| Path | What |
| --- | --- |
| `client/coordination.py` | v4 candidate from deployed v3 blob `1fd8b97b` (Select = Merge): owners v3 ∪ {`network`}, **cap stays 3**, owner check per protocol version, owner check also in `request()` |
| `client/coordination-v4n-transition.py` | audit/migrate helper (local files only; `migrate` not on the CLI) |
| `client/coordination-v4n-test.py` | unittest, 6 tests (v3 unchanged + `network` refused; v4 four owners/cap 3/`fifth` refused; wrong cap; deployed v3 blob fails closed on v4; migration preserves records and needs all four ACKs; stale client / bad ACK refused) |
| `client/control.py` | Network client derived from Select `control.py` blob `b8f88ce8` (Select head `10e13a41`); window re-checked immediately before `reserve`. `ROOT=parents[3]` is correct only once copied to `cloud-build/`; inherited `download` stays reachable |
| `client/test_network_control.py` | unittest, 8 tests (empty table; inherited Select phases unreachable; owner/lane/ceiling/window/status mismatches; past deadline; submit window/timeout; budget; profile SHA binding) |

Run: `python3 -B client/coordination-v4n-test.py` and `python3 -B client/test_network_control.py`
(both pass on the VPS, 2026-10-22; no Cloud calls).

## Why v4 = four owners, cap 3

* v3 clients raise on any record whose owner is outside `V3_OWNERS`
  (`reservations()`), so a `network` record in a v3 envelope would break the
  other clients. A version bump makes every unmigrated client fail closed on
  the envelope (`protocol()` rejects unknown versions) instead.
* The project-wide limit of 3 (CORE) is kept: `PROTOCOLS[4] = 3`.
* The earlier unadopted v4 template (`infra/coordinator-v4-refinedrust-20261012`,
  `3bf951e5`, owners + `refinedrust-feasibility`, cap 4) is superseded by this
  proposal if accepted; a client running that code rejects this envelope
  (cap mismatch) and vice versa — fail closed either way.
* Found while deriving: Select's submit path calls `coordination.request()`
  before `require_capacity()`, and v3 `request()` does not validate the owner.
  The candidate validates it, so an unadmitted owner cannot write
  `requests/<owner>.json` and delay admitted owners.

## Migration plan (owner-run, all four owners at a quiet boundary)

1. Owner accepts the candidate (review record) and fixes its SHA.
2. Each owner commits the identical `coordination.py` into its own
   `cloud-build/` on its branch, publishes, and writes an ACK
   `{owner, coordination_sha256, infra_commit}` (pattern of
   `coordinator-v3-adoption-20261012`). Network: `client/*` → `cloud-build/`.
3. With no unresolved submit, the owner runs `audit`, then `migrate` (v3 → v4;
   reservations re-serialised and checked by value on read-back). `audit`
   does not itself check that each `infra_commit` is published on the owner's
   branch, and assumes the client path `research/challenge-8/cloud-build/` —
   both are manual checks of this step. Before: live Build
   inventory check as in the v3/v4 procedures (not in this helper).
4. Read-back of `active.json` `{schema_version: 4, max_active: 3}`; each client
   `status` once.
5. Rollback: only while no `network` record exists — rewrite the envelope to
   v3 with the same reservations; otherwise wait until network reservations clear.

Not covered here (owner decision): Cloud quota for concurrency stays at 3; IAM
unchanged (same dispatcher account); no trigger/backend change.

## Phase registration draft (not applied)

A Network phase is registered by one reviewed commit that adds an entry to
`NETWORK_PHASES` and the matching ledger + recipe:

```python
NETWORK_PHASES = {'NETWORK-R4-<DATE>-N2': {
  'ceiling': <granted seconds>, 'lanes': frozenset({'network-r4'}),
  'start_utc': <T0>, 'main_deadline_utc': <T0+120m>, 'deadline_utc': <T0+150m>,
  'profile': 'research/challenge-8/network/r4/<PROFILE>.json',
  'profile_sha256': <sha256>, 'timeout': (270, 1200)}}
```

Ledger (path inside the Network worktree, e.g.
`research/challenge-8/network/BUDGET-NETWORK-R4-<DATE>-N2.json`):
`{phase, owner:"network", status:"AUTHORIZED", authorization, ceiling_build_seconds,
used_build_seconds:0, remaining_build_seconds, allowed_lanes:["network-r4"],
start_utc, main_deadline_utc, deadline_utc, maximum_build_timeout_seconds,
report_reserve_seconds:240, builds:[], active_build:null}`.
Recipe `cloud-build/recipes/network-r4.json` (schema `smallsort-cloud-recipe-v1`)
with entrypoint running `network/r4/swap-if-less-body.py` and the profile's
overlay chain; the remaining common runner files (`run-proof.sh`,
`package-evidence.py`, `source-input.py`, `verify-evidence.py`, `provider.py`,
`proof-audit.py`, `overlays/`) are copied from Select at one exact commit with
blob SHAs recorded, per the coordinator HANDOFF.

## Session tool changes needed (shared workflow; owner/maintainer of `smallsort-session`)

* `assignment.py`: `CLOUD_OWNERS` += `network` (enables non-zero budgets).
* `session_prepare.py`: owner allowlist += `network`; a first-session path with
  no previous ledger/profile (bootstrap) — today `prepare` requires a closed
  old ledger of the same owner.
* `watch_bindings.py`: `OWNER_REPOS["network"] = (/root/verify-rust-std-networks,
  "challenge-8/networks")`; today `wait` would raise `KeyError` for network.
* `checkpoint.py` already accepts `network`.

These are requests, not edits: the workflow tool lives in the shared
`/root/verify-rust-std-evidence-brief` worktree, outside this task.
