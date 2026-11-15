# C2-SLICES stage0 — worker15 handoff

Entry g0:203c712c6b7ac3898f105c3ca89fe0d9a026baf6. Static research only. Dedicated clean detached read-only worktree: /root/kani-fix-3300-c2-slices-w15 at F ad499e41dd2db9ccd432f89721638a1f3a0bbd44. Worker14 source-map is read for cross-links and remains its sole write area.

Delivered:

- ORACLE-MAP.json / ORACLE-MAP.md: all182 final source/golden pairs,364 paths, flags/identities, source assertions, literal final oracles, owner, earliest complete-fixture dependency bound, linked worker14 source hunk sets;28 added compiler units.48 exact-N vs134 literal-only goldens explicitly distinguished.
- DOCS-MAP.json / DOCS-MAP.md: all3 docs files + edge README, every changed added-character/removal assigned once. Shared sentence/physical hunk ownership explicit; exact final F text retained.
- BASELINE-DELTA.json / .md: all20 unresolved-calls B1→F changed/added paths, including8 changes to submitted sources and6 new fixture pairs. No U test removal/modification; no B1 rewrite.
- SEMANTIC-LINEAGE.json: all21 old semantic rows →22 final selectors,8 strong cases,7 modes and7 composition roots, Replace companion selection and reduced mixed-inventory coverage preserved.
- ../ci/QUICK-PLAN.md / .json: per-head cumulative counts/selectors, unit9/9/1/1/6/2, exact12 expected /25 kani contract-smoke source selectors,17 inherited JSON suites,4 sensitivity mutations and artifact/exit requirements.
- ../f7/EXTRACTION-PLAN.md / F7-RESIDUAL.json: separate F7 plan,5 unchanged S4→F files,14 historical zero-context hunks, exact pre-F7 writer adaptation, both backends/writers,6+2 units and18 mixed-vs-isolated comparisons with order/binding limitations.
- INPUTS.json / UPSTREAM-SNAPSHOT.json: pinned inputs, required-read hashes, authoritative later acceptance references. Snapshot main=U, #5172 open/unmerged head=B1/base=U; merge_commit_sha is not merged base.
- STATIC-VALIDATION.json:15 passed static checks; all368 U→F test/docs paths covered exactly once. Current source clean, source/golden hashes/flags/counts, docs spans, semantic rows, unit counts, Quick expansion, F7 anchors and sensitivity hashes checked.

Native verification, local builds, source slicing, CI overlays/runs, push/publication and full-tree recomposition are NOT_RUN. Existing accepted F Quick/Gate A/Gate B′ are references, not qualification of future intermediate heads or new independent formal proof credit.

STOP dependency/test-map review before implementation. DEPENDENCY-REVIEW.md gives exact findings and minimal coordinator choices: head1 final integration fixtures require4/5; generic cycle units and ordinary smoke do not establish reached MIR/ordinary-entry integration. Nested layout fixtures also need4. Marked-model4 vs ordinary-union constant branch6 is an explicit shared dependency question, not permission to omit a required4 control or to change accepted order. No runtime regression is claimed without execution.
