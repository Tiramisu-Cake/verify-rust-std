# Короткие задания, checkpoint и подготовка сессии

Обязательное чтение — [CORE](CORE.md), CURRENT-TASK и CHECKPOINT/STATUS своей ветки. Здесь справка по конкретным действиям. Инструкции принимаются в **следующей** сессии; текущие T0/inputs/ledgers/client gates неизменны. Инструменты используют Python standard library и локальный Git; actual proof/toolchain и Cloud вызовов нет.

## 1. Координатор выдаёт короткое задание

Заполни [assignment.example.json](examples/assignment.example.json) по последнему **закрытому** checkpoint. Нулевые SHA и REPLACE — placeholders, не авторизация. Одно goal, до3 steps, до3 особых границ с exact profile/review references. Handoff содержит факты/evidence, OPEN, blocker, отвергнутые подходы, next и artifacts. Текст CURRENT ограничен6144 UTF-8 байт: длинное описание остаётся в связанном артефакте, значения/SHA не обрезаются.

```bash
smallsort-session task create --spec /tmp/assignment.json --out /tmp/CURRENT-TASK.preview.md
smallsort-session task install --spec /tmp/assignment.json
```

`create` делает только новый reviewable draft. `install` проверяет assigned Git branch/fork, baseline/profile/tool identities, **закрытый** previous ledger и отсутствие own occupied/unresolved reservation под shared lock. Затем сохраняет прежние task/STATUS/instructions/checkpoint в task-history, устанавливает короткий AGENTS/CORE, новый CURRENT и NOT_STARTED checkpoint/views. T0 не устанавливает, новый live ledger/profile не создаёт, Git commit/push не выполняет. При active account, conflicting history, wrong SHA/branch или symlink отказывает до изменений. Координатор проверяет diff, коммитит и публикует только назначенные файлы. Не переносить чужую историю/whole branch ради инструкции.

## 2. Агент поддерживает один checkpoint

Формат `smallsort-checkpoint-v1` описан в [checkpoint.py](checkpoint.py), пример — в [tests](test_checkpoint.py). Это переданное состояние, **не самостоятельное evidence/admission**. `confirmed` требует assurance SOURCE_REPORTED или INDEPENDENTLY_ESTABLISHED и evidence path/SHA/Build ID. Unknown — null/UNKNOWN; source claim не превращается в independent proof. Для реальной scientific acceptance действуют прежние receipts/gates.

Обязательные сведения: owner/task/phase; exact source/tool/profile; state NOT_STARTED/ACTIVE/CLOSED/HANDOFF и время; T0/main/absolute; spent/retired/remaining; active/unresolved; подтверждённое и OPEN; точный blocker; rejected approaches с причиной; следующий шаг. Remaining включает зарезервированное время. Для CLOSED остаток0/нет active-unresolved; незавершённый handoff помечается HANDOFF с IDs. assignment_sha256 связывает checkpoint с байтами CURRENT **до** единственного `## Отчёт агента`; обновление отчёта не меняет этот digest.

```bash
smallsort-session checkpoint validate research/challenge-8/CHECKPOINT.json
smallsort-session checkpoint render research/challenge-8/CHECKPOINT.json --format status
smallsort-session checkpoint write-views research/challenge-8/CHECKPOINT.json \
  --status research/challenge-8/STATUS.md --task research/challenge-8/CURRENT-TASK.md
```

STATUS показывает handoff; итог в CURRENT — короткое состояние/бюджет/blocker/next со ссылкой на подробности. Они генерируются, вручную переписывать пять одинаковых сводок не нужно. Existing ledger/Build receipts остаются источником actual charge/status; checkpoint их не исправляет. Исторические отчёты сохраняются. При несовпадении assignment digest или переполнении view — явный отказ, без усечения.

## 3. Агент готовит новую сессию

В фактический T0 заполни [session.example.json](examples/session.example.json). Бюджет3600, main120+finish30, max timeout<=1200, report reserve>=420 Merge/>=240 Select. T0 передаётся явно; подготовка не придумывает дату и не переносит старый счёт. Указывай baseline закрытой сессии; HEAD может быть новее после публикации задания. Закрытые ledger/profile должны оставаться точными committed bytes. `profile_updates` — явные JSON pointers для рассмотрения в review, не разрешение менять trusted semantics.

```bash
smallsort-session prepare --spec /tmp/session.json --out /tmp/session-review
smallsort-session check --bundle /tmp/session-review
smallsort-session closure --worktree /root/verify-rust-std-merge-origin \
  --commit FULL_SHA --recipe research/challenge-8/cloud-build/recipes/merge.json
```

Уточни actual recipe path из своей ветки. Новый output directory должен отсутствовать и находиться вне worktree. Bundle содержит fresh ledger, draft profile, изменённый recipe, mode/blob/SHA256 closure, исходные historical bytes, inventory и registration-plan с найденными функциями/строками client hooks. Старый исходный каталог не изменяется. `check` повторно строит ожидаемые данные по spec и committed source; одного совпадения inventory hashes недостаточно.

**Результат — PREPARED_NOT_REGISTERED.** У нынешних Select/Merge clients phase admission жёстко зарегистрирован в control.py; генератор его не обходит и не принимает произвольный manifest вместо owner authorization. По registration-plan агент делает узкую exact-phase регистрацию и необходимые environment/profile/entry bindings, получает review, проверяет shared static closure и затронутые service tests, публикует exact source. Только после этого используется прежний client request/submit. Готовый draft ledger намеренно не проходит существующие submit gates; перевод в разрешённое состояние — часть reviewed регистрации. Финальные encoded payload/config transport caps проверяет прежний client на committed candidate; один closure inventory их не устанавливает. Новые per-round source-preflight scripts для одинаковых проверок closure создавать не нужно: общий `closure` выполняет эту механическую часть, а особые proof gates остаются в своём клиенте.

## 4. Готовить пакет независимого review

Заполни [review.example.json](examples/review.example.json): exact baseline/candidate commits, defect/applicability, invariants, controls, explicit dependency paths, prior review references и limitations. Нулевые SHA/REPLACE — placeholders, не результат review. В packet входят полный committed diff, inventory всех changed paths, снимки явно выбранных dependencies и короткий reviewer.md. Dirty/untracked файлы не становятся candidate inputs. Зависимости перечисляет автор изменения: автоматический сборщик не доказывает полноту semantic dependencies.

```bash
smallsort-session review create --spec /tmp/review.json --out /tmp/review-packet
smallsort-session review check --bundle /tmp/review-packet \
  --expect-candidate FULL_CANDIDATE_SHA --expect-spec-sha256 SPEC_SHA256
```

Запиши выданные spec/packet digests вместе с exact candidate в задании reviewer; при проверке используй ожидаемые identities. Начинать с reviewer.md и metadata; diff/dependencies открывать по затронутым местам. Пакет не подменяет независимый Luna HIGH review и не выдаёт GO. Reviewer возвращает findings и решение, связанное с exact candidate/diff/dependencies; поправки передавать тому же reviewer как delta, если границы/гарантии не изменились. При смене существенных dependencies/модели расширить review. Прежний GO не распространяется автоматически на новый candidate. Bounded synthetic tests/compile/integrity и formal credit различать.

`review check` повторно строит содержимое по Git и spec. Источник истины для поставленной reviewer задачи — переданные ему ожидаемые candidate/spec identities; самосогласованный переписанный пакет не доказывает, что это прежняя задача. Размеры ограничены, oversized diff/пакет отказывается без усечения. Разделить изменение по содержательным границам, сохраняя необходимые зависимости.

## 5. Сохранить наблюдение Brief один раз

После обычного `smallsort-brief` заполни [observation.example.json](examples/observation.example.json) реальными возвращёнными identities/selector/exact/complete/coverage. Пример synthetic, не real evidence. Неизвестные SHA — null, exact/complete — UNKNOWN; не придумывать значения. Сохраняются короткий факт, stage/target/status/exit если явно сообщены, SOURCE_REPORTED либо отдельно обоснованное INDEPENDENTLY_ESTABLISHED и ссылки. Evidence/receipt references — переданные автором path/SHA, их содержимое инструмент не проверяет; запись не устанавливает независимый proof credit.

```bash
smallsort-session observations record --spec /tmp/observation.json \
  --store research/challenge-8/observations
smallsort-session observations list --store research/challenge-8/observations \
  --build BUILD_UUID --limit 5
smallsort-session observations render --store research/challenge-8/observations \
  --build BUILD_UUID --limit 5
smallsort-session observations check --store research/challenge-8/observations
```

Record — неизменяемый SHA-256-named JSON; повтор той же записи не создаёт копию. Его path и digest подходят для evidence entries CHECKPOINT. `render` — генерируемая view для session/release/coverage, а не ещё одна ручная сводка; существующие receipts/ledgers и historical classifications не переписывать. CHECKPOINT хранит текущую сводку/OPEN/blocker и references на факты; STATUS/task итог по-прежнему строятся из него.

Вывод ограничен 12000байт/20записей. Для продолжения брать только возвращённые `next_offset` и `records_snapshot_sha256`: передать `--offset NEXT_OFFSET --expect-snapshot-sha256 RECORDS_SNAPSHOT_SHA256`; при изменении выбранного набора начать новый просмотр. Фильтр `--index-sha256` отделяет наблюдения выбранного индекса, но не подтверждает его актуальность: latest identity уточняется обычным Brief. Отсутствие записи не NOT_RUN; старый индекс не делает историческое наблюдение ложным. Никакого автоматического скачивания страниц, raw payload, исполнения selector/commands либо прямого GCS.

## 6. Ожидание Build

[Реальный queue experiment](WAIT-EXPERIMENT.md): новая Luna HIGH сессия оставалась idle30с без turns/изменения usage и сама продолжилась после одного `codex queue`; всего2turns. Это подтвердило wakeup на текущем Codex0.163.0, не production admission/deadline/dedup integration. Новый watcher не внедрён; существующие coordinator/status, owner/ledger параметры и интервалы ≤60с сохраняются. Probe явно запускает модель и не должен становиться повторным preflight. Выполнять независимую работу при ожидании; не добавлять пустые объяснения неизменного WORKING.

## Установка и принятие

`/usr/local/bin/smallsort-session` указывает на [smallsort_session.py](smallsort_session.py) этого versioned пакета. У всех worktrees есть доступ к нему; `task install` переносит маленькое CORE/AGENTS только при выдаче новой сессии после closed check. Активные CURRENT/STATUS/recipes/ledgers этим обновлением не переписываются. Политика canonical worktree хранится в Git; полные старые инструкции сохранены в [legacy](legacy/AGENTS-before-v1.md).

## Проверка инструментов

```bash
python3 -B -m unittest discover -s research/challenge-8/agent-workflow -p 'test_*.py'
```

Tests используют маленькие synthetic Git repositories/files. Проверяют active refusal, provenance/paths/symlinks, budget/deadline/status согласованность, refreshed-inventory tampering, сохранение истории и views. Это service tests, не compiler/verifier и не formal credit. Сокращение текста можно измерить по размеру файлов; фактическую экономию токенов оценивать отдельно по данным сессий.

Для сравнения нескольких сессий до/после фиксировать реальные model calls и input/output/cached tokens, отдельно reviewer usage, повторные чтения, долю подготовки и полученный proof-результат. RTK estimates, размер Markdown и число внутренних status queries не подменяют эти измерения. Новые инструменты не заявляют процент экономии без таких данных.
