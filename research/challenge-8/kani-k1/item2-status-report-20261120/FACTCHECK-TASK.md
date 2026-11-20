# TASK — independent fact-check of the item 2 status report (2026-11-20)

One stage. Read-only except for your own output. Do not run CI, cargo/rustc/Kani/CBMC, do not post anything.

## Input
`REPORT-CH8-ITEM2-STATUS-RU.md` in this directory (planner commit `1e27f92344`). Its author check (`AUTHOR-CHECK.json`) is not evidence for you; verify against the sources themselves.

## Do
1. Every number, commit, run id, path, count, timing and claimed status in the report: check against the cited committed artifact (and GitHub metadata for run ids / PR #752 head only via `gh` metadata, no logs). Sample at least 60 claims, covering every section, all table rows of the summary table, and all numbers in sections 5 and 6.
2. Check that each "что это НЕ значит" / limitation statement matches the admission notes (no overclaim: e.g. bounded vs general, real body vs model, u8 vs generic T, fixed lengths vs all lengths, init assumptions).
3. Check the challenge criteria quoted in section 1 against the repository copy of the challenge text.
4. Flag anything a skeptical external auditor would see as overclaiming, unclear, or missing (a gap we know about from the sources but the report omits).
5. Check the report does not mention other people's PRs/solutions for this challenge or external research links.

## Output
`FACTCHECK.md` here: verdict (ACCURATE / MINOR FIXES / MAJOR FIXES), list of checked claims with PASS/FAIL (compact table), each FAIL with exact correction and source, list of overclaims and omissions with suggested wording. Commit `[skip ci]` as Tiramisu-Cake <igkharin@gmail.com>, push origin, stop.
