# KANI3300 — final export, composition and gates (DRAFT / NOT ISSUED)

2026-11-13. Это верификация корректности, не security-работа.
Только проект следующих стадий. Этот документ не выдаёт работу и не разрешает запуск CI/Cloud.

## Принятый вход

- Kani `94c00a8859bc9e4f0f1b7db73a95dbee88f6213a`, read-only `/root/kani-fix-3300-cc5`.
- Coordinator-reported Quick `43465107918`: kani 22/0, expected 168/0, ui 14/0, script 1/0,
  json-handler 2/0; восемь сильных оракулов совпали. Это Quick этой головы, не полный regression gate.
- Ordinary/SimpleCheck Replace companions и recursive SimpleCheck проходят; actual analysis cycles
  в recursive ordinary/check дают явный Unsupported. Replace/Recursive shadow-transfer support не заявлен.
- Object-bits 12 для тяжёлых PFC tests принят владельцем. Исторические M2/resource HELD не новый STOP
  для этой базы; исторический `TASK-KANI3300-M3.md` не переписывать.

## Две полосы и последовательность

| Сессия | Worker 14 | Worker 15 | Зависимость / приёмка |
|---|---|---|---|
| 1, параллельно | `TASK-KANI3300-FINAL-EDGES-draft.md`: четыре semantic edges | `TASK-KANI3300-EXPORT-CLEAN-draft.md`: export/JSON cleanup | Оба от exact 94; раздельные файлы |
| Интеграция | Координатор принимает bounded fixes/ограничения и сводит E1+X1 в C0 | Подготовка gate/replay request уже возможна | Exact SHA/tree, без незаявленных production deltas |
| 2 | `TASK-KANI3300-M3-FINAL-draft.md`: композиция + mixed-root на C0 | `TASK-KANI3300-FULLGATE-REPLAY-draft.md`: подготовка CI и replay | W15 не меняет исходники/новые тесты W14 |
| Freeze | M3 tests и принятые corrections входят в C1, intended final export | W15 связывает manifests/argv/оракулы с C1 | M3/mixed qualification, затем полный gate и replay на том же export |

Одна выданная стадия на сессию; новая выдача/запуск остаются за координатором. Сейчас все четыре TASK — черновики.
Если M3 потребует correction, W15 обновляет только bindings после review; не запускает gate на старом C0.
Новый source/test delta после freeze аннулирует применимость затронутых receipts: повторить нужные targeted checks,
а выпускной полный gate получить на окончательном export. CI-only workflow overlay хранить отдельно от export tree.

## Владение файлами

- W14: bounded compiler fixes из E1; новые `tests/expected/uninit/part1-edges/**`,
  `part1-composition/**`, `mixed-promoted-allocations/**` (только проверенный C1-T2-A snapshot tests),
  новый `tests/json-handler/uninit-part1-composition/**`. Затем M3 в этих же областях, последовательно.
- W15: только существующие `tests/json-handler/uninit-contract-oracles/**`,
  `uninit-contract-mode-boundaries/**`, два внутренних `docs/dev/kani3300-m2bs*-handoff.md`;
  отдельный CI-only overlay и отдельный SmallSort test-only replay overlay. Общие JSON schema/driver/compiletest не менять.
- `library/kani_core/src/mem_init.rs` и принятая runtime/model policy заморожены. Новый transfer protocol,
  SCC/cache architecture или расширение MU-of-flat/realloc/foreign/ZST scope — STOP с отдельным предложением.
- W14 не импортирует частный checker W15 в новый suite; разрешён неизменённый общий JSON validator.
  Изменение property identities возвращается владельцу соответствующего suite, без автоматического обучения оракула.

## Что должно войти в export и что остаётся открытым

Убрать research-ссылки и организационную историю из обоих JSON README, упростить tooling без потери
восьми оракулов/шести mode roots. Внутренние handoff docs сохранить в research, убрать из export.
Маркерная диагностика вместо `unwrap_or_default` остаётся явно отложенной координатором; уборка не реализует её молча.
Не превращать compile-only/Unsupported/ожидаемый negative в formal proof; final readiness требует M3/mixed,
полного штатного regression и uninit-on SmallSort replay, каждый с exact identities и собственным результатом.
Никаких локальных cargo/rustc/Kani/CBMC/Miri/builds; Cloud $0 для подготовки. Push/CI/публикации здесь не разрешены.
