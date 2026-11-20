# Item 2 report: apply fact-check fixes and readability pass (planner, 2026-11-20)

Input: REPORT-CH8-ITEM2-STATUS-RU.md at 1e27f92344; independent fact-check FACTCHECK.md at 62ff1c6af5 (verdict MINOR FIXES, 118 PASS / 2 FAIL).

Edit REPORT-CH8-ITEM2-STATUS-RU.md in place (one commit, [skip ci], author Tiramisu-Cake <igkharin@gmail.com>, no Co-Authored-By). Do not change facts, statuses, numbers or admissions beyond what is listed.

1. F01: add the baseline array-model caveat from the published #752 body (Limitations / Model trust) to section 2 or 4.1, using the wording proposed in FACTCHECK.md, F01 paragraph.
2. F02: in section 9 replace the bare CH8-DISPATCH-LEDGER.md path with research/challenge-8/kani-k1/CH8-DISPATCH-LEDGER.md, keeping commit 26db9b6306.
3. Section 4.5: add the lifecycle-diagnostics clarification proposed in FACTCHECK.md (bounded preview; omitted events UNKNOWN).
4. Readability for an external auditor who did not follow the process:
   a. At the very top, after the title, a plain-language summary of at most half a page: what item 2 requires, what is proven and on which domains, what is not, the main blockers, the next step. Minimal jargon.
   b. A glossary section right after the summary: every internal term or abbreviation used in the report (for example PFC, Q, U, V34, base1, child600, root, admission, C/O roles, S1..S4P3, N13/N17, MU48, KeyLess, OFF/ON lanes, QUALIFIED_BOUNDED_SOURCE_REPORTED, charge0, pin names). One line each.
   c. Fix missing spaces between words and numbers or identifiers (for example до16, run42363378063, N0..9 glued to words). Mechanical only.
5. Leave the heading Дополнение координатора and its placeholder as is; the coordinator writes it.
6. Update MANIFEST.json hashes if it lists the report hash.

Constraints: no external research links, no other challenge PRs or solutions, no CI runs, no cargo/rustc/Kani. End the turn after the commit with a short handoff line: commit SHA and a list of changes.
