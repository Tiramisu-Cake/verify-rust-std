# Coordinator v4 adoption — independent reviews (N2)

Reviewer: `claude-subagent:smallsort-reviewer` (Opus 5.5, effort high, separate context, read-only, no nested delegation). No proof credit.

## R1 — coordinator v4 + transition (network worktree)

- Packet `scratchpad/rev1/packet` SHA-256 `c8899c907350ad62699d351e10d2b57f352269e21a728e694909518f2b910aac`, spec `5864558646971aefd34ea972e79d3615af047618026ec69483fd08b22646c75b`, candidate `a810b3a9530df58af8cb2909c353068cd7f948d2`: **GO_WITH_NITS**. Should-fix: renames hid deleted paths in the changed-path check; client roots/branches not distinct/pinned. Nits: no timeouts under the flock; v3 `request()` does not call `protocol()` (invariant overstated); Network support files outside the ACK; empty gcloud output treated as `[]`; non-object ACK.
- Delta `a810b3a9..0f5928b5d3fd04d606e3f166c0b6c5dcd0859912` (same reviewer, continuation): **GO_WITH_NITS**; all soundness points fixed (`--no-renames -z`, pinned roots/branches, 60 s bounded non-interactive git/gcloud, empty inventory error, ACK type); remaining nits: PLAN table formatting (fixed in docs), `TimeoutExpired` instead of `RuntimeError` (still aborts before any write). `coordination.py` unchanged by the delta: SHA-256 `2fa7affd54b63cf6eea3924bc69f8a9db63b8c1b29a092cddfcfbbacc4616bc3`.

## R2 — smallsort-session envelope v4 / network owner (evidence-brief worktree)

- Packet `scratchpad/rev2/packet` SHA-256 `052b6ba216fc66b8fbb62349aaab535276618ec4cf7a9761824de632e7299554`, spec `ef76e5c3e651886efe5fb42ce2357c1c3a90bb095c5a6ad59dd13176671794dc`, candidate `895c2648c4c68a3b4a3031ecd4e987e5bf0d583c`: **GO_WITH_NITS**, 173/173 tests (also from a clean export). Findings: network `wait` needs the client at `cloud-build/` (provided by the adoption commit); `CLOUD_HISTORY_OWNERS` should include network once it has a Cloud ledger; install guard accepts a network budget task under v3 (declared); unhashable `schema_version` raised TypeError (fixed in the next commit).

## R3 — smallsort-session first-session prepare (continuation of R2)

- Packet `scratchpad/rev3/packet` SHA-256 `03736e9987527657d88081210f5ee0b800bb33d1728d38b5cffc4da5e4eb3c29`, spec `b23177b15f80fe5ce5ec0026d7b082d4a99633228de89ef8f338e7f5cbbd2881`, candidate `9f152efe26902c5b2265e2d7622fcac2e91580a9` (delta from `895c2648`): **GO_WITH_NITS**, 176/176 from a clean export; candidate tests against baseline code: 3 failures + 2 errors on the new cases only. Merge/Select paths unchanged by static trace (author byte comparison: merge draft/reuse bundles identical). Open nits: first-session recipe is not forced to reference the generated ledger/profile; `FIRST_SESSION_OWNERS`/`CLOUD_HISTORY_OWNERS` must drop/add network once it has a Cloud ledger; network `wait`/prepare need the client at `cloud-build/` (adoption commit `4876c66f`, not yet published).
- Delta `9f152efe..929fe0a9f5411438348c5cb56a201abf7caf6c5e` (same reviewer, continuation): **GO_WITH_NITS**; nit 1 resolved (first-session recipe must reference generated ledger/profile, enforced in prepare and check), 177/177 from a clean export, new controls fail on `9f152efe`. Carried should-fix (client at `cloud-build/`) is satisfied by published Network commit `4876c66f`. Published: evidence-brief `929fe0a9`.

## Live switch status

NOT PERFORMED. Network adoption commit `4876c66f42edb9e95d7c9f4de6cb322a05d09c6a` (only `cloud-build/{control.py,coordination.py}`, baseline `b55a9e59`) exists locally. Committing `coordination.py` into `/root/verify-rust-std-select-night` was refused by the session's permission classifier (Modify Shared Resources); no Select/Merge file, push, ACK, audit or migrate followed. Live `active.json` stayed `{schema_version: 3, max_active: 3, reservations: []}`.
