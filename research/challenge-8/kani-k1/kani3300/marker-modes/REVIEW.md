# Preparation review — worker15

Verdict: **STOP_REQUIRED_STATE_PREDICATE** under task §2; not READY for implementation/CI.

Research branch was clean at `be5bdb511676c0f441662528c0b88aab9c3fe007`; `git pull --ff-only`
reported up to date. Read-only source was clean at the required base. Isolated local clone
`/root/kani-fix-3300-marker-modes`, branch `fix/kani-3300-marker-modes`, remains at the same base.
No source patch/commit exists. Exact inspected source hashes are in INPUTS.json.

The source audit establishes available APIs and why candidate shortcut predicates lack the
required extent binding; it does not establish a new compiler fact or emitted-model outcome.
REQUIRED-STATE.md describes each operation family, late immutable seeding, delayed-pass updates,
and the unresolved composition/control-flow problem. Function-pointer paths have existing
Unsupported checks: their presence is not presented as an unguarded supported shadow path.
No totality claim or proof of impossibility is made.

Changed files in this preparation (research directory only):

- INPUTS.json
- REQUIRED-STATE.md
- LOOKUP-CONTROLS.md
- MODE-SCOPE.md
- TEST-MANIFEST.json
- CI-REQUEST.md
- REVIEW.md
- RESULT-MARKER-MODES-PREP.md
- STATIC-AUDIT.py
- STATIC-CHECKS.json

Python static audit checks source hashes, source anchors and the consistency of explicit STOP /
NOT_RUN declarations. It does not execute the proposed lookup truth table against production
code. Rust resolver units, source fixture preparation, emitted binding, compiler typechecking,
formatting and all verifier runs remain unperformed. No rustfmt run was needed without Rust edits.
No negative golden, xfail or Unsupported result is treated as proof credit.

No blanket guard/exemption, new static, target change, any_modifies/Arbitrary(MU) rewrite,
assert-to-assume change, hook pairing, mode selection, checks or S3 change was made.
Worker14's files and inventories were not modified. Quick r6 is coordinator-reported history;
the final common gate remains NOT_RUN here. No publication, push or CI was performed.
