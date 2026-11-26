# REV2 валидность · repin · FIX3 после run 45857466917

Задание для **w11**, та же стадия. Прогон по GO из `0f721d04d2` завершён: job success, `diagnostic_status=INCOMPLETE_OR_UNEXPECTED`. [Артефакты](/root/ch8-artifacts/run-45857466917/ch8-rev2-validity-repin-Linux-X64-45857466917-1/) · [Handoff](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md) · [GO](REV2-VALIDITY-MAIN-REPIN-GO.md)

## Что произошло

- **Фаза 0 — PASS.** Kani `0.68.0 (4caf097)` собран на nightly-2026-11-21, CBMC 6.11.0. Чистый Std merge `7f961eda87` скомпилирован. Пара совместима.
- **Фаза A — 18/18 `MISMATCH`, причина в гейте.** Нативные terminal совпадают с ожиданием во всех 18 слотах (сводка координатора):
  - три `*_invalid_read-on` дают `VERIFICATION:- FAILED` с `Undefined Behavior: Invalid value of type char` на typed read;
  - остальные 15 дают `SUCCESSFUL`.
  Во всех слотах есть 2–4 свойства класса `unsupported_construct` со статусом **`SUCCESS`**, а не `UNREACHABLE`. Например: `core::panicking::panic_nounwind_fmt::runtime.unsupported_construct.1` (foreign `rust_begin_unwind`), `std::panic::Location::caller.unsupported_construct.1` (`caller_location`), `kani::mem::cbmc::same_allocation.unsupported_construct.1`. `verdict.py:239` (`blocking_unsupported = status != 'UNREACHABLE'`) переводит всё это в `MISMATCH`.
- **Фаза B — `NOT_RUN`**, её закрыл гейт A.

## Что сделать

1. **Разобрать семантику.** Почему на этом Kani свойства `unsupported_construct` выходят со статусом `SUCCESS`, а не `UNREACHABLE`? Опирайся на исходники Kani-кандидата `4caf097d84` (codegen unsupported/unimplemented, постобработка reachability-проверок в kani-driver) и на receipts этого прогона. Нужен точный ответ с координатами: какое утверждение генерируется, получает ли оно парную reach-проверку и при каких условиях `SUCCESS` означает «точка недостижима в пределах заданных границ». Отдельно проверь, действуют ли в этих слотах unwinding assertions и не может ли `SUCCESS` маскировать достижимость при отсечке unwind.
2. **Исправить гейт без ослабления.** Если доказано, что `SUCCESS` у `unsupported_construct` при `assert(false)`-форме и успешных unwind checks означает недостижимость, принимай `SUCCESS` и `UNREACHABLE` как недостижимость. Блокирующими остаются `FAILURE`, `UNDETERMINED`, `ERROR` и любой неизвестный статус. Правило сохраняется для фаз A и B. Если доказательства нет, оставь гейт строгим и опиши альтернативу.
3. **Офлайн-переклассификация.** Прогони исправленный verdict на 18 receipts из `run-45857466917` только как данные: без запуска инструментов, с `python3 -I`, из отдельного каталога. Приведи таблицу: слот, expected, terminal, новый verdict. Ожидается 18/18 `MATCHED`, `read_binding` у ON-слотов по правилам пакета. Если какой-то слот остаётся `UNKNOWN` или `MISMATCH` по другой причине, разбери его.
4. **Тесты.** Синтетика на `unsupported_construct`:
   - `SUCCESS` при успешных unwind checks → не блокирует;
   - `FAILURE`, `UNDETERMINED` и неизвестный статус → блокируют;
   - `SUCCESS` при проваленном unwind check → блокирует или `UNKNOWN`, по выводу пункта 1.
   Suite на штатной и свежих шкалах, YAML, `bash -n`, `git diff --check`.
5. **Пересоздать пакет.** Новый control поверх `bf4e1d882a`. Kani-кандидат, Std merge, overlay, bundles, fixture, roster и workflow не менять, если пункт 1 не потребует. Request пересобрать, только если в нём закреплён хэш `verdict.py`. Новый review-trigger с тем же sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Переменная Actions прежняя, `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`. Новое значение укажи в handoff, менять его будет координатор после GO.

Раздел **FIX3** в `REV2-VALIDITY-MAIN-REPIN-HANDOFF.md`: результат прогона, ответ по п. 1 с координатами, дельта, таблица переклассификации, тесты, новые пины. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`, ledger Item 2. Локально не запускать CI, push, cargo, rustc, Kani и CBMC, Actions variables не менять. Коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Перед заморозкой проверь author и committer. Сдай раздел FIX3 и остановись.

## Уточнение по опубликованным receipts

1. **Есть второй блокер после исправления `unsupported_construct`.** У каждого из трёх A-negative ON ровно два нативных `FAILURE` класса `safety_check` с описанием ``Undefined Behavior: Invalid value of type `char` ``. Таблица относится к одному `SOURCE-READ` на слот.

| Слот A ON | Location в `validity_fixture.rs` | Exact property IDs |
| --- | --- | --- |
| `copy_invalid_read` | `41:29` | `copy_invalid_read.safety_check.5`, `copy_invalid_read.safety_check.8` |
| `nonoverlap_invalid_read` | `78:29` | `nonoverlap_invalid_read.safety_check.5`, `nonoverlap_invalid_read.safety_check.8` |
| `write_bytes_invalid_read` | `166:29` | `write_bytes_invalid_read.safety_check.5`, `write_bytes_invalid_read.safety_check.8` |

`verdict.py:207–218,247–253` требует по одному свойству и одному отказу. Сверь оба свойства с проходом `check_values.rs`: `DerefValidity` и проверка типизированного чтения после untyped write могут иметь одну source location. Закрепи ожидаемую группу каждого из этих трёх селекторов для текущего пина по файлу, строке, столбцу, классу, типу и точным ID. При успешной привязке требуй совпадения **всего множества отказов** с группой и сохранения cover записи до чтения. Сдвиг координаты, подмена типа, пропуск одного ID, третий или посторонний отказ дают отказ. Для B сохрани прежнее ожидание до появления собственного привязанного свидетельства. У положительных ON тоже встречаются два `SUCCESS` на одном typed read. `read_binding=OBSERVED` допустим для привязанной группы с полным набором наблюдений, иначе остаётся `UNKNOWN`. В OFF и ON raw-only `read_binding` остаётся `NOT_REQUESTED`.

2. **Проверяй именно происхождение guard.** Помимо трёх примеров сверху, в A ON есть guards для untyped reads `Result<char, CharTryFromError>` в `Result::is_ok` и `from_u32_unchecked::precondition_check`. В `check_values.rs:265–310` такой guard находится на ветке `untyped`. У `same_allocation` вызов `unsupported` тоже условный (`library/kani_core/src/mem.rs:264–273`). `SUCCESS` у `assert(false)` означает, что недостижима ветка с guard, а сама функция может исполняться. Для общего правила сверяй все emit sites класса на пине, включая foreign call, intrinsic и `UnsupportedCheck`. Альтернатива — привязать допуск к установленным guard-семействам. Fallback по словам `unsupported construct` в произвольном description сохраняет строгую проверку. Новый допуск `SUCCESS` требует подтверждённого CBMC argv с включёнными unwinding assertions и отсутствия failed/undecided unwind checks. Во всех 18 receipts профиль `OBSERVED`, есть `--unwind 16` и `--no-self-loops-to-assumptions`, отсутствует `--no-unwinding-assertions`. Среди опубликованных свойств нет unwind records. Отдельный обязательный `unwind.SUCCESS` здесь был бы ложным блокером. Добавь тесты на отсутствующий или несовместимый профиль и guard с неподтверждённой семантикой.

3. **Реплей учитывает ограничение публикации.** У `A-nonoverlap_valid_read-on` пропущено одно свойство из 257. Разность полных `status_counts` и сохранённого инвентаря даёт один `SUCCESS`. В публикации сохранились 31/31 validity properties, 4/4 unsupported guards, обе проверки typed read на `:59` и два требуемых cover. При офлайн-переклассификации используй эти счётчики и сохранённые anchors как данные. Сохрани пометку об усечении. Если сохранённых данных для какого-либо обязательства не хватает, оставь `UNKNOWN`. Прежние receipts и решение ledger остаются историческими записями.

В пункте 5 остаются те же fixtures, selectors, режимы и argv. Если для групп требуется заморозить новые ожидания в request, пересобери его с этой ограниченной дельтой и приложи новые хэши к handoff.
