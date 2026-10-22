# Coordinator v4 adoption — independent reviews (N2)

Reviewer: `claude-subagent:smallsort-reviewer` (Opus 5.5, effort high, separate context, read-only, no nested delegation). No proof credit.

## R1 — coordinator v4 + transition (network worktree)

- Packet `scratchpad/rev1/packet` SHA-256 `c8899c907350ad62699d351e10d2b57f352269e21a728e694909518f2b910aac`, spec `5864558646971aefd34ea972e79d3615af047618026ec69483fd08b22646c75b`, candidate `a810b3a9530df58af8cb2909c353068cd7f948d2`: **GO_WITH_NITS**. Should-fix: renames hid deleted paths in the changed-path check; client roots/branches not distinct/pinned. Nits: no timeouts under the flock; v3 `request()` does not call `protocol()` (invariant overstated); Network support files outside the ACK; empty gcloud output treated as `[]`; non-object ACK.
- Delta `a810b3a9..0f5928b5d3fd04d606e3f166c0b6c5dcd0859912` (same reviewer, continuation): **GO_WITH_NITS**; all soundness points fixed (`--no-renames -z`, pinned roots/branches, 60 s bounded non-interactive git/gcloud, empty inventory error, ACK type); remaining nits: PLAN table formatting (fixed in docs), `TimeoutExpired` instead of `RuntimeError` (still aborts before any write). `coordination.py` unchanged by the delta: SHA-256 `2fa7affd54b63cf6eea3924bc69f8a9db63b8c1b29a092cddfcfbbacc4616bc3`.

## R2 — smallsort-session envelope v4 / network owner (evidence-brief worktree)

- Packet `scratchpad/rev2/packet` SHA-256 `052b6ba216fc66b8fbb62349aaab535276618ec4cf7a9761824de632e7299554`, spec `ef76e5c3e651886efe5fb42ce2357c1c3a90bb095c5a6ad59dd13176671794dc`, candidate `895c2648c4c68a3b4a3031ecd4e987e5bf0d583c`: **GO_WITH_NITS**, 173/173 tests (also from a clean export). Findings: network `wait` needs the client at `cloud-build/` (provided by the adoption commit); `CLOUD_HISTORY_OWNERS` should include network once it has a Cloud ledger; install guard accepts a network budget task under v3 (declared); unhashable `schema_version` raised TypeError (fixed in the next commit).
