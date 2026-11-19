# PR 5172 offline review READY

Task `3dfa44344bd9c91a7307236d3bd9e5c9f6a848cc`. Review is complete and recommendation-only. Containing g0 commit is returned externally and binds MANIFEST.json; no implementation, CI or publication approval is implied.

- Published head: `80e5d6fabc0103b0b3117440007ad2d9475f9a9c`; tree `64adc9337b59f93d0d3acc1960666f0b1a42fb6b`; ref `fix/kani-uninit-unresolved-call-v3` in `Tiramisu-Cake/kani`.
- Base snapshot and merge base: `0aac16ef62da9e9d5645782d458593e5d78143ba` in `model-checking/kani`.
- Read-only detached source: `/root/kani-pr5172-slop-readonly-20261119`, still clean and exact.
- PR body SHA256: `09eb0ccd45ce870ea58eccb5c2038e353e5d680bf77722267795eded30531c56`.
- Full patch SHA256: `e1434be376fd3861ae4eee5c07bcf9cd3ffcd4de0bd44698114178ffb6457cce`.
- STYLE snapshot SHA256: `5932c080cd5938ad7fcb159b1847e663df828beffc17196716b001e6a5cb9e7a`.

All50 changed files have a disposition:6 compiler source files and22 source/expected test pairs. The22 source files contain24 proof harnesses. Recommend retaining them all, sharing the11 identical byte-copy helpers through standard excluded auxiliary storage and sharing8 byte-identical expected files through the existing directory fallback. No new test framework or forced harness quota is proposed. Keep plain/seeded compilations separate; actual codegen grouping and delayed-target collection make a combined file change the analysis condition.

REPORT.md gives prioritized findings and traces the unresolved-call/points-to/local/global instrumentation path. COVERAGE-EDITS.md/JSON names all current tests, helpers, flags, oracles and exact retain/share edits. FILE-DISPOSITIONS.json covers every changed file. CODE-COMMENT-EDITS.md corrects the misleading return-state-transfer comment and names small code/comment edits while preserving the fail-closed guards and upstream comments/licenses. PR-BODY.suggested.md contains only proposed public text, preserving #3300, the license and AI disclosure with a pending standard-CI placeholder.

The main separate follow-up is negative coverage for the expanded generated-shim union/unclassified-storage guards. Their source is retained; no unsafe execution is established by this review. SOUNDNESS-FOLLOWUP.md specifies discrimination requirements and explains why an earlier UnionAsField/setup failure or a caller guard alone does not establish the intended entry-guard coverage. Do not implement that fix as an automatic cleanup expansion.

STATIC-CHECKS.json records all50 blob/hash/byte and exact task snapshot/diff checks, source-clean identity,24 explicit harnesses,11 identical helper bodies,8 duplicate oracle files and actual discovery/fallback rules. A bounded port of the existing substring matcher shows why a naive initialized/partial merged oracle can accept swapped safety statuses. All current expected files require completed verification output; no internal-error golden was found. Native main-vs-head results and the CI claims in the original PR body were not freshly established.

Return this exact full commit and manifest to root. Later scoped implementation, exact review, native regressions/standard CI and owner publication remain separate. No source/test edits, compiler/rustc/rustfmt/Cargo/Kani/CBMC/expansion/verifier/fullrunner, CI/push/live-PR/body/comment changes, raw logs/GCS, ledger/accounting, subagents or model/settings changes occurred. High/FastOFF preserved. Do not auto-start PR5195; VRS752 stays deferred.
