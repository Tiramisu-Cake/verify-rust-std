# Workflow v1 — validation and review

Independent reviewer: GPT-6 Luna HIGH, `workflow_safety_review`, no nested delegation. This review concerns local assignment/checkpoint/static-preparation tools, not verification of Rust or qualification of a proof profile.

Concrete findings fixed by original workers and covered by synthetic refusal tests:

- A modified draft ledger could pass a refreshed inventory: `check` now reconstructs and compares the complete fresh ledger from spec.
- Git wildcard pathspecs could broaden closure: recipe entries are literal files/directories. Legitimate infra/proof cross-role membership is retained.
- A closed worktree ledger could disagree with committed HEAD: installation requires exact committed bytes and accepts both existing Select/Merge closed-account formats without rewriting them.
- A symlinked history ancestor could redirect archives: all destination ancestors are checked before writing.
- The coordinator shared lock spans installation, including the final inactive-owner check and archive/view replacement. Existing live state is never edited.

Localized independent follow-up: GO for ledger binding, history ancestor safety, retained lock lifetime and targeted tests. Main integration also checks actual historical account readers, CLI draft generation/size, Markdown links, Python syntax and static source-closure behavior. Actual mutable Build ledgers deliberately fail a committed-byte preflight until their state is committed; this is not a reason to rewrite old evidence.

Startup policy is versioned in CORE. `task install` is a local handoff after a closed session, not a runtime client activation. Prepared ledger/profile/recipe bundles remain PREPARED_NOT_REGISTERED; the exact branch-client admission, transport caps, scientific controls and proof credit remain separate. No Cloud Build or local proof pipeline is run by these tools/tests.

Integrated validation: **40 synthetic service tests PASS** via `python3 -B -m unittest discover -s research/challenge-8/agent-workflow -p 'test_*.py'`. All six CLI help paths and task creation were smoke-tested; example CURRENT is3347bytes with the6144-byte cap. Local Markdown links (53), Python syntax, exact legacy AGENTS preservation and real closed-account readers for Merge-R15/Select-R14 passed.

## Workflow v2 — review packets and Brief observation records

2026-10-21. Independent reviewer: GPT-6 Luna HIGH, `workflow_v2_review`, no nested delegation. Initial review identified three concrete findings; the original workers fixed them:

- Git capture used full buffering before checking limits. Popen now streams bounded stdout/stderr with timeout/kill/wait cleanup; tree and changed-path outputs/counts also have explicit caps.
- Observation values could inject Markdown headings/assurance rows. Every dynamic rendered value is JSON-quoted inside a backtick fence longer than embedded runs; newlines remain data.
- Directory enumeration materialized all entries before checking the record cap. The scan now checks the cap incrementally before processing an excess entry.

Localized re-review: **GO**, no further concrete issue; **26/26** targeted synthetic tests PASS. Reviewed module SHA-256:

- `review_packet.py`: `34dca37270e91d87cd66bd0e7b33e2f86bf2eb208bd28d5373e3e26adf7be80f`.
- `observations.py`: `b4aa7d72a60bf340b9e239f199b8e4fa6ea833406c900cba6a1b9cb2b3daf9cf`.

Main integration: **67/67** service tests PASS (41 prior +12 packet +14 observation), including refreshed-inventory tampering, expected candidate/spec identities, committed versus dirty inputs, selected versus unrelated symlinks, bounded Git output/timeout, immutable records, byte-bounded pages, append-between-pages refusal, unknown/incomplete fields, independent receipt references and Markdown injection. Installed CLI smoke also passed on already published workflow Git commits: all3 changed paths inventoried and current uncommitted files excluded. Observation record/duplicate/list/render/check used explicit synthetic data only. New documentation local links and diff whitespace checked.

Review/check structural validity is not reviewer approval, proof acceptance, semantic dependency completeness, receipt validation or index freshness. Observations retain author-asserted assurance and references; they grant no independent credit. No Cloud calls, Builds, local proof pipeline, active-task/ledger edits or real evidence harvesting occurred. Tools are available through the existing `/usr/local/bin/smallsort-session`; updated CORE is adopted at the next closed-session handoff.

Point4 remains a documented experiment, not a deployed watcher: [WAIT-EXPERIMENT](WAIT-EXPERIMENT.md). Terminal-only output was observed, but fewer model resumptions or token savings were not established. No percentage savings is claimed.

## Queue wakeup experiment — subsequent measured result

2026-10-21. User explicitly authorized an isolated synthetic test. Native WebSocket connected to the existing managed Codex0.163.0 Unix endpoint; no daemon restart, GCP call, Build, proof pipeline or existing-agent message. A new non-forked thread explicitly selected gpt-6-luna/HIGH/read-only. During30.008s idle there were0 new turns and no usage change. One `codex queue` started the next turn automatically; exact initial/wake replies matched,2turns completed, own paginated history contained only userMessage/reasoning/agentMessage and no tools. Only the created thread was archived. Exact metadata/usage and executed-script SHA are retained in [result](experiments/queue-wakeup-20261021.json).

This is real model execution on synthetic input, not another fake status loop. It establishes wakeup on this installed version; it does **not** establish production restart/persistent dedup/admission/accounting/deadline integration or a project-wide token-saving percentage. Routing guard cases are pure function tests, not live CI authorization. Existing review-packet/observation independent GO remains limited to its previously pinned files; it is not an independent production review of this probe.

Integrated service tests **74/74 PASS** (prior67 +7 probe-isolation/routing tests). These tests never launch Codex/model/GCP; only the explicitly opted-in experiment did so. Documentation links/diff whitespace and the executed-script SHA were checked. Production watcher remains undeployed; active Select/Merge tasks, profiles, accounts and deadlines were not edited. [WAIT-EXPERIMENT](WAIT-EXPERIMENT.md) now separates the old shell-loop limitation from this successful queue result.

## Persistent Build watcher — opt-in for subsequent sessions

2026-10-21. User authorized implementing the watcher after the queue experiment. Independent reviewer: GPT-6 Luna HIGH, `watch_safety_review`, no nested delegation. **GO for future proof sessions**, not activation of current Select/Merge jobs. Independently reviewed module SHA-256 (before the formatting-only adjustment below):

- `build_watch.py`: `b2b94f545cfc61aea48b505b9a31b7864d52bd68d859922a49f7189fda67c54c`.
- `watch_bindings.py`: `41407340030113caaac38e189fd2a31e9507fd2aa36005d4d0aaed4d8b61b817`.
- `watch_codex.py`: `3df1105f9b6428eb70d0a0a813314d7833e00701ae210be20133c64c0db3428c`.
- `smallsort_session.py`: `0684f409226cef149b94308d596734d287b484d6f48a6af9d15b30ee3d5b2c6c`.

The independent review found a stop/ack race: stop waited for the state lock while ACK held it across metadata/receipt checks. The original worker moved the durable stop marker before the lock and added final stop checks around acknowledgement. Regression tests cover stop during receipt confirmation and during an enqueue already in progress. A started enqueue may complete; its stopped receipt cannot be acknowledged.

Main integration found and the original workers fixed: absolute binding versus relative spec ledger mismatch; ACK incorrectly expecting the original rather than resumed turn; terminal/unaccounted state skipping the ordinary reconciliation poll; missing pre-delivery cwd binding; stale startup heartbeat/duplicate runner races; DELIVERING restart recovery; outstanding UNKNOWN/DELIVERED rearm; and unknown goal metadata being treated as explicit null. Receipt validation now requires the exact persisted payload as the sole userMessage in the resumed turn, followed by unchanged-turn and fresh authority/window checks. Delivery revalidates after metadata IO and reserves the bounded enqueue duration before absolute. One durable attempt only; ambiguous enqueue/crash becomes DELIVERY_UNKNOWN and is never automatically retried.

**129/129 isolated service tests PASS** (prior74 +55 watcher/binding/adapter/integration tests). The final communication-only literal/help delta also passed both integration tests. The integrated test uses the actual three modules, a temporary committed Python status stub that reconciles its synthetic own ledger, fake read-only Codex RPC, a fake queue executable and an unused private Unix socket. It exercises HANDOFF → status/accounting → READY until armed turn completes → exact queue payload → resumed-turn ACK. No Codex model, production daemon, existing thread or Cloud endpoint is called by these tests. CLI help, Python syntax, example JSON, root-installed instruction-template identity,24 local links and diff whitespace passed.

One separate read-only metadata check of the experiment's own already archived test thread established the actual `archived_sessions` rollout path; no messages/turns were created. This implementation turn submitted/cancelled no Builds and switched no active proof agent. Canonical instructions and CLI are available now; `task install` adopts the new CORE only after the existing closed-session check. CORE links the canonical WATCH guide directly, so worktrees do not need to copy another runbook.

The first authorized future proof session remains the real Build integration check. Tests/GO establish the bounded workflow implementation, not proof acceptance, exactly-once delivery or a measured token-saving percentage. Unknown delivery may lose a notification; reboot does not automatically restart the process. Existing owner/phase/ledger/slots/deadlines/budget/client admission and Evidence Brief remain authoritative. No IAM, GCP service/trigger, daemon restart, proof input or historical evidence/ledger rewrite was introduced.

Main staging check removed exactly one surplus trailing newline byte from `watch_codex.py`; an exact byte comparison confirmed `reviewed_bytes == final_bytes + bytes([10])`. Final file SHA-256: `e124ed0b189bdb1f984a433985b08e668e87c3b4dc3a536cf576bd04a652bb5b`. No executable token changed; the manifest retains both identities. Default staged diff whitespace check then passed.

## Closed Select account compatibility — R17 handoff

2026-10-21. Actual closed R16 accounts revealed an initialization-time `spent_build_seconds=0` alias alongside the coordinator-maintained `used_build_seconds=2170`. The assignment reader now prefers the latter when present, retaining legacy fallback only when absent. A malformed present primary counter still refuses; it cannot fall back to an apparently valid alias. Existing owner/closure/committed-bytes/active-reservation/terminal-accounting/retirement/carry/budget checks remain intact. No historical ledger was rewritten.

Independent GPT-6 Luna HIGH `watch_safety_review`: **GO** for the localized reader fix and final renderer wording. `assignment.py` SHA-256 `67701a360b435d855fdbdaf6b4a6587422463f89544fa0538553e00618bc1478`. Two new synthetic tests cover successful closed-account installation with a stale alias, exact old-ledger preservation, fresh NOT_STARTED/T0-null state, and null/bool/negative/inconsistent primary refusal. **131 service tests PASS**; all14 assignment tests also pass after the final wording-only change. Renderer now states that preparation counts in the actual-start T0 window and registration never restarts that clock.

Permanent CORE retains the complete context-saving workflow and now states the exact thread-cwd requirement at startup. The Select launcher is a stable reference to CURRENT-TASK, not a repeated pause-specific instruction or separate budget. These changes prepare the next assignment; no Cloud Build or local proof tool was executed.
