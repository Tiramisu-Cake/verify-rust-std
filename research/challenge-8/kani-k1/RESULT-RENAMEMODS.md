# RENAMEMODS — PRE-BUILD, G1 PENDING
Library `85ced7f8a8bcdf6b4ffe2e29a65d1d940ff10737`, tree `def2d65ddc5e73ed6ccb94df0afbb36e475d80d8`.
База LEANHELPERS `5c929ba094cef478efc350b3cd9d7b8fc73fe203`; восемь файлов перенесены через git mv один к одному.
Статика PASS: 233 ordinary + 13 контролей = 246; явная биекция, потерь и дубликатов нет.
Все раскрытые items, 246 корней и их замыкания токен-идентичны базе после разрешённой обратной подстановки.
Число, позиции и аргументы covers сохранены; ранее разные сообщения внутри каждого замыкания остаются разными.
Изменены 64 места сообщений (59 различных литералов); canonical comparator и пять контролей specfix_* → profile_*.
Имена: [name-map.tsv](renamemods/name-map.tsv); сообщения: [message-map.json](renamemods/message-map.json).
rustfmt --check PASS, stdout пуст; строк>100 и запрещённой лексики TIDYDOCS в verify нет.
smallsort.rs побайтно неизменён; tooling совпадает с `59893bff1fbb2af1a0c08862afd7e3bb87c19cdd`.
Старых имён модулей/specfix_* в verify и комментариях smallsort.rs нет (границы идентификаторов).
Substring-исключения wrap: 17 строк — wrapping API, arbitrary_wrapped_u64_order и описательные wrapper(s), не кодовые имена модулей.
Все места и причины: [remaining-name-mentions.json](renamemods/remaining-name-mentions.json); root/helper/API имена сохранены по границам задания.
G1 `942bc6d1-191d-4777-acc5-d0d724564fde` SUBMITTED: inventory controls=false, standard4, harnesses=[]; exact-packet GO `0504202814f16c4a962687c6933a4e43b171d45b`.
Ожидаемый sorted ordinary SHA256 (233): `bd539369aead46f534868511eecef993b086cacd11e08b0b15f022103482a93b`.
Ожидаемый sorted cfg-on SHA256 (246): `3e03f6051cb8d0ab71d1a40f73c58234acbc7964315529ac9c603c49f9d222eb`.
Compiler inventory count/hash и новые warnings: PENDING; cfg-on compiler/runtime 13 контролей отложены в интеграционный пакет.
Расход $0/$1.20, reserve $0.999, builds1; G1 reserve $0.999 (74 мин × $0.0135), retries0.
Project при подготовке: used $107.0520, reserve0, cap $118.96; перед dispatch обновить.
Окно main240+closeout30 мин; T0 `2026-11-06T15:54:11.361779+00:00`. Нового proof credit нет.
Пакет: [PREBUILD](renamemods/PREBUILD-RENAMEMODS.md), [статика](renamemods/check-report.json), [ledger](renamemods/RUN-LEDGER.json).
