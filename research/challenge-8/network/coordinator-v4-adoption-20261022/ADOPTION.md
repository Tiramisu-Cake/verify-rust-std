# Coordinator v4 adoption — 2026-10-22 (Network N2)

Owner-authorized: CURRENT-TASK step 3, then explicit owner permission in the session after a permission-classifier refusal. Quiet boundary checked at 19:14Z: no `control.py` process, `requests/` empty, `active.json` v3 with reservations `[]`, nothing staged in either client, no worktree file modified in the preceding 30 min. Select checkpoint CLOSED (R20); Merge HANDOFF (R19, deadline passed). No Build, request, reservation or phase registration.

| owner | worktree / branch | baseline | adoption (published) | changed paths |
| --- | --- | --- | --- | --- |
| select-sort4 | select-night / `research/night-select-sort4-cloud-2026-10-09` | `b96f16be` | `a44ac9c583bad7ec5f2edc0d0ff34a9642a8a341` | `cloud-build/coordination.py` |
| merge | merge-origin / `merge/incoming-origin-20261009` | `0c0b48f2` | `f0b2268780fcfe245c254306c5af4185412c78ca` (push includes 15 local R19 commits, owner decision) | `cloud-build/coordination.py` |
| network | networks / `challenge-8/networks` | `b55a9e59` | `4876c66f42edb9e95d7c9f4de6cb322a05d09c6a` | `cloud-build/{control.py,coordination.py}` (= reviewed prepared client) |

`coordination.py` SHA-256 `2fa7affd54b63cf6eea3924bc69f8a9db63b8c1b29a092cddfcfbbacc4616bc3` (reviewed candidate `0f5928b5`). `control.py` bytes unchanged in Select and Merge. Foreign dirty files of Select (17 entries) were left untouched. The VeriFast worktrees were not touched; the deployed v3 blob `1fd8b97b` now refuses the envelope.

Sequence: three ACKs (`*-ack.json`) → `coordination-v4-transition.py audit` PASS → `migrate` (audit + idle check incl. one read-only `gcloud builds list --ongoing` returning `[]`, under the shared flock) → `before.json` v3/3/[] → `after.json` v4/3/[] (`MIGRATE.json`) → per-client readback (`READBACK.json`: each client's own `coordination.py` reads `(4,3)`, `[]`, owner admitted; `verifast` not in v4). The readback replaces `control.py status`, which without an owner and ledger would use the default ledger and state directory. `smallsort-session` install guard (all three owners) and watcher accept the live envelope.

Rollback (only while there is no network reservation or request): `python3 -B research/challenge-8/network/cloud-readiness/client/coordination-v4-transition.py rollback`.

Not established: three simultaneous Builds under v4; Network submit (it needs the phase registration plus `package-evidence.py`, `source-input.py`, `verify-evidence.py` and the rest in `cloud-build/`, and a ledger under `cloud-build/` for `wait`). No proof credit.
