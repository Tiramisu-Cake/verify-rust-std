# Network N7 — RefinedRust G1 via Artifact Registry image

Task ID: `network-refinedrust-g1-2026-10-24-n7`; previous task: `network-refinedrust-g1-2026-10-24-n6`.
Owner: **Network**. Phase: `NETWORK-RR-G1-2026-10-24-N7`. Lane: `network-rr-g1`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `747feae4f699c7f1c346a596b2b3ca2f0ee65ef3`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff` on `main` at `332d945fafa14bf55c0c8390cb35ec4b0c012cff`.
Profile `research/challenge-8/cloud-build/network-rr/RR-G1-PROFILE-20261024-N7.json` SHA-256 `9660cacd8dc1f5f2dc5b3b772a971afc63440bf90251e7753aed5af500cd44cb`. New ledger path: `research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N7.json`; previous closed ledger: `research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N6.json`.
Cloud budget: 5400 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1740 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

N7 and Builds authorized. Extended window: close on goal, budget or a real boundary, not on time (N7-OWNER-DIRECTIONS). Owner decision: the RefinedRust image lives in Google Cloud. Build it online in Cloud Build, push to smallsort-tools/refinedrust-g1, run stock G1 on exact core insert_tail inside that image; answer GO_G2 / STOP_RR / INCONCLUSIVE by the N6 exit criteria.

1. Adapt the inherited cold recipe to the online route: pinned ubuntu digest, nightly-2026-08-28 archives by SHA-256, RR clone at 332d945f verified by tree b33bcccb, crates by Cargo.lock --locked; drop the offline deb/vendor/cargo-config gates; freeze = image digest + binary SHA-256s + apt list + Cargo.lock in Build evidence. Branch-local per-lane image support, up to E2_HIGHCPU_8 for the cold Build only; service error-path tests; one review; register phase/lane/ledger.
2. Cold image Build (1740/1800, one attempt plus one setup-error repair), push, record the digest in the N7 profile and freeze.json (delta review of pins only); then warm G1 (1200/1260, up to two attempts) executing in the image by @sha256 digest; classify the first causal failure via Brief.
3. Rewrite network/rr/RR-G1-RESULT.md with the N7 verdict, identities (image digest, Build IDs, Brief file/index), first causal failure, missing specs and, for GO_G2, a G2 cost estimate; keep the N6 result as history. Re-check Select P2 for PUBLISHED; W7/W8 stay bounded.

## Special bounds

- Window deadlines exist only for ledger/watcher. Never shorten a timeout; setup error fixed statically, same config never repeated. After each terminal Build commit and push ledger accounting and CHECKPOINT/STATUS before the next step. Review once per semantic candidate; progress note about every 2 h.
- No RefinedRust frontend/semantics patch, no only_spec/shim/stronger FnMut/Copy/Freeze/purity premise, no Tool Application or CI integration. Generation or collector SUCCESS is not a safety PASS; proof credit 0 under every outcome; the readiness index does not change.
- Image/registry support only in the own branch client for lane network-rr-g1; coordination.py v4, IAM, shared transport, other lanes/worktrees/ledgers unchanged. Warm recipes reference the image by digest, never by tag. No local RR build or verifier on the VPS.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: No RefinedRust image yet: cold online image Build to smallsort-tools is the first action.
Next: Adapt recipes to the online image route, register lane network-rr-g1, cold image Build and push, warm G1 in the image, classify, rewrite RR-G1-RESULT.md.

## References

- [Owner directions N7 (registry route)](network/rr/N7-OWNER-DIRECTIONS.md)
- [Owner directions N6 (exit criteria)](network/rr/N6-OWNER-DIRECTIONS.md)
- [Draft RR G1 profile N7](cloud-build/network-rr/RR-G1-PROFILE-20261024-N7.json)

## Отчёт агента

**network-refinedrust-g1-2026-10-24-n7 · network · NETWORK-RR-G1-2026-10-24-N7 · ACTIVE**
Updated: 2026-10-23T21:12:09Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `332d945fafa14bf55c0c8390cb35ec4b0c012cff` / `9660cacd8dc1f5f2dc5b3b772a971afc63440bf90251e7753aed5af500cd44cb`.
Dates: T0 `2026-10-23T20:56:24Z`; main `2026-10-26T20:56:24Z`; absolute `2026-10-26T21:56:24Z`; window 4320 min main + 60 min closeout (explicit). Budget 5400s: 297s spent, 0s retired, 5103s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Cold EXPIRED; metadata execution0s; Brief pending.
Next: Read Brief; changed setup repair only if supported.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
