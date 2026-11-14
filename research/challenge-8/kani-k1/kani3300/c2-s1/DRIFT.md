# S1 follow-up — quick 43600410208

READY `69b13711e60a87458200833445d47488ab466344`  
Tree `1df668c6896eaed2b08385d307b8ddf178613c6f`; sole parent `ba0e5cfedf31e20d18e95b50ba5dbd6946277d2c`.

**В предоставленном inventory потерь нет: все 227 старых checks имеют уникальные соответствия с прежними description/status; добавлены 2 реальные upstream overflow-проверки. Это не только ID/location drift.** Обе добавленные проверки SUCCESS. Старые 218 SUCCESS + 9 UNREACHABLE стали 220 SUCCESS + 9 UNREACHABLE; FAILURE нет. Это локализация одного isolated root, не прохождение composition suite или новый proof credit.

## Форматирование и границы

Отдельный source commit `69b13711e60a87458200833445d47488ab466344` — `Format delayed initialization body fallback`, author/committer Tiramisu-Cake <igkharin@gmail.com> через `git -c`. Единственное изменение — блок closure `.unwrap_or_else(|| { ... })` в `delayed_ub/mod.rs:140–145`, как просит переданный rustfmt-диагноз. Выбор тела и выражение checked_body неизменны. `git diff --check` прошёл; повторный format check и CI на новом SHA **NOT_RUN**. Нет локальных Rust-сборок/верификаторов, push или CI. Research без commit; source inputs и прежние research-записи не изменены.

Переданный координатором итог относится к source `ba0e5cfedf` + CI-only overlay `ddd242820b`, run `43600410208`: build/clippy PASS; kani 24/0, expected 204/0 (2 ignored), ui 17/0, script 2/0; oracles/mode-boundaries ok; composition FAIL на этом корне; format FAIL. Это source-reported CI итог, не новый запуск агента. Новый source коммит не включает overlay.

## Сопоставление всех 229 строк

Входы — переданный `ci-quick-43600410208/ordinary_ensures_legal.regular.txt` и `/roots/2/expected_inventory` в неизменённом `tests/json-handler/uninit-part1-composition/roots.json`. Строгий существующий `checker.regular_properties` разобрал ровно Check 1…229 без пропусков; summary: `0 of 229 failed (9 unreachable)`, `VERIFICATION:- SUCCESSFUL`.

Полная карта — **DRIFT-CHECKS.json**: для каждой фактической проверки исходная строка regular, исходный номер/место в файле, old inventory index/JSON pointer, raw и диагностически нормализованная запись, классификация, source-причина и отдельные признаки перестановки. Все old rows отображены взаимно однозначно; lost=[], status/description changes=[]. Воспроизведение только разбора данных: `python3 analyze-drift.py` (не запускает runner/compiler/verifier и не меняет oracle). SHA256 входов записаны в JSON. Source diff для причин — DRIFT-SOURCE.diff.

| Класс | Количество | Причина и оценка |
| --- | ---: | --- |
| Exact row | 184 | Совпадают ID, location, description, status; номер печати может отличаться |
| Raw checkout path в closure ID/location | 2 | `set_ptr_initialized::<0, {closure@…mixed.rs:27:17: 27:43}>.safety_check.{1,2}`; absolute runner prefix вместо checkout-relative пути. Оба прежних checks присутствуют, SUCCESS |
| Raw toolchain location | 11 | 10 `std::ptr::read::<u8>` + 1 `std::fmt::Arguments::<'_>::from_str`; относительный `.rustup/.../library/` против сохранённого `rust-toolchain:…/library/`; тот же toolchain/файл/строка/колонка/status |
| Upstream source location | 30 | enter/exit/in_contract_clause pointer checks, точная карта ниже; те же ID, description, status |
| Реальное добавление check | 2 | enter/exit overflow assertions из #5093, подробности ниже |

13 raw path-различий снимаются **уже существующей**, не изменённой функцией `checker.normalize` (`checker.py:45–64`, применение `run.py:217–228`). Для диагностики взят видимый в closure IDs prefix `/home/runner/work/kani/kani`; оригинальный receipt отсутствует, его build_prefix не выдумывается и receipt не восстанавливается. Это разделение raw/normalized представлений, не новая нормализация или основание принять oracle. После существующей нормализации остаются именно 30 location differences + 2 новых checks.

## Source-причина каждого содержательного расхождения

Все они объясняются закреплённым upstream **`2ec6953d9` / #5093** (`Avoid saturating method calls in contract clause depth helpers`); candidate `library/kani_core/src/lib.rs` совпадает с U. C1b → tested source меняет этот файл только указанным патчем. Точная source-дельта сохранена в DRIFT-SOURCE.diff.

| Семейство ID | Старое место → новое место в library/kani_core/src/lib.rs | Количество и source-причина |
| --- | --- | --- |
| `kani::internal::enter_contract_clause.pointer_dereference.1…6` | 833:45 → 833:33 | 6: чтение static вынесено из аргумента saturating_add в `let depth = CONTRACT_CLAUSE_DEPTH` |
| `kani::internal::enter_contract_clause.pointer_dereference.7…12` | 833:21 → 835:25 | 6: запись static перенесена внутрь `if depth < usize::MAX` |
| `kani::internal::exit_contract_clause.pointer_dereference.1…6` | 846:45 → 849:33 | 6: чтение static вынесено из saturating_sub, плюс сдвиг от предыдущего helper |
| `kani::internal::exit_contract_clause.pointer_dereference.7…12` | 846:21 → 851:25 | 6: запись static внутри `if depth > 0`, плюс сдвиг |
| `kani::internal::in_contract_clause.pointer_dereference.1…6` | 892:26 → 898:26 | 6: тело `CONTRACT_CLAUSE_DEPTH > 0` неизменно, только +6 строк от двух helper-правок |

Две новые проверки — **не переименования**:

- Regular **Check 24**: `kani::internal::enter_contract_clause.assertion.1`, `attempt to add with overflow`, SUCCESS, `lib.rs:835:49`. Источник — новый `depth + 1` вместо вызова `saturating_add(1)`; условие `depth < usize::MAX` ограничивает арифметику.
- Regular **Check 87**: `kani::internal::exit_contract_clause.assertion.1`, `attempt to subtract with overflow`, SUCCESS, `lib.rs:851:49`. Источник — новый `depth - 1` вместо `saturating_sub(1)`; условие `depth > 0` исключает underflow.

Overflow-инструментация выражений теперь даёт явные assertions. Возвращать saturating method calls или удалять эти проверки ради совпадения старого inventory нельзя. Удалённых ID после сопоставления путей нет; прежние initialization/protocol/root assertions сохранены. Closure pair из raw old-only/new-only соответствует прежним safety checks в неизменном `mem_init.rs:278:17`, а не потере/замене проверки.

## Порядок

Все 227 прежних числовых `Check N` изменились; после удаления двух новых строк **90 из 227** retained rows стоят на другой позиции. Отдельный номер для каждой пары есть в JSON. Номер не является ID свойства: `cbmc_property_renderer.rs:295–296` перечисляет полученный backend vector без сортировки, а `compare.check_single` (`compare.py:109–110`) сравнивает **Counter полных rows**, поэтому одна перестановка не могла вызвать этот отказ. Конкретную причину backend-перестановки из regular/source alone не устанавливаем. Это не доказательство порядка codegen harnesses, isolation или исправления F7.

## Решение для S5

Composition gate остаётся **FAIL**, inventory **не bless-ился**, roots.json/checker/compare/normalization/fixtures не изменены. Не применять T1b allowance к двум новым helper assertions: это isolated upstream source delta, а не добавление checks общего `std::ptr::read` между mixed roots. Передать в S5 portable expected oracle: сохранить own assertion `ordinary_ensures_legal.assertion.1`, intended initialization/protocol checks и verdict, учитывать реальные +2 upstream assertions, не закреплять host paths/source line drift.

Оригинальные export/receipt artifacts, по переданному summary, не загружены. Поэтому здесь проверено соответствие **предоставленного полного regular inventory**, а не независимо восстановленная JSON/receipt identity, actual AST/MIR→GOTO binding или вся composition matrix. Lost-check STOP не требуется по этому сопоставлению. Новые runtime/CI результаты NOT_RUN; F5–F8/S2 не начаты.
