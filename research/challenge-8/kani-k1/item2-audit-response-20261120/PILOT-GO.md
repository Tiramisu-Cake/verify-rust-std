# GO координатора: q-пилот, кампания 1 (2026-11-21)

Решение координатора (полномочия владельца от 2026-11-21: q-пилот — главный шаг, лёгкая дорожка, CI без лимита, экономно). Планер согласовал направление (FIX-DIRECTION.md, PILOT-FIX-TASK.md).

- std: Tiramisu-Cake/verify-rust-std `5544e01921d5c67c21d4ab919e8f76b43f884d92` (tree `551a7300bb…`), ветка `experiment/ch8-q-pilot-v1`, запушена.
- control: tree `3cead694cbc4ae70b39be2a6b5f12284838305bb`, parent `ba32286ee4…`, request sha256 `827d58e5e4…`; триггер — коммит-близнец 876a75ca9f без [skip ci], push в `uninit-ci/ch8-q-pilot-v1` в Tiramisu-Cake/kani. Срабатывает только `ch8-q-pilot.yml`.
- tool: model-checking/kani `0aac16ef62…`.
- Семь корней P-1…P-5c, child ≤600 с каждый, job ≤180 мин.

Delta review (PILOT-DELTA-REVIEW.md, 9b7b31b901): CHANGES_REQUIRED по двум путям отказа финализации — (1) порча рабочего CI-REQUEST.json во время прогона, (2) EIO на fsync каталога. Решение: **принять риск для исследовательского прогона.** Оба сценария на чистом GitHub runner маловероятны; худший исход — потеря артефакта одного прогона и повтор, без риска для достоверности (результаты RESEARCH_ONLY, proof_credit=NONE, интерпретация офлайн по PILOT-ANALYSIS-CHECKLIST.md). Исправить до приёмочного использования runner.

Ledger: строка «item 2 q-pilot campaign 1» в CH8-DISPATCH-LEDGER.md.
