# TASK — worker11: acceptance v3 — роль unreachable по per-row stdout (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Вход: твой accept-v2 (g0 `42c382b7cc`): 9 ACCEPTED / 53 UNKNOWN, единственная причина 53 — роль 1710 unreachable
неизвестна, т. к. export не несёт description/location. Но в том же artifact (14190662926) per-row `<row>/stdout.log`
— regular output Kani с полным списком checks: `Check N: <id> / Status / Description / Location: file:line in function`.
Пример `swap_contract_u8_n2/stdout.log`: `fmt::Arguments::<'_>::from_str.assertion.1` UNREACHABLE,
"attempt to shift left with overflow", `library/core/src/fmt/mod.rs:820:38`.

1. Для каждой строки: проверить, что stdout не усечён (receipt truncation flags/размер vs cap) и что блок checks
   принадлежит именно этому harness (в batch stdout разбит по harness маркерам — используй receipt-разбиение runner'а).
   Усечённый/несвязанный stdout → строка остаётся UNKNOWN.
2. Сопоставить каждое unreachable из export (exact ID) с записью stdout (тот же ID; status UNREACHABLE) → description,
   file:line, function. ID-несовпадение/дубль → UNKNOWN.
3. Роль по политике: обязательные postcondition/frame/relation/required-section для target/wrapper → блок;
   библиотечные/defensive ветки вне заявленного сценария (например fmt overflow, panic formatting) → допустимы с причиной.
   Правила — явная таблица семейств (function/file паттерн → роль → обоснование), не ad hoc.
4. Переклассифицировать 62 строки (consumers после leaf). Synthetic tests на новые ветки, review.
5. g0 `.../run-43784551069/accept-v3/`: ACCEPTANCE.md, ACCEPT.json, UNREACHABLE-ROLES.md, HANDOFF.md.
   Последней строкой `READY <g0>` или `STOP <причина>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
