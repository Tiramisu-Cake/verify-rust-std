# TASK — worker13: пакет S1-05 = повтор S1-04 с полным evidence (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: пакет S1-04 (твой, `kani3300/ch8-s1/s1-04/`, control `205b0e98c7`, std `5be85699b8`, tool 0aac), run
43830757263, твой intake (`run-43830757263/RESULT.md`) и офлайн-приёмка w11
(`run-43830757263/accept/ACCEPTANCE.md`, ACCEPT.json, g0 `64eded688d`).

Итог S1-04: 35 harness выполнены (27 SUCCESS, 8 FAILURE = негативы), но positive acceptance 0. Причина —
evidence, а не proof: runner запускал Kani с `--output-format=terse`. Stock export поэтому не сохранил
description/file/line для 413 UNREACHABLE checks и 115 covers, а SUCCESS checks пришли только счётчиком. Без этого
нельзя связать unreachable с ролями (post/frame/relation) и covers с сообщениями.

Задача — подготовить пакет S1-05 (без dispatch), который даст этот evidence. Proof-содержимое тот же std
`5be85699b8`, те же 35 harness; source не менять, если не обязательно.

1. Вывод Kani: по pinned исходникам 0aac (`cbmc_property_renderer.rs`, `schema_utils.rs` и др.) выбрать режим,
   при котором для **каждого** check и cover сохраняются ID, class, description, file, line, status: regular output
   и/или проверенный structured export. Учесть размер логов/artifacts для 14 групп; artifacts — компактный
   структурированный файл на группу, raw stdout не нужен целиком.
2. Runner: убрать in-runner oracle/veto-классификацию (она давала устаревшие метки). Runner только собирает
   per-row evidence с exits/elapsed/RSS; приёмка офлайн по ACCEPTANCE-POLICY-BATCH (классификатор w11).
   Сохранить: preflight, single parent, changed paths, `GITHUB_RUN_ATTEMPT==1`, типизированный YAML-гейт, depth 3.
3. Включить исправление macro source binding (`source-binding-fix.patch`, line 29 + anchors 66/67/68).
4. F7/F8 attachment mutants: заранее объявить oracle по `future_oracle_proposal` из ACCEPT.json w11 (exact
   ID/description/site, единственный разрешённый failure, unmutated companion с достижимыми post-return covers).
   Для F1–F6 — сохранить объявленные oracles.
5. Тесты пакета: регрессии на (a) парсинг rich export по реальному фрагменту S1-04 и (b) отказ, если у какого-то
   check нет description/location. Плюс прежние shallow/YAML регрессии.
6. Порядок групп и max-parallel — как в S1-04; оценить общее время.

Выход: g0 `kani3300/ch8-s1/s1-05/`: control-кандидат (новый commit поверх parent как в S1-04, локально, без push),
CI-REQUEST.json/md, VALIDATION.json, review-packet, HANDOFF.md (что изменилось относительно S1-04 и почему, точный
ожидаемый размер artifacts). Коммит в g0 `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Последней строкой READY <g0> <control SHA> или STOP <причина>.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs целиком не читать.
