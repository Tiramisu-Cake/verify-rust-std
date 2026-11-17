# TASK — w13: intake S1-08 run44095954742 (одна компактная стадия)

**PREPARED_NOT_ISSUED. Выдать только после terminal run44095954742 attempt1.**
Это верификация корректности, не security-работа. Отвечай кратко. Runtime Codex;
свежая сессия, текущая pane-модель/effort, без субагентов. Времени/объёма достаточно;
не STOP из-за размера задачи/контекста/«не успеваю», только реальный blocker/достигнутый лимит.

Pins/пути — `kani3300/ch8-s1/s1-08-postrun/INPUTS.json` (task preparation g0 от1937a7dd22).
Tiramisu-Cake/kani run44095954742/attempt1/head21592884db, tree как reviewed7c41333f9b;
std99e8456d20, stock tool0aac, embedded request77ae1113…1431c7e. Длинные SHA брать из INPUTS.
Открывать только относящиеся входы: s1-08-r1 identities/request/ROLE-MAP/review и прошлый S1-07 intake
как шаблон. Большую историю/планы и полный audit не перечитывать.

1. Перед чтением artifacts подтвердить terminal status, exact run/head/attempt/request/source/tool identities.
   Получить bounded structured artifacts ожидаемых14 групп. Проверить GitHub digest до извлечения ZIP,
   embedded SHA/bytes, caps/namespace и полноту. Полные stdout/stderr/raw evidence не читать и не сохранять.
   При missing/cancelled/failed/partial group сохранить наблюдаемое и UNKNOWN/NOT_RUN, не подделывать полноту;
   terminal failure не запрещает intake доступных данных. Job success не равен proof acceptance.
2. Для35 rows собрать source verdict, полный stock/rich property inventory и ID/status partitions,
   required binary before/after snapshots, source/variant hashes, native metadata refs/manifest,
   exception tuples, group exits/elapsed/RSS/termination. Per-root process metrics оставить UNKNOWN,
   если они не измерены. Использовать collect.py executed trigger21592884db, без full runner/build.
3. Подготовить вход w11: exact evidence projections + native metadata, request/ROLE-MAP, provenance и hashes.
   Для111 новых labels дать **диагностический** coverage список найденных/missing/duplicate/status по root/role,
   не admission.16 старых semantic bindings/sets требуют свежей проверки, не переносить historical IDs.
   Сравнить с S1-07 verdicts/groups и объяснить deltas; **9986 properties,187 U и18 location occurrences
   не являются обязательными числами нового run**. Exception — только approved exact tuple policy.
4. Добавить **TIMING-COMPARISON.json/md** по всем общим harness S1-07/run43923266772 и S1-08/run44095954742:
   точный row/selector+variant/mode/type/N/unwind/flags/domain key, оба source outcomes, raw `resources.verification_time_s`,
   limits, delta и отношение S108/S107 при сопоставимости. Проверять request/config, не сводить одноимённые production
   и mutant roots. Missing/null/NOT_RUN не превращать в0; несовместимые/непарные rows явно перечислить.
   TIMEOUT — цензурированное наблюдение: показать observed elapsed/limit и нижнюю границу отдельно, не точный slowdown
   завершённой верификации; ratio completed→completed отделить от TIMEOUT/FAILURE. Не использовать job/group/compile
   wall вместо per-harness field и не объявлять это чистым solver time. Контекст runner/config и source label delta
   раскрыть; корреляция около1.6x не доказывает причинность kani::assert. Писать сравнение прямо в существующий intake,
   не отдельную новую кампанию или broad audit. Не ждать и не подмешивать будущий targeted retry1200s.

Write scope g0: только `kani3300/ch8-s1/s1-08/run-44095954742/`, без вложенного `accept/`.
Выход: RESULT.md, collected.json, TIMING-COMPARISON.json/md, HANDOFF.md, INPUTS/manifest + replay/validation и компактные projections
по примеру S1-07. Не дублировать native/artifacts вне необходимого intake; ZIP — временный transport,
в g0 только structured payload/provenance как в S1-07. Replay/identity/hash/inventory checks один раз;
новые tests лишь для реально изменённого intake adapter. Не запускать заново старые broad suites.
Admission оставить PENDING_OFFLINE; сообщить все потери/неэкспортируемые поля без новых provenance gates.

Одна стадия, без source/control/compiler fixes и policy changes. При дефекте — точный handoff, не CI retry.
Без push/CI/публикаций/ledger/cargo/rustc/Kani/CBMC/rustfmt; не менять historical receipts и task INPUTS.
Commit только своих путей, без git add -A/reset/rebase чужих изменений; `[skip ci]`,
author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` с completeness либо реальный STOP.
