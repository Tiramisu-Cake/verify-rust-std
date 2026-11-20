# TASK (planner) — status report on Challenge 8 item 2 (sorting) for an external audit, 2026-11-20

The owner will hand this report to an independent auditor, who will check everything, assess the work and propose ideas we have not found. Write it so that a strong Rust/Kani engineer who has not followed our process can verify every claim from the repository.

## Deliverable
`REPORT-CH8-ITEM2-STATUS-RU.md` in this directory (Russian; technical terms, identifiers and paths as is). Target 300–500 lines; tables where they help. Commit with `[skip ci]` as Tiramisu-Cake <igkharin@gmail.com>, push origin, then tell the coordinator (no reply needed before that). You may hand bounded fact-gathering sub-tasks to the coordinator, who can dispatch free workers (14, 15).

## Required structure
1. **Цель и критерии.** What Challenge 8 item 2 requires (quote the challenge text / tracking issue wording from the repository copy), and how we interpret each criterion (lengths, element types, comparator, form of contracts, "no UB"). Mark where our interpretation is a choice.
2. **Что опубликовано.** What verify-rust-std#752 contains today (head, harness count, lengths/types, Kani pin), and what of the new item-2 work is NOT yet in #752.
3. **Что сделано после #752 (S1–S4P3).** For each stage: function(s) under proof, real body vs model/summary, domains (types, lengths, base/geometry, aliasing, initialization), properties (sortedness, permutation/multiplicity, no panic, memory safety, frame), result class and what it does **not** mean. One summary table: function × property × domain × status × evidence (admission commit, run id).
4. **Как сделано.** Method in plain words: harness/contract design, negative controls and `cover` nonvacuity, the U-site / unreachable policy, the `lib.rs:0:0` exact location exceptions and why no general rule, "QUALIFIED_BOUNDED_SOURCE_REPORTED" — what each word means, the pipeline (std source branch → same-tree no-skip sibling → CI lane `ch8-s2.yml` → compact evidence → intake → independent review → admission), Kani version and flags. State what is trusted (Kani/CBMC, models, stubs, assumptions) explicitly.
5. **Ресурсы.** CI runs used for item 2 (from the coordinator ledger), wall time and RSS per proof family, distance to the 600 s per-harness budget, which families do not fit.
6. **Блокеры и проблемы.** N13/N17 (child 600 s timeout, incomplete inventories) and the options you see; partial `MaybeUninit` initialization (needs `-Z uninit-checks`, depends on item-1 work); full lengths 16/32; fitting S5 into the organizers' CI; the stale Kani pin in verify-rust-std (c5e65fdfc3) and what it blocks; anything else you consider a risk (including process problems: compile failures, wasted runs, over-engineering, places where we might be proving the wrong thing). Be candid.
7. **План.** Remaining stages (S4 rest, S5 plan `cf0b8f4e9f`, closure map / #752 update plan `4576414177`) with order, dependencies, rough cost in CI runs and calendar time, and what would let us declare item 2 done.
8. **Вопросы к аудитору.** Where we are unsure, where an outside idea would help most (e.g. alternative proof decomposition, cheaper oracle for N13/N17, induction vs bounded enumeration, model vs real body trade-offs).
9. **Приложение.** Index of key artifacts: path, commit, one line each (plans, admissions, intakes, reviews, ledger, run ids).

## Rules
- Every number and claim must come from a committed artifact; cite path + commit. Mark **[факт]** (verified against a source) vs **[оценка]/[гипотеза]**. If you cannot verify something, say so.
- No marketing, no padding; strengths first is fine, but list gaps plainly.
- Do not reference other people's PRs or solutions for this challenge, and do not cite external research links; describe only our own work and the upstream challenge text.
- No CI, no pushes outside g0, no publications.
