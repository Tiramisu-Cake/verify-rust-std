# C3c — autoharness, парные пробы и риск macOS

Итог: цель ordinary≤300с на macOS не принята. Полный GCB job имеет статус FAILURE / PARTIAL;
точные наблюдения и ограничения приведены ниже. Приёмка требует нового П-6. Окно 01:08–07:08 UTC, 2026-10-29; предел $10 / 8 Cloud Builds,
агент `k1-network`; глобальный `CAP_USD=63.96` не меняется. Actions/CircleCI не запускались.

## Кандидат и домены

Измеренный library-кандидат — `fd854ca7545df59b5307b629155ca61dc3d74d0f`, с C3a `e9655515`:
`7919dbbed3` включает types/smoke/registration, `9d019577a8` исправляет review C3b и возвращает
CaDiCaL, `fd854ca754` добавляет разбиения START5/6 и верхних safety routes. Это отдельные library-коммиты
с `[skip ci]`. Временные baseline snapshots (`baa795c5cb`, `ae777deb96`) и восстановления
(`4a8fd69ea5`, `6274153c14`) нужны только для парных измерений в экспериментальной ветке; ветка подачи не изменялась. Совокупный переносимый
[diff против e9655515](c3c/candidate-library.diff) содержит только `verify.rs`, correct, merge, network.
Коммиты C3c предполагают library-изменения C3b на `96ed6f61`; при переносе на e9655515
нужен combined diff целиком, либо соответствующие library-коммиты обоих этапов.
C3a types и smoke совпадают с e9655515. Runtime SmallSort, requires/ensures и organizer workflow/scripts
не изменялись. Proof-гармоники в opt-in не переносились.

| Старый домен | Итоговые ordinary-гармоники / сохранённое объединение |
|---|---|
| mutating insertion Cell N11..12, offsets1..N | N11 и N12 отдельно, все offsets; unwind13/14, без отключения unwinding assertions |
| u64 tail START1..6, START < tail <17, allocation17 | 75 exact-tail случаев: 15+14+13+12+11+10, unwind25; const assert защищает литералы |
| bytes16/17 dispatch N15/16/17, stable/unstable | 12 случаев = 2 типа × 3 длины × 2 маршрута, прежние bodies/stub/unwind65 |
| correct u8 N14/N15, stable=false/true | 2 старые модели → 4, те же full-width массивы, probe, stubs и unwind50 |
| merge general/stable: u64 N11/12/16, u8 N12/13/16 | 6 старых моделей → 12, те же assertions/stub/unwind34 |
| upper safety N31/N32, route u8=0/1/2..255 | 2 старые модели → 6: direct general u64, non-Copy u64, stable u64; прежние bodies/unwind34 |
| Остальные correct/merge/network | Входы и assertions сохранены; E переносит auxiliary covers в controls, предикаты ordinary вычисляются |

Полная [карта семейств](c3c/analysis-domain-map.tsv), [соответствие выбранных доменов](c3c/paired-domain-map.json)
и [source audit](c3c/source-audit.json) отделяют проверку исходников от выполнения Kani. Source prediction
итогового ordinary-набора — 421; приёмка inventory требует удалённого `kani list` того же SHA.

Все обязательные замечания REVIEW-C3B исправлены: три dispatch reachability сохраняют настоящий
`kani::cover(true)` после вызова, measurement не требует covers от ordinary, route covers проверяют
только выбранную stable/general ветвь, exact-tail literals проверяются константным assertion.

Kissat снят во всех изменённых семействах. C3b имел combined D/K/R screen и тайм-ауты, но не изолированный
измеренный выигрыш K; оставлять K как установленное лечение нет оснований. Explicit CaDiCaL совпадает
с default solver baseline pin. Это решение по имеющимся данным, а не утверждение о худшем solver.

E меняет coverage policy: ordinary больше не устанавливает перенесённые existential witnesses.
[Baseline call-site manifest](c3c/cover-migration-from-baseline.json) перечисляет исходные covers и их
сопоставление; [текущие proof_cover!](c3c/moved-covers.json) содержит точные source coordinates и вызовы.
Это source sites, включая macro/control definitions, не число instantiated ordinary properties.
Малые assembly/smoke, mutation witness и три исправленных dispatch witnesses остаются ordinary.
Аудит opt-in на том же library-кандидате — отдельный результат ниже; он не заменяет ordinary proof.

Финальный library patch после аудита: `e45cfc72508bf3b86df0c9f5ee5de0a533446e29`. В `e45cfc7250` исправлена генерация covers:
shared helper больше не содержит двух cover statements; nondeterministic wrapper сохраняет два
предиката stable/!stable, fixed-route wrapper выдаёт один completion cover. Это сохраняет прежние
входы, assertions, stubs и unwind; меняется controls-проверка, ordinary macro остаётся no-op.
[Статическая проверка](c3c/post-audit-source-check.json) и rustfmt PASS; **CI этой редакции не было**
из-за8/8 builds. Все измерения и remote inventory ниже относятся к fd854ca754, не к новому SHA.
[Diff позднего исправления](c3c/post-audit-cover-fix.diff); переносимый combined diff обновлён.
[Manifest измеренного кандидата](c3c/moved-covers-measured.json) содержит100 sites, финальный manifest —102.

## Лейн и проверки

Лейн `249a2791b1` + `d3d6e6c17f` добавляет kind `autoharness`, standard4, empty harness list и whole-job
work budget270 минут, включая полный std inventory. Шаг `Run Kani Verification` извлекается целиком из job `kani_autoharness`
`.github/workflows/kani.yml` проверяемого checkout: includes/excludes, timeout10m, unwind1000, jobs3,
terse, tee и gzip сохранены [дословно](c3c/autoharness-step.sh). Shell `bash -e -o pipefail` сохраняет
ошибку Kani через tee и не маскирует её успешным gzip. После ремонта inventory (`340cad71d3`) build timeout300 минут, резерв $4.05 по
$0.0135/мин; резерв не обнуляется из-за empty harness list. Controls/uninit/jobs/worker overrides для
этого kind запрещены.

Парсер разделяет `Thread N:`, не склеивает соседние workers, допускает повтор печатного имени
monomorph std, обрабатывает TIMEOUT без Verification Time и оставляет начатые без результата как
MISSING_RESULT. Финальные Complete counts и exit-код сверяются. RSS sampler2s собирает driver/CBMC/
отдельный solver, одновременную сумму с временем, per-PID peaks и direct/ambiguous attribution,
читаемые cgroup counters/deltas и dmesg OOM status. Per-PID страницы: `k1g.sh peaks BUILD OFFSET COUNT`,
COUNT≤8; общий peaks читается без OFFSET. Read-only `status` добавлен `25d5c981af` для точного wall всей сборки. RSS не равна занятой физической RAM, сумма одновременных RSS
не равна сумме независимых максимумов. CaDiCaL обычно находится внутри CBMC; отсутствие отдельного
solver PID не означает отсутствие solver-памяти. GCB swap=0 проверяется по machine view; отличие от
указанных в задании примерно3–4ГБ swap GH Ubuntu сохраняется.

Локально выполнены только Python и rustfmt: 69 unit tests, Bash syntax, dispatcher-style validation,
Python syntax и diff-check исходников — PASS; предписанный rustfmt-check всех затронутых library Rs — exit0,
строки≤100. В regression tests входят выбор auto/selected/partition, failure-through-tee/gzip,
dispatcher без script-out, jobs3/timeout/missing/duplicate rows, ordinary/controls covers и память.
[Точные hashes и пределы резервов](c3c/validation.json). Первый candidate request ошибочно использовал
неподдерживаемый `kani list --harness`; GCB `dfada6fc-2f83-4c2e-abf5-2ce45c6e3e81`
дал RUNNER_ERROR / 50 NOT_RUN и стоил $0.0945. Это setup, а не отказ proof.
Обычный `kani list` поддерживается pin; он ограничен 60м, его прежние 49м учтены в резерве.
[Диагноз по source pin](c3c/analysis-inventory-repair.md). Локально rustc/cargo/Kani/CBMC не запускались.

## Входы, пробы и пределы сравнения

В TSV Mac 2313 строк / 2068 печатных имён, 322 SmallSort; суммы Verification Time 28518.6с и25367.5с.
Указанные в задании 25368с согласуются после округления; 28524с отличаются от суммы TSV на5.4с.
Ubuntu: 2065 строк / 1826 имён, 105 SmallSort; суммы8791.2с и4682.5с. Заявленные1829 на3 больше числа
завершённых имён; сами три in-flight имени во входах отсутствуют. Терминальные TSV не содержат
Thread/start/stop snapshot, поэтому три имени не угаданы. [Hashes и подсчёты](c3c/input-identities.json).
Три Mac TIMEOUT600 взяты явно из TASK-C3C; их длительности не добавлены к суммам успешных строк.

Первая matched diagnostic серия: jobs3, одинаковая отсечка180с, 12 обязательных исторических доменов
(3 TIMEOUT и9 successes≥400с), ещё2 correct-family калибровочных домена и8 общих assembly.
Baseline22 гармоники; candidate50, поскольку все преемники выбранных разбиений включены полностью.
Для точной memory attribution и более длинной отсечки выполнена вторая серия: baseline26 и candidate54
(два непересекающихся куска30+24), jobs3, отсечка300с. Добавлены четыре умеренных неизменённых
семейства: network correctness u64 N7/N9, merge contract u64 N5, general/stable merge u64 N8.
Основные paired-таблицы используют только целиком вторую серию, без смешивания отсечек.
Все12 обязательных тяжёлых baseline доменов дали T300. Старый combined correct u8 N14 успел SUCCESS
с VT303.7755с: cooperative timeout способен слегка выйти за300с, этот результат не переименован в timeout.
Baseline library tree побайтно совпадает с e9655515, candidate — с fd854ca754; bind делается отдельно
от head SHA, содержащего новые lane/request файлы. Полного baseline autoharness не было: причина
исторической остановки Ubuntu и измеренное улучшение полного job этим экспериментом не устанавливаются.

Точная привязка памяти добавлена в `0be0387d2f` / `b853c68c65`: CBMC model `.out` однозначно
связывается с `goto_file` соседней compiler metadata (`.symtab.out` → `.out`, cwd процесса), затем
с `pretty_name`; записаны hashes metadata, request/head/build identities, PID, время наблюдения.
Положение model в argv не предполагается последним. Конфликт/пропуск остаётся unknown/ambiguous.
В новой matched серии 79/80 строк имеют direct attribution. Короткий
`assembly::advancement_merge_up_u8_n2` не попал в2с sampler: его память NA, не0.
Подробные значения по каждой гармонике, источники и hashes — [per-harness-memory.tsv](c3c/per-harness-memory.tsv).

У pin TIMEOUT печатается как FAILED, затем `CBMC timed out`, без Verification Time. Старый parser
в первых двух proof-пробах закрывал такой блок поздно и ошибочно выставлял overlap/INCONSISTENT.
Это исправлено и regression-tested до второй matched серии. Bounded replay baseline transitions
даёт22 блока,9SUCCESS/13TIMEOUT,0overlap; исторические summary сохранены исходными.
Полный autoharness был отправлен на прежнем parser; фактический итог — PARTIAL, exit124, gate=false.
Его исходные summary/counts сохранены; новый parser не подменяет evidence уже завершённого snapshot.

## Парные результаты и сумма разбиений

Основная серия — baseline `e358163c`, candidate `5ae76959` + `4722df9d`; точные UUID и head SHA приведены
в таблице сборок ниже. Все результаты этой таблицы имеют одинаковую отсечку300с. `T300` не заменяется
числом300 в сумме VT. Диагностические chunks не являются измерением whole-job speedup или пика всего job.

| Старое имя (verify::) | До: status / VT, с | Преемников | SUCCESS / TIMEOUT | Наблюдаемая сумма / max VT, с |
|---|---:|---:|---:|---:|
| merge::merge_contract_u64_n14 | T300 | 1 | 0 / 1 | NA / NA |
| network::network_correctness_u8_n17 | T300 | 1 | 0 / 1 | NA / NA |
| merge::merge_contract_u64_n15 | T300 | 1 | 0 / 1 | NA / NA |
| merge::route_safety_all_routes_n31 | T300 | 3 | 3 / 0 | 230.675 / 105.073 |
| merge::route_safety_all_routes_n32 | T300 | 3 | 3 / 0 | 225.460 / 101.159 |
| network::insert_tail_contract_u64_start6 | T300 | 10 | 10 / 0 | 206.291 / 34.936 |
| network::network_correctness_u8_n16 | T300 | 1 | 0 / 1 | NA / NA |
| network::network_correctness_u64_n8 | T300 | 1 | 0 / 1 | NA / NA |
| network::network_correctness_u64_n13 | T300 | 1 | 0 / 1 | NA / NA |
| merge::merge_contract_u64_n16 | T300 | 1 | 0 / 1 | NA / NA |
| network::insertion_permutation_u64_n12 | T300 | 1 | 0 / 1 | NA / NA |
| network::insert_tail_contract_u64_start1 | T300 | 15 | 15 / 0 | 350.463 / 47.671 |
| correct::sorted_permutation_general_stable_u8_n14 | SUCCESS / 303.776 | 2 | 2 / 0 | 254.414 / 142.251 |
| correct::sorted_permutation_fallback_u64_n8 | SUCCESS / 76.922 | 1 | 1 / 0 | 37.113 / 37.113 |
| network::network_correctness_u64_n7 | SUCCESS / 108.130 | 1 | 1 / 0 | 58.325 / 58.325 |
| network::network_correctness_u64_n9 | SUCCESS / 97.640 | 1 | 1 / 0 | 30.823 / 30.823 |
| merge::merge_contract_u64_n5 | SUCCESS / 142.967 | 1 | 1 / 0 | 56.916 / 56.916 |
| merge::general_stable_sorted_permutation_u64_n8 | SUCCESS / 137.748 | 1 | 1 / 0 | 54.633 / 54.633 |

START1 показывает, зачем считать сумму:15 преемников имеют max47.671с, но их суммарный VT350.463с.
Для старой censored модели выигрыш суммы неизвестен. У correct u8 N14 наблюдаемая сумма снизилась
с303.776 до254.414с при max142.251с; это эффект объединённого кандидата, не изолированная оценка E или R.
Память по каждой строке — [TSV с direct metadata/PID binding](c3c/per-harness-memory.tsv).

## Калибровка и прогноз macOS

Калибровка использует P6 `6cfc76cb211d088aebaff8a449bcac953e97f942` и baseline `e9655515`,
а не изменённый кандидат: common callee/stubs, solver и unwind исходно совпадают. Проверены также
workflow, scripts, pin, toolchain и Cargo files; [source binding](c3c/source-bindings.json).
14 успешных точек на26 baseline моделях. Отношение r = Mac VT / GCB VT; отдельные типизированные группы
не заменяются одним коэффициентом для всего модуля. P90 здесь ближайший наблюдаемый квантиль,
при n≤5 он часто совпадает с max; доверительная верхняя граница не установлена.

| Группа | Точек / censored | r median | Наблюдаемый r min..max (P90) | Верхние censor bounds | Dual censor |
|---|---:|---:|---:|---:|---:|
| assembly.primitive_witness | 3 / 0 | 0.510 | 0.408..0.576 (0.576) | NA | 0 |
| assembly.zst | 5 / 0 | 0.481 | 0.292..0.584 (0.584) | NA | 0 |
| correct.fallback.u64 | 1 / 0 | 0.404 | 0.404..0.404 (0.404) | NA | 0 |
| correct.general_stable.u8 | 1 / 0 | 0.440 | 0.440..0.440 (0.440) | NA | 0 |
| merge.contract.u64 | 1 / 3 | 0.343 | 0.343..0.343 (0.343) | 1.401, 1.350 | 1 |
| merge.general_stable.u64 | 1 / 0 | 0.302 | 0.302..0.302 (0.302) | NA | 0 |
| merge.upper_route_safety | 0 / 2 | NA | NA..NA (NA) | 1.400, 1.685 | 0 |
| network.correctness.u64 | 2 / 2 | 0.407 | 0.299..0.514 (0.514) | 1.597, 1.560 | 0 |
| network.correctness.u8 | 0 / 2 | NA | NA..NA (NA) | 1.500, 1.358 | 0 |
| network.insertion_permutation.u64 | 0 / 1 | NA | NA..NA (NA) | NA | 1 |
| network.tail_contract.u64 | 0 / 2 | NA | NA..NA (NA) | 1.950 | 1 |

При GCB T300 и известном успешном Mac времени дано r ≤ MacVT/300 для этого baseline наблюдения.
При Mac T600 и GCB success получилось бы r >600/GCBVT; таких точек нет. Три dual-censored случая
не дают конечного отношения и не отброшены. Значения округлены; cooperative timeout и platform noise
ограничивают точность. Censor bounds не включены в median успешных точек.

Для candidate строк вычисляются point = VT×median и отдельный stress-сценарий = VT×max(наблюдаемые r,
верхние censor ratios) только внутри той же группы. Перенос коэффициентов на изменённые E/D/R модели —
явное допущение прогноза; stress не является гарантированной верхней границей. При отсутствии группы/точек
прогноз остаётся NA. Mac-timeout lower-transfer выделен отдельно, сейчас он NA во всех группах.
Все исторические Mac T600 successor-модели помечаются отдельно даже при успешном GCB.
Итоговая приёмка цели ordinary≤300с — новый П-6 по решению владельца.

<!-- RUN-RESULTS -->

## Сборки и CI-budget

Источник времени и стоимости — Cloud startTime/finishTime (`*.status.json`), ledger с округлением вверх
до минуты по$0.0135/min. Это расчётный ledger, не счёт billing. Kani wall — отдельный GNU time,
не wall всей сборки. Суммы VT включают только наблюдаемые времена, без восстановления TIMEOUT/NOT_RUN.

| Запуск | Build UUID | Head SHA | Cloud / summary | SUCCESS / всего | Cloud wall, с | Kani wall | Ledger USD |
|---|---|---|---|---:|---:|---|---:|
| baseline | ba81d888-90db-49c7-a04d-d6dbb9108fac | 7b6bf1ede05d | FAILURE / INCONSISTENT | 9 / 22 | 1369.5 | 16:27.83 | 0.3105 |
| candidate-setup-failed | dfada6fc-2f83-4c2e-abf5-2ce45c6e3e81 | af406030589a | FAILURE / RUNNER_ERROR | 0 / 50 | 401.0 | NA | 0.0945 |
| candidate | fa7d2d00-8470-40e3-be55-c96f0eaa76dc | 66a7ad1fae73 | FAILURE / INCONSISTENT | 42 / 50 | 1553.5 | 19:39.31 | 0.3510 |
| autoharness | be070a8b-f0ca-4d6c-8f86-f8aff7915cbd | 2cc4a5871bf6 | FAILURE / PARTIAL | 1951 / 1959 | 17703.8 | NA | 3.9960 |
| baseline-memory | e358163c-9006-4ea0-a402-c12a5a009747 | f9bdf626a42a | FAILURE / COMPLETE | 14 / 26 | 2219.0 | 29:38.32 | 0.4995 |
| candidate-memory-1 | 5ae76959-e306-4b33-9506-402bc9909768 | 1216fc2884f0 | FAILURE / COMPLETE | 22 / 30 | 1686.0 | 21:23.49 | 0.3915 |
| candidate-memory-2 | 4722df9d-7a70-46d1-b761-deef420bb1f2 | eefb512a3fe8 | SUCCESS / COMPLETE | 24 / 24 | 838.3 | 8:44.83 | 0.1890 |
| controls | 0b2482ba-6db6-4125-8aa1-2503a7a8ccf4 | 34c3cf025802 | FAILURE / COMPLETE | 9 / 10 | 781.9 | 6:32.83 | 0.1890 |

| Запуск | Driver HWM, GiB | CBMC HWM, GiB | Отдельный solver HWM | Одновременная RSS-сумма, GiB @с |
|---|---:|---:|---:|---:|
| baseline | 1.82 | 3.93 | NA | 9.36 @620 |
| candidate-setup-failed | NA | NA | NA | NA @NA |
| candidate | 5.02 | 2.46 | NA | 8.09 @523 |
| autoharness | 8.06 | 4.34 | kissat 0.043GiB @2089 | 13.54 @10754 |
| baseline-memory | 5.53 | 4.12 | NA | 11.02 @912 |
| candidate-memory-1 | 0.82 | 2.49 | NA | 5.45 @567 |
| candidate-memory-2 | 5.40 | 1.23 | NA | 6.41 @427 |
| controls | 6.12 | 1.35 | NA | 6.76 @213 |

Всего 8/8 сборок, расчётный ledger $6.0210/$10; глобальный CAP_USD=63.96 не изменён.
Резервы и исходные guards — [session](c3c/session.json), `budget-before-*` / `budget-final.txt`.
Источники каждой цифры, exact SHA, все statuses, counters и process summaries:
[подробные таблицы](c3c/report-tables.md), [derived measurements](c3c/measurements.json), [bounded evidence](c3c/evidence/).

| Job / источник | Все строки / сумма VT, с | SmallSort строки / сумма VT, с | Доля SmallSort | Wall, с | RSS-пик, GiB | Failures / timeouts |
|---|---:|---:|---:|---:|---:|---|
| P6 Mac, предоставленный TSV run40748125754 | 2313 /28518.6 | 322 /25367.5 | 88.95% | NA | NA | 3T600 по TASK, вне сумм TSV |
| GCB full `be070a8b-f0ca-4d6c-8f86-f8aff7915cbd` | 1959 /25773.944 | 238 /18045.638 | 70.02% | 17703.8 | 13.54 | {"SUCCESS": 1951, "TIMEOUT": 5, "MISSING_RESULT": 3} |

У P6 нет исходных wall/RAM/USD; сравнивать суммы VT с wall нельзя. Наблюдаемое изменение сумм VT
не является matched улучшением whole job: baseline full отсутствует, число моделей изменилось, цензура различается.

## Единственный полный autoharness

Build `be070a8b-f0ca-4d6c-8f86-f8aff7915cbd`, head `2cc4a5871bf6da42d23137208247c0cf8dacb44c`, library `fd854ca7545df59b5307b629155ca61dc3d74d0f`.
Gate=False; summary=PARTIAL; native inventory=421 ordinary.
SmallSort statuses: {"SUCCESS": 233, "TIMEOUT": 2, "MISSING_RESULT": 3}.
Inventory/source prediction: missing=0, extra=0; results missing=183, duplicate=0.
Все native inventory страницы проверены по request/head/build identity, offset/count/next_offset и names SHA256.
Старый parser полного snapshot и его gate не переписывались после запуска. Любой INCONSISTENT/PARTIAL
сохраняется как ограничение evidence, а не превращается в PASS. Источники — `autoharness.*` в evidence;
доступные machine/cgroup/OOM/dmesg сведения сохранены в `autoharness.peaks.txt`.
В историческом summary строка per-harness timeout270min — ошибка подписи общего бюджета. Фактически literal workflow использовал10m на гармонику; подпись исправлена отдельным lane-коммитом `3184754242` с regression test.
Bounded machine view: inventory/setup заняли3186с после validate; остаток verify_budget14454с. GNU time при общем timeout не разобран, поэтому Kani wall=NA; это не потеря Cloud wall.
Пик13.54GiB — sampled RSS, driver8.06GiB, CBMC4.34GiB; отдельный kissat0.043GiB встречался в других std-моделях, SmallSort K удалён. Cgroup events в snapshot недоступны; dmesg=none_seen не доказывает отсутствие OOM.
Native inventory421 подтверждён, но только238 SmallSort моделей начаты:233SUCCESS,2T600,3MISSING_RESULT;183 не имеют result rows в этом частичном прогоне. Они не названы NOT_RUN, diagnostics не подставлены вместо full результатов.
RSS-пик относится к стандартной GCB машине без swap; это наблюдение не гарантирует успех GitHub.

## Opt-in covers-аудит

Состояние: ROWS_AUDITED; выборочный covers-аудит passed=False (Mac acceptance=false).
Проверяется тот же library-кандидат, cfg `kani_smallsort_controls`. Выборка по correct/merge/network
и оба фиксированных correct R маршрута; это выборка измеренного fd854ca754 (100 sites); финальный source fix e45cfc7250 не проходил CI.
Успех requires SUCCESS, covers_total>0 и covers_satisfied==covers_total для каждой выбранной строки.
Фактически9SUCCESS/1TIMEOUT180: correct::contract_insert_tail_u8_prefix не завершён. Семь SUCCESS harnesses имеют все covers SAT; оба fixed correct R u8N14 имеют1/2. Поэтому выборочный аудит НЕ ПРИНЯТ.
Оба недостающих R cover относятся к противоположной константной ветви (stable/general); это объясняет UNSAT, но не превращает аудит в PASS. Это source-объяснение по константной ветви; terse log не дал property IDs (bounded grep: no match), поэтому отдельная трасса свойств не заявляется. Final source fix e45cfc7250 описан выше; его повторный аудит не выполнен:8/8 builds.
Необъяснённые UNSAT/UNREACHABLE не исключаются из критерия. Ordinary proofs остались ordinary.
[Построчные counts и источник](c3c/report-tables.md#аудит-controls).

## Оставшиеся риски и варианты владельцу

Полный реестр содержит 421 native ordinary строк: [risk-register.tsv](c3c/risk-register.tsv).
Числа флагов (пересекаются): HISTORICAL_MAC_TIMEOUT600_NOT_RETESTED=17, MAC_OBSERVED_TAIL_OVER_300=10, MISSING_RESULT=3, NO_MAC_POINT_FORECAST=396, NO_RESULT_ROW=183, RUN_PARTIAL=421, TIMEOUT=2.
NA означает отсутствие прогноза, а не выполнение цели300с. Оценки и traceability сохранены для всех
ordinary, включая не входившие в исторические тяжёлые18 доменов.

| Ordinary (verify::) | GCB status / VT, с | Mac point, с | Mac stress, с |
|---|---:|---:|---:|
| correct::sorted_permutation_fallback_u64_n10 | MISSING_RESULT / NA | NA | NA |
| merge::route_safety_all_routes_n21 | SUCCESS / 180.412 | NA | 304.054 |
| network::dispatch_safety_stable_unstable_drop_u8_n15_16_17 | MISSING_RESULT / NA | NA | NA |
| network::insertion_permutation_u64_n12 | TIMEOUT / NA | NA | NA |
| network::network_correctness_u64_n7 | MISSING_RESULT / NA | NA | NA |
| network::network_correctness_u8_n17 | TIMEOUT / NA | NA | NA |
| network::insert_tail_contract_u64_start10 | SUCCESS / 314.319 | NA | 612.817 |
| network::insert_tail_contract_u64_start11 | SUCCESS / 322.130 | NA | 628.046 |
| network::insert_tail_contract_u64_start12 | SUCCESS / 247.752 | NA | 483.034 |
| network::insert_tail_contract_u64_start13 | SUCCESS / 180.132 | NA | 351.197 |
| network::insert_tail_contract_u64_start14 | SUCCESS / 165.009 | NA | 321.713 |
| network::insert_tail_contract_u64_start15 | SUCCESS / 181.945 | NA | 354.732 |
| network::insert_tail_contract_u64_start7 | SUCCESS / 468.612 | NA | 913.636 |
| network::insert_tail_contract_u64_start8 | SUCCESS / 453.166 | NA | 883.524 |
| network::insert_tail_contract_u64_start9 | SUCCESS / 432.203 | NA | 842.651 |

Именованный перечень теряемых доменов, source coordinates и зависимых композиционных утверждений
для каждой строки с проблемой времени/результата, а также для преемников исторических Mac T600:
[owner-risk-options.tsv](c3c/owner-risk-options.tsv). **Ни один перенос proof в opt-in не применён.**
Сохраняются full-width входы, все offsets/routes и прежние assertions; соседний N/T или иной allocation
не заменяет пропущенный контракт. В частности, потеря merge u64 N16 затронула бы предпосылку обеих
ordinary upper-route proofs, использующих verified merge stub; existing allocation-locality gaps остаются.

Варианты владельцу: новый П-6 для всего кандидата; продолжить точные разбиения тяжёлых доменов
с проверкой объединения и суммы VT; либо отдельно принять раскрытую потерю конкретных доменов.
Новые обнаруженные кандидаты для точных разбиений — tail START7..15 (объединение tail=START+1..16, allocation17) и route_safety N21 (три прежних класса). Для START15 остаётся лишь один tail: само переименование не обещает ускорения. Проб и повторного full для этих изменений в текущем8-build окне нет.
Перед принятием E policy нужен повторный covers-аудит финального source fix и завершённый prefix-contract audit; текущие результаты не дают такого GO.
Никаких дополнительных удалений/переносов для достижения метрики не сделано. У разбиений число
моделей и удерживаемых результатов растёт, поэтому max VT и суммарная стоимость контролируются вместе.

Локальные проверки:69 lane unit tests,6 report fixtures, Python/Bash syntax, source/domain audits,
git diff --check для кода/отчёта и заданный rustfmt-check — PASS. Literal TSV exports сохраняют пустые конечные поля, patch artifacts — пробелы context lines; они исключены из whitespace-check без изменения данных. Локальных rustc/cargo/Kani/CBMC не было.
Все commits `[skip ci]`; normal push только экспериментальной ветки, Actions/CircleCI не запускались.

Отчёт сформирован 2026-10-29 06:59 UTC; окно сессии01:08–07:08 UTC.
