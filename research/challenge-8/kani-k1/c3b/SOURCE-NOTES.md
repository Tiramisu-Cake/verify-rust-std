# Источники C3b и границы интерпретации

Kani pin: `9461e07af7ec929f050aa4192f29363c9be07779`; CBMC: `6.11.0`.
Читались только upstream-исходники, без кода запрещённых PR.

## Удержание результатов

В `kani-driver/src/cbmc_output_parser.rs` структура `Property` содержит
`trace: Option<Vec<TraceItem>>`; `ParserItem::Result` содержит `Vec<Property>`.
`Parser::clear_input` вызывает `String::clear()`: длина обнуляется, capacity остаётся
до окончания чтения CBMC. Во время serde исходный JSON и разобранный item сосуществуют.
`process_cbmc_output` сохраняет обработанные items; `extract_results` передаёт их по ownership.
`call_cbmc::VerificationResult.results` принимает весь вектор свойств.
`harness_runner::run_until_abort` собирает результаты завершённых гармоник в общий `Vec`;
`check_all_harnesses` возвращает его в `main::verify_project` для итоговых операций.
Печать результата отдельной гармоники не освобождает этот результат.

`terse` управляет rendering, а не временем жизни `Property` и `trace`.
`cbmc_property_renderer::update_results_of_cover_checks` документирует кодировку
`cover(cond)` как `assert(!cond)` и меняет raw `Failure` на `Satisfied` без удаления `trace`.
Kani запускает CBMC с `--json-ui`. В CBMC non-plain UI включает trace, если не задан
собственный CLI `--cover`; Kani covers являются assertions и этот CLI не используют.
CBMC `output_properties_with_traces` записывает trace для raw `FAIL`.
Следовательно, достижимые covers сохраняют witness traces даже в успешной гармонике.
Многогигабайтность конкретного результата устанавливается только замером.

Ссылки даны без якорей строк: координаты HTML-экстрактора не являются строками Rust/C++.

- [Parser](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/cbmc_output_parser.rs)
- [CBMC invocation/result](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/call_cbmc.rs)
- [Cover postprocessing](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/cbmc_property_renderer.rs)
- [Runner](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/harness_runner.rs)
- [Driver](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/main.rs)
- [CBMC trace defaults](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/cbmc/cbmc_parse_options.cpp)
- [CBMC JSON serializer](https://github.com/diffblue/cbmc/blob/cbmc-6.11.0/src/goto-checker/report_util.cpp)
- [Pinned dependencies](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-dependencies)

## Параллельность и autoharness

`VerificationArgs.jobs` имеет тип `Option<Option<usize>>`: без `--jobs` обычный verify
последователен, `-j` выбирает число потоков Rayon по умолчанию, `--jobs=N` задаёт N.
`apply_autoharness_parallel_defaults` выбирает terse и параллельность по умолчанию для
обычного autoharness. Явный regular/old может менять default; в этой работе флаги CI
не меняются. `scripts/run-kani.sh::run_verification_subset` использует `-j` либо
`--jobs=$KANI_JOBS`; ветка autoharness напрямую вызывает Kani autoharness.

`autoharness::add_auto_harness_args` передаёт include/exclude-pattern компилятору как
фильтры генерации autoharness. Они не отбирают ручные proof harnesses.
`verify_project` получает общий `project.get_all_harnesses()`, применяет обычный
`determine_targets` и вызывает общий runner. Поэтому ordinary SmallSort остаются в
одном процессе вместе с другими ручными и автоматически созданными гармониками.

- [Arguments/defaults](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/args/mod.rs)
- [Autoharness](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-driver/src/autoharness/mod.rs)

## Linux/macOS и исторические входы

`49f7e73b` final-CI workflow явно добавлял Linux `KANI_JOBS=2` перед запуском,
хотя request и summary содержат `unset (-j)`. На macOS оставался `-j`.
Тот же workflow собирал `ps rss=,comm=` раз в 5 секунд: исторические peaks являются
максимумами наблюдённого RSS, несмотря на общую подпись summary «kernel VmHWM».
При jobs=1 `Checking harness` печатается после instrumentation, до `run_cbmc`;
наблюдения sampler имеют погрешность опроса, но позволяют связать PID с гармоникой.
Новый GCB sampler действительно читает `/proc/.../status` VmHWM/VmRSS раз в 2 секунды.

На macOS процесс driver называется `kani`: его отсутствие под именем `kani-driver`
не означает отсутствие памяти driver. Для p2 это 4,032,752 KiB = 3.846 GiB;
whole-run max RSS 4,082,512 KiB = 3.893 GiB, а не 4.08 GiB.
Linux p2: driver 10,319,864 KiB = 9.842 GiB; whole-run 10,605,204 KiB = 10.114 GiB.
Сумма RSS не равна физической занятой RAM: есть общие страницы, а на macOS ещё
компрессия/своп. Историческая p2 имела 280 SmallSort, p4 — 75; это не точная
инвентаризация нынешних 325 ordinary после подготовки подачи.

Kani явно задаёт Linux/glibc `GLIBC_TUNABLES=glibc.malloc.hugetlb=1`, если переменная
не задана. Это отличие платформ, но исходники не устанавливают его численный эффект.
Время жизни результатов одинаково; разницу RSS нельзя полностью приписывать jobs,
буферизации печати или THP без дополнительного опыта на macOS.

Shutdown signal из Actions не доказывает OOM: нет kernel/cgroup OOM evidence.
Механизмы H1/H2 и измеренная нагрузка позволяют оценить риск, а не установить причину
исторического выключения раннера.

## Дополнительный вход C3a от координатора

Получены через `k1g.sh summary/peaks` build
`2f10637a-a1d4-420f-ab5c-7eae9ecb8d97`, head `8003d40a`, jobs=1:
4 гармоники, 3 SUCCESS, одна TIMEOUT 600 с; driver 2.16 GiB, CBMC 1.43 GiB,
максимальная наблюдённая RSS-сумма 2.41 GiB, whole verify wall 18:37.15.
Завершённые гармоники имеют 573/739/738 проверок и 14/14/18 достигнутых covers;
время 40.576/53.582/349.691 с. Таким образом, число проверок само по себе тоже
не заменяет длину и содержимое cover-trace: 738 и 739 проверок не означают
одинаковую длину исполнения. По этим агрегатам нельзя приписать пик именно
TIMEOUT-гармонике: нет времени пика и RSS-ряда. `COMPLETE` означает законченный
прогон, но gate=False и TIMEOUT не являются успешным доказательством четвёртой.

Сравнение с сообщёнными координатором 12 лёгкими гармониками `e5ba3173`
(driver 1.41 GiB) отвергает простую модель «RSS зависит только от числа гармоник».
Полного UUID этого второго build нет в задании; его цифра остаётся внешним входом.

Рабочая модель H2: сохранённые Property/trace завершённых гармоник плюс временный
JSON/serde/parser state текущих гармоник и память allocator. Длительность сама
по себе не является причиной роста driver: долгое SAT-решение может почти
не выдавать новых данных. Проверяются число свойств/достигнутых covers, изменения
при удалении только дублирующих witnesses и время роста driver относительно
последовательных гармоник. Байтовый объём CBMC JSON в этом лейне не измеряется;
terse kani.log не является полным CBMC JSON и его длина не используется как proxy.
