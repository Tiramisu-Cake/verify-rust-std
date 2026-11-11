# RESULT-KANI3300-U1T
TOOL_ERROR, gate false: build `ff0988c7-d2f2-4872-b4ea-be581d9de02f`; 7/12 native PASS, 5 ERROR; acceptance не выполнена.
Exact build head `21f7d3dffc1da40f8c647237d933c9fc8f9da39a`; request `kani3300-u1t-native-20261111-01`.
Request SHA-256 `f0e8f7ca4082f69108ded989780eefe69ff89b4d4c6941427b1b07a38be2768b`.
Patch SHA-256 `37689b6c615b6c8e4f321113f07c6c8d124cdf2aa30ff94eeda909a6ba18a1e6`; production побайтно равен U1.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, local tests commit `647109cf6342474d899aa463315a37dac14fd831`.
Cloud applied tree `0e16a12fd4ce531e03c121c1160243426a51f49e` = preflight; check-tooling PASS against `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a`.
Kani 0.68.0 / CBMC 6.11.0; Kani build 236 s, compiletest build 16 s. Static checks PASS; production/tooling не менялись.
Evidence: bounded `k1g.sh summary/native`, check-tooling и budget; ограничение подробно в `EVIDENCE-KANI3300-U1T.md`.
Пути относительно `tests/expected/uninit/`, общий суффикс `/main.rs`; UNKNOWN не означает ложный SUCCESS/отказ.
| Selector | Native | Вердикт кандидата / результат |
|---|---|---|
| `maybe-uninit-review-overwrite-copy` | ERROR | UNKNOWN: есть описание uninit `[u8; 2]`, статус свойства недоступен |
| `maybe-uninit-review-overlap-copy` | ERROR | UNKNOWN: есть описание uninit `u8`, обе ветки не установлены |
| `maybe-uninit-review-repeat-local` | ERROR | UNKNOWN: есть описание uninit `u64`, статус свойства недоступен |
| `maybe-uninit-review-reset-zst` | ERROR | UNKNOWN: есть описание uninit `u64`, статус свойства недоступен |
| `maybe-uninit-review-padded-manually-drop` | PASS | Подтверждён: golden FAILURE/uninit `Padded` |
| `maybe-uninit-review-argument-return` | ERROR | UNKNOWN: есть описание uninit `u16`, статус свойства недоступен |
| `maybe-uninit-review-positive` | PASS | 7/7 SUCCESS, require-success, Kani exit 0 |
| `maybe-uninit-initialized` | PASS | 8/8 SUCCESS, require-success, Kani exit 0 |
| `maybe-uninit-scratch-array` | PASS | 1/1 SUCCESS, require-success, Kani exit 0 |
| `maybe-uninit-partial-copy` | PASS | Golden FAILURE/uninit `[u8; 4]` |
| `maybe-uninit-reset-alias` | PASS | Golden FAILURE/uninit `u8` |
| `maybe-uninit-volatile-read` | PASS | Golden FAILURE/uninit `*const u8` |
Расход $0.1080, резерв $0; остаток cap $0.3920. Repair $0.4725 дал бы $0.5805 > $0.50; новый Build не разрешён.
Пять ERROR не диагностированы: `native` exit 2 `one native record exceeds the bounded page size`; Brief HTTP 404.
Текст uninit-описания не доказывает FAILURE; negative SUCCESS не установлен и не исключён. Все positive прошли; ложный отказ не наблюдался.
Upstream: подтверждены padded + 7 парных positive; пять остальных negative удержать до чтения своих bounded статусов/ошибок.
Следующий шаг координатора: bounded errors/output_excerpt/property statuses для native offsets 0,1,2,3,5; при negative SUCCESS — blocker, стоп, без production fix.
