# OPTINMOVE — PRE-BUILD, compiler evidence PENDING
Library `461dac0c43902c7a929e7164492ad4a5f84a4a3b`, tree `f1d36898b962cb654e66f8b05c9fde7ef512a560`.
Статика PASS против TIDYDOCS `6443b4d99d`: ordinary233, controls13, cfg-on246; удалены ровно22 (realcontracts8/permtags10/scratchgeom4).
Все246 раскрытых items и транзитивные closure/covers токен-идентичны; smallsort.rs побайтно неизменён, tooling заморожен.
Уточнение resolver: удалено ложное межмодульное ребро к private permtags::arbitrary_u64_order; локальная недостижимость/отсутствие внешних путей проверены отдельно.
В verify нет строк>100 и запрещённой лексики. Compiler inventory и новые unused warnings: NOT_RUN, ожидают GO и G1/G2.
Cfg-off ожидается233, sorted SHA256 `a73e3c308728c7e7e560665547f79775ddffef2676d4ddee1cecd1b572bdd374`; compiler совпадение/hash NOT_RUN.
Cfg-on ожидается246, sorted SHA256 `bdc2ed2e82937fa6a0ce575e8d23025d1655e3e60a8af7f406325507ef4a08e0`; compiler совпадение/hash NOT_RUN.

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
План: G1/G2 kind inventory controls=false/true, timeout74мин каждый, max reserve $0.999+$0.999=$1.998≤$2; отдельный GO для каждой стадии.
Расход $0, reserve0, builds0/2, retries0, repairs0. Dispatch не выполнялся; PRE-BUILD review pending.
[Статика](optinmove/check-report.json), [пакет](optinmove/PREBUILD-OPTINMOVE.md), [ledger](optinmove/RUN-LEDGER.json).
