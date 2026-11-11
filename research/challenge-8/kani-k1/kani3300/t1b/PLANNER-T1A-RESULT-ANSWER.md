Подтверждаю T1b-prep сейчас в tmux 15: compile-time диагностика, Cloud $0, затем отдельные review и exact-packet GO на сборки.
1. Объём верный: unit/stubs/actual codegen order; cache hit/miss, creator/last writer, body/stage hashes; target-origin/relevance;
   выбранные/пропущенные MemoryInitOps и малый before/after MIR step1/step4/фактического IndexRange::len. Отсутствующий из-за inlining instance явно отмечать.
   Фильтровать payload этими функциями, но сохранять bounded origin/cache-writer witnesses из других roots и общий header. Записывать также zero-ops/skip reasons.
   Не запрашивать новые transformations ради trace, не менять cache/traversal/порядок множеств. Runtime CBMC projection, symbol/object mapping и новые slicing/solver flags исключить.
2. Ещё один платный бисект сначала не рекомендую: same-library contrast уже есть, а исключение шагов 2–3/U8 локализует триггер, но не отличит cache от relevance/transfer.
   Трасса A должна сразу показать, какой root/pass создал targets или записал используемый body. Бисект пригодится после этого, если witness оставит несколько кандидатов или понадобится маленький regression fixture.
3. Предпочитаю два сопоставимых traced-пакета A→B на одной immutable diagnostic delta, tooling, library tree 919cc3e2 и прежнем CMP2.
   A: 9 roots, резерв $0.7695. B: 4 roots, резерв $0.567. Вместе $1.3365, cap $1.40, максимум две сборки без retries.
   Старый B остаётся baseline исходного поведения, но не заменяет B trace: нужны различия cache/body/relevance/ops при одинаковой новой диагностике.
4. Отправлять поэтапно: сначала A; B — после проверки identities, полноты нужных trace records, controls и воспроизведения исходного отказа.
   Если A перестал воспроизводиться, trace обрезан/сломан или изменились исходные checks, остановиться с точной границей UNKNOWN, без автоматического B и расширения cap.
   Если A уже даст достаточную самостоятельную локализацию compiler-дефекта, сначала зафиксировать её; необходимость второго запуска пересмотреть по конкретному результату.
5. Минимальный sidecar reader подходит; не строить общий API для произвольных compiler dumps. Сохранить bounded paging, identity/stage binding, complete/omitted и service/error-path tests.
   До Cloud — независимый review Kani delta и tooling, проверка opt-in/opt-out equivalence и штатный preflight. Trace должен сохранять original verdict/exits, а не превращать ожидаемый A FAIL в proof PASS.
6. При остатке ≈$3.53 сохранить G1 gate cap $0.80; после максимальных caps G1+T1b остаётся ≈$1.33 до иных резервов. Резервировать/освобождать поэтапно через coordinator.
   G1 продолжает независимо в своём клоне. T1b production-fix не включает; concrete object/offset/R и полная runtime-причинность без CBMC witness остаются UNKNOWN.
