# Cumulative head5 — request only, no dispatch

Source `96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f`, tree
`445fe95f622016728286e2b820c52b626809923b`, parent accepted4
`345cedfd67df679e326474385308349d609fc43d` (run43710024495).
Worker15 prepares/reviews a separate CI-only overlay. This writer session creates no
overlay, push, run or publication. Recipe/settings: CI-REQUEST.json; exact selectors,
hashes and unchanged directives: TEST-MANIFEST.json.

Use accepted Quick on ubuntu-24.04: fmt, build-dev, workspace/tests clippy `-D warnings`,
units ActiveCalls9 / immutable_allocations9 / argument_size1 / marker_category1, and
the complete cumulative manifest. `RUST_TEST_THREADS=2`, job cap120min, test cap2400s,
no retries or global object-bits override. Required deduplicated selectors460:
expected368 (362 pass +6 existing ignores), kani53 (50+3), ui17, script-based-pre3,
json-handler17, std-checks2. Total451 expected passes +9 existing ignores, plus20 units.
These are static discovery expectations, not test results. No present test is filtered.

Target all47 new pairs, including every mode/root and generated-modifies-no-shadow.
Per-fixture native results must close CLOSURE-OBLIGATIONS.json with exact-head identity,
argv/exits/term reasons, intended useful SUCCESS and exact negatives from ORACLE-DELTA.
No early extra Unsupported/protocol/frame failure can replace the intended read/ensures.
Keep Replace companion harnesses and exact caller selectors; do not infer companion
execution. Accepted4 head4 integration receipts remain historical evidence only.

After clean tests, require all4 S5 mutations using `--force-rerun`, unique outputs and
fresh independent snapshots of this same source. S5-MUTATIONS-READINESS.json gives
patch/input hashes, expected native verdict/N and mismatch reason. A compile failure,
timeout, early unrelated Unsupported or compiletest exit1 alone is not detection.
Golden inversion is sanity only. Mutations must never enter the exported source tree.

Keep source before/after identities, original argv, all exits/exceptions/term reasons,
native per-fixture outputs, always artifacts, nonzero unit counts and all failed attempts.
No F7 delayed_cache/scope units or E1 fixtures yet. No Gate A or formal proof credit.
All native checks and mutation execution on this head: NOT_RUN.
