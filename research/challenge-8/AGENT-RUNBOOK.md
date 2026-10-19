> **Evidence v0.9, 2026-10-19 — приоритет:** [краткий guide](EVIDENCE-READER-GUIDE.md). `/usr/local/bin/smallsort-brief`: Brief → адресный Reader → при нехватке данных `--refresh --file` (targeted) → admin audit, только если всё ещё недостаточно. Refresh разрешён без отдельного audit; общая квота 16 резервирований на Build, ошибки тоже могут её расходовать. Полные/raw логи, массовая выгрузка и обход удержания запрещены. Заменяет старый порядок Reader → сразу audit; сессии/budgets не меняются. [Literal Locators v0.10](EVIDENCE-LITERAL-LOCATORS.md): `--locate` → координаты → bounded fragment; `--near-position --unit` по установленному anchor. Доступны по подтверждению владельца; общая16-квота, без вывода AST/type/parser binding и без обхода WITHHELD.

> **Процесс итераций, 2026-10-19:** [ранние checks → целевой proof → полная матрица](ITERATION-PROCESS.md). Service error-path tests обязательны для затронутого runner; использовать существующий Cloud preflight. Принять на безопасной границе без изменения активных inputs/T0. Измерять закрытые proof obligations отдельно от setup-работы.

# Challenge 8: единая процедура работы

Нормативные границы, миссии и режим сессий — в [WORK-POLICY](WORK-POLICY.md);
правила proof integrity — в [AGENTS](../../AGENTS.md). Этот файл задаёт процесс,
[Cloud runbook](cloud-build/README.md) — команды и учёт,
[COMPLETION-PLAN](COMPLETION-PLAN.md) — конечные обязательства.
[SmallSort Evidence Brief](EVIDENCE-BRIEF.md) задаёт приоритетный порядок
получения и интерпретации результатов CI.
[Архив](archive/team-procedure-2026-10-10/README-ARCHIVE.md) сохраняет прежние
Actions-примеры, ветки, бюджеты и stop-условия без действующей авторизации.

## Вход в работу

1. Проверить `git status --short`, remotes, branch, HEAD, `git worktree list`,
   отдельные git-dir/index. Работать в назначенном worktree; не переключать чужой.
   Выполнить `git fetch origin`; проверить, что origin — наш форк. Не сбрасывать
   локальные правки и не объединять исследовательские истории ради docs.
2. Прочитать общие правила и записать policy revision (полный commit прочитанной
   редакции) в существующей session card/checkpoint. Принять docs по
   [ADOPTION](ADOPTION.md) на безопасной границе, сохранив inputs активного Build.
3. Прочитать STATUS своей ветки и самый свежий checkpoint/evidence/ledger.
   Хронологически новый заголовок не заменяет точные source/tool/run identities.
   При устаревшем STATUS или ledger с истёкшим deadline не предполагать живую
   авторизацию: зафиксировать расхождение, не переносить остаток.
4. Сверить действующее поручение: миссия, конкретный scope/tool profile,
   patch authority, lanes, owner/ledger/state, начало, main/absolute deadlines
   и Cloud ceiling. Docs-only/status запрос не возобновляет stop.
   В новом режиме миссия продолжается между отдельно разрешёнными сессиями;
   старые закрытые phase cards остаются историей.
5. Для proof-работы проверить доступ к существующему dispatcher и собственные
   active/unresolved Build IDs. Использовать разрешённые эквивалентные клиенты
   при проблемах доступа, не заменять Cloud локальной verification.

## Experiment card до реализации и запуска

Дополнить существующий EXPERIMENT-LOG/phase card; не вводить второй параллельный
журнал. Записать:

- Actual std function/source и обязательство; caller и источник каждой premise.
- Фальсифицируемую гипотезу и отличие от последнего эксперимента.
- Точный domain, safety resources и полные target normal/unwind/abort posts;
  partial diagnostic явно отделить от конечного контракта.
- Tool/compiler/spec/patch/profile identities, разрешённую область изменения,
  semantic rationale и trust/admission/regression gates для патча.
- Positive cases и каждый negative: expected stage, predicate и location.
  Изолировать baseline от unrelated failing helpers.
- Source/ghost-strip/MIR/AST/refinement, actual callee/caller execution,
  nonvacuity, leak/unwind, covers/UB и full unit exit checks, которые нужны claim.
- Решение для каждого исхода: рутинный fix, следующий шаг миссии или запрос
  владельцу при выходе за разрешённые границы; reviewed lane и доступный бюджет.

Нельзя выводить pointee права из равных numeric addresses или ownership bridge
из `slice.share`. Setup/frontend/unsupported-operation failure до target не
является intended negative. Повторный отказ без новой информации требует
переоценки, а не ещё одного такого же запуска.

## Edit → publish → Cloud → evidence → следующий шаг

1. Сделать минимальное изменение внутри миссии/allowlist. Проверить diff и
   разрешённые static/service checks. Proof/extraction/build локально не запускать.
2. Commit и обычный push в собственную назначенную ветку форка. Проверить полный
   remote SHA. Proof и infrastructure SHAs могут различаться; оба опубликованы.
   Рабочее дерево не является Cloud input.
3. Сверить свой ledger/deadline/allowlist и v2 capacity. Если есть подходящий
   active/unresolved Build, разрешить/мониторить его вместо дубликата. Submit
   выполнять по [Cloud runbook](cloud-build/README.md) с exact SHAs и recipe.
4. Записать token, Build ID, inputs/config hashes. Неизвестный ответ API остаётся
   unresolved; отсутствие ID не разрешает повторный submit. Не обходить лимит
   owner alias или ручным удалением reservation.
5. Следить за конкретным Build в активной сессии: короткие poll/wait, обычно
   примерно раз в минуту; не отдавать мониторинг владельцу. Примерно через час
   дать короткий отчёт по [режиму сессии](WORK-POLICY.md#1-миссия-полномочия-и-сессия),
   затем продолжать в scope. Сборка/очередь сама по себе не повод закрыть сессию.
6. После terminal status получить отчёт командой `smallsort-brief BUILD_UUID`.
   Следовать [Evidence Brief policy](EVIDENCE-BRIEF.md): при недостатке отчёта
   сначала выполнить адресные Reader-запросы, затем узкий --refresh по guide; если фактов всё ещё нет,
   зафиксировать ограничение и запросить отдельно разрешённый administrative audit.
   Не читать raw evidence. NOT_RUN не считать PASS.
7. По Brief классифицировать blocker: setup/build, frontend/export/decode,
   unsupported operation, resource/post proof, refinement, timeout/OOM или infra.
   Если причинность не установлена отчётом, оставить её неподтверждённой; первое
   наблюдаемое сообщение об ошибке само по себе не доказывает causal blocker.
   Рутинный fix внутри scope и промежуточный PASS не требуют остановки при наличии
   времени/бюджета. Новая trust/architecture область требует отдельного решения.
8. После изменения source/proof/profile нужен новый exact-SHA proof run. Для
   classifier/parser-only fix допустимы малые синтетические service tests по
   WORK-POLICY §4. Полный raw-evidence replay требует отдельно разрешённого
   administrative audit. Прежний verdict сохранять отдельно.
9. Обновить компактный STATUS и существующий evidence record. Выбрать следующий
   actual шаг миссии. За main deadline не начинать новый Build/эксперимент;
   до absolute deadline — только начатый шаг, evidence, учёт и checkpoint.

## Компактный STATUS и существующая отчётность

STATUS своей рабочей ветки содержит один текущий блок, обычно до одной страницы:
миссия/owner; авторизация текущей сессии; последнее проверенное обязательство
с точным domain/profile; первый blocker; следующий шаг; ссылки на evidence и
checkpoint. Main содержит краткий индекс состояния команды и датированный
snapshot, а не авторизацию или копию чужих рабочих STATUS.

Предыдущий блок сохранять до замены: в существующем датированном checkpoint,
EXPERIMENT-LOG или архиве STATUS. Не удалять исторические run IDs, failures,
verdicts и retired budgets. coverage/design обновлять только если изменился claim.
Phase cards с прошедшими сроками — evidence; их старые «next» не инструкции.

В существующей session card/checkpoint записывать следующие поля рядом с уже
имеющимися результатами, без нового обязательного machine schema:

| Поле | Что фиксировать |
| --- | --- |
| Actual caller progress | Какой caller теперь устанавливает/использует какие premises; что пока supplied или не достигнуто |
| Target reached by run | Build ID → actual obligation, entry/target/post reached, verdict; new proof / replay / NOT_RUN раздельно |
| Время | Подготовка/dependencies/verifier build; extraction/refinement/proof; packaging/upload/hash/Evidence Brief analysis отдельно |
| Учёт | Wall-clock начало/main/absolute/end; conservative Cloud charge, remaining/retired, active/unresolved IDs |
| Общий blocker | Одна причинная формулировка, затронутые select/merge/maintainer и ссылки; fixes и trust debt раздельно |
| Следующий шаг | Одно полезное действие в миссии и нужная будущая авторизация, если сессия закрыта |

Использовать существующие ledger API timestamps, stage resource/time files,
summary/classifier/receipts. Не считать create→finish временем proof: это charge
с queue/setup/upload. Неизмеренные интервалы отметить «нет данных»; ручные оценки
пометить. Автоматические данные не переписывать ради формы отчёта.

На закрытии сверить accounted terminal Builds, integrity, собственные unresolved
и draft state; убрать только свой stale ready request через client, если разрешено.
При активном/unresolved Build записать ID/token и следующий reconciliation action;
не удалять состояние ради чистого checkpoint и не обещать работу после окна.
Остаток закрытого счёта retired, миссия сохранена. Documentation-only changes
требуют diff/link review, без proof build.
