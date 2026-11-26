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
