# Merge-R17 — actual caller / CURRENT; refinement and borrow

Task ID: `merge-caller-refinement-autonomous-2026-10-21-r17`; previous task: `merge-caller-current-autonomous-2026-10-21-r16`.
Owner: **Merge**. Phase: `MERGE-CALLER-REFINEMENT-R17-2026-10-21`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance.
The owner may proceed within this task and its bounds. Start with T0 NOT_SET; prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, then obtain the required independent review and register the exact phase through the assigned branch client before proof work.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `5b685bafdc8d88f6b22a93e52ea7446ffcccfeac`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/actual-glue-instance-20261011` at `660b576b6b1608db913c51e0785b443a8733396f`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R17-BUDGET-20261021.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R16-BUDGET-20261021.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until the owner registers.

## Goal and steps

Новая R17/3600с/Cloud явно разрешена. Автономно продвигай actual caller normal/unwind и original borrow/unsize по миссии Merge. Bounded body отдельно от B2; продолжай до окна/реальной границы.

1. Сохрани R16 syntaxfix. Reviewed same-op RawPtr refinement + controls/new pins → exact caller target. Review semantic diff: Luna HIGH; preparation/compiler/proof только Cloud.
2. Проверь raw caller normal/unwind с actual callee и точными source/stage/target receipts. Отдельно решай original as_mut_ptr/unsize через source-bound metadata, реальный borrow/lifetime и checked resource conversion; raw adapter не заменяет original prefix/caller.
3. После blocker продолжай CURRENT/backedge, false/true/panic/Drop/Resume и final matrix. Review packets/observations/CHECKPOINT — по CORE. Сам выбирай полезные следующие steps.

## Special bounds

- Сначала full plan timeout1200/execute<=780/soft<=765/reserve>=420. Учти nested compile reserve140; иной plan только после effective-budget review/tests. После main — завершение начатого, без новых Builds/retries/гипотез.
- RawPtr matching: одинаковые mutability/pointee/place/full origin; без RawPtr↔Ref, address-only ownership, broad placeholders, новых borrow/trusted premises. Сохрани прежнюю narrow R8 allocation boundary, posts и controls; см. pinned GLUE profile и R16 designs. Новые source-preserving fixes/profiles разрешены.
- Original gate/raw caller/isolated body — разные claims. Missing bindings => INCONCLUSIVE; bounded/source PASS не B2/independent credit. Сохрани array11/R9, publication guards/caps и чужие dirty policy/guides. Blocker у Merge, не maintainer.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: P3 raw caller: refiner RawPtr not yet supported; verifier Parseerror443. Syntaxfix at last source6fd50c6 is reviewed but P4 never reached proof. Original caller still rejects placeholders441/249. (refinement_checker.ml:2853; verified/lib.rs:443; original full441/prefix249) [Build e2c971ba-ab62-4cd9-a193-3d4f98797cd7]
Next: Register fresh R17 after effective-budget check; reviewed checked RawPtr matching/new pins and controls, then actual raw caller; retain and advance original reference/unsize gate.

## References

- [R16 raw caller / next contract](cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md)
- [Original caller borrowing boundary](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md)
- [Prior reviews / timing correction](cloud-build/origin-layout/R16-REVIEW-20261021.md)

## Отчёт агента

**merge-caller-refinement-autonomous-2026-10-21-r17 · merge · MERGE-CALLER-REFINEMENT-R17-2026-10-21 · NOT_STARTED**
Updated: 2026-10-21T18:22:15Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `660b576b6b1608db913c51e0785b443a8733396f` / `eb61e49397cd9973ec12d1675bd8bd4867c7374de22e7c1c6a8a58e991266375`.
Dates: T0 `NOT_SET`; main `NOT_SET`; absolute `NOT_SET`. Budget 3600s: 0s spent, 0s retired, 3600s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: P3 raw caller: refiner RawPtr not yet supported; verifier Parseerror443. Syntaxfix at last source6fd50c6 is reviewed but P4 never reached proof. Original caller still rejects placeholders441/249. [Build `e2c971ba-ab62-4cd9-a193-3d4f98797cd7`]
Next: Register fresh R17 after effective-budget check; reviewed checked RawPtr matching/new pins and controls, then actual raw caller; retain and advance original reference/unsize gate.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
