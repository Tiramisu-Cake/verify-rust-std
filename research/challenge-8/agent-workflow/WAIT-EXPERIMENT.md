# Ожидание Build: результат проверки протокола

2026-10-21. **Текущее состояние: пробуждение через `codex queue` подтверждено на реальной изолированной Codex-сессии.** Production watcher ещё не установлен; работающие Select/Merge, Builds, accounts и deadlines не менялись. Исходный опыт с shell-loop ниже остаётся верным для обычного tool polling.

## Реальный тест queue — PASS

CLI и работающий app-server **0.163.0**, модель строго **gpt-6-luna / HIGH**, новая сессия без наследования чужой истории. [Неизменённый результат с метаданными](experiments/queue-wakeup-20261021.json), [воспроизводимый opt-in probe](experiments/queue_wakeup_probe.py). Общий daemon не запускался и не перезапускался; использован штатный WebSocket через его private Unix socket. Managed socket легитимно опубликован symlink; probe разрешает его до owned private endpoint.

1. Новая test-сессия ответила `ARMED_FOR_SYNTHETIC_EVENT` и завершила первый turn.
2. В течение **30.008с** status оставался idle: **0 новых turns, token usage не изменился**.
3. Один `codex queue --thread EXACT_TEST_UUID --message SYNTHETIC_EVENT…` вернул exit0 и автоматически начал второй turn. Отдельный `thread/queue/start` не потребовался.
4. Получен `SYNTHETIC_EVENT_RECEIVED`. Всего **2 completed turns**. Проверка собственных items дала только userMessage/reasoning/agentMessage, без tools. Архивирована только созданная test-сессия.

Источник сообщает usage **33394 total /33315 input /23040 cached input /79 output tokens** для обоих test-turns. Это расход **всей тестовой сессии**, не расход ожидания и не оценка тарифа/общей экономии; main coordinator research/review в него не входит. Поле `cloud_calls=0` в JSON относится к GCP/Cloud Build: OpenAI inference в двух test-turns реально выполнялся. Real Builds/GCP calls=0, proof credit=0.

Шесть synthetic routing cases вернули DUPLICATE, STALE_IDENTITY (thread/phase/build), CLOSEOUT_ONLY при main и EXPIRED при absolute. Это проверки чистой функции маршрутизации; **не end-to-end проверка persistent dedup, restart, cancellation или CI authorization**. Эти события повторно в модель не отправлялись. Семь isolated service tests проверяют routing, запрет overwrite/symlink destination, сохранение startup failure и обязательный opt-in; они не запускают Codex/model/GCP.

Запуск probe **создаёт новую сессию и выполняет два коротких Luna HIGH turns**, поэтому только по явному поручению на тест, не как preflight каждого Build:

```bash
python3 -B research/challenge-8/agent-workflow/experiments/queue_wakeup_probe.py \
  --run-real-probe --out /tmp/NEW-QUEUE-PROBE-DIRECTORY --idle-seconds 30
```

## Что остаётся для production

Технический wakeup подтверждён. Следующий небольшой компонент — процесс мониторинга **зарегистрированного собственного** Build через существующий coordinator/status плюс bounded event delivery в exact thread. Нужны persisted handoff/event identity и защита от duplicate/unknown delivery/restart, проверка owner/phase/ledger/dispatch/Build/thread, user-stop/main/absolute и запрет нового окна/бюджета/submit из уведомления. Само сообщение — технические данные; SUCCESS metadata не proof acceptance. После terminal агент использует Brief.

Агент должен завершать turn с незавершённым HANDOFF/active Build, не закрывая счёт, и продолжать тот же task/T0 после события. Сначала проверить это вместе с существующим admission/accounting и deadline handling; текущий тест не даёт права внедрять watcher в активные сессии. Новые сервисы GCP, IAM, hooks или polling-агент с отдельной моделью для этого опыта не нужны.

Официальные интерфейсы: [CLI queue](https://learn.chatgpt.com/docs/cli/reference#codex-queue), [app-server](https://learn.chatgpt.com/docs/app-server). Background hooks сами не начинают новый idle turn: [hooks](https://learn.chatgpt.com/docs/hooks#how-background-hooks-run).

## Предыдущий опыт: shell-loop

Существующие Select/Merge `research/challenge-8/cloud-build/control.py` принимают `status BUILD_UUID`. По исходникам `main` этот путь проходит shared coordination lock, reconciliation и учёт выбранного ledger. Это не произвольный read-only HTTP poller. Использовать его следует с прежними owner/phase/ledger/state параметрами; текущие clients и ledgers не изменялись.

Локальный процесс с тремя synthetic состояниями WORKING → WORKING → SUCCESS и интервалом 1с печатал только один terminal JSON. `exec_command` с `yield_time_ms=1000` вернул session ID без вывода; результат был получен отдельным `write_stdin`. Фильтрация промежуточных состояний работает, но сама по себе не устраняет возврат управления модели.

При ограничении блокирующих шагов ≤60с сценарий на 600с требует не менее десяти последовательных интервалов ожидания. Это модель протокола, **не измерение токенов или фактических GCP времён**:

| Synthetic duration | Status interval | Queries, включая t=0 и terminal | Terminal output | Интервалы ≤60с |
|---|---|---|---|---|
|600с|60с|11|1|≥10|
|600с|15с|41|1|≥10|
|25с|5с|6|1|≥1|

Более частый внутренний polling здесь увеличивает число status requests; сокращение model resumptions из него не следует. Состояние SUCCESS — synthetic Build status, не принятие доказательства.

## Решение после shell-loop, до queue-пробы

Сохраняем существующий coordinator и прерываемые интервалы ≤60с. При наличии независимой работы агент выполняет её вместо пустых рассуждений о WORKING. Не добавляем ещё один wrapper с теми же пробуждениями и не удлиняем непрерываемые waits.

На этом этапе требовался проверенный механизм уведомления о terminal/error/deadline, возвращающий управление агенту без участия модели в промежуточных опросах. Последующая queue-проба выше подтвердила wakeup, но не завершила production integration. Сохраняются owner/phase/slots/budget/deadlines, unknown-submit handling, accounting и Evidence Brief после terminal; metadata status не заменяет verification evidence.

Сокращение стартового контекста, пакеты review и индекс Brief внедряются независимо от этого результата.
