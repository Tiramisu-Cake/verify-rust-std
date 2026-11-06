# RENAMEMODS — PASS
Library `85ced7f8a8bcdf6b4ffe2e29a65d1d940ff10737`, tree `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`.
G1 `942bc6d1-191d-4777-acc5-d0d724564fde`, source `0504202814f16c4a962687c6933a4e43b171d45b` (exact-packet GO).
Request `renamemods-g1-20261106-01`, SHA256 `4f73c163c10ec2e1f5e7737d231ba9359efb919badc9c4c0232fb4edb5eb27b5`; Kani `cd355b0bccd32300713bc2ce4f765dafa1510607`.
Cloud SUCCESS, COMPLETE, gate=true, Kani exit0; inventory, controls=false, standard4; proof rows0.
Привязки source/request/build/Kani/pool/tooling PASS; tooling base `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Восемь файлов перенесены через git mv один к одному; все mod/use/пути атрибутов и карта verify.rs обновлены.
Статика PASS против LEANHELPERS `5c929ba094`: 233 ordinary + 13 контролей = 246, биекция без потерь/дубликатов.
Все раскрытые items, 246 корней и замыкания токен-идентичны после разрешённой обратной подстановки.
Число, позиции и аргументы covers сохранены; ранее разные сообщения в каждом замыкании остаются разными.
Изменены 64 места сообщений (59 литералов); canonical comparator и пять контролей specfix_* → profile_*.
Таблицы: [полные имена](renamemods/name-map.tsv), [сообщения](renamemods/message-map.json), [модули/файлы](renamemods/rename-map.json).
Compiler ordinary inventory: ровно **233** ожидаемых имени, дубликатов нет; все три bounded-страницы/identities/hashes сверены.
Sorted compiler SHA256 `bd539369aead46f534868511eecef993b086cacd11e08b0b15f022103482a93b` совпал с ordinary-expected.
Native compiler names SHA256 `9d3dbe8fd4f352c81dfdab68ebbdd89c06e93d8968fdf37fd460f2088ac8b0e0`; порядок standard/contract отличается от sorted.
Inventory artifact SHA256 `a4ef473682e40906076159123344c3166590a2151a10227f53f439dbddae8c83`.
Cfg-on compiler inventory/компиляция и runtime всех13 контролей: **DEFERRED_TO_INTEGRATION**, не выполнялись.
Cfg-on source expected246, sorted SHA256 `3e03f6051cb8d0ab71d1a40f73c58234acbc7964315529ac9c603c49f9d222eb`; compiler совпадение не установлено.
rustfmt --check PASS; строк>100 и запрещённой лексики TIDYDOCS в verify нет; smallsort.rs побайтно неизменён.
Целевой cfg-off smallsort/verify/unused warning scan: **no match**; cfg-on warnings отложены.
Старых имён модулей/specfix_* по границам идентификаторов нет. Substring wrap остаётся в17 строках: wrapping API, arbitrary_wrapped_u64_order и описательные wrapper(s).
Это не кодовые имена модулей; все места и причины: [remaining-name-mentions.json](renamemods/remaining-name-mentions.json).
Расход **$0.6075/$1.20**, reserve0, builds1/retries0/repairs0; Cloud elapsed44мин31.604с.
Нового proof credit нет; proof rows, RSS и runtime covers заново не измерялись; summary memory fields MISSING.
Evidence: [summary](renamemods/evidence/summary.md), [проверка](renamemods/evidence/verification-report.json), [статика](renamemods/check-report.json), [ledger](renamemods/RUN-LEDGER.json).
