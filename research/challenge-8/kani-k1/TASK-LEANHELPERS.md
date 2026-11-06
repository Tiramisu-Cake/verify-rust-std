# LEANHELPERS — мёртвые параметры и inherent-методы на типе std

**Выдано координатором 2026-11-06, решение владельца.** Третий, последний этап очистки перед подачей Part 1.
Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-leanhelpers**, ветка **experiment/kani-k1-leanhelpers-20261106** от
  **cea2621208** (OPTINMOVE PASS: library `461dac0c43`, tree `f1d36898b9`; 233 ordinary + 13 контролей, cfg-on 246).
- Slug **leanhelpers**, stable owner **k1-merge**. Request_id/stage/ledger `leanhelpers-*`.
- Project cap **$118.96**, свой cap **$1.50**. **Одна сборка** (G2 — только для исправления нашей ошибки после GO).
  Retry нет. Один compile-error repair, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 240 + closeout 30 мин.

## Цель

Убрать три вещи, которые ревьюер upstream заметит как лишние. Смысл всех доказательств сохраняется; меняется форма
кода, поэтому затронутые корни выборочно перепроверяются.

1. **`MUTANT`** (`verify/merge.rs`, `drop_route_properties`): const-параметр единственный раз инстанцируется `0`;
   ветки `MUTANT == 1/2` и `const { assert!(MUTANT <= 2) }` мёртвые. Удалить параметр, assert и обе ветки, поправить
   вызов в макросе и комментарий над функцией.
2. **`START`** (`verify/network.rs`, `insert_tail_start1_frame`, `insert_tail_group_value`): const-параметр всегда
   `1` (`assert!(START == 1)`). Заменить на литерал/локальную константу `1`; цикл `while i < START` по одному
   элементу записать прямой проверкой того же элемента **с тем же текстом сообщения** assert. Остальные проверки и
   `unwind` не трогать.
3. **`impl<T> CopyOnDrop<T>`** (`verify/merge.rs`): три метода (`probe_count`, `probe_count_unrolled`,
   `regions_are_disjoint`) добавляют inherent-методы к типу std из модуля проверки. Перенести их в свободные
   generic-функции в том же модуле с теми же телами (`fn probe_count<T>(base: *const T, len: usize)` и т. д.),
   обновить все вызовы (`merge.rs`, `scratchgeom.rs`, `merge/specfix.rs`) и импорты `CopyOnDrop`, если они станут
   не нужны. Комментарий «live here to mention `T`…» переписать или убрать.

**Нельзя:** менять что-либо ещё — имена корней, атрибуты, другие тела, списки длин/типов, covers, контроли,
`smallsort.rs`. Новые общие модули, объединение тел проверок, переименования — не делать.

## Статические проверки (скрипт в `research/challenge-8/kani-k1/leanhelpers/`)

Переиспользовать лексер/expander из `optinmove/check_optinmove.py`.
- Имена cfg-off = 233 и cfg-on = 246 — ровно как в OPTINMOVE.
- Перечислить **затронутые корни**: те, чьё транзитивное замыкание содержит изменённые функции. Для всех остальных
  корней раскрытый item и замыкание токен-идентичны `461dac0c43`.
- Для затронутых: число и место `kani::cover` и тексты assert не изменились; diff ограничен тремя пунктами выше.
- Строк > 100 нет; запрещённой лексики нет; `smallsort.rs` побайтно неизменён.

## Сборка G1

kind diagnostic, `controls: true` (заодно компиляция cfg-on дерева), `inventory: false`, jobs 1, standard4.
Строки — выборка по одному-два **самых коротких** корня из каждого затронутого семейства, `expect: SUCCESS`:
- `MUTANT`: например `merge::drop_general_drop_count_n4`, `merge::drop_general_tag_permutation_n4`;
- `CopyOnDrop`: корень с `probe_count` (например `merge::sort4_arbitrary_comparator_u64_n4`), корень с
  `probe_count_unrolled` (короткий general/stable route), корень `scratchgeom`, один профильный PFC, где
  `regions_are_disjoint` стоит в `requires` (короткий `sort4`/`merge` профиль);
- `START`: `network::insert_tail_contract_u64_start1_tail15_to16` (самый короткий из группы; в CI v8c 156–164 с).
Не более 8 строк. Лимит на корень выбрать так, чтобы `tail15_to16` уместился с запасом (например 8 мин), и
рассчитать лимит сборки: компиляция cfg-on + строки × лимит + запас.

Для каждой строки сравнить время и covers с прежними замерами (наши RESULT/GCB-строки, если есть; иначе с TSV CI
v8c `experiment/kani-k1-veightcci-20261106:research/challenge-8/kani-k1/v8cci/v8c-autoharness-smallsort.tsv`).
Рост более чем на ~25% — разобрать в RESULT; новый TIMEOUT/OOM — этап не принят, остановиться и спросить.

## Коммиты

- Library-коммит(ы) (по одному на пункт 1–3 допустимо) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не опрашивать
  статус в цикле.

## RESULT

**RESULT-LEANHELPERS.md**, ≤ 35 строк: identities (library SHA и tree); статика (число затронутых корней по
пунктам); таблица строк G1 (status, время, covers, прежнее время); строки удалено/добавлено; расход.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep. Raw logs, archives, Cloud Logging и credentials не
  читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Workflows, скрипты, tooling и `smallsort.rs` не менять.

Маркеры `REVIEW REQUEST <sha>` / **LEANHELPERS ЗАВЕРШЁН**, одна стадия, затем стоп.
