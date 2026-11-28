# REV2 Wide N12 / N16 witness · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-28. **GO_WITH_NITS**, блокеров нет. Пины: Std `b465318cc95001c651011c2e5579bba12669b467` / tree `9d4c78baf7`, parent `bec3b6ee80`; Control `507a01258faac8d748dbdcbea9aa82a16f4467fc` / tree `a128c58ffe`, parent `e54fde9f4c`; review-trigger `f7db388ba89a0b8a22529ceb30ee96e5b8779fa5` / тот же tree, sole parent `467af9cb8d`. Задание g0 `44538d9436`, handoff `8f73d34608`. SHA-256 пересчитаны: CI-REQUEST `a5a5d1c1…`, roster `7f4ae44e…`, bindings `8df3d8ed…`, bundle `45dfe97f…` (92 368 байт), relay `5c9fed47…`.

1. Should-fix (до dispatch). `ch8-cal1/run.py:704,726,734,741`, `ch8-cal1/stdout_relay.py:18,169-188`. `stdout_relay.collect` выполняется внутри окна проекции (`receipt_seconds=5` минус 1 с, SIGALRM), в том же окне, что `slot_projection`, а `memory_telemetry`/`group_census` прикрепляется только там (`run.py:590-601`). При остановке до replay `spill_prefix_markers` разбирает до 16 MiB: локально 5,6–7,1 с. Сценарий: N16 снова RSS_LIMIT → SIGALRM внутри `collect` → DEADLINE, в receipt нет CNF префикса и census, ради которых слот и запускается. Fail-closed (ложного MATCHED нет), но диагностика теряется. Тест `test_relay.py:363` (200 сообщений, вне окна) этого не ловит.
2. Nit. Handoff §5 (строка 78) утверждает, что при любом сбое байты не передаются; при `REPLAY_INCOMPLETE` (`cbmc_relay.py:224-247`) часть байтов уходит (проба: 131072 из 300000, exit 125, spill остался). Безопасно: Kani 9834c96ce9 трактует 125 как неполные результаты, `report.py:167` требует delivery `COMPLETE`. Исправить текст, добавить тест EPIPE в середине replay.
3. Nit. `cbmc_relay.py:147-161,208-213,290-301`: после `RelayFailure` обработчики SIGTERM/SIGINT/SIGHUP остаются взведены; групповой сигнал во время `stop_child` прерывает собственный reap relay. Pgid-reap супервизора всё равно собирает CBMC.
4. Nit. `report.py:233`: в receipt/SUMMARY `expected_result.status` может быть `MATCHED` при слоте `OPEN` из-за доставки; показывать `stdout_delivery` рядом.
5. Nit. Размещение spill проверяется только `statvfs`, tmpfs не отвергается (на GH `RUNNER_TEMP` на корневом диске, риск низкий).
6. Nit. Self-test в шаге `pins`: 4 прогона по 90 с, локально 59–67 с; запас ~25%, при таймауте отказ дешёвый, до измерений.

Проверено и в порядке: идентичности и гигиена коммитов; N10 и FIX2 — побайтные префиксы нового файла, `smallsort.rs` без изменений; ручная трасса маршрута len 12 (Freeze+Copy → general scratch48 → два `sort4_stable` → fill → merge) даёт `[1,3,4,5,7,9,10,11,0,2,6,8]` и после обмена `[1,3,4,7,5,…]`; границы (V14 max 13, массивы 12 max 11); после обмена падает только `STABLE_EQUAL_KEYS` `:1493:9`. Relay: argv/cwd/stdin/stderr/env без изменений, ни одной записи stdout до `wait`, упорядоченный replay с дозаписью, проброс сигнала, пин реального CBMC (path/SHA-256/size/version, dev/ino/mtime на каждом вызове), PATH только у N16, census не считает relay за CBMC, ожидаемый argv совпадает с `cbmc_flags` Kani 9834c96ce9; доставка может только не допустить совпадение. N16 roster побайтно равен FIX2 (digest `9241da11…`, 30 cfg), лимиты без изменений, нет `--harness-timeout`. Guards trigger на месте. `test_relay` 18/18.

NOT_RUN: rustfmt, source gate, discovery против реальных rustc/Kani, GH Actions, receipt FIX2 (равенство argv опирается на fixture).

Решение координатора: GO откладывается до исправления п. 1 (дешёвое исправление против дорогого прогона, диагностика — цель слота). П. 2–4 исправить в том же раунде, п. 5–6 — по усмотрению исполнителя.

## R2 · delta FIX1

Delta-ревью (тот же `smallsort-reviewer`) 2026-11-28. **GO_WITH_NITS**, все находки R1 исправлены. Пины: Control `b5e6c89c0e06cc55e264c4d297086e3ae629300a` / tree `4d4e7f5b3b4ccb6fc112eb5b93645d8052c801e0`, parent `507a01258f` (fast-forward); review-trigger `60650bf250f7021623eac6e54993f66e98b05608`, тот же tree, sole parent `467af9cb8d`. CI-REQUEST `1247e9e65a6be3fe41862b3559f6996284024d1d3ee3e03bbaf9546ecd4ba3f9` (дельта — одна строка, SHA relay), relay `c8b4c070dbd12a8acafa4b23df0b74833b600333f539b66fc9d27eccee3613b7`; Std/roster/bindings/bundle без изменений. Лимиты: 120 с VT, 4 GiB, 180 с cold, `receipt_seconds` 5 — без изменений.

Проверено: census прикрепляется сразу после reap (`run.py:729-734`), разбор spill после проекции в пределах прежнего окна (`run.py:771-783`), удаление spill после receipt (`run.py:797-802`); данные префикса не влияют на вердикт; текст REPLAY_INCOMPLETE и тест EPIPE; `ignore_termination()` перед `stop_child`, relay не делает exec после SIG_IGN, восстановление обработчиков только в fixture; `stdout_delivery` в receipt/`expected_result`/SUMMARY; отказ tmpfs/ramfs не задевает ext4/xfs. `test_relay` 23/23, suite 169 за 62 с.

Nits:
- (a) `stdout_relay.py:195-217`: лимит текста 1 MiB обычно срабатывает раньше лимита 16 384 сообщений (реалистичные `Unwinding loop …` — 7 768 сообщений), CNF после них не находится, причина пишется как `NO_RECOGNIZED_NATIVE_MARKER_IN_PREFIX`. Предложено: отдельная причина или дешёвый `re.search` CNF по всем 16 MiB.
- (b) Таймаут self-test в `.github/workflows/ch8-q-pilot.yml:51-55` 90 с → ~150 с; шаг 8 мин помещается, proof-лимиты не меняются.
- (c) Косметика: `stdout_delivery=INSTALLED`, если `collect` не выполнялся; не `COMPLETE`, вердикт не затронут.

Решение координатора: (a) и (b) исправить раундом FIX2 до dispatch. CNF на N16 теперь доступен только через spill (вывод CBMC больше не идёт в Kani вживую), и это главная диагностика при RSS_LIMIT. (b) дешевле, чем новый trigger после таймаута. (c) по усмотрению.
