# Network Cloud readiness — PREPARED_NOT_REGISTERED

> N2 (2026-10-22): v4 finalized for three owners; see the Contents table. Live switch status is recorded in `../coordinator-v4-adoption-20261022/` once performed.

Task `network-bootstrap-2026-10-22-n1`, budget 0. Nothing here is registered,
deployed or executed: no coordinator/`active.json`/`requests` change, no
client of Select/Merge/VeriFast touched, no Build. Files live outside
`cloud-build/`, so neither `smallsort-session` nor any watcher picks them up.
Execution of any step below needs a separate owner decision.

## Contents

| Path | What |
| --- | --- |
| `client/coordination.py` | v4 from deployed v3 blob `1fd8b97b` (Select = Merge). **N2 final:** v4 owners exactly {`select-sort4`, `merge`, `network`} (`verifast` refused, owner decision 2026-10-22), **cap stays 3**, owner check per protocol version, owner check also in `request()`; v3 behaviour unchanged |
| `client/coordination-v4-transition.py` | N2: `audit` (three ACKs: installed = adopted commit bytes, adoption diff only client paths, dispatcher bytes unchanged from baseline, branch checked out and adoption published via `ls-remote`), `migrate` (audit + idle check under the lock: no reservation/unresolved submit, no request file, `builds list --ongoing` empty; v3 → v4 read-back), `rollback` (v4 → v3 while no `network` reservation/request) |
| `client/coordination-v4-test.py` | unittest, 8 tests; transition tests on real temporary Git repos with a bare origin |
| `client/control.py` | Network client derived from Select `control.py` blob `b8f88ce8` (Select head `10e13a41`); window re-checked immediately before `reserve`. `ROOT=parents[3]` is correct only once copied to `cloud-build/`; inherited `download` stays reachable |
| `client/test_network_control.py` | unittest, 8 tests (empty table; inherited Select phases unreachable; owner/lane/ceiling/window/status mismatches; past deadline; submit window/timeout; budget; profile SHA binding) |
| `../runner/network-run.py` (+ `test_network_run.py`, 8 synthetic tests with a fake `verifast`) | Network runner core: runs every R4/W7 control crate under the P1 opt-in (`NETWORK_SWAP_IF_LESS_*` from meta), records exit/timeout/output digests as OBSERVED_UNCLASSIFIED or explicit NOT_RUN/ERROR; never classifies PASS. Not wired to a recipe yet (tool build/env setup come from Select's common runner files) |

N2 review notes (GO_WITH_NITS, fixed in the delta): client roots/branches pinned to the actual dispatcher worktrees; changed paths via `--no-renames -z`; git/gcloud calls bounded (60 s, no terminal prompt); empty inventory output is an error. Limits kept: a deployed v3 `request()` does not call `protocol()`, so a v3 client could still write `requests/<owner>.json` under v4 (informational; it blocks only a later idle check). The Network adoption commit carries only `cloud-build/{control.py,coordination.py}`: enough for `status`; `submit` also needs `package-evidence.py`, `source-input.py`, `verify-evidence.py` etc. in `cloud-build/`, added by the later phase-registration commit (not bound by the ACK).

Run: `python3 -B client/coordination-v4-test.py` and `python3 -B client/test_network_control.py`
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
