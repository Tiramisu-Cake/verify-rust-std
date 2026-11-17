# TASK — w13: cell-u34 missing RESULTS, только офлайн-разбор

Это верификация корректности, не security-работа. Отвечай кратко. Свежая Codex-сессия;
модель/effort оставить установленными в pane, без субагентов. Одна компактная диагностическая стадия.
Это отдельное разрешение прочитать завершённую cell-группу сейчас; полный intake/acceptance ещё НЕ выдаются.

Run Tiramisu-Cake/kani `44095954742`, attempt1, trigger21592884db, std99e8456d20, stock tool0aac.
Job **134105615173**, group **cell-u34**, artifact **ch8-s1-05-44095954742-1-cell-u34** (~37KB по координатору).
Runner error: `ValueError: regular stream invalid: missing regular harness RESULTS`.
Координатор сообщает около21min после старта runner против20min в S1-07; heavy ещё выполняются.
Exact full pins/request77ae… — `kani3300/ch8-s1/s1-08-postrun/INPUTS.json`, approved s1-08-r1 package.

1. Получить **только этот compact structured artifact**, проверить repository/run/attempt/job/group/head,
   GitHub digest ZIP до извлечения и SHA/bytes embedded members. Сохранить provenance и необходимые compact
   projections, не raw logs. По request определить exact selected harnesses, по rich/export/receipt/compile/native
   данным — у какого отсутствует RESULTS, у какого он есть; missing/partial/export states сохранить как есть.
   Не восстанавливать невыданный verdict по счётчику, group exit или имени harness.
2. Найти первичную причину, предшествующую decoder completeness error: child/CBMC timeout/exit/signal/RSS/cap,
   compile/export failure, renderer/stream format или ошибку самого parser. Сопоставить receipt execution,
   bounded stdout/stderr previews, original termination, compile marker, partial metadata и measured times.
   Job elapsed, group wall, compile и per-harness verification time различать; недоступное оставить UNKNOWN.
3. Если artifact не даёт причины, разрешён **только bounded grep job134105615173 log**. Не вызывать tool,
   возвращающий полный лог в контекст, не сохранять/download полный лог/ZIP логов на диск. Использовать поток
   API job logs → фильтр, удерживающий только нужные matches/контекст: selected harness headings, RESULTS/SUMMARY,
   CBMC timeout/failure/error/termination, parser error и assertion-message extraction diagnostics. Сначала узкий
   поиск, затем только нужный соседний контекст. Ориентир≤80 строк/8KiB на запрос,≤160 строк/16KiB суммарно;
   если реально недостаточно — запросить конкретный дополнительный фрагмент, а не вычитать весь лог.
   Сохранить line/timestamp coordinates, selector/filter и короткие excerpts; чтение лога не заменяет original exit.
4. Проверить гипотезу о kani::assert labels по найденным данным и pinned source/producer/runner/renderer:
   реальная message extraction/format проблема либо более долгий solver/другая причина. Одно совпадение
   по времени и изменение числа properties не доказывают причинность labels. Разделить CONFIRMED/INFERRED/UNKNOWN.
   Новых прогонов, compiler/verifier commands, воспроизведения solver или чтения других групп не делать.

Write scope g0 только `kani3300/ch8-s1/s1-08/run-44095954742/cell-diagnostic/`:
RESULT.md (краткий ответ: exact harness, причина/остаток UNKNOWN, связь labels, следующий адресный шаг),
DIAGNOSTIC.json, PROVENANCE/INPUTS/необходимые компактные projections, HANDOFF.md. ZIP только временный transport.
Не создавать общий collected/ACCEPT, не объявлять группу qualified и не менять source/control/parser/oracles.
Минимальный prospective fix/retry вариант можно описать, **решение о повторе только через координатора**.

Никаких cancel/rerun/CI/push/публикаций/ledger; локальных cargo/rustc/Kani/CBMC/rustfmt; полных raw logs/archives.
Времени/объёма достаточно: не STOP по объёму/контексту/«не успеваю»; UNKNOWN оформить точно при отсутствии
данных, реальный access/scope blocker — с причиной. Старые receipts/task INPUTS не менять, только свои paths.
Коммит `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` либо реальный STOP.
