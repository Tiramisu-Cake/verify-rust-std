# Короткие задания, checkpoint и подготовка сессии

Обязательное чтение — [CORE](CORE.md), CURRENT-TASK и CHECKPOINT/STATUS своей ветки. Здесь справка по конкретным действиям. Редакция v1 применяется к **следующим** сессиям; текущие T0/inputs/ledgers/client gates неизменны. Три инструмента используют Python standard library и локальный Git; actual proof/toolchain и Cloud вызовов нет.

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

## Установка и принятие

`/usr/local/bin/smallsort-session` указывает на [smallsort_session.py](smallsort_session.py) этого versioned пакета. У всех worktrees есть доступ к нему; `task install` переносит маленькое CORE/AGENTS только при выдаче новой сессии после closed check. Активные CURRENT/STATUS/recipes/ledgers этим обновлением не переписываются. Политика canonical worktree хранится в Git; полные старые инструкции сохранены в [legacy](legacy/AGENTS-before-v1.md).

## Проверка инструментов

```bash
python3 -B -m unittest discover -s research/challenge-8/agent-workflow -p 'test_*.py'
```

Tests используют маленькие synthetic Git repositories/files. Проверяют active refusal, provenance/paths/symlinks, budget/deadline/status согласованность, refreshed-inventory tampering, сохранение истории и views. Это service tests, не compiler/verifier и не formal credit. Сокращение текста можно измерить по размеру файлов; фактическую экономию токенов оценивать отдельно по данным сессий.
