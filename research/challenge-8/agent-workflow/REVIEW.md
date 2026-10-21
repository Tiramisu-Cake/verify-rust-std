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
