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

## Приоритет 1: тайм-аут macOS и solver

Локальный `.github/workflows/kani.yml` autoharness явно передаёт
`--harness-timeout 10m --default-unwind 1000 --jobs=3 --output-format=terse`.
На pin Kani собственный `autoharness::AUTOHARNESS_TIMEOUT` равен `60s`, но
`KaniSession::add_default_bounds` применяет его только при отсутствии timeout CLI.
Таким образом, фактические 600 секунд у организаторов задаёт workflow.
`run_cbmc_piped` оборачивает чтение/разбор stdout CBMC и ожидание child в
`tokio::time::timeout`; `instrument_model` выполняется перед этим. Путь один для
manual и auto harnesses, что объясняет три macOS отказа из дополнения.

`call_cbmc::DEFAULT_SOLVER` — CaDiCaL. Приоритет: CLI > harness attribute > default.
`handle_solver_args`: Cadical → `--sat-solver cadical`, Kissat → внешний
`--external-sat-solver kissat`, Minisat → отсутствие solver-флага CBMC.
Следовательно, добавлять `#[kani::solver(cadical)]` к default бесполезно.

Kissat штатно устанавливается pinned Kani setup на обеих платформах:
`kani-dependencies` задаёт `KISSAT_VERSION=4.0.1`, общий installer собирает
`rel-4.0.1` и ставит `/usr/local/bin/kissat`. Оба platform `install_deps.sh`
вызывают его; локальный `run-kani.sh::build_kani` проверяет pinned версию и
при необходимости запускает setup. Workflow/flags менять не требуется.
Память внешнего процесса `kissat` должна учитываться отдельно от `cbmc`;
уменьшение только RSS процесса `cbmc` не считается уменьшением суммарной памяти.

- [Kissat installer](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/scripts/setup/install_kissat.sh)
- [Linux setup](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/scripts/setup/ubuntu/install_deps.sh)
- [macOS setup](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/scripts/setup/macos/install_deps.sh)

## Временная привязка H2, собственный sequential build

`02b3bd09-26e8-401d-84b5-b33c6d55f759`, всего три SUCCESS, jobs=1:

- correct u8 N14: Checking на 72с, Verification Time 213.544с; CBMC PID9206
  наблюдался 72–276с (пик 2,237,412 KiB), driver VmHWM 5,278,436 KiB на 284с.
- Следующая merge u64 N13 начинается только на 290с; её CBMC 290–764с,
  пик 2,228,512 KiB; время проверки 476.776с.
- Mutating insertion N11..12: Checking 768с, CBMC 768–946с, пик 3,661,528 KiB,
  время 180.034с.

Driver RSS до 210с ≈6.6 MiB, на 240с ≈668 MiB, на 270с ≈1.410 GiB;
на 300с уже 3.090 GiB и остаётся примерно таким до конца. Пик 5.034 GiB
на 284с относится к чтению/обработке результата ПЕРВОЙ гармоники (723 проверки,
два SATISFIED cover); затем остаётся большой resident footprint. Это точнее
модели «линейно от числа»: одна гармоника даёт большой transient peak и
retained/allocator footprint. По RSS нельзя разделить live allocations и
не возвращённые allocator-ом страницы, но время роста установлено sampler-ом.

Собственные light12/light60 диагностические наборы оказались не полностью
быстрыми: соответственно 1 и 21 TIMEOUT при отсечке 60с. У 60 — 39 SUCCESS,
пик driver1.20 GiB; у12 — 11 SUCCESS, peak1.14 GiB. Поэтому они не являются
линейной калибровкой по числу 12→60; их цензурированные результаты сохранены
и не засчитываются как успешное доказательство всех выбранных доменов.
