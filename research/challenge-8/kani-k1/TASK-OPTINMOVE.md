# OPTINMOVE — вынести исследовательские opt-in из Part 1 и убрать точные дубли макросов

**Выдано координатором 2026-11-06, решение владельца.** Второй из трёх последовательных этапов очистки перед подачей
Part 1. Dispatch только после exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-optinmove**, ветка **experiment/kani-k1-optinmove-20261106** от
  **01c090dc1d** (TIDYDOCS PASS: library `6443b4d99d`, tree `6062452294`; 233 ordinary, 13 контролей, 22 прочих
  opt-in; cfg-on 268).
- Slug **optinmove**, stable owner **k1-merge**. Request_id/stage/ledger `optinmove-*`.
- Project cap **$118.96**, свой cap **$2.00**. **До двух сборок**; G2 — только после разбора G1 и GO координатора.
  Retry нет. Один compile-error repair на сборку, если own spent + reserve ≤ cap.
- Tooling base для check-tooling: **59893bff1f**. Tooling не менять.
- Окно: main 300 + closeout 30 мин.

## Цель

Подаваемое дерево должно содержать только то, что заявляется: 233 ordinary-корня и 13 отрицательных контролей.
22 прочих opt-in корня (более широкие/медленные исследовательские варианты, часть с TIMEOUT) из подачи убрать, но
**не потерять**: сохранить их опись в research. Заодно убрать точные дубли макросов и одноразовые обёртки.
**Ни одно ordinary-доказательство и ни один контроль не должны измениться по смыслу и по кодированию.**

## 1. Вынос 22 исследовательских opt-in

- Определить точный список 22 корней: cfg-on имена минус 233 ordinary минус 13 контролей
  (`tidydocs/cfg-on-expected.txt`, `tidydocs/ordinary-expected.txt`; контроли — 12 прежних + 
  `realcontracts::rejects_swap_comparator_writing_outside_frame_u8`). Ожидается: `realcontracts` 8, `permtags` 10,
  `scratchgeom` 4 — проверить, а не принять на веру.
- Удалить эти корни и **только** те хелперы, импорты, типы и макросы, которые используются исключительно ими.
  Всё, что нужно хотя бы одному ordinary-корню или контролю, сохранить (например, хелпер отсечения паники в
  `permtags`, который использует контроль с дублированным тегом). Решать по графу зависимостей, а не по совпадению cfg.
- Если файл после выноса пустеет или в нём остаётся один-два элемента — **не** переносить и не переименовывать файлы
  на этом этапе; только записать наблюдение в RESULT.
- Новых `unused` предупреждений быть не должно (проверить компиляцией в обеих cfg).
- Поправить карту в `verify.rs` и локальные комментарии, которые упоминают вынесенные корни («broader or slower
  variants», `_with_callback_covers`, прямые insertion PFC и т. п.): теперь за `cfg(kani_smallsort_controls)` только
  отрицательные контроли. Стиль комментариев — как в TIDYDOCS (коротко, без истории этапов, строки ≤ 100).

**Сохранение в research** — `research/challenge-8/kani-k1/optinmove/MOVED-OPTIN.md`: таблица 22 строк — полное имя
корня; файл и строка в коммите `44b972435aeff6ea88cd01e64ccea3727a98294e` (GitHub permalink на
`Tiramisu-Cake/verify-rust-std`, этот коммит публичен в ветке `submission/ch8-smallsort-part1-v8c`); одна строка «что
проверяет»; последний известный статус (SUCCESS с временем / TIMEOUT / NOT_RUN) и ссылка на RESULT, где он получен.
Источники статусов — только наши RESULT: REALCONTRACTS `d648179493`, REALCONTRACTSTWO `588c002998`, PERMTAGS
`6542b3c4ba`, SCRATCHGEOM `151c193b63`, VEIGHTINTEG `4fa6151b6a`, WIDEDOMAINS `30b4a0796a`, TAILDIAG `59ada14d0a`
(читать `git show <sha>:research/challenge-8/kani-k1/RESULT-<NAME>.md`). Если статус не найден — NOT_RUN/неизвестен,
не выдумывать. Плюс как запустить: `RUSTFLAGS="--cfg kani_smallsort_controls"` и `--harness <name> --exact` на
дереве `44b972435a`.

## 2. Точные дубли макросов и одноразовые обёртки

Менять форму кода можно **только** если раскрытый (после `macro_rules!`) item каждого затронутого корня —
атрибуты, имя, тело — **токен в токен** совпадает с исходным. Иначе не трогать и записать в RESULT.

Кандидаты (номера строк по `44b972435a`, ориентировочно):
- `merge.rs:423–442`: `define_general_sortedness_harness` и `define_general_direct_harness` побайтно одинаковы —
  оставить один (имена генерируемых корней сохранить).
- `merge.rs:444–466`: четыре ручных корня `general_stable_direct_u64_n2..n5` — если существующий макрос (например,
  `define_direct_u64_route_harness`) раскрывается в точно такой же item, использовать его (определение — до
  использования).
- `network.rs:1024–1047`: два ручных PFC `swap_contract_*_indices_n17` — через `swap_contract_arbitrary_indices_case`,
  если раскрытие идентично.
- `network.rs:389–406`: `dispatch_pair_route_safety_case` — макрос ради одного корня; записать корень обычной
  функцией.
- `merge.rs:549–559`: `define_merge_scratch48_contract_harness` — используется один раз; записать корень явно.

Не делать здесь: общий модуль хелперов, объединение тел проверок (`check_swap`/`check_insert`, route properties),
`CopyOnDrop`, `MUTANT`, `START`, слияние файлов, переименования модулей и корней — это изменения кодирования или
структуры, они не входят в этап.

## Статические проверки (скрипт в `research/challenge-8/kani-k1/optinmove/`, в пакет и RESULT)

Переиспользовать лексер/expander из `tidydocs/check_tidydocs.py` / `codefix/trimpart_static.py`.
- cfg-off имена = 233, ровно `tidydocs/ordinary-expected.txt`.
- cfg-on имена = 246 = 233 + 13 контролей; удалённые = ровно 22 из п. 1.
- Для каждого из 233 ordinary и 13 контролей: раскрытый item (атрибуты + тело, токены) идентичен TIDYDOCS
  `6443b4d99d`; транзитивное замыкание вызываемых им verify-функций/типов/макросов также идентично (кроме
  комментариев). Число и место `kani::cover` не изменились.
- `smallsort.rs` не изменён.
- Строк > 100 в `verify.rs`/`verify/**` нет; запрещённой лексики (TIDYDOCS, правило 1) нет.

## Сборки

Цель сборок — компиляция обеих cfg и **compiler inventory** (локальный cargo/Kani запрещён):
- нужно подтвердить компилятором cfg-off = 233 ожидаемых имени и cfg-on = 246 ожидаемых имени, без новых
  предупреждений в `smallsort/verify`;
- если статика показала, что ни один ordinary/контроль не изменился по раскрытию, proof-строки не обязательны;
  можно добавить 1–2 самых коротких корня из затронутых макросов как дымовую проверку;
- учесть особенность lane: diagnostic+inventory перечисляет корни до применения controls RUSTFLAGS, поэтому cfg-on
  inventory может требовать kind inventory. Inventory-компиляция занимала ~47 мин — рассчитать лимит сборки с
  запасом (прошлая ошибка: лимит rows×t+30 не вместил inventory).
- План сборок (одна или две) обосновать в пакете; G2 — только после GO.

## Коммиты

- Library-коммит(ы) и research-коммит отдельно, `[skip ci]`. Push без force.
- Последней строкой `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание сборки: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход. Не опрашивать
  статус в цикле.

## RESULT

**RESULT-OPTINMOVE.md**, ≤ 40 строк: identities (library SHA и tree); результаты статики; inventory cfg-off/cfg-on
(число, совпадение, SHA256 списка); строки удалено/добавлено по файлам и итог `verify*`; какие дубли убраны и какие
нет (с причиной); ссылка на MOVED-OPTIN.md; расход.

## Запреты

- Evidence — только bounded K-1 summaries/rows/peaks/log-grep/inventory. Raw logs, archives, Cloud Logging и
  credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani. Чужие PR, их ветки и код не открывать.
- Workflows, скрипты, tooling и `smallsort.rs` не менять.

Маркеры `REVIEW REQUEST <sha>` / **OPTINMOVE ЗАВЕРШЁН**, одна стадия, затем стоп.
