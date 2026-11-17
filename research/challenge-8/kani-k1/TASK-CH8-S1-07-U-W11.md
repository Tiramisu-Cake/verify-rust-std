# TASK — w11-A: только 187 U records и mutation checks

Это верификация корректности, не security-работа. Отвечай кратко. Runtime: Codex.
Свежая сессия, модель/effort оставить установленными в pane; без вложенной делегации.
Эта выдача заменяет для w11 незавершённое объединённое задание ACCEPT-V2. Не выполнять PFC или source labels.
Вход g0 `118fd0774a5a7379ca12555daafb3b677e074813`; repo `/root/verify-rust-std-kani3300-g0`.

## Объём и результат

Только postprocessing уже имеющихся 187 unresolved status=UNREACHABLE check records S1-07 run `43923266772`.
Вход: `kani3300/ch8-s1/s1-07/run-43923266772/accept/{ACCEPT.json,INPUTS.json}`,
`kani3300/ch8-s1/COORDINATOR-REVIEW-AFTER-S1-07.md`, pinned std `5be85699b8`, tool `0aac16ef62`.
Незавершённый `accept-v2/` — stop-marker, не receipt; сохранить его неизменным и не брать из него admission.

Write scope: только новый `kani3300/ch8-s1/s1-07/run-43923266772/accept-u/`.
Сделать replayable `U.json` с exact group/row/harness/property ID/class/description/status/site, evidence hash,
source SHA/context, rule и проверенными premises для каждого из 187 records; `U.md`, replay.py,
meaningful mutation tests, VALIDATION.json, HANDOFF.md. Общий ACCEPT.json/число qualified не пересчитывать:
интеграция с PFC и success bindings — координатор отдельно. Не дублировать artifacts.

## Правила

- Проверить source-local аргументы, а не принять количество записей как доказательство: abs_diff 50
  (ветка larger-minus-smaller), is_aligned_to 25 (align>=1 после guard), is_multiple_of 12 (rhs!=0),
  is_valid_allocation_size 18 (size!=0), fmt shift 28 (literal RHS=1 < word bits), active_post 54
  (CAP=32, length guards, loops/index/counters). Точные sites и pinned producer — в coordinator review.
- Для fmt достаточно семантики shift count: pinned Kani codegen/rvalue.rs:328–338; не вводить новую предпосылку
  о длине строки. Для active_post аргумент должен работать независимо от ensures/caller/canary origin.
- Сверять exact source SHA/context/function/site/class/description/status и original input namespace.
  Нет blanket exemption по файлу/helper имени, назначения роли по ordinal или подмены UNREACHABLE на SUCCESS.
  Закрываем только generated safety check applicability, не объявляем саму sorting relation достигнутой/доказанной.
  Необоснованную/неизвестную запись оставить UNKNOWN с причиной; полнота обработки 187 обязательна.
- Сохранить существующие 226 allowed records и 2 negative-return covers read-only; если найдена ошибка в них,
  сообщить отдельно, не расширять эту стадию в общий аудит. Не менять policy, historical receipts или исходники std.
- Проверки: повторный replay воспроизводит U.json; mutation SHA/site/function/operation/description/status,
  missing/duplicate/foreign row/harness/request/property и нарушенных rule premises дают UNKNOWN/error, не PASS.
  Указанные source-local premises должны проверяться кодом/точными pinned source anchors, не просто текстом
  объяснения и не словарём заранее проставленных PASS по ID. Покрыть все шесть rule families.

## Продолжение и ограничения

Времени и объёма достаточно для этой ограниченной стадии. Старое окно и 15 часов простоя сюда не переносятся.
Начать новое обычное рабочее окно по CORE с фактического старта. Выполнить реализацию и проверки до результата.
Объём работы, оценка «этот запуск не успевает», накопление контекста, исправимый KeyError/parse error — не blocker
и не основание STOP. После compaction продолжать. STOP только при реальном доказанном внешнем/scope blocker
или фактически достигнутом установленном лимите; указать факт, затраченное время, попытки и точный остаток.
Не создавать ещё один stop-marker вместо доступной реализации.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC и чтения полных raw logs/archives.
Shared g0: w15 пишет только accept-pfc, w13 только s1-08 и isolated source/control. Не трогать их файлы/index;
stage/commit только свои пути, без reset/rebase чужих коммитов и git add -A.
Коммит `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал: `READY <g0>` с числом обработанных/обоснованных/UNKNOWN и тестами либо `STOP <реальный blocker>`.
