# Source-only PR checklist — static observation, 2026-11-13

PR source is clean `cd41a5c74b0c42edf4f08834b3e2808dd3344cab`, parent
`107a1e504cd69a2f3483717c8bcfcfa59814c557`, tree
`92c03401d6c2a6da069670260244bc021bbdba99`. It is one bugfix commit with a
nonempty explanatory body and tests in that commit. No CI-only tree is a PR head.
The source delta contains one production-line change, 13 regression directories
with 13 descriptors and one unit source defining three focused cases. All 28
changed file blobs and full src/unit/regression subtree IDs remain unchanged in
our CI-only HEAD; SOURCE-UNCHANGED.json records the hashes.

Pinned `.github/pull_request_template.md` is recorded by blob/SHA256 in INPUTS:

- Commit message body: present, explains zero-width conversion and tests.
- Added production procedures documented: none added; not applicable.
- User Guide: draft proposes no update for this internal conversion fix. This is
  the stated template disposition for owner/upstream review, not a new docs edit.
- Regression/unit tests: present in the same source commit (paths in INPUTS.json).
- Performance data: no performance claim, not applicable.
- Single feature/bugfix: one bits2expr array-width guard fix and related tests.
- Unrelated formatting: no extra production changes; pinned formatter outcome
  reused from r2, fresh formatter invocation remains NOT_RUN locally. Empty diff
  is accepted by the unchanged r2 check_format.py.

Pinned issue template fields (version, OS, command, expected, actual) are present
in the existing ISSUE draft; existing PR/issue drafts are not changed here.
Disclosure remains verbatim:
Disclosure: this change and description were prepared with the help of AI assistants.

Counts must remain distinct: focused C13 includes an intended negative, so it is
13 successful oracles, not 13 VERIFIED programs. Neighbour13 directories have14
descriptors (byte_extract1 has two). Focused unit3 is separate from the remaining
`[util]~[zst-bits2expr]` denominator212 in r2. Fresh actual count/list/results are
NOT_RUN; workflow reports actual selection and never hardcodes212/212.
R2 fix focused13/neighbours13/unit3 PASS and util205/212 are coordinator-reported
historical receipts, not fresh results. Later owner-literal/Kani-like C claims
remain attributed to PR-READINESS.md; early CI-RESULT-R2.md is not rewritten.

Fetched upstream develop is `37a17adc07f29e1127f100debf1d8eea00532a24`.
Its delta from the source parent touches C frontend void-pointer arithmetic and
three regression paths; no source-delta path overlaps. Git merge-tree --write-tree
returns0 and source-only merge tree `71eff7206aed7683e649fea4e151ac2dae2f7b61`.
This is static mergeability, not a build/CI PASS. No source rebase is performed.
If a later upstream overlap or equivalent fix appears, hand off rather than
silently rebasing or adding a second source fix.

Only coordinator may push the CI-only HEAD and run the workflow. Source/tests,
old results/ledgers/default develop and issue/PR state remain unchanged. No local
compiler/CBMC/Kani build/verification, raw artifact download, worker push/dispatch,
full regression, macOS, or Kani replay. Cloud $0; stop after reviewed package.
