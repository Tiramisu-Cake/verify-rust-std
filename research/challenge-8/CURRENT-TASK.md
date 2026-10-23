# Network N8 — RefinedRust G1, Docker API repair and actual-start accounting

Task ID: `network-refinedrust-g1-2026-10-24-n8`; previous task: `network-refinedrust-g1-2026-10-24-n7`.
Owner: **Network**. Phase: `NETWORK-RR-G1-2026-10-24-N8`. Lane: `network-rr-g1`.

## Mission

This is a new account within the existing fixed owner window; deadlines do not move.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Fixed-window tooling anchor is 2026-10-23T20:56:24Z; actual N8 work start is 2026-10-23T21:33:57Z. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `b38e1a1229dacebe5853a47139f4c8db306a0ba5`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff` on `main` at `332d945fafa14bf55c0c8390cb35ec4b0c012cff`.
Profile `research/challenge-8/cloud-build/network-rr/RR-G1-PROFILE-20261024-N8.json` SHA-256 `c3e91c1b7d287bddca2277927271e1646f0a78eea195c249c381c9a3a7723335`. New ledger path: `research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N8.json`; previous closed ledger: `research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N7.json`.
Cloud budget: 5009 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1740 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

Direct owner authorization: fix Docker API, cold image -> digest/freeze -> warm G1 -> Brief classification. New5009s grant; N7 account unchanged. Fixed deadlines main2026-10-26T20:56:24Z / closeout21:56:24Z; no renewed window.

1. Review/register exact N8 phase and fresh ledger; repair Docker API and use owner actual-Dockerfile-start counting.
2. Cold1740/1800 -> Brief-bound start/receipt/digest -> pins-only review -> warm1200/1260; preserve source/tool/controls.
3. Classify GO_G2/STOP_RR/INCONCLUSIVE via N6 criteria, preserve N7 history; re-check Select P2.

## Special bounds

- Count only Evidence-Brief confirmed target Dockerfile starts as cold attempts; pre-start infrastructure costs budget but no cold attempt/setup-submit limit. UNKNOWN stays UNKNOWN. Coldmax2 actual starts, warmmax2; no unchanged config retry.
- Fixed owner deadlines use original20:56:24Z23Oct tooling anchor, actual N8 start21:33:57Z separately recorded. N7 closed391spent/5009retired/carry0 remains byte-identical; N8 is new authorization.
- After every terminal Build immediately commit/push ledger and CHECKPOINT/STATUS. Timeouts/reserve never shorten; RR frontend unpatched, no stronger premises/shims/only_spec or CI/ToolApplication; credit0/readiness unchanged. Own lane/client only, shared coordinator/IAM/transport and foreign lanes/ledgers unchanged. All actual tools Cloud-only; existing runtime review/watch rules.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Docker API compatibility repair and N8 admission pending.
Next: Register N8, fix Docker API, cold image then warm G1.

## References

- [N8 owner contract](network/rr/N8-OWNER-DIRECTIONS.md)
- [Owner cold counting update](network/rr/N7-COLD-ATTEMPT-OWNER-UPDATE.md)
- [N6 exit criteria](network/rr/N6-OWNER-DIRECTIONS.md)

## Отчёт агента

**network-refinedrust-g1-2026-10-24-n8 · network · NETWORK-RR-G1-2026-10-24-N8 · HANDOFF**
Updated: 2026-10-23T21:44:51Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `332d945fafa14bf55c0c8390cb35ec4b0c012cff` / `c3e91c1b7d287bddca2277927271e1646f0a78eea195c249c381c9a3a7723335`.
Dates: T0 `2026-10-23T20:56:24Z`; main `2026-10-26T20:56:24Z`; absolute `2026-10-26T21:56:24Z`; window 4320 min main + 60 min closeout (explicit). Budget 5009s: 0s spent, 0s retired, 5009s remaining including reservations.
Active Build IDs: 03245c6c-a86c-4cba-8c06-3927fef55672; unresolved: none recorded.
Blocker: N8 cold Build active; Dockerfile start not yet classified.
Next: Watcher ack; terminal Brief/accounting push, then classify start/receipt.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
