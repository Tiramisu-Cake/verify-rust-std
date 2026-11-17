# TASK — w11: свести S1-07 U/PFC components в новый receipt

Это верификация корректности, не security-работа. Отвечай кратко. Runtime Codex.
Свежая сессия, модель/effort оставить установленными в pane. Без вложенной делегации.
Вход g0 `013f288ca5111c0587e087567d2ec4182856be1d`.

## Единственная цель

В `/root/verify-rust-std-kani3300-g0` создать новый replayable S1-07 admission receipt
`kani3300/ch8-s1/s1-07/run-43923266772/accept-v3/`, композицию трёх immutable входов:
- исходный `accept/` из `b84003a4fd` с integrity/identity/source/covers/oracles/success gates;
- U component `accept-u/` commit `16e36c4a2c244bb23ae71c80e5aa6db5f95e5338`;
- PFC component `accept-pfc/` commit `013f288ca5111c0587e087567d2ec4182856be1d`.
`accept-v2/` — неполный stop-marker, не вход admission. Все старые каталоги неизменны.

## Условия композиции

1. Read-only replay исходного receipt и обоих components должен пройти с exact hashes. Сверить run, source/tool,
   request, group/row/harness/property namespaces и версии/assurance; stale/foreign/partial/duplicate inputs fail-closed.
   Не заменить повторную проверку components чтением только их summary. Потреблять committed component versions;
   временные изменения/артефакты соседних source/control worktrees не являются evidence.
2. Убрать U gate конкретной строки только при точном покрытии всех её ранее UNKNOWN records проверенными U records;
   исходные статусы UNREACHABLE и 226 уже allowed checks/2 negative-return covers сохранить. Любой остаток — PENDING.
3. Убрать PFC binding gate только при exact BOUND chain этой же строки по Profiles v4 source-reported policy.
   Не превращать это в independent compiler/MIR proof credit. PFC component не заменяет остальные row gates.
4. 111 непривязанных success-message roles остаются PENDING. Нельзя использовать source S1-08/ROLE-MAP или новые
   labels для заднего числа на S1-07. Изначальные 16 exact bindings/113 required SAT covers не переугадывать.
   Сохранить все inventory, identity, snapshots, location exception, unsupported links, checks и 8 predeclared
   sole-failure negative oracles. Позитивный source verdict и negative expected FAILURE различать.
5. Пересчитать named companion qualification транзитивно из actual local gates и того же run/pins. SOURCE SUCCESS
   companion не равно qualified. Не убирать dependency по общему group verdict. N0..3 unions квалифицировать лишь
   если все их exact member rows qualified с прежним domain; остальные unions оставить PENDING.
6. Report qualification вычислять, не hardcode ожидаемое количество. Каждое изменение old→new объяснить consumed
   component records/edges; не менять historical receipts. Отдельно указать source-reported assurance и independent
   proof credit NONE. W14 review входных компонентов и нового composer пока PENDING — readiness к review не CI GO.

## Выход и validation

Только новый accept-v3/: ACCEPT.json, ACCEPTANCE.md, INPUTS.json, replay.py, targeted tests, VALIDATION.json,
HANDOFF.md. Никаких копий artifacts/изменений std/control/ledger. Replay по умолчанию read-only, побайтно сравнивает
receipt; write режим явный и пишет только свой receipt. Mutation cases: partial/missing/foreign/wrong-status U coverage,
неполная PFC chain, неверные namespaces/hashes, успех source при открытых success gates, companion cycle/missing/
unqualified/foreign-run, pending member union. Проверить gates под outer hash слоем, не только digest rejection.

Времени/объёма достаточно: выполнить реализацию и проверки, не останавливаться из-за оценки «не успеваю»,
контекста или исправимой ошибки. Новое рабочее окно по CORE от фактического старта; старый T0 не наследовать.
STOP только по реальному external/scope blocker либо фактически достигнутому установленному лимиту с фактами.

Без push/CI/публикаций/ledger, локальных cargo/rustc/Kani/CBMC и full raw logs/archives.
W14 параллельно делает read-only review, пишет только review/; shared g0 stage/commit только собственный accept-v3/,
без git add -A/reset/rebase чужих коммитов. `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <g0>` с computed qualification/gates/tests либо `STOP <реальный blocker>`.
