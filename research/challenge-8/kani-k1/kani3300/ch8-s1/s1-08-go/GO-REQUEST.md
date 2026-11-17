# S1-08 — пакет к GO координатора

**READY_FOR_COORDINATOR_GO. Dispatch/push/reservation не выполнялись.**
Запрашивается один S1-08 fork workflow attempt, без auto-rerun, для получения различимых role labels.

## Замороженные pins

| Назначение | Exact identity |
|---|---|
| Std source | `99e8456d200fff1299ee5756279cddb23921dc65` |
| Reviewed control | `7c41333f9bfcfd7eb4e0ede7bd316443090c9025` |
| Локальный trigger без skip-ci | `21592884db439389364b416dea1515bfa9d8018e` |
| Stock tool | `0aac16ef62da9e9d5645782d458593e5d78143ba` |
| Embedded request SHA256 | `77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e` |
| Package g0 | `d5dcb0fa5db210116101f440048a4f1fae7c2d20` (`../s1-08-r1/`) |
| Independent delta-review g0 | `e14db2d0dd0f45a0cf9067c198911b38bca83012` |

Trigger имеет **тот же tree и единственный parent9208**, что reviewed control; diff пуст.
Он сохранён только локально: `/root/kani-ch8-s1-08-go-control`,
ref `prepared/ch8-s1-08-go-20261117`. Его existing control preflight прошёл в synthetic GitHub context.
Полные tree/file/role-map hashes, flags и состояния — [GO-REQUEST.json](GO-REQUEST.json),
[PREPARED-TRIGGER.json](PREPARED-TRIGGER.json), [COORDINATOR-CHECKS.json](COORDINATOR-CHECKS.json).

## Review и смысл запуска

[W14](../review-after-07/delta-r1/REVIEW.md): **composer APPROVE; repaired package APPROVE;
W14-S108-01 CLOSED; новых findings нет.** Исправлены только source-derived closure spans двух negative IDs;
exact matching и logical failure oracles сохранены. Исходные кандидаты/receipts неизменны.

Новый S1-07 [receipt](../s1-07/run-43923266772/accept-v3/ACCEPTANCE.md): 14/35 qualified;
21 строка /111 success-message roles ещё PENDING, 0/4 qualified unions.
Новые labels не использовались задним числом. S1-08 сохраняет smoke N0..3, 35 roots/14 групп,
127 required roles (111 новых labels +16 прежних bindings),113 required covers,8 negative oracles.
U принимаются по per-site аргументам; PFC — source-reported Profiles v4 с доверием stock compiler.
Compiler/verifier/runtime S1-08 **NOT_RUN**; PASS не обещан, independent B1/B2/general proof credit NONE.

## Бюджет и порядок после отдельного GO

- По зафиксированному ledger item2 использует7/14. Запрос — ещё1 accepted run/attempt; проекция8/14,
  остаток6. Нового расхода или reservation сейчас нет; перед действием сверить актуальный учёт.
- Ubuntu24.04, jobs/max-parallel1, serial14 groups;600s/root,900s compile/group,
  setup1800s/job, phase8100s/job, reserve900s/job, timeout180min/job. Group RSS ≤12GiB с2GiB headroom;
  extra uninit/valid-value OFF, object-bits12. Сумма conservative serial envelopes71540s
  (19h52m20s) **без queue**; календарное окно/deadline с queue margin задаёт координатор до submit.
- Artifacts: один compact structured файл на группу, ≤8MiB compressed /32MiB uncompressed;
  суммарно≤112MiB compressed. Raw stdout целиком не публикуется.
- После GO: оформить reservation с exact request/source/tool/trigger/tree/caps; сначала опубликовать source
  в std fork и проверить remote SHA, затем trigger в Kani fork на `uninit-ci/ch8-s1k-*`.
  Запускается существующий `.github/workflows/ch8-s1.yml`; record actual head/run ID/attempt1 и charge.
  Любой rerun требует отдельного решения и учёта.
- Intake: все14 same-run snapshots/inventories,113 required SAT covers,8 exact sole-failure negatives,
  compatible companions,127 actual role bindings и PFC/U gates проверяются заново на S1-08.
  Не переносить старые property IDs/qualification по ordinal, source promises или агрегатным counts.

Пакет готов к решению координатора о GO; сам документ запуск не разрешает.
