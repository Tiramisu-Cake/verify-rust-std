# PolymorphicIter: статическая стадия worker15

База g0: `5221d9b3418a963f39c3339c7529c162f01bddfe`.
SEL1: `14bc57fdb99960240c4944845a3d985c8af4dcf7`, parent C2
`8e299aa6243bc5f06a29c51e98aafa9564478220`.
Baseline: `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Runtime source: `70ba5befc617627073738e26cb1466bd4fb76e41` + R3 test overlay.
Статическое чтение pinned Git objects; не compiler patch, не запуск проверки.

## 1. Точная ветка отказа

Все compiler coordinates ниже — **на `14bc57fdb9`**, не текущий HEAD клона.
Префикс `CU` = `kani-compiler/src/kani_middle/transform/check_uninit/`.

| Шаг | Source | Что происходит |
|---|---|---|
| Присваивание результата `Self { alive, data }` | `CU/ptr_uninit/uninit_visitor.rs:548–567` | `visit_statement` сначала обходит rvalue; для destination проверяет `maybe_uninit_storage`. Для struct ответ None, затем `PointeeInfo::from_ty(ty)` возвращает `UnionAsField`, и создаётся `MemoryInitOp::Unsupported` с текстом A1 |
| Ограниченное распознавание storage | `CU/ty_layout.rs:119–138` | `wrapper_inner` проверяет lang item, а `maybe_uninit_storage` снимает максимум один внешний Array/Slice и проверяет непосредственно `MaybeUninit`. Struct и `ManuallyDrop<struct>` сюда не входят |
| Раскладка обычного sized struct | `CU/ty_layout.rs:193–242`, `408–418` | `from_ty` идёт по sized fallback в `data_bytes_for_ty`; struct рекурсивно обходит поля с rustc field offsets |
| Вложенный массив | `CU/ty_layout.rs:281–300` | Array рекурсивно раскладывает element с rustc stride; element здесь `MaybeUninit<usize>` |
| Корень ошибки | `CU/ty_layout.rs:518`, текст `111–114` | `FieldsShape::Union(_) => Err(UnionAsField(ty))`. Здесь `ty = MaybeUninit<usize>`, а не весь struct |
| Instrumentation | `CU/mod.rs:230–232`, `852–859` | Unsupported превращается в unsupported check. Это не обнаруженный uninitialized read и не ошибка `select_unpredictable` |

Runtime coordinates **на `70ba5befc6`**: `library/core/src/slice/sort/shared/smallsort.rs:307`
содержит `for offset in [0, len_div_2]`. Desugaring использует consuming array iterator.
`library/core/src/array/iter.rs:77–81` переводит `[T; N]` в
`[MaybeUninit<T>; N]`, вызывает `InnerSized::new_unchecked`, затем
`ManuallyDrop::new`. `iter.rs:16,25` задаёт alias/поле wrapper.
`library/core/src/array/iter/iter_inner.rs:45,59,95–96` содержит ordinary `alive`,
`data: DATA` и присваивание `Self { alive, data }`.
Именно эту цепочку согласуют source и failed-property summary R3; отдельного
MIR/parser-input binding настоящая стадия не устанавливает.

## 2. Почему #5151 покрыт; какой срез C2

Для прямого `[MaybeUninit<D>; 2]` проверка на `uninit_visitor.rs:558` успешна:
идёт `assign_storage` (`282–357`), а не раскладка всего массива как typed data.
`CU/mod.rs:266–289` разделяет допустимое чтение storage, typed transfer и raw copy:
чтение самого storage не требует всех payload bytes initialized; последующий
доступ как `D` проверяется отдельно. `for_typed_storage` (`ty_layout.rs:151–176`)
использует payload data mask и реальный slot stride, raw storage copy —
`for_storage` (`179–190`). Это сохраняет пустой слот, вместо фиктивного Set(true).

Основной срез — **PR-04, storage and transfer protocol**, commit
`345cedfd67df679e326474385308349d609fc43d` (parent PR-03 `5ca51679e3…`).
Он вводит распознавание storage, assignment/constant masks, typed/raw различие,
парные transfers и conservative nested resets. Зависимости C2 остаются:
PR-01 selected-body/delayed analysis и PR-02 immutable masks; PR-03 layout/raw-eq
предшествует PR-04. Это не утверждение, что изолированная часть PR-04 на 0aac
достаточна. Основание: pinned diff PR-03→PR-04 и
[`PR-04.md`](../../c2-slices/pr-texts/PR-04.md), порядок —
[`INDEX.md`](../../c2-slices/pr-texts/INDEX.md).

SEL1 добавляет select fallback поверх финального C2, но не расширяет storage
на nested struct. Важная вторая граница: `transfers_shadow` (`uninit_visitor.rs:145–155`)
распознаёт только union или указанный flat storage. Nested struct не получает
парного переноса; `reset_nested_call` (`157–179`, вызов `883`) очищает Move source
до вызова и destination на normal return. Copy source сохраняется.
Снять только отказ layout недостаточно для корректного initialized companion.

Уже предоставленный R3 RESULT сообщает для native #5151: baseline обе пары
unsupported (43/44 properties), SEL1 negative — intended uninit UB (141/1),
companion SUCCESS (142/0). Это source-reported CI evidence из
[`RESULT.md`](../r3/run-43779285270/RESULT.md), не новое независимое proof credit.
Empty Drop negative проверяет slot 1, хотя slot 0 записан; отсутствие тела Drop
не даёт права считать неинициализированный `D` корректным значением.

## 3. Минимальное направление исправления — предложение владельцу

Отдельный follow-up issue/PR, связанный с #3300/#5151 и зависящий от PR-04
(практически — от принятого C2), **не расширение уже замороженного семисрезового
пакета**. Предмет: limited sized products с ordinary fields, flat MaybeUninit
storage leaves и прозрачным lang-item `ManuallyDrop`. Существующий byte-shadow
и direct-call protocol сохраняются; решение compiler design остаётся владельцу.

1. Структурно собрать descriptor допустимых полей с rustc offsets/array strides.
   Разделить required typed-data mask ordinary fields и preserve mask storage
   payload. Чтение struct не требует initialized payload пустых MaybeUninit,
   но не должно освобождать `alive`/другие обычные поля от проверок.
2. При aggregate construction перенести shadow каждого storage operand в его
   поле, обычные поля отметить только по проверенным typed values. Copy/Move
   всего struct и direct argument/normal return перенести тем же snapshot/load
   механизмом C2 (`CU/mod.rs:709–829`), применяя составной typed preserve mask.
   Все snapshots — до очистки Move sources; padding не становится initialized.
3. Согласованно расширить admission, `assign_storage`, layout dispatch и
   `transfers_shadow`; снять conservative reset **только для квалифицированного
   нового случая**. `ManuallyDrop` не является событием инициализации. Простое
   unwrap без переноса state на argument/return seam недостаточно.
4. Обычные unions, неизвестные layouts, unsized by-value, indirect/hook calls,
   recursion/stub transfer и другие прежние ограничения оставить за прежними
   gates. Не special-case имя `PolymorphicIter`, не превращать UnionAsField в
   общий пустой/all-true mask и не расширять select domain по совпадению layout.

Главный риск — false SUCCESS: blanket Set(true), потеря пустого слота при
aggregate/return, сохранение padding при typed Move, потеря offsets обычных
полей или приращение фиктивного доверия при `ManuallyDrop`. Возможны и false
positives от оставленного nested reset. Это расширение поддержанного structural
случая, требующее review и controls; дизайн здесь не принят и не реализован.

До будущего допуска нужны как минимум: MRE negative/companion; mixed initialized
slots; empty storage с законными metadata; отдельный read неинициализированного
ordinary field; padded payload и raw-vs-typed copy; ненулевой field offset,
stride/N=0/ZST; Copy source/Move source, self/overlap snapshots; normal return,
unwind/abort без normal load; nested reset вне нового domain; ordinary-union,
unsized/indirect/hook negative controls. Сохранить existing C2 и SEL1 controls.

## 4. MRE и диагностический обход A1

[`MRE/main.rs`](MRE/main.rs) — один файл, local struct, без std.
Две negative/companion пары проверяют struct и внешний `ManuallyDrop`.
Матрица ожидаемых baseline/SEL1 исходов и ограничения — в
[`MRE/README.md`](MRE/README.md). Все четыре harnesses **NOT_RUN**; будущий fix
должен различать intended uninit UB и SUCCESS, не просто менять unsupported.

Без изменения runtime std можно выбрать root, не достигающий general scratch:
direct sort4/sort8/insert/merge для локализации составляющих или существующий
`unstable_network_u64_n18` вместо N32. В runtime `small_sort_network`
(`smallsort.rs:353–412` на `70ba5befc6`) нет данного array iterator:
scratch — `MaybeUninit<[T;32]>` на `369`, две половины обрабатывает loop на
`380–403`, затем merge. Для N18 это два sort9, для N32 — два sort13 + insertion;
это разные roots/объём формулы. N18 в R3 остался NOT_RUN после fail-fast.
Источник уже подготовленных selectors/routes:
[`ROUTE-MAP.md`](../ROUTE-MAP.md), [`std-test-only.patch`](../r3/std-test-only.patch).

На тех же general/stable N32 roots переименование selector или изменение
harness input не убирает обязательный array for-loop. Замена его на while,
stub iterator, проверка копии изменённого helper или отключение uninit checks
не закрывают исходный claim. Другой root может диагностировать отдельный
callee/масштаб, но не доказывает general/stable N32, исходный caller либо всю
A1-кампанию. Network N32 уже пробовали: обход PolyIter не устранил RSS blocker.

## 5. Network N32 ON >13 GB: что известно

Доступен coordinator intake R3, а не paired export/receipt comparison. Ниже
значения из RESULT; новые exports/receipts не получены, raw logs не читались.

| Row | Известное bounded наблюдение |
|---|---|
| general_nocopy N32 | 907 properties, 1 unsupported failure; 194.3 s verify; max RSS 2.82 GiB |
| stable_freeze N32 | 895 properties, тот же 1 failure; 255.8 s verify; max RSS 2.90 GiB |
| network N32 | INCOMPLETE/SIGTERM; symex 141.7 s; 143434 VCC / 59525 после simplification; watchdog group RSS 13579075584 B при threshold 13575032832 B |

Watchdog sample = около 12.65 GiB (13.58 decimal GB); это group measurement,
а не гарантированно тот же individual max-RSS counter, что в первых строках.
13 GB и 13 GiB не взаимозаменяемы. Finished property count general нельзя
сравнивать напрямую с network VCC count; RSS sample не локализует фазу пика.

Source даёт рабочую гипотезу: другой маршрут sort13/comparator/insertion/merge
и uninit instrumentation может создавать больше symex/SSA/shadow операций.
Однако стоимость конкретного компонента, доля ON overhead и причина >13 GB
**UNKNOWN**: нет general VCC/phase counters, размера формулы, распределения
checks и сопоставимой memory series. Сортирующая сеть сама по себе ещё не
доказана причиной. Нет основания объявлять это solver OOM или утечкой памяти.

Bounded следующий запрос/измерения (не разрешение на запуск):

- Сначала получить paired row receipts/exports R3 через разрешённый интерфейс
  с точными row/artifact/file SHA, tool/std/overlay/target/config identities:
  `argv`, unwind/object bounds, solver, property totals/classes, `original_exit`,
  watchdog signal/reason и признаки completeness. Не исполнять argv из evidence.
- Для обеих строк: symex/preprocessing/solver timings, VCC до/после simplification,
  SSA/goto/bitvector-variable/clause counts, если экспортируются; иначе UNKNOWN.
  Запросить bounded histogram checks по функциям/class и небольшие top-K
  contributors, не full verifier output. Размер export сам по себе не RSS model.
- Одинаковая bounded memory series по фазам: process-tree RSS, backend PID RSS,
  cgroup peak/limit и timestamp watchdog; сохранить условия/единицы счётчиков.
- Если receipt comparison недостаточен, отдельно авторизованная диагностическая
  матрица: general/network N18/N32, ON/OFF на тех же pins/bounds; фиксированные
  time/RSS ceilings с reserve и fail-stop, без повышения threshold для PASS.
  OFF — только cost control, не proof. Изолированные sort9/sort13/merge roots
  допускают локализацию роста, но меняют программу и не дают causal attribution
  всей N32 formula простым вычитанием RSS.

Итог стадии: точный source blocker установлен; исправление спроектировано как
ограниченный follow-up; fixture и следующая диагностика подготовлены.
Compile/verification/proof credit: **NOT_RUN / NOT_ESTABLISHED**.
