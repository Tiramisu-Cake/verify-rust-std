# B3 T1b preparation validation — NOT RUN in CI

Local validation is limited to Python synthetic fixtures, Git and static parsing.
No local cargo/rustc/Kani/CBMC/goto-instrument, build, model recreation, artifact
download, push or CI dispatch was performed.

The synthetic suite uses only temporary text/JSON files and mocked subprocesses:

```
python3 -m unittest discover -s research/challenge-8/kani-k1/kani3300/b3p/t1b -p 'test_*.py' -v
```

Coverage includes exact-only AllocId renumbering and alias consistency; sensitive
positive-control payload replacement; unchanged padded-wrapper metadata/layout;
unknown and mixed function/type changes; complete 409-record/131-final inventory;
records/index disagreement, duplicate JSON keys and missing records; hash/tool
mismatch; null/wrong-type/partial/explicit NOT_RUN input; source/target argv drift;
original exits, command exception, timeout and partial output; bounded hash filenames;
mocked complete comparison with three distinct twice-dumped models in both modes;
A/A precedence and tentative B comparisons; insensitive control and tool nondeterminism.

Static workflow checks use YAML BaseLoader and bash -n on each run block. One job,
ubuntu-24.04, 60-minute cap, read permissions, attempt guard and always-upload are
present. Branch matching checked for `uninit-ci/b3-t1`, `uninit-ci/b3-t1b` and
`uninit-ci/b3-t1b-test`: the latter two match only T1b; the first matches only T1.
Python AST parsing and git diff --check also pass.

Independent Luna HIGH review used a separate context, without nested delegation.
Concrete parser findings were returned to its original worker: dropped/unexamined
text and duplicate fields, missing explicit padding, hashed/raw type spellings,
and preservation of component order and every non-payload byte. Final review
identities and final test count are recorded below.

This establishes package preparation only. The source artifact's accessibility,
installed binary hash, real dump determinism, positive-control gate and comparison
outcome remain unverified until the coordinator's CI job. No performance,
harmlessness, resource-regression, SAT or formal-proof credit is established.

Kani CI-only commit: `1a8faa3b60ee9a19534cdb57315e8887f5666301`,
parent `cfa4b0c5296b1f7735b0d4a138d339431dfbf93d`. Its four changed files
are confined to `.github/`; Kani source is unchanged.

Final synthetic result: **38/38 passed**. Independent review: earlier findings
resolved; no remaining findings in the final candidate. No actual display output
was substituted for the CI run. Source-format binding was also checked against
`Symbol::aggr_ty` (Base name is the full raw tag), `ensure_struct`, `ToIrep`
and CBMC 6.11.0 `expr2c`/`show_symbol_table` (raw type tags, Unit, natural padding).

Final reviewed file SHA256 identities:

| File | SHA256 |
|---|---|
| `.github/b3-t1b/run.py` | `173d2b7e76fe5d983f853208b1c3564f907e9681a9b8ffc8437584b31849defa` |
| `.github/b3-t1b/analysis.py` | `614ffda4a635eaff4c017572e6e4ac40adee4c2063f3541c4ea3532c2bf0b861` |
| `.github/workflows/b3-t1.yml` | `fab98580231950ecdc04cc675024a0d35efe5e16015dd414656b4767a5239edc` |
| `.github/workflows/b3-t1b.yml` | `cf2ed02beab6d2e827b1d4c2ed24e79496a6c4aa2aec02cefeea76fc8aa7d31f` |
| `.github/b3-t1/compare.py` (unchanged dependency) | `60a0537e3e102f1c91cf7dd92ca07c6dd849121150b05390f92c72ffda2b674a` |
