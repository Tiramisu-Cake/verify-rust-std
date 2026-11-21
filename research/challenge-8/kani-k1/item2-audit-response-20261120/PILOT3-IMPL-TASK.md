# Кампания 3 q-пилота: только P-2, local RSS cap 9 GiB (воркер, 2026-11-21)

Основание: `PILOT-RUN2-ANALYSIS.md` — рекомендация планера, решение координатора: принять.

Изменяется **только control**. std `0e9b28b293f4360b005d33583d2cf9ac06d1790b` и tool `0aac16ef62…` без изменений.

- Worktree `/root/kani-ch8-q-pilot-control-v1`. Новый коммит с parent `ba32286ee4f370593a2c9f0d8834a12d473c82d7` (как прежние; текущий кандидат кампании 2 — `301bd6465a`, trigger `86d670c170`).
- Roster: один корень `slice::sort::shared::smallsort::verify::sorting_q_pilot::p2_sort13_u8_b01_len17_q_any`, normal cfg, прежний argv, unwind36, child 600 с.
- Local RSS cap 9 GiB (`9437184` KiB) только для этого профиля; outer 12 GiB, reserve 2 GiB, правило `group_cap=min(12 GiB, A−2 GiB)` и `min(local, group)` — без изменений. Записывать nominal и effective cap в raw index.
- Frozen `ROOTS`/`LIMITS` в `run.py` и `CI-REQUEST.json` согласовать с одиночным roster; workflow не трогать, если не нужно (если нужно — минимально и с пересчётом хеша в request). Без mutable inputs.
- Тесты: добавить/обновить в `test_run.py` проверки одиночного roster, отказа при неверном root/cap, применения effective cap; все прежние сценарии сбора/очистки должны проходить.
- Локально: `run.py validate` с синтетическими GitHub metadata, `check-source` на std 0e9b28b293, `test_run.py`.

Без cargo, rustc, Kani, CBMC, CI и пушей. Коммит `[skip ci]`, Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By. Handoff `PILOT3-IMPL-HANDOFF.md` в этом каталоге (SHA/tree/parent, request sha256, дельта, тесты), коммит в g0 `[skip ci]`.
