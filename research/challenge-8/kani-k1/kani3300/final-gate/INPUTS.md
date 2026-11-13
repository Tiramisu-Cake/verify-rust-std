# KANI3300 Gate-P — worker15 preparation, 2026-11-13

Authority: `../../TASK-KANI3300-FULLGATE-REPLAY.md`, issued preparation only.
This package authorizes no push, Actions run, Cloud Build, slot, phase, ledger or
publication. Local work is Git/Python/static only. Preparation Cloud cost $0.
This is correctness verification. All new executable results are **NOT_RUN**.

- Research input: `841f6a1f8c` on `experiment/kani-k1-kani3300g0-20261111`,
  `git pull --ff-only`: up to date, initial worktree clean.
- Kani C0: read-only `/root/kani-fix-3300-c0`,
  `478aad601fc5a45b142d6a8a2ae85594add9a0e6`, tree
  `41ca556b9975dd12125bdb73b256c422a7897db7`.
  Lineage `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a` → E1 `dc24745c6` + X1.
- Coordinator-reported Quick C0 run `43474396386` is not a full gate:
  five immutable Part1-edge failures remain for worker14/E2. No independent
  evidence or M3 acceptance inferred here.
- **C1 is not frozen.** Its SHA/tree, accepted E2/M3/mixed-root changes, exact
  source diff and binaries/model identities remain unset. No C0 dispatch.
- SmallSort selected inventory: read-only `/root/verify-rust-std-kani-traitpfc`,
  `70ba5befc617627073738e26cb1466bd4fb76e41`; library tree
  `6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f` =
  `1aac64c50d69382c8ce90811880225d0a047525f:library`.
- Upper PR is `model-checking/verify-rust-std#752`. Located through
  `/root/smallsort-pr-drafts/TODO.md` (PR #752 section) and frozen
  `research/challenge-8/kani-k1/RESULT-TRAITPFC-G3.md` in the traitpfc repository.
  TODO still makes G3 integration conditional on organizer Kani pin, then owner
  review. Current PR head was not queried or equated with this snapshot.
  Coordinator must confirm the final library pin before binding replay.
- Historical G3 build UUID `368b93f4-e7ae-4603-bf41-ea3fb6573e3e`, source
  `2f1c45e519cc89e1dae532ad0f44243255a514d7`: inventory/compatibility reference,
  uninit OFF and valid-value OFF on another Kani; no ON replay credit.

`EXPORT-MANIFEST.json` records exact C0 baseline source hashes and subtree IDs,
and selected SmallSort file hashes. Baseline fields are not final C1 bindings.
No raw Cloud artifacts/logs were downloaded/read for preparation. Future Cloud
evidence uses the coordinator lane and Evidence Brief v0.11; integrity alone is
not proof credit. Historical ledgers/download_verified remain untouched.
