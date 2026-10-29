# C3b — память и тайм-аут ordinary harnesses

Исход: **недостаточно данных для допуска итогового ordinary-набора**.
Диагностика и варианты реализованы, но требование «все ordinary надёжно
укладываются в macOS 600с при jobs3» не доказано. Набор нельзя рекомендовать
как проверенное исправление autoharness. Новое ограничение из
[c3b/ADDENDUM-C3B.md](c3b/ADDENDUM-C3B.md) имеет приоритет: macOS autoharness
ограничивает каждую ручную гармонику 600 секундами при трёх потоках.
Бюджет C3b: не более $12 / 20 сборок; глобальный CAP_USD=63.96 сохранён.

## Установленные механизмы

Workflow явно передаёт `--harness-timeout 10m --default-unwind 1000 --jobs=3`.
Собственный default autoharness на Kani pin — 60s; workflow переопределяет его.
Один timeout path применяется к manual и auto harnesses. Он включает CBMC,
чтение/разбор stdout и ожидание child, но не предшествующий `instrument_model`.

H2 подтверждается как **зависимость от объёма результатов отдельных гармоник**,
а не как линейная функция их числа. Driver сохраняет `Vec<Property>` каждого
завершённого harness до конца run. Достижимый `cover(cond)` кодируется как
`assert(!cond)`, получает raw FAIL с полной witness trace, а затем превращается
в SATISFIED без удаления trace. Terse меняет печать, не хранение результатов.
Автоматические assertion reachability companions включены по умолчанию.
Они тоже получают raw FAIL traces, но postprocessing переносит только
reach status и удаляет companion properties вместе с traces. Они создают
временную нагрузку разбора; их накопление в финальном Vec не установлено.
Глобальный `--no-assertion-reach-checks` нарушил бы условие о флагах CI.
Во время разбора одновременно существуют исходный JSON и decoded result;
`String::clear()` обнуляет длину, но сохраняет capacity до завершения parser.

Собственный sequential build H3 установил время большого пика:

- Correct u8 N14 начинается на 72с; CBMC наблюдался до 276с.
- Driver достигает 5.034 GiB на 284с, до начала merge N13 на 290с.
- У первой гармоники только 723 проверки и два SATISFIED cover.
- После неё RSS остаётся около 3.090 GiB до конца остальных двух проверок.

Пик относится к одной гармонике и обработке её результата. По RSS нельзя
отдельно вычислить live retained allocations и освобождённые, но оставшиеся
у allocator страницы. Длительность сама по себе не объясняет рост памяти:
долгое SAT-решение может почти не создавать новых данных driver.
Байты CBMC JSON и число TraceItem этим лейном не измеряются; размер terse log
не используется как их замена. Подробности и upstream pin-ссылки:
[c3b/SOURCE-NOTES.md](c3b/SOURCE-NOTES.md).

H1 является дополнительной нагрузкой от параллельных CBMC/solver. В исходном
H6, jobs=3, измеренная RSS-сумма достигла 9.58 GiB. Это не доказывает OOM
в историческом Actions run: shutdown signal без kernel/cgroup evidence
не устанавливает причину остановки.

## Завершённые исходные замеры

Все значения памяти — GiB; время ниже — timed verify со std compilation,
без первоначальной сборки самого Kani. RSS-сумма измерена одновременно;
она не является суммой независимых максимумов и не равна физической RAM.

| Набор | driver | CBMC | RSS-сумма | wall | исход |
|---|---:|---:|---:|---|---|
| L12, jobs1 | 1.14 | 0.77 | 2.22 | 5:37 | 11 SUCCESS, 1 TIMEOUT |
| L60, jobs1 | 1.20 | 1.50 | 2.81 | 39:24 | 39 SUCCESS, 21 TIMEOUT |
| H3, jobs1 | 5.03 | 3.49 | 6.57 | 15:47 | 3 SUCCESS |
| H6, jobs3 | 5.04 | 3.49 | 9.58 | 20:43 | 3 TIMEOUT; INCONSISTENT |
| H6+A, jobs3 | 5.04 | 3.32 | 7.39 | 22:46 | 3 TIMEOUT; INCONSISTENT |
| C3a types4 | 2.16 | 1.43 | 2.41 | 18:37 | 3 SUCCESS, 1 TIMEOUT |

Полные UUID и source/request identities находятся в [c3b/builds.json](c3b/builds.json)
и отдельных summary/peaks:

- L12: `586c0d76-5fcb-454b-9147-7c6c4e6aa0ec`.
- L60: `02bacd6a-52d0-4c9e-ad76-7fe1edb81f4c`.
- H3: `02b3bd09-26e8-401d-84b5-b33c6d55f759`.
- H6: `311f6aa7-0e7c-4e0b-828f-eed3d3b68e56`.
- H6+A: `6196139d-3428-4e11-8c70-39dcde7c25d2`.
- C3a: `2f10637a-a1d4-420f-ab5c-7eae9ecb8d97`, внешний вход координатора.

Внешняя точка координатора `e5ba3173` (12 лёгких, driver1.41 GiB) также
не является matched comparison для типов C3a: четыре types дали2.16 GiB.
Это согласуется с зависимостью от отдельных результатов, а не только счётчика.

L12/L60 оказались не полностью лёгкими; их цензурированные результаты
не подтверждают успешный proof всех выбранных доменов и не являются
линейной калибровкой памяти по числу 12→60. Число свойств тоже недостаточно:
в C3a 739/738 проверок соответствовали 54/350с, а память агрегирована по run.

INCONSISTENT у H6 связан с framing после TIMEOUT без Verification Time.
Эти записи не используются как формальный допуск; память/исходные строки
сохранены. Sequential H3 не имеет этой неоднозначности.

## Реализованные варианты

Изменения library выделены отдельными commits с `[skip ci]`.
Runtime SmallSort и тела контрактов не менялись; флаги/скрипты организаторов
не менялись. [Source audit](c3b/SOURCE-REVIEW.md) не нашёл потерянных assertions
или дыр в объединении входных доменов. Audit исходников не заменяет GCB proof.

| Вариант / commit | Изменение | driver / CBMC / solver GiB; wall | Что теряется |
|---|---|---|---|
| A / `47419c3e4a` | Дедупликация covers и короткий mutation witness | H6: 5.04 / 3.49 → 5.04 / 3.32; 20:43→22:46, три TIMEOUT600 | Не входной домен/не assertions; меньше дублирующих witnesses |
| B / `686f4d3336` | N11..12 → N11,N12; unwind35 → 13/14 | Изолированный matched after не получен: run отменён ради P1 | Ничего при успешном proof |
| E / `bb7a797166` | Большие user covers в controls | Partial6: 1.94 / 2.85 → 1.66 / 2.85; первый proof513.556→435.713с | Ordinary больше не доказывает auxiliary covers |
| D / `f79a516512` | Exact tail и dispatch partitions | D+K screen1: 1.88 / 2.81 / 0.60; 1:00:52; изолированного D нет | Объединённый входной домен сохранён |
| K / `ac5f818d05` | Kissat в тяжёлых proof families | Тот же combined screen; 16 TIMEOUT120, не общее лечение | Не домен/не assertions |
| R / `7cedf2deb9` | 8 joint-route proofs → 16 | General12: 2.53 / 3.01 / 0.50;22:47, 8TIMEOUT120; полного re-test нет | Домен сохранён по source; окончательный proof не получен |
| Opt-in option | 19гармоник под controls; patch не применён | Не измерено | Точные ordinary домены раскрыты в OPTION-OPTIN.md |


A уменьшил время mutating range с 210.404 до 118.029с в двух jobs3 run,
но driver остался 5.04 GiB из-за другого большого результата. Общая wall
не уменьшилась; остальные три тяжёлых проверки достигли 600с. Одного A
недостаточно. Эти single-run различия не являются статистической гарантией.

E сохраняет вычисление predicates, все input choices, assertions и stubs.
При `kani_smallsort_controls` выполняются прежние covers; ordinary CI больше
не устанавливает эти auxiliary existential witnesses. Маленькие assembly,
smoke и отдельный mutation witness остаются ordinary. Это явная смена
coverage policy, а не уменьшение доказуемого входного домена.

Default Kani solver уже CaDiCaL; добавление атрибута cadical бесполезно.
Pinned setup устанавливает Kissat 4.0.1 на Linux и macOS. В новых измерениях
учитывается отдельный RSS `kissat`, а не только уменьшившийся RSS `cbmc`.

## Все ordinary, разбиения и критерий времени

Локальный source-прогноз: **325 исходных → 395 текущих ordinary**. Первые
изменения дали 387, затем восемь joint-route имён заменены 16 именами.
Удалённых входных случаев по source audit нет:

- N11..12 разбит на две длины со всеми offsets1..N.
- START1..4 / tail START+1..16: 54 точных случая в том же `[u64;17]`.
- Bytes16/17: обе ветви stable/unstable × длины15,16,17, всего12 случаев.
- Correct u8 N14/N15 и merge u64 N11/N12/N16, u8 N12/N13/N16:
  general и stable отдельно, с прежними входными массивами и stubs.
- Дополнительно введён один короткий mutation witness.

[Полное соответствие имён](c3b/renamed-harnesses.tsv),
[все текущие имена](c3b/predicted-ordinary.txt),
[распределение по шести группам](c3b/screen-registry.json).
Remote `kani list` подтверждает 327 имён на старом A+B commit `84dfc4b58e`,
а не текущие 395. Оба старых запроса bare list заняли около 49 минут каждый,
из-за чего verify6 оказался PARTIAL по общему лимиту сборки. Лейн исправлен:
list ограничен тем же verify namespace до codegen; этот быстрый путь не измерен.
Текущие 395 — source prediction, не подтверждённый remote inventory.
Три оставшиеся полные группы 72/72/71 сохранены как план, не отправлены.
После R все 35 merge-route моделей требуют повторного измерения, даже при
неизменном имени wrapper. Анализатор исключает их старые результаты.

Предварительный target — 90с GCB; timeout screen — 120с. После калибровки
по общим harnesses старого macOS CI target может быть снижен. Для коэффициента
k переносимости и вариации1.7 требуется `target × k × 1.7 < 600` с запасом.
Факт полного screen устанавливает [анализатор](c3b/analyze_screens.py),
который проверяет source/build/request SHA, полноту страниц и каждый результат.

## Тайм-аут: результаты и незакрытые риски

Screen1 (`45a0dd0c-8f94-49d1-932b-ba5759453cac`, jobs1, Kissat, 65 имён)
завершён: **49 SUCCESS, 16 TIMEOUT120**, из успешных три превысили target90.
Driver 1.88 / CBMC 2.81 / Kissat 0.60 / одновременная RSS-сумма 4.50 GiB,
verify wall 1:00:52. Полный перечень риска и границы актуальности находятся в
[c3b/SCREEN-COVERAGE-NOTES.md](c3b/SCREEN-COVERAGE-NOTES.md).
Это новые риски сверх slowest-15, но TIMEOUT120 GCB сам по себе ещё не доказывает
TIMEOUT600 macOS. Одна joint-route модель заменена R; её старый timeout
не переносится автоматически на два новых доказательства.

Matched A+B/E пары `bc9ee7b8-a3e8-43e4-8aa7-2f91c175b2de` и
`d7c18274-1281-4c8c-95fd-6bc9148102bb`: оба PARTIAL, не полный proof6.
Первый merge general/stable u8 N13 дал SUCCESS 513.556с против435.713с;
driver 1.94→1.66 GiB, CBMC 2.85 в обоих, RSS-сумма 4.02→3.83 GiB.
Merge u64 N16 и старый START1 достигли 600с в обоих. Insertion permutation
N12 имеет UNKNOWN из-за общего cutoff, остальные два — NOT_RUN.
Перенос user covers не устранил тяжёлые проверки и не дал требуемого запаса.

Общий Mac/GCB calibration point для старого u8 N13:
720.369 / 513.556 ≈ **1.40**. Это разные jobs/образы/момент измерения, один point,
а не верхняя граница. Для предварительного проектирования взят k=3.5:
90×3.5×1.7=535.5с, запас64.5с до600. Для наблюдённого k=1.40 было бы214.2с.
Число 3.5 — консервативное допущение, не установленный доверительный предел;
скрининг90с необходим как рабочий критерий, но недостаточен для гарантии.
Недоступны итоговый Mac jobs3 run, полная calibration matrix и повторные run.

Критическая general-проба `031fa8c0-d86b-49e9-a19e-67b4cd420725`:
COMPLETE12, четыре SUCCESS и восемь TIMEOUT120. General u64 N11 —105.343с,
general u8 N16 —124.207с (оба выше90); exact START1 tail16 —53.698с,
stable dispatch bytes17 N17 —28.310с. Driver2.53 / CBMC3.01 / Kissat0.50,
RSS-сумма4.93 GiB; verify wall22:47. Остальные general N12/N13/N16,
correct general u8 N14/N15, merge contract u64 N16 и network u64 N14
достигли лимита. Отдельное разбиение routes не закрыло требование.

Driver peak2.53 GiB на12case, против1.88 на65case screen1. Пик1034с
идёт после CBMC general u8 N16 (912–1030с), до следующего Checking1040с.
User covers здесь отключены, но автоматические reach checks остаются.
Это подтверждает важность отдельных payload; объём JSON не измерен и
точный вклад retained данных/allocator/reach traces не установлен.

Окончательная сводка собранных screen/probe находится в
[c3b/FINAL-MEASUREMENTS.md](c3b/FINAL-MEASUREMENTS.md),
[проверка полноты](c3b/screen-analysis.json),
[все измеренные строки](c3b/ordinary-timings.tsv).
Неизмеренные, устаревшие и timeout строки не получают proof credit.

## Прогноз job и рекомендация

Установленной верхней границы памяти и wall для полного autoharness нет.
Для Ubuntu, 3 потока: исходный H6 уже наблюдал 9.58 GiB RSS-суммы, driver 5.04;
для шести старых covers-treated — 7.39 GiB при неизменном driver 5.04.
У текущего кандидата есть jobs1 screen1 и general12: driver до2.53, один
CBMC до3.01, Kissat до0.60. Условная оценка
`2.53 + 3×(3.01+0.60)` = **13.36 GiB** до
прочих процессов и удерживаемых результатов оставшихся сотен гармоник.
Она предполагает такие же максимумы всех остальных доказательств, что не проверено,
и не является верхней границей RAM. Сумма RSS также учитывает shared pages.
Ubuntu 16GB не получает подтверждённого memory допуска.

Для macOS 7GB та же условная модель 13.36 GiB не помещается. Исторический
Mac sampled driver/whole max — 3.846/3.893 GiB (4032752/4082512KiB),
не 4.08GiB; peak Linux driver 9.842 и whole 10.114GiB. Перенести коэффициент
между ОС нельзя: отличаются concurrency, proof schedule, аллокатор,
сэмплирование, memory compression/swap; их отдельные вклады не измерены.
Показателей нового кандидата на Mac нет. Гарантия 7GB отсутствует.

Screen1 затратил 3652с на 65 гармоник, включая timeouts. Грубое продолжение того
же состава на 395 даёт около 6.2ч jobs1 или 2.1ч при идеальных jobs3,
до остальных ≈1746 manual/auto и setup. Это иллюстрация риска, а не прогноз
успешного run: timeouts цензурированы, группы отличаются, на 3CPU solver
конкурируют. Исходный organizer main 60–70мин не является верхней границей
нашего изменённого набора. Обоснованный конечный wall range не установлен.

Рекомендация: **не переносить весь кандидат как готовый CI fix**. Варианты
A/B/D/R — отдельные reviewable изменения proof; E меняет coverage policy,
K требует продолжения измерений (Kissat не устранил все риски). Контракты,
runtime и organizer workflow не менялись. Для окончания нужны bound inventory
текущего SHA, оставшиеся группы и re-tests после R, лечение каждого оставшегося
risk case, matched jobs1/jobs3 и Mac calibration с повторением.

Последний вариант владельцу — [неприменённый opt-in patch](c3b/OPTION-OPTIN.patch)
и [точное раскрытие 19 гармоник](c3b/OPTION-OPTIN.md). Он удаляет ordinary proof
трёх реально отказавших Mac доменов и их зависимых N16 route obligations;
остальные найденные риски остаются. На текущей ветке эти 19 остаются ordinary.

## Учёт и проверка

Все отправленные UUID/SHA/резервы: [c3b/builds.json](c3b/builds.json).
Расход и финальные статусы фиксируются в FINAL-MEASUREMENTS; лимит $12 / 20,
общий CAP_USD 63.96 не изменялся. Очередные EXPIRED/CANCELLED не являются proof. Повтор screen2 отменён в00:31UTC,
чтобы освободить слот для P1 stable-route/Mac-failure пробы, которая ещё
находилась в очереди. Новых длинных запусков после00:30 нет.
Пилот `3d1251b6-c028-45f6-a6af-1fa11832ca0e` и screen2
`aad9e376-d86f-45d4-9ab1-c6b4d7157778` EXPIRED без артефактов.

Лейн расширен только для диагностики: jobs3/до80names в diagnostic, sampler
VmHWM/RSS2s + timestamps/PID, bounded rows/inventory pagination, cancel и
own-UUID budget. Старые ограничения остальных видов запросов и CAP сохранены.
`k1g watch` со старым открытым bash script получил parse error после изменения
длины этого файла; это ошибка уведомителя, не дополнительный отказ verifier.
Текущий script проходит bash syntax check; результаты прочитаны по UUID.

Локально запускались Python unit tests и rustfmt; rustc/cargo/Kani/CBMC нет.
Final validation и SHA записаны в FINAL-MEASUREMENTS. Все коммиты `[skip ci]`,
push только experiment branch. Исход «недостаточно данных» сохраняется даже
при успешных последних критических probes: полного ordinary допуска они
не устанавливают.
