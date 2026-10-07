## Текущий результат STOCK-26.10-BASELINE — 2026-10-08

Владелец отдельно возобновил stock26.10 phase с новым бюджетом1800s.
[Отчёт / новая карта переноса](STOCK-26.10-BASELINE.md): proofa0cfd30e,
run37694000195, stock chain PASS на независимых u32/raw/unwind controls;
exact generic forget INCONCLUSIVE на dead-code gate, физический ключ UNKNOWN.
Фаза CLOSED,99/1800used(1701remaining), old5306/5400(94) untouched/S7c UNACCEPTED.
Ни один semantic patch не переносился; следующие scoped diagnosis/transfer gates
требуют отдельного решения. Исторические ограничения/оценки ниже сохранены.

# Оценка переноса профиля VeriFast на 26.10

Дата оценки: 2026-10-08. Это исходниковое сравнение для будущего решения о
переносе. Сборки и проверки не запускались; доказательные результаты
26.09 остаются привязаны к своим SHA и не переносятся на 26.10. На закрытии
S7c учтено 5306/5400 hosted job seconds, осталось 94; эта оценка не добавляет
job seconds. Профиль S7c пока не принят, запусков на 26.10 нет.

## Сравниваемые версии и граница

| Компонент | Закреплённая версия | Кандидат |
|---|---|---|
| Наш fork std/compiler | `dd2bbad51eb50fdf9730e14802dcaf8a9290092a` | upstream `model-checking/verify-rust-std` `cd371e035c7e573760c43bf934d53e8118ee3e7d` |
| VeriFast source | `809de4596839b739dd999f9e462242c835e3af46` (26.09) | `f76012fb518703b1d98e243ac4f487f16877cfcb` (tag 26.10) |

Upstream PR [#687](https://github.com/model-checking/verify-rust-std/pull/687)
обновил Rust subtree до nightly-2026-09-25. В рассматриваемом upstream состоянии
`rust-toolchain.toml` действительно указывает
`nightly-2026-09-25`; наш закреплённый commit указывает `nightly-2026-02-05`.
Для повторяемости важны полные SHA, а не только названия PR или nightly.

26.10 содержит новые schema, rustc exporter, OCaml decoder/translator и
refinement checker. Поэтому это смена всей границы MIR, а не замена одного
бинарного файла. Upstream verify-rust-std [PR #714](https://github.com/model-checking/verify-rust-std/pull/714)
переключил tool setup на VeriFast 26.10 для nightly-2026-09-25; merge commit —
`a4e1cd0c21238ecadfce813c29174e42d5b5797d`. Кандидат VeriFast закреплён точным
commit `f76012fb518703b1d98e243ac4f487f16877cfcb` и tag `26.10`. Для
повторяемости важны source SHA, release archive и зависимости.

## Что уже есть upstream и что остаётся локальным

Upstream перенёс совместимость с новым rustc: его exporter кодирует новые
формы MIR/ty и clauses, схема и decoder согласованы, а translator обновлён под
новые данные. В частности, upstream умеет представить `!`, const generic
arguments, closures, новые MIR assert payloads и rustc clauses. Это покрывает
часть общей compiler/frontend работы и может устранить старые ошибки подготовки
на конкретных новых MIR формах; это не доказывает прохождение наших fixtures.

Ни узкая логика S6v4, ни S7c CFG ремонт не включены в VeriFast upstream:

| Локальное изменение | Вывод сравнения |
|---|---|
| `verifast-select-pointer-drop.patch` (активный кумулятивный профиль S6v4), SHA-256 `c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1` | Два файла: `bin/rust/std/lib.rsspec` и translator. Содержит четыре source-certified families: `MaybeUninit::new`, `as_mut_ptr`, typed `select_unpredictable` и raw-pointer `drop_in_place`; добавляет `MaybeUninit_pointer_own`/checked lemmas и typed MIR/source shape gates. Эти exact rules upstream не обнаружены. Полный patch не применяется к 26.10 из-за translator context drift; каждую family нужно заново обосновать по обновлённому source/MIR, затем адаптировать и тестировать отдельно. |
| `verifast-manuallydrop-new-cfg.patch` (эксперимент S7c), SHA-256 `89b0d80bd1e6382a9bf5be2f1ed208bae6aac5e907a21dd782c4c22307578da7` | Не покрыта upstream. В 26.10 сохранились `FnCallResult` для `ManuallyDrop::new`, identity expression, построение обычного target перехода и итог `targets @ unwind_targets`; `find_blocks` продолжает обходить inventory successors. Patch не применяется напрямую из-за перестройки функции. Повторить AST/physical-loc диагноз и вручную адаптировать узкую successor правку. |
| Временный `verifast-dead-code-loc-trace.patch` | Диагностика, а не профильный semantic patch. Для решения о переносе сначала повторить её на 26.10, затем убрать из приёмочной сборки. |

Локальный S6v4 pointer-drop rule остаётся доверенной точной специализацией, а не
общей семантикой Rust `Drop`. Новая версия `ManuallyDrop` поменяла представление
и runtime тела, поэтому прежний source certificate намеренно должен fail
closed. Нельзя просто обновить закреплённые хеши без нового source/MIR
обоснования. Условия actual-call linkage, ownership guard, `assume_init`, модель
памяти и actual `forget` по-прежнему за пределами S7c и оценки переноса.

## Изменения, затрагивающие наши проверки

| Слой | Изменения между pins | Последствие для Challenge 8 |
|---|---|---|
| Rust compiler и std | #687 меняет nightly и сам std. В `smallsort.rs` меняются marker attribute и формы построения slice references. `ManuallyDrop<T>` переходит от `MaybeDangling<T>` к прямому полю `T`, получает сравнимые/хешируемые derives и переписывает `new`, `into_inner`, `take` и `drop`. `MaybeUninit::assume_init` меняет raw read на `transmute_neo`. | Имена, MIR граф, drop glue и сертифицируемые тела изменились. Исходные адаптеры, source identity pins и spec-to-source аргументы нужно пересмотреть на новых файлах. Особенно нельзя переносить старые предпосылки о `ManuallyDrop`/`MaybeDangling` или считать `assume_init` эквивалентным доказательством. |
| Exporter и wire schema | `vf_mir.capnp` меняет представление clauses, aliases, constants, aggregates и assert; Rust exporter обновляет rustc API, кодирует clauses вместо predicates, передаёт данные Assert и корректирует Box projections. | Двоичный MIR и AST могут измениться даже при одинаковом Rust fixture. Экспортёр, schema, decoder и translator должны быть из одного pin. Сравнить normal и readonly export, полные MIR, block ids, target/unwind данные и экспортируемые spans. |
| Translator | Переход на clauses, новые const/alias варианты и closures, тип `!`, несколько изменений type/projection/call/aggregate lowering. При этом текущий 26.10 translator всё ещё добавляет unwind successors после `ManuallyDrop::new` identity lowering. | Старые патчи применяются к иному коду; повторно проверить signatures, terminators и instruction-to-AST mapping. Реализовать только локальную successor поправку после диагностики, сохраняя MIR export и общий cleanup с реальным предшественником. |
| Refinement checker | Изменились сравнение clauses и проверка assert terminators. В реализации нового assert refinement следует только normal target; комментарий оставляет unwind path как TODO. | Успешная refinement сама по себе не закрывает unwind proof. Отдельно требовать execution/проверку unwind в полном VeriFast AST и не считать обновлённую refinement проверку заменой verifier gate. |
| `bin/rust/std/lib.rsspec` | В diff добавлены/перемещены spec для `Alignment`, `NonNull::into`, `slice::from_raw_parts_mut` и UTF-8/slice методов; изменена конверсия const `N` для `MaybeUninit` массива. S6v4 `MaybeUninit_pointer_own` и pointer-drop lemma отсутствуют. | Зафиксировать полный effective spec hash и аудитировать каждое пересечение по функциям, достижимым из fixtures. Старые доказательства для неизменённых предикатов не означают, что новые исходники/спеки эквивалентны. |

Read-only preprocessor отдельным VeriFast patch не меняется: текущий forget
harness сначала запускает exporter с `--preprocess-readonly`, затем normal export,
decode обоих MIR и refinement. PR #714 меняет используемую версию VeriFast setup;
поэтому оба exporter режима и их source/hash invariants нужно проверить вновь.

Наблюдение о CFG подтверждено статическим чтением версии 26.10: lowering
ManuallyDrop всё ещё возвращает `FnCallResult arg`; общий call builder при
обычном `Goto` формирует присваивание и normal переход, а возвращаемый список
targets объединяет normal и unwind targets. `find_blocks` затем использует
successor inventory. Это делает прежнюю гипотезу актуальной, но не заменяет
повторного hosted воспроизведения: компилятор и exporter теперь строят другой
MIR. Исходники можно сверить в [26.10 translator: identity lowering](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L2593),
[call successors](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L2690)
и [block traversal](https://github.com/verifast/verifast/blob/f76012fb518703b1d98e243ac4f487f16877cfcb/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L3701).

## Архивные исследовательские патчи

Текущий S6v4 runner применяет только один кумулятивный файл
`verifast-select-pointer-drop.patch`; исторические patch-файлы не добавляются к
нему автоматически и не являются активной цепочкой. Статический `git apply
--check` к чистому 26.10 checkout ниже проверяет лишь совместимость текстового
контекста. «Покрыт» означает найденную в upstream эквивалентную реализацию
того же локального изменения; успешное применение само по себе покрытие не
доказывает.

| Архивный delta | Результат сравнения с 26.10 | Статус для будущего использования |
|---|---|---|
| `verifast-tuple-own.patch` | Patch применим (`rust_parser.ml`), но специальная генерация `std_tuple_2_` own predicate в source не найдена. | Не покрыт; нужен только если возобновляется tuple ownership ветка. |
| `verifast-fnmut-hrtb.patch` | Patch не применяется после переработки translator. 26.10 переводит predicates в clauses, но регистрация function projection по-прежнему ограничена `bound_regions = []`; HRTB equality из патча не обнаружена. | Не считать покрытым; подтвердить актуальность на минимальном callback fixture до переноса. |
| `verifast-end-lft-binding.patch` | Patch затрагивает translator и `verifast.ml` kernel и не применяется. `#strict_lft_binding_scope`/CFG ingress validation в 26.10 не обнаружены. | Не покрыт; отдельное доверительное решение, не активен в S6v4/S7c. |
| `verifast-address-taken.patch` | Patch применим, но upstream ветка `MergeFractionsStmt` всё ещё вызывает `ass_mark_addr_taken` без `cont locals`. | Не покрыт; только для архивного address-taken сценария. |
| `verifast-manually-drop-ref.patch` | Patch применим, но special case shared reference к `ManuallyDrop<T>` в translator не найден. | Не покрыт; только для архивного borrow сценария. |
| `verifast-local-drop-call.patch` | Patch не применяется; отдельный hook same-unit actual `Drop` call не найден. | Не покрыт; только для архивного Drop caller сценария. |
| `verifast-local-decls-first.patch` | Patch не применяется. Порядок в 26.10 по-прежнему `projection_clause_stmts @ vf_local_decls @ vf_bblocks`. | Не покрыт; нужен только при возврате соответствующего frontend ordering failure. |
| `verifast-projection-name.patch` | Сам patch не применяется из-за перемещённого hunk, но эквивалентная `canonicalize_item_name` уже стоит при переводе projection clause trait name. | Покрыт статически в `translate_projection_clause` (строки4870–4875); отдельный хунк не переносить. |
| `verifast-rust-fieldless-layout.patch` | Patch не применяется к изменённой schema. В 26.10 не найдены `RustLayoutInfo`/`rustLayoutInfo` metadata или соответствующая layout rule. | Не покрыт; изолированный layout профиль, не текущая SmallSort цепочка. |

Старые отдельные `maybeuninit-new-pointer`, `maybeuninit-pointer-own`,
`select-pointer` и `select-pointer-intrinsics` patches — исторические версии
частей кумулятивного S6v4 файла; не применять их поверх S6v4. Вся активная
семантическая поверхность остаётся двумя перечисленными файлами для S6v4 и
одной translator-only successor правкой S7c. Ни одна из них не проверялась на
26.10.

## Минимальный план решения о переносе

Сначала создать отдельный экспериментальный pin/profile 26.10, не переименовывая
и не переписывая архивные 26.09 результаты. До любого semantic patch сохранить
source/tool/spec/exporter/schema/refiner SHA, команду compiler, effective
patch-chain и hashes сырых input/output артефактов.

1. **Stock baseline:** на неизменённом 26.10 прогнать заведомо независимые от
   новых S6 predicates базовые bodies (`u32_sync`, `u32_share_mono`) и тот же
   автономный `checked_forget_generic` для CFG диагностики. Не запускать в этой
   группе constructor/as-mut/intrinsic/pointer-drop fixtures, требующие
   `MaybeUninit_pointer_own` или `pointer_drop_glue_identity`. Зафиксировать
   отдельно setup/build, extraction, export/decode, refinement и VF результат.
   Ошибки сборки/helper preparation не являются intended proof negatives.
2. **CFG причинность:** проверить, воспроизводит ли тот же автономный
   исходник/контракт на чистом кандидате dead-code отказ; новый compiler/exporter
   могли изменить CFG. Если отказ есть, запустить физическую trace для
   регистрации/исполнения/остатка loc; связать остаток с конкретным AST
   statement. При другом остатке сначала объяснить фактическую причину; только
   при подтверждении той же CFG гипотезы на отдельном candidate overlay изменить successor
   inventory существующего `ManuallyDrop::new` identity lowering для normal
   target, сохранив экспортированный MIR и обязательный dead-code gate. Требовать
   VF exit 0, исполнение тела, return/leak и dead-code pass.
3. **Небольшой CFG набор:** обычный потенциально паникующий вызов с достижимым
   unwind; общий cleanup с действительным вторым предшественником; ложное
   normal post; ложное unwind post; непустое тело с противоречивым pre. Первые
   два должны доказать, что настоящие cleanup edges остаются живыми; последние
   три должны отказать на ожидаемых постусловиях/обязательствах, а не при
   frontend или неподдержанной операции.
4. **S6 fixtures после отдельной адаптации:** actual-source constructor,
   `as_mut_ptr`, `select_unpredictable`, pointer drop и `MaybeUninit` adapter
   запускать на candidate с соответствующим адаптированным S6 overlay. До него
   отсутствие custom helper predicate/rule классифицировать как profile setup,
   не как доказательный negative. Проверить certificates против нового source,
   затем пройти позитивные/негативные admission mutations по типам, вызовам,
   body, contracts и MIR. Проверить normal и readonly preprocessing/export,
   decode, refinement, source integrity и полные tool/spec/profile hashes.
5. **Регрессии:** существующие constructor, as_mut_ptr, intrinsics, pointer-drop
   matrices и все необходимые baseline controls на том же новом профиле. Сверить
   количество обязательств и предназначенные failure stage/predicate/location;
   не считать export, timeout, unsupported op или admission setup за intended
   proof negative.

Решение о смене профиля возможно только после нового исходного card, аудита
изменений rustc/exporter/schema/translator/spec, прохождения этих ворот на
GitHub-hosted runner и отдельного review доверенной S6v4 семантики на изменённом
std. До этого корректный статус — «оценка переноса готова; профиль 26.10 не
принимался и не проверялся».

## Источники

- [verify-rust-std PR #687](https://github.com/model-checking/verify-rust-std/pull/687), merge/update nightly-2026-09-25.
- [verify-rust-std PR #714](https://github.com/model-checking/verify-rust-std/pull/714), selects VeriFast 26.10 for nightly-2026-09-25; merge commit `a4e1cd0c21238ecadfce813c29174e42d5b5797d`.
- [VeriFast 26.10 source commit](https://github.com/verifast/verifast/commit/f76012fb518703b1d98e243ac4f487f16877cfcb).
- Сравнение `809de459…` → `f76012fb…` в локальном checkout; сравнение fork `dd2bbad…` → upstream `cd371e03…`. Исходники только читались, исполняемые проверки не запускались.
