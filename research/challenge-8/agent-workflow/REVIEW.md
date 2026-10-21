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
