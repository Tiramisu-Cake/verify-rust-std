# OPTINMOVE — G1 authorized, compiler evidence PENDING
Library `461dac0c43902c7a929e7164492ad4a5f84a4a3b`, tree `f1d36898b962cb654e66f8b05c9fde7ef512a560`.
Статика PASS против TIDYDOCS `6443b4d99d`: ordinary233, controls13, cfg-on246; удалены ровно22 (realcontracts8/permtags10/scratchgeom4).
Все246 раскрытых items и транзитивные closure/covers токен-идентичны; smallsort.rs побайтно неизменён, tooling заморожен.
Уточнение resolver: удалено ложное межмодульное ребро к private permtags::arbitrary_u64_order; локальная недостижимость/отсутствие внешних путей проверены отдельно.
В verify нет строк>100 и запрещённой лексики. Cfg-off compiler inventory/unused warnings: ожидают G1; cfg-on проверка отложена координатором в интеграционный пакет после этапа3.
Cfg-off ожидается233, sorted SHA256 `a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374`; compiler совпадение/hash NOT_RUN.
Cfg-on ожидается246, sorted SHA256 `bdc2ed2e82937fa6a0ce575e8d23025d1655e3e60a8af7f406325507ef4a08e0`; compiler совпадение/hash DEFERRED_TO_INTEGRATION_AFTER_STAGE_3.

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
22 исходника/статуса/воспроизведение: [MOVED-OPTIN.md](optinmove/MOVED-OPTIN.md); это source-reported evidence, нового proof credit нет.
GO только G1 на `3b12f9cc0d2a11ab0a1a7df00e5aa93624c212cf`: inventory controls=false, timeout74мин, max reserve $0.999≤$2; G2 не запускать. PASS этапа при успешном G1; cfg-on и13 контролей — интеграционный пакет после этапа3.
G1 `242b83e1-d9bc-46d9-a504-1cd3e929fcf0` отправлен с принятого SHA; результат ожидается. Расход $0, reserve $0.999, builds1, retries0, repairs0; G2 запрещён в этом этапе.
[Статика](optinmove/check-report.json), [пакет](optinmove/PREBUILD-OPTINMOVE.md), [ledger](optinmove/RUN-LEDGER.json).
