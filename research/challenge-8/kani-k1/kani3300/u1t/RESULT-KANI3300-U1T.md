# RESULT-KANI3300-U1T
Статус: PRE-BUILD, все native результаты NOT_RUN; ожидание exact-packet GO координатора.
Runtime Codex; stage `kani3300-u1t`; owner `k1-merge`; research branch `experiment/kani-k1-kani3300u1t-20261111`.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tests-only commit `647109cf6342474d899aa463315a37dac14fd831`.
Applied preflight tree `0e16a12fd4ce531e03c121c1160243426a51f49e` совпал с локальным Kani; production побайтно равен U1.
Tooling `c98d7cee0d509b1633ab61c9a1ae989e286c8e2a` не изменён.
Patch SHA-256 `37689b6c615b6c8e4f321113f07c6c8d124cdf2aa30ff94eeda909a6ba18a1e6`.
Request `kani3300-u1t-native-20261111-01`, SHA-256 `f0e8f7ca4082f69108ded989780eefe69ff89b4d4c6941427b1b07a38be2768b`.
Статические validate/apply/tree/flags/golden/rustfmt/diff/tooling checks PASS; native PASS не установлен.
Таблица: пути относительно `tests/expected/uninit/`, общий суффикс `/main.rs`.
| Selector | Ожидание | Native / вердикт кандидата |
|---|---|---|
| `maybe-uninit-review-overwrite-copy` | uninit `[u8; 2]` | NOT_RUN / не установлен |
| `maybe-uninit-review-overlap-copy` | uninit `u8`, две harness | NOT_RUN / не установлен в обе стороны |
| `maybe-uninit-review-repeat-local` | uninit `u64` | NOT_RUN / не установлен |
| `maybe-uninit-review-reset-zst` | ZST допустим, затем uninit `u64` | NOT_RUN / не установлен |
| `maybe-uninit-review-padded-manually-drop` | uninit `Padded`, поле b | NOT_RUN / не установлен |
| `maybe-uninit-review-argument-return` | uninit `u16`, второй аргумент | NOT_RUN / не установлен |
| `maybe-uninit-review-positive` | SUCCESS 7/7, require_success | NOT_RUN |
| `maybe-uninit-initialized` | SUCCESS 8/8, require_success | NOT_RUN |
| `maybe-uninit-scratch-array` | SUCCESS 1/1, require_success | NOT_RUN |
| `maybe-uninit-partial-copy` | uninit `[u8; 4]` | NOT_RUN |
| `maybe-uninit-reset-alias` | uninit `u8` | NOT_RUN |
| `maybe-uninit-volatile-read` | uninit `*const u8` | NOT_RUN |
12 selectors / 26 harnesses; новые тесты: 6 negative fixtures (7 harnesses), один positive (7 harnesses).
Расход $0; плановый резерв одной сборки $0.4725 из cap $0.50; dispatch не выполнен, активный резерв не заявляется.
Upstream: включить шесть кандидатов и парные контроли после подтверждения native; текущие результаты не дают proof credit.
Следующий шаг: PRE-BUILD review/GO полного опубликованного SHA, затем одна разрешённая сборка и bounded summary/native.
