# RESULT AUDITREADY (2026-11-03): audit package wording + cover-parser prototype

- **Docs base** `eee578edd54cd27c2b227e621c1b61472848174f`; **final docs SHA** = the commit that adds this file on
  branch `docs/ch8-auditready-20261103` (its parent is the base). Documentation/prototype files only.
- **Library unchanged:** `library/` tree `a45388ac593c809405558ea0c27599f487b17e4e` (= INTEGRATED); workflows,
  `scripts/run-kani.sh`, K-1 tooling and pins untouched. Scope, counts and source snapshots of the report unchanged.
- **Wording:** the v6 CI run is now named "upstream `kani.yml` run in our fork", separated from upstream PR checks and
  committee acceptance; partition jobs (split the full `kani list`) vs the separate autoharness schedule stated, Run
  41404150041 / v6 / 16 success jobs kept, per-harness times and covers stay UNKNOWN. CASE5: `KeyB16`, `KeyB17`,
  `Sort4ReadB16` rows "reported SUCCESS with an OPEN model-trust caveat" in README Section 2, harnesses.tsv rows and
  claims `V6-SWAP`/`V6-SORT4`. Cover enforcement of the ordinary workflow OPEN; 57 panic cuts = normal-return scope,
  not defects or proven vacuity.
- **Prototype:** [cover_parser.py](cover_parser.py), [COVER-PARSER.md](COVER-PARSER.md); prototype only, **not
  integrated into CI; no historical cover acceptance established**; never run on a real log. Integration: NOT_RUN.
- **Tests/checks (local, Python stdlib + Git):** `test_cover_parser.py` 44/44 synthetic tests OK;
  `check_audit_report.py` PASS on its pinned inputs (453 harness rows, 64 claims, 15 findings, 12 snapshots); the
  checker gained the new package files and lexical wording checks, nothing was relaxed.
- **Limitations:** terse record shapes taken from the K-1 parser, not re-validated on a pinned real log; terse output
  gives cover counts only (route witness = all covers satisfied); no v6 cover manifest (totals UNKNOWN).
- **Not done:** no cargo/rustc/Kani/CBMC, no proof, Build, Actions/CI or deploy. Cloud spent $0, reserved $0.
- **Pending owner decisions:** integration of a cover gate (separate patch, not a v6 property); any PR/issue, its
  text and submission; any v7/rebase; CI on such a version.
