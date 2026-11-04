# CODEFIX — правки Part 1 по аудитам → кандидат v8

**Выдано координатором 2026-11-04 (ночь), решения владельца: подавать Part 1 после небольших правок.**
**Dispatch только после exact-packet PRE-BUILD review/GO координатора.** Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-codefix**, ветка **experiment/kani-k1-codefix-20261104** от **59893bff1f**:
  upstream `233f96f66a` (Kani `cd355b0b`, nightly-2026-10-22), library Part 1 v7 (tree `32ce0c62f6`), тулинг K-1 с
  `valid_value_checks` и потолком $120.
- Slug **codefix**, stable owner **k1-network**. Новые stage/ledger/UUID/request_id `codefix-*`.
- Project cap **$118.96**, свой cap **$1.50**. **Одна сборка**. Исключение — один repair (compile error или
  warning в `smallsort/verify`), если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**.
- Окно: main 180 + closeout 30 мин.

## Что изменить (только файлы `library/core/src/slice/sort/shared/smallsort/verify*`)

1. **`verify/comparators.rs`, doc.** Убрать фразу о «verifier's volatile-ZST limitation». Написать: на этом
   Kani чтение ZST через `read_volatile` в измеренных in-core фикстурах давало pointer-проверки, источник не
   установлен; поэтому для ZST используется `ptr::read`.
2. **`verify/network.rs` около строк 644–663.** Комментарий о структурной композиции перестановки при N ≥ 9
   заменить фактом: при N ≥ 9 этот харнесс проверяет только порядок, перестановка суффикса вставок проверена
   отдельными харнессами.
3. **Комментарии о геометрических предикатах** (`can_dereference`, `can_write`, `same_allocation`) там, где они
   подразумевают инициализацию или права. Сузить: инициализацию дают построенные фикстуры, предикаты задают только
   геометрию.
4. **Doc модуля `verify.rs`.** В начале кратко и фактически:
   - у трёх `small_sort` контрактов нет. На текущем pin Kani не принимает контракт на specialization `default fn`
     и PFC на trait-метод с собственным generic `F`; это воспроизведено на `cd355b0b`, Actions runs 41894986646 и
     41894991130;
   - контракты хелперов здесь на профилях, которые фиксируют один компаратор.

   Не утверждать, что контракты на свободных generic-функциях невозможны. Остальной doc сверить с новым составом.
5. **Новый ordinary-харнесс: `swap_if_less` при `a_pos == b_pos`.** Прямой вызов реального `swap_if_less` на u8,
   обе ветви ответа компаратора (`kani::any()`), проверка сохранения полного значения, covers на обе ветви. Профиль
   `swap_geometry` (требует `a != b`) не использовать.
6. **Новый ordinary-харнесс: ветвь `Freeze + !Copy`, размер > 85 байт → fallback** в default-реализации
   `UnstableSmallSortFreezeTypeImpl`.
   - Свой тип: прозрачная обёртка над `[u8; 86]` без `Copy`.
   - Статически подтвердить `!Copy` и выбор этой специализации (const-assert на размер и подходящий маркер).
   - Вход через Unstable entry, N2. Safety и сохранение значений, cover на достижение fallback.
7. **`#![allow(dead_code)]`** в `merge.rs` и `network.rs`: попробовать убрать. Перед этим статически удалить
   подтверждённые сироты, в том числе неиспользуемые impl `ArbitraryValue`. Проверить обе конфигурации, с cfg
   контролей и без. PFC-зависимости и функции, вызываемые только макросами, не удалять по одному лишь отсутствию
   прямого вызова.

Остальное не трогать: ordinary-корни v7, их тела и атрибуты, а также 8 контролей. Каждый новый харнесс должен
укладываться в ≤ 60 с на GCB, иначе это факт для RESULT, а не повод расширять лимит.

## Статика до PRE-BUILD

- Набор ordinary = 202 v7 + новые (ожидаемо +2). Тела 202 v7 совпадают с v7 по токенам, кроме комментариев.
  Повторно использовать скрипт `research/challenge-8/kani-k1/trimpart/check_trimpart.py` из `120e443536` или
  написать аналог в `research/challenge-8/kani-k1/codefix/`.
- rustfmt `--check`, `git diff --check`, строки ≤ 100. Diff против `e470652790` только в `smallsort/verify*`.
- `test_kani_k1.py` OK; `check-tooling` против 59893bff1f.

## Пакет

Одна сборка, kind diagnostic, `inventory: true`, `controls: true`, gcb-e2-standard-4, jobs 1:
- новые ordinary-корни, expect SUCCESS, все covers;
- `assembly::reject_mutant_swap_u8_n2` как контроль, что мутант по-прежнему падает.

Inventory в этом режиме — список без cfg (cfg-off). Он должен дать ровно новый ordinary-набор.

После сборки сделать `k1g.sh log-grep` по `warning` с путём `smallsort/verify`: предупреждений быть не должно,
иначе один repair.

## Коммиты

- **Library** — один коммит `[skip ci]`: кандидат v8, поверх `59893bff1f`.
- **Research** — отдельно, `[skip ci]`.

Push без force. Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.

**Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`** (detached, будит thread через
`codex queue`), затем завершить ход. Не опрашивать `k1g.sh status` в цикле.

## RESULT

**RESULT-CODEFIX.md**, ≤ 35 строк:
- identities;
- список правок по пунктам 1–7: что изменено, что оставлено и почему;
- inventory: count и delta;
- таблица строк сборки;
- предупреждения;
- строки до/после.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Runtime `smallsort.rs`, workflows, скрипты и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **CODEFIX ЗАВЕРШЁН**, одна стадия, затем стоп.
