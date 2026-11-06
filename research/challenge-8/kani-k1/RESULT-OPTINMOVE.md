# OPTINMOVE — PASS
Library `461dac0c43902c7a929e7164492ad4a5f84a4a3b`, tree `f1d36898b962cb654e66f8b05c9fde7ef512a560`.
G1 `242b83e1-d9bc-46d9-a504-1cd3e929fcf0`, source `3b12f9cc0d2a11ab0a1a7df00e5aa93624c212cf` (exact-packet GO).
Request `optinmove-g1-20261106-01`, SHA256 `d283842f2e85c4a1910f63039f8b98af675e0bda182046cf1d849dfb5cdd88be`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Cloud SUCCESS, COMPLETE, gate=true, Kani exit0; inventory, controls=false, standard4. Source/request/Kani/pool/check-tooling PASS против `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Статика PASS против TIDYDOCS `6443b4d99d`: ordinary233, controls13, cfg-on246; удалены ровно22 (realcontracts8/permtags10/scratchgeom4).
Все246 раскрытых items и транзитивные closure/covers токен-идентичны; smallsort.rs побайтно неизменён, tooling заморожен.
Уточнение resolver: удалено ложное межмодульное ребро к private permtags::arbitrary_u64_order; локальная недостижимость/отсутствие внешних путей проверены отдельно.
Cfg-off compiler inventory **233**, точный ожидаемый набор, дубликатов нет; все три bounded-страницы и их identities/hashes сверены.
Compiler native names SHA256 `7b466e9686cdf5f56c3a8359464399b13652f6ced336b479eb01cdb1e048c738`; artifact `21e1203a1d34be93715bf25d26caa8ddaae2ffa78cc2662ef479d13b585b5646`.
Sorted compiler names SHA256 `a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374` совпал с ordinary-expected; native порядок standard/contract отличается от sorted.
Cfg-on compiler inventory/компиляция и runtime всех13 контролей: **DEFERRED_TO_INTEGRATION_AFTER_STAGE_3** по решению координатора; G2 не запускался.
Cfg-on ожидается246, source sorted SHA256 `bdc2ed2e82937fa6a0ce575e8d23025d1655e3e60a8af7f406325507ef4a08e0`; compiler совпадение/hash не установлены.
В verify нет строк>100 и запрещённой лексики. Целевой cfg-off verify/unused warning scan: no match; cfg-on warnings отложены. Общая warning-выборка ограничена200 и насыщена.

| Файл от smallsort/ | Удалено | Добавлено |
| --- | ---: | ---: |
| verify.rs | 4 | 3 |
| verify/merge.rs | 51 | 26 |
| verify/network.rs | 28 | 9 |
| verify/permtags.rs | 82 | 0 |
| verify/realcontracts.rs | 112 | 2 |
| verify/scratchgeom.rs | 30 | 0 |
| Итого verify* | 307 | 40 |

Убраны все5 кандидатов: duplicate general macro; u64 n2..5 и swap indices n17 через существующие макросы; явные dispatch_safety_stable_bytes16_n32 и merge_scratch48_contract_u8_n9.
Отказанных кандидатов нет: каждый item совпал токен-в-токен. Exclusively-used helpers6/импорты3/permutation_case удалены; panic-cutoff контроля permtags сохранён.
scratchgeom содержит один proof и нужные helpers/макрос; файлов с1–2 элементами не осталось, переездов нет.
22 исходника/статуса/воспроизведение: [MOVED-OPTIN.md](optinmove/MOVED-OPTIN.md); сохранённые статусы source-reported, нового proof credit нет.
Расход **$0.5805/$2**, reserve0; builds1, retries0, repairs0. Cloud elapsed42мин25.519с; proof rows/RSS/covers заново не измерялись.
PASS этапа по решению координатора: успешный G1 + принятая статика246; cfg-on проверки остаются в интеграционном пакете после этапа3. Новых dispatch нет.
Evidence: [summary](optinmove/evidence/summary.md), [отчёт](optinmove/evidence/verification-report.json), [статика](optinmove/check-report.json), [ledger](optinmove/RUN-LEDGER.json).
