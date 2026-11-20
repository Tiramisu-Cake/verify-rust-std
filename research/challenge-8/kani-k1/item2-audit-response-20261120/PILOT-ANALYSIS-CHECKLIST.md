# Офлайн-чек-лист анализа q-пилота

Чек-лист применяется после отдельного запуска. Роли контрактов, covers, свойства, контроли
и пригодность провайдеров оцениваются офлайн по собранным наблюдениям. [Задание на исправление runner](PILOT-FIX-TASK.md)

Результат анализа исследовательский. Всегда указывать `proof_credit=NONE`.

## 1. Зафиксировать запуск и полноту артефактов

- [ ] Записать run ID, attempt, event/ref, trigger SHA, tree и parent control, std/tool commit и tree, request/workflow hashes. Сопоставить trigger с control-кандидатом из delta review и записью GO/ledger. Сверить тот же request и исходники, включая изменённые строки covers. При расхождении оставить наблюдение непривязанным.
- [ ] Проверить selector каждого корня на точное равенство закреплённому selector из запроса. Не анализировать соседний или частичный selector как нужный корень.
- [ ] Зафиксировать lifecycle запуска и каждого корня, start/end, exit code или signal, timeout, результат reap/cleanup и фактический каталог target. При отсутствии достоверного подтверждения завершения или очистки оставить состояние неизвестным.
- [ ] Проверить, что `q-pilot-raw.json` и перечисленные в нём bounded-файлы stdout, stderr и export укладываются в cap на каждый файл и общий предел 256 MiB. Для сохранённых байтов сверить SHA-256, путь и длину. Отметить truncation, ошибку чтения, отсутствие, `INCOMPLETE` или `PARTIAL` export как неполноту evidence, отдельно от lifecycle процесса.
- [ ] Читать только `q-pilot-raw.json` и объявленные в нём bounded-файлы этого fork run. Для отсутствующего или неполного артефакта оставить пробел, соблюдая границы доступа к полным CI логам, raw GCS и Cloud Logging.
- [ ] Ошибка одного корня не меняет статусы других. Корни, до которых запуск не дошёл, имеют `NOT_RUN` с причиной. Отсутствие property или строки в неполных данных само по себе не означает `NOT_RUN`.

## 2. Сверить наблюдения с native выводом

Для каждого корня сравнить сохранённые regular stdout и export. Записать отдельно native наблюдения и выводы из исходников. Общий префикс селекторов в таблице — `slice::sort::shared::smallsort::verify::`.

- [ ] Сверить один terminal harness с точным selector, tool identity и regular inventory по ID, статусам, counts и buckets, включая covers, failed и unsupported. Stock содержит агрегированный SUCCESS count. Идентификаторы SUCCESS брать из полного regular inventory после сверки количества и разбиения. Обрезанный stream, отсутствующие записи и несовпадение оставляют соответствующую часть неизвестной.
- [ ] Записать native verdict, run state, features и все properties с точными native ID, классом, описанием, статусом и доступной source location. В feature list включить `unstable-options` из `-Z unstable-options` и сверить остальные features с argv и схемой пина. Сверить флаги checks, solver, unwind36 и отсутствие ON/loop-contracts/quantifiers в запрошенной конфигурации. Сохранить отсутствующие координаты и предупреждения явно.
- [ ] Для каждой роли отметить, что непосредственно наблюдалось в regular/export, что выводится из режима трансформации и что остаётся неизвестным. Разрешены статусы `OBSERVED`, `INFERRED` и `UNKNOWN`. Неоднозначное совпадение оставлять `UNKNOWN`.
- [ ] Для `Check` requires трактовать как assumptions, а не как требуемые native properties. Проверять native postconditions и frame properties по точному site и уникальному matcher.
- [ ] Для `Replace` проверять assertions для caller Pre. Ensures в Replace вводятся как assumptions после havoc, их доказательство относится к Check провайдера. Границы havoc сверять по `modifies` и mode metadata, observed frame assertions — по inventory. Указывать точный site, callee/instance и класс там, где их можно связать. Для insert Pre опираться на фактическое выражение с `&&` из source и native описания. Одно похожее имя свойства даёт `UNKNOWN`.
- [ ] Сверить kind, PFC target и точные уникальные наборы verified stubs по таблице, отдельно отсутствие ordinary stubs. Для P-2 ожидается только `{swap_if_less}`, для P-4/P-5c ровно `{sort13_optimal, insert_tail}`. Check/Replace выводить из метаданных и transform на пине. Привязку отдельных вызовов отмечать отдельно по доступным данным.
- [ ] Сохранить необработанные observed statuses и отдельно рассчитанные выводы. Не маркировать property PASS или MATCH только по наличию похожего имени.

## 3. Проверить корни, роли и covers

| Корень и selector | Native ожидание для анализа | Covers и особая проверка |
| --- | --- | --- |
| P-1 `sorting_q_pilot::p1_swap_u8_v34_q_any` | Check actual `swap_if_less`, без stubs. Проверить postconditions AND/OR, q-frame и frame байтов вне адресов swap. | Taken/untaken, равные индексы, split, границы base и q, return. `P1_Q_ABSENT` проверяет отсутствие q в сравниваемых `[base+a]` и `[base+b]`. |
| P-2 `sorting_q_pilot::p2_sort13_u8_b01_len17_q_any` | Check actual `sort13_optimal`, Replace `swap_if_less`. Проверить все 45 call sites и точные роли Replace, включая caller Pre, post и frame. | Activation, mixed, ties, extremes, return. `P2_Q_ABSENT` относится к логическому входу `V34[1..14]`, без tail frame. Целевое время child не более 300 с. |
| P-3 `sorting_q_pilot::p3_insert_u8_b01_rel1_16_q_any` | Check actual `insert_tail`, без stubs. Проверить Pre-domain и post/frame роли. | Все 16 tail covers, early return, полный sift, q-монотонный численно неотсортированный prefix. `P3_Q_ABSENT` проверяет inclusive insert input `V34[1..1+len]`. |
| P-4 `sorting_q_pilot::p4_network_u8_b01_n17_q_any` | Actual network, Replace ровно `sort13_optimal` и `insert_tail`. Проверить caller Pre, post/frame и полный N17 результат. | Mixed, ties, extremes, return. `P4_Q_ABSENT` проверяет `V34[1..18]`. Целевое время child не более 300 с. |
| P-5a `sorting_q_controls::p5_swap_false_or_q_any` | Check actual mutant swap. Единственная назначенная native failure `swap_false_or_post`. | `P5_SWAP_SPLIT_THRESHOLD` должен быть достигнут до actual swap. Полезный return cover анализировать отдельно. Не требовать mixed cover после вызова. |
| P-5b `sorting_q_controls::p5_swap_false_or_q_fixed0` | Check actual fixed-q mutant swap. Native SUCCESS ожидается, но он не доказывает универсальность q-домена. | Проверить заявленные covers и отсутствие требования mixed cover. На provider gate результат должен получить `Q_DOMAIN_NOT_UNIVERSAL`, потому что домен `{0}` не равен `all_u8`. |
| P-5c `sorting_q_controls::p5_network_n17_qpost_corrupt` | Actual N17 path, Replace ровно `sort13_optimal` и `insert_tail`. Единственная назначенная failure `P5C_CORRUPT_QPOST`. | Проверить достижимость пути до corruption assertion, а также native covers и frame/contract evidence отдельно от назначенной failure. |

- [ ] Проверить exact labels `P1_Q_ABSENT`, `P2_Q_ABSENT`, `P3_Q_ABSENT` и `P4_Q_ABSENT` в заданных выше доменах. P-5a использует `P5_SWAP_SPLIT_THRESHOLD` до actual вызова. P-5b не требует Q-absent cover. Не считать mixed или ties свидетельством отсутствия q во входе.
- [ ] Для P-1…P-4 ожидается native `SUCCESS`, обязательные роли и достижимость covers, перечисленных в таблице и закреплённых исходниках. Для контролей записать точный native ID отказа, source site и статус, затем оценить соответствие ожиданию. Ни exit 0, ни exit 1 сам по себе не устанавливает этот результат.
- [ ] Записать unwind setting и native evidence о достижении или исчерпании unwind. Отдельно перечислить U, unsupported и неразрешённые свойства с их статусами. Не интерпретировать отсутствие соответствующей строки в неполном export как отсутствие проблемы.
- [ ] Указывать только поддерживаемые измерения elapsed для child/supervise/job и явно указывать границу каждого. Compile входит в child, отдельную оценку compile не выводить. P-2 и P-4 отдельно сравнить с целевым child временем ≤300 с. Не вычислять campaign, step, phase или slot elapsed из несовпадающих часов.

## 4. Проверить controls и provider chain

- [ ] Для P-5a назначить одну каноническую роль `swap_false_or_post`. По cfg, callee и месту ensures связать её с единственной native `FAILURE`. Alias прежнего runner не создаёт отдельного ожидания `SUCCESS`. Split cover проверяется до actual вызова, полезный возврат — на неповреждённой части домена после вызова.
- [ ] Для P-5b разделить native SUCCESS и совместимость домена. Для каждой связи провайдер → потребитель проверять включение требуемого q-домена в проверенный, наряду с T/F, длиной, геометрией, Pre и frame. Для потребителя `all_u8` провайдер с `{0}` отклоняется с `Q_DOMAIN_NOT_UNIVERSAL`, даже при native SUCCESS. Контроли исключены из множества провайдеров.
- [ ] Сверить, что q получается независимо через `kani::any()` и компаратор не читает q. Проверить P-1 → P-2 на всех 45 парах base1 и P-2 → P-4/P-5c на slice len17 с frame хвоста. P-3 → P-4/P-5c покрывает tails13–16 при том же q и q-монотонном Pre. Отсутствующий provider или неподтверждённая роль оставляет вывод о потребителе диагностическим `UNKNOWN`.
- [ ] Для P-5c связать единственный `FAILURE` с `P5C_CORRUPT_QPOST`. По covers подтвердить вход `[0;17]`, q=1 и путь до проверки порчи. Это контроль чувствительности постусловия. Вывод P-4 оформляется отдельно.
- [ ] В заключении дать строку на каждый root с verdict, полнотой, свойствами/covers, контролями и измерениями. Указать пропуски, зависимости и причины `UNKNOWN`. Целевой исследовательский сигнал требует четырёх положительных исходов, трёх различённых контролей и child≤300 с на P-2 и P-4. Итог ограничен u8, фиксированной геометрией и N17 до merge. Приёмка, UB/ON и общность по T остаются отдельными задачами. Записать `proof_credit=NONE`.
