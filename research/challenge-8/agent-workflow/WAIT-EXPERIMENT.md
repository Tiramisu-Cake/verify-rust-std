# Ожидание Build: результат проверки протокола

2026-10-21. Только локальный synthetic experiment, без Cloud calls, Builds, чтения evidence или изменения active accounts. Полезность отдельного wait helper для сокращения **обращений к модели** пока не установлена; новый runtime watcher не установлен.

## Что проверено

Существующие Select/Merge `research/challenge-8/cloud-build/control.py` принимают `status BUILD_UUID`. По исходникам `main` этот путь проходит shared coordination lock, reconciliation и учёт выбранного ledger. Это не произвольный read-only HTTP poller. Использовать его следует с прежними owner/phase/ledger/state параметрами; текущие clients и ledgers не изменялись.

Локальный процесс с тремя synthetic состояниями WORKING → WORKING → SUCCESS и интервалом 1с печатал только один terminal JSON. `exec_command` с `yield_time_ms=1000` вернул session ID без вывода; результат был получен отдельным `write_stdin`. Фильтрация промежуточных состояний работает, но сама по себе не устраняет возврат управления модели.

При ограничении блокирующих шагов ≤60с сценарий на 600с требует не менее десяти последовательных интервалов ожидания. Это модель протокола, **не измерение токенов или фактических GCP времён**:

| Synthetic duration | Status interval | Queries, включая t=0 и terminal | Terminal output | Интервалы ≤60с |
|---|---|---|---|---|
|600с|60с|11|1|≥10|
|600с|15с|41|1|≥10|
|25с|5с|6|1|≥1|

Более частый внутренний polling здесь увеличивает число status requests; сокращение model resumptions из него не следует. Состояние SUCCESS — synthetic Build status, не принятие доказательства.

## Решение

Сохраняем существующий coordinator и прерываемые интервалы ≤60с. При наличии независимой работы агент выполняет её вместо пустых рассуждений о WORKING. Не добавляем ещё один wrapper с теми же пробуждениями и не удлиняем непрерываемые waits.

Для дальнейшей реализации нужен проверенный механизм уведомления о terminal/error/deadline, который возвращает управление агенту без обязательного участия модели в каждом промежуточном опросе. До его проверки экономию model calls и токенов не заявлять. При будущей интеграции сохранить owner/phase/slots/budget/deadlines, unknown-submit handling, accounting и Evidence Brief после terminal; metadata status не заменяет verification evidence.

Сокращение стартового контекста, пакеты review и индекс Brief внедряются независимо от этого результата.
