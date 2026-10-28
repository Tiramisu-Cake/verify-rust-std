# C3b — память и тайм-аут ordinary harnesses

Статус: **в работе; полного допуска по времени ещё нет**. Новое ограничение из
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

| Вариант / commit | Что изменено | Что теряется |
|---|---|---|
| A / `47419c3e4a` | Убраны дублирующие cover; короткий mutation witness | Не домен/не assertions |
| B / `686f4d3336` | N11..12 → N11,N12; unwind35 → 13/14 | Ничего при успешном proof |
| E / `bb7a797166` | Большие covers переведены в controls-аудит | Их повторная проверка default CI |
| D / `f79a516512` | Exact tail и dispatch partitions | Объединённый домен сохранён |
| K / `ac5f818d05` | Kissat в тяжёлых proof families | Не домен/не assertions |

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
Pinned setup устанавливает Kissat4.0.1 на Linux и macOS. В новых измерениях
учитывается отдельный RSS `kissat`, а не только уменьшившийся RSS `cbmc`.

## Все ordinary, разбиения и критерий времени

Локальный source-прогноз: 325 исходных → 387 текущих ordinary. Добавлены
69 имён, заменены семь групповых имён; net +62. Удалённых входных случаев нет:

- N11..12 разбит на две длины со всеми offsets1..N.
- START1..4 / tail START+1..16: 54 точных случая в том же `[u64;17]`.
- Bytes16/17: обе ветви stable/unstable × длины15,16,17, всего12 случаев.
- Дополнительно введён один короткий mutation witness.

[Полное соответствие имён](c3b/renamed-harnesses.tsv),
[все текущие имена](c3b/predicted-ordinary.txt),
[распределение по шести группам](c3b/screen-registry.json).
Прогноз обязательно сверяется с bound remote `kani list`; без этого полного
допуска по всем ordinary нет. Каждый элемент проверяется на GCB jobs1.

Предварительный target — 90с GCB; timeout screen — 120с. После калибровки
по общим harnesses старого macOS CI target может быть снижен. Для коэффициента
k переносимости и вариации1.7 требуется `target × k × 1.7 < 600` с запасом.
Факт полного screen устанавливает [анализатор](c3b/analyze_screens.py),
который проверяет source/build/request SHA, полноту страниц и каждый результат.

## Остаток работы и ограничения

Ожидаются calibration6, matched trace-only6, Kissat pilot и все шесть screen.
Окончательные таблица «до/после», target, риск-список, прогноз RSS/времени
ubuntu/macOS и рекомендация будут заполнены по этим данным.

Прямой запуск итогового autoharness на macOS не разрешён этим лейном;
перенос GCB→macOS останется прогнозом с раскрытыми допущениями. Historical
macOS driver называется `kani`; его отсутствие под `kani-driver` не означает
отсутствие памяти. Исторические ps-пики — sampled RSS, а не kernel VmHWM.
Новые GCB peaks действительно используют `/proc` VmHWM/VmRSS с шагом2с.

Тесты лейна: 52 unittest passed; bash syntax checks passed. Rustfmt проверялся
после изменений proof-кода; обязательный check будет повторён на итоговом HEAD.
