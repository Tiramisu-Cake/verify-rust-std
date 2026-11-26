# REV2 · exact merge pair по форме FIX3

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Локальный пакет из четырёх последовательных Check для Ubuntu 24.04. Отдельные ревью и GO пакета предшествуют нативному compile preflight и измерениям. [Задание](REV2-MERGE-PAIR-FIX3-SHAPE-TASK.md) · [Разбор предыдущего пакета](REV2-N20-N21-PROVIDERS-RESULTS-ANALYSIS.md)

## Exact roster и исходники

Префикс selector и Check instance — `slice::sort::shared::smallsort::verify::rev2_merge_pair_fixed::`. Все четыре строки ожидают `VERIFIED`, exit 0, `MATCHED`, 11/11 covers, полные обязательные regular/stock anchors и своевременный receipt.

| Слот | Selector после префикса | Check target | Половины · k | Latest start |
| --- | --- | --- | --- | ---: |
| `M32-PAIR-FIXED` | `m32_pair_fixed` | `actual_pair_step_n32` | 16+16 · 0..15 | 50:00 |
| `M20-PAIR-FIXED` | `m20_pair_fixed` | `actual_pair_step_n20` | 10+10 · 0..9 | 53:25 |
| `M21-PAIR-FIXED` | `m21_pair_fixed` | `actual_pair_step_n21` | 10+11 · 0..9 | 56:50 |
| `M31-PAIR-FIXED` | `m31_pair_fixed` | `actual_pair_step_n31` | 15+16 · 0..14 | 60:15 |

Шаблон FIX3 материализован в четыре функции и четыре fixture с литеральными N, m и смещениями. Это даёт отдельный `proof_for_contract` target на N и литеральные координаты меток без макрораскрытия. Сверка одновременно подставила `N`, `N+1`, `m`, `m−1`, `N−1` и `N−2` в исходную форму FIX3 и получила все четыре блока побайтно. После обратной подстановки имён и меток N32 совпадает с FIX3. Исходный selector `slice::sort::shared::smallsort::verify::rev2_provider_cost::m32_pair_step` входит в cfg-off и cfg-on discovery. [Четыре Check](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_merge_pair_fixed.rs:13) · [Исходный FIX3](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:269)

Каждый fixture создаёт произвольный инициализированный V34, срез `backing[1..1+N]`, отдельный writable `MaybeUninit<[u8;32]>` и `KeyLess<u8>` с независимым q. Три проверки применимости фиксируют readable N, writable 32 и disjoint. Единственная предпосылка о порядке половин задана в fixture через CAL1 `merge_halves_numeric_order`. Helper принимает 20..=32. Для будущей специализации N18/N19 эквивалентный предикат проверяет числовой порядок обеих частей после `split_at(m)`. В текущем Check четыре исходных requires FIX3 ограничивают счётчики и адреса. У предыдущего общего M20/M21 Check символический n входил в геометрию и DFCC, raw-порядок повторялся во внутреннем requires, а свойства и covers разветвлялись по n. Здесь 9 локальных assert и 10 локальных covers на строку, плюс cover actual компаратора. [CAL1 helper](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_q_merge_model.rs:122) · [Прежняя обёртка](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:180)

Видимость сверена по исходнику. Родительский `smallsort::verify` регистрируется под `cfg(kani)`. Дочерний модуль видит private helpers через `super::super` и CAL1 модель через `super`. `merge_wide` и функция порядка доступны в пределах `smallsort`, `KeyLess::with_q` и `q` доступны дочернему модулю `verify`. Std diff содержит новый модуль, его gate с унаследованными cfg и декларацию check-cfg. Исходный runtime, модели, контракты FIX3 и пять опор N20/N21 имеют прежние blobs. [Родительская регистрация](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:1076) · [Gate](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify.rs:173) · [Check-cfg](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/Cargo.toml:60)

## Геометрия, записи и достижимость

Для `N=2m` или `N=2m+1` и `0≤a,c≤k<m` положим `b=k−a`, `d=k−c`. Тогда `a,b,c,d∈[0,m−1]`. Смещения прямого и обратного чтения слева `a` и `m−1−c` лежат в `[0,m−1]`. Справа `m+b∈[m,2m−1]` и `N−1−d∈[N−m,N−1]`, оба в `[m,N−1]`. Счётчики обоих направлений независимы. Совпадение read-адресов допустимо, а запись идёт в отдельную область.

Wrapper вызывает `merge_up(S+a,S+m+b,D+k,...)` и затем `merge_down(S+(m−1)−c,S+(N−1)−d,D+(N−1)−k,...)` в actual порядке. Из `k≤m−1` следует `k<N−1−k<N≤32`. Обе цели лежат между ранее заполненными `D[0..k)` и `D[N−k..N)`. Две однобайтовые записи и `modifies(D[k],D[N−1−k])` сохраняют эти края и оставляют `D[N..32)` во frame. Fixture читает ровно две новые ячейки, проверяет условный byte oracle min/max, весь V34 и q. Инициализация прочитанных ячеек следует из двух actual копий и известной инициализации V34 при профиле uninit OFF. [Actual loop](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:1022)

Up берёт L при `R≥L` и сдвигает выбранный source через `add(1)`. Левый successor имеет смещение до m, правый до 2m≤N. Значение `S+N` допустимо как one-past логического входа. Down берёт L при `R<L` и отступает выбранный source через `wrapping_sub(1)`. Левый successor лежит в `[−1,m−1]`, правый в `[N−m−1,N−1]`. Терминальный `S−1` имеет provenance V34 и соответствует `backing[0]`. Actual код использует его для `wrapping_add(1)` при вычислении `left_end`. Destination successors `D+k+1` и `D+N−2−k` находятся внутри scratch. У N31 проверены отдельно `D+30−k` для записи и `D+29−k` для successor после исправления исходной раскладки. [Actual up](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:883) · [Actual down](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:916) · [Терминальные курсоры](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:1027)

Для всех k подходят постоянные половины L<R и L>R, которые дают оба выбора каждого направления. Равные постоянные половины дают ties обоих направлений и общий cover `up_tie || down_tie`. В actual теле `src` выбирается перед копией той же сравнительной ветвью, что и курсоры, поэтому на tie прямой проход копирует слева, обратный справа. Проверка пары связывает это через курсоры и min/max. Отдельный указательный oracle `SELECTED_SOURCE` сохранён в предыдущем N21 odd-center Check. [Числовой компаратор и его cover](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26) · [Odd source oracle](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n20_n21_providers.rs:454)

## Сверка нативных свойств после GO

В каждой строке request закреплены stock `ProofForContract.target_fn`, exact instance для regular `single_top_level_call` и `no_recursive_call`, их связь со stock contract symbol и диапазоном атрибутов wrapper. Для двух cursor assert regular ID должен принадлежать Check closure своего N. Метки остальных assert и covers привязаны к fixture или actual `FnMut` по функции, имени свойства, файлу, строке и столбцу. Числовые суффиксы нативных ID даёт вывод pinned tool, а cover IDs сверяются с stock `satisfied`. Статический gate читает начало буквального вызова `kani::assert/cover` в pinned blob, вычисляет line по переносам и column по отступу. [Frozen roster](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/CI-REQUEST.json) · [Координаты](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/request.py:377) · [Regular и stock](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/results.py:198)

Actual `ptr::copy_nonoverlapping(src, dst, 1)` на строках 885 и 918 исполняются straight-line внутри каждой checked специализации `u8/KeyLess<u8>`. Обязательные `ptr::copy_nonoverlapping::<u8>` свойства в `ptr/mod.rs:587:14` включают `precondition_instance.1/.2/.3`, `safety_check.1/.2` и `arithmetic_overflow.1`. DFCC anchors — `memcpy.assigns.1/.2` в builtin memcpy, строки 46/47. Для переноса grouped `SUCCESS` на обе копии нужны exact target, Check anchors, отсутствие провалов unwind, comparator cover и `USEFUL_RETURN` после обеих копий. CBMC группирует все достигнутые SSA экземпляры одного ID конъюнкцией. Stock success counts сверяются с regular, конкретные статусы этих anchors закреплены в regular. [Up copy](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:885) · [Down copy](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/slice/sort/shared/smallsort.rs:918) · [Ptr preconditions](/root/verify-rust-std-rev2-merge-pair-fixed-w14/library/core/src/ptr/mod.rs:587) · [Правило grouped properties](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

Исторический FIX3 M32 даёт 53,169 с VT, 86,751 с cold wall, 75 950 SSA steps, 391 оставшуюся VCC и первую CNF 247 286 / 1 462 727. После измерения сверить с новым M32 и остальными строками SYMEX и SSA steps/times, исходные и оставшиеся VCC, первую и поздние CNF, VT, cold wall, пиковые RSS группы и CBMC, последнюю наблюдаемую фазу и reap. Проекции удерживают ранние и поздние CNF с координатами потока и счётчиком пропусков. При смене worker TID Linux может недоучесть RSS. [Историческое сравнение](REV2-N20-N21-PROVIDERS-RESULTS-ANALYSIS.md#чем-отличаются-три-check) · [Проекция метрик](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/native_metrics.py)

## Пины и контроль

| Роль | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Std base | `87ef4442ded137d2ee5f65bc29a4f87b8a3b69cd` | `832289728d493a114f89c318546c7e50d36f6d45` | `959087ac8632c68d8a6f0e28f58a8708475d564b` |
| [Std · work/rev2-merge-pair-fixed-w14](/root/verify-rust-std-rev2-merge-pair-fixed-w14) | `f72f4303bacfff4706b20268a87b2a1031a8ee0b` | `03f9ce753b375729c2f8e53c18b2eaf7f3f07fc1` | `87ef4442ded137d2ee5f65bc29a4f87b8a3b69cd` |
| Control base FIX1 | `2954a195a5997631fe21169493637531bcc21765` | `f56b8ec3d5a8564a4076f3867e35ecb0b8e813c3` | `414f0060c5eea9aded387c0431d9aae8b13a9870` |
| Control четырёх слотов до стабилизации | `c3108126877ae4e26c934bec638dca01d76546ba` | `8fa8eb4e404301d4ea0fc48d7f6815d9ac91864a` | `2954a195a5997631fe21169493637531bcc21765` |
| [Финальный control · work/rev2-merge-pair-fixed-control-w14](/root/kani-rev2-merge-pair-fixed-control-w14) | `8e1603eef95407eaf03bb592266d7513540682f8` | `b4a386280f9a01b72e435ce0fe0546353fd757c4` | `c3108126877ae4e26c934bec638dca01d76546ba` |
| [Локальный review-trigger · detached](/root/kani-rev2-merge-pair-fixed-trigger-w14/control) | `7dff41424cf0a327262336b37e549abae02a4f4b` | `b4a386280f9a01b72e435ce0fe0546353fd757c4` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Локальный ref trigger — `review/rev2-merge-pair-fixed-trigger-w14`. Ожидаемый внешний pin `CH8_REV2_MERGE_PAIR_FIXED_TRIGGER_TREE=b4a386280f9a01b72e435ce0fe0546353fd757c4`. Workflow читает Actions variable в `REV2_MERGE_PAIR_FIXED_TRIGGER_TREE`. `pins`, `sources` и `finish` требуют tree, clean detached checkout, exact payload SHA, fork `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1 и sole parent. `sources` и `finish` дополнительно сверяют первичный admission receipt. Upload зависит от успешных `pins` и `finish`. [Workflow](/root/kani-rev2-merge-pair-fixed-control-w14/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/request.py:208)

Std CI-base — `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Bundle объявляет один `HEAD` и включает 13 последовательных overlay-коммитов поверх этой базы. Stock Kani — `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/CI-REQUEST.json) | `1cd7e0bd9ce6791c91be87700d40410c3a43fbc745d21377ba73bcfdb68f3b08` |
| Roster, canonical JSON с сортированными ключами и разделителями `(",", ":")` | `71afd91aefbb2c4fb5ff6f5fa74d65736c0031afd01fe29e8e0029999f6968a2` |
| [std-overlay.bundle](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/std-overlay.bundle), 36 566 байт | `0d521e9f4dfa872d425c0289c67aa121c4c8c70bcf61d358a6d529c05eb70811` |

| Source на Std HEAD | Blob |
| --- | --- |
| `library/core/Cargo.toml` | `56998faddc8ffdc1297ddca58f8ee10a946f9e98` |
| `smallsort/verify.rs` | `5b6f365ead0a6e8c3c963cdc3c38d1472698b295` |
| `rev2_merge_pair_fixed.rs` | `b8580df3448e100d7ecb0811ebba0f14041ad412` |
| `rev2_provider_cost.rs` · FIX3 | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` |
| `rev2_n20_n21_providers.rs` · прежние опоры | `c88c3a1240181b0949be7cd7154de20ff83304b3` |
| `cal1_model.rs` · компаратор | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` |
| `cal1_q_merge_model.rs` · порядок | `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `smallsort.rs` · actual | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `library/core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |

## Профиль и сроки

Одна job `ubuntu-24.04`, внешний лимит 100 мин. Stock CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`. Safety, overflow, unwind, undefined-function и assertion-reach ON, uninit/validity OFF. VT ≤120 с, cold wall ≤180 с, группа ≤4 GiB, резерв ОС 2 GiB. Каждый слот имеет холодные отдельные CWD, Cargo/Kani target, TMPDIR и export. Compile preflight до discovery сохраняет первые rustc diagnostics. Cfg-off включает одиннадцать унаследованных флагов и прежний inventory. Cfg-on добавляет `kani_smallsort_rev2_merge_pair_fixed` и ровно четыре contract-harness, с проверкой selector/kind/file. [Команда и runner](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/run.py:405) · [Preflight](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/run.py:257) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

| Этап | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup, compile preflight и discovery | 50:00 | 50:00 |
| Четыре слота по 205 с | 13:40 | 63:40 |
| Итоговая аттестация | 2:00 | 65:40 |
| Finish | 5:00 | 70:40 |
| Upload | 7:00 | 77:40 |
| Резерв | 9:00 | 86:40 |

На слот выделено 180 с cold wall, 10 с reap, 5 с receipt и 10 с launch headroom. Атомарный checkpoint фиксирует child outcome/exit и reap до проекции. Дедлайн receipt — минимум конца слота и пяти секунд после supervisor. Последняя секунда отведена финальной записи. Отложенная запись остаётся в журнале с late flag. Неподтверждённый reap блокирует дальнейшие запуски. Лимиты проекции и артефакта — 4 MiB и 96 MiB. [Runner](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/run.py:483) · [Finish](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/report.py:187)

| Шаг | Внутренний бюджет, с | Внешний таймаут, мин |
| --- | ---: | ---: |
| pins, включая четыре watchdog | 425 | 8 |
| sources | 120 | 3 |
| prepare | 3 000 от epoch | 51 |
| measure | 1 005 и абсолютная отсечка 65:40 | 18 |
| finish | 300 и абсолютная отсечка 70:40 | 6 |
| upload | 420 в плане | 8 |

В `measure` входят 820 с слотов, 120 с аттестации, 5 с журнала и 60 с для входного gate. При более ранней шаговой отсечке latest starts сдвигаются вместе с границей слотов, сохраняя их полные окна.

## Локальная проверка

- `rustfmt --check` прошёл с `/root/rustfmt-toolchains/nightly-2026-11-19/bin/rustfmt --edition 2024 --config use_small_heuristics=Max`. Для registry применены `skip_children=true,reorder_modules=false`. `git diff --check` прошёл для Std, control, test-only коммита и trigger относительно его sole parent. YAML разобран с проверкой дублирующихся ключей, `bash -n` прошёл для шести shell-блоков, оба встроенных Python-блока и контрольные модули прошли AST-разбор. Проверка областей имён в runner/request/report прошла. Локальное имя `workspace` в функции `workspace()` заменено на `checkout_root`.
- Для N32/N20/N21/N31 перебраны соответственно 1 496/385/385/1 240 допустимых `(k,a,c)` и четыре комбинации сдвига курсоров на каждом. Сверены четыре read offsets, различие назначений, границы successor/sentinel и сохранение заполненных краёв scratch. Побайтовая сверка с FIX3 после подстановки проверила саму специализацию отдельно от перебора формул.
- Bare shallow Std depth 2 получен локальным Git transport без alternates. `bundle verify/list-heads/unbundle` подтвердили 13 commit/tree/parent, исходные HEAD/refs/shallow boundary остались прежними. На этом импорте проверены layout, четыре связки `proof_for_contract/unwind` и 80 закреплённых координат (76 уникальных меток модуля и четыре ссылки на один actual cover). Сдвиг любого закреплённого столбца на +1 отклонён в 80 из 80 мутаций. Для bare-импорта проверка worktree и submodules заменена прямой проверкой exact shallow-base и объектов. [Тест отступов](/root/kani-rev2-merge-pair-fixed-control-w14/ch8-cal1/test_run.py:154)
- Синтетика runner и projection покрывает неверный selector/kind/file, чужую специализацию Check, неверную или пропущенную колонку, потерю cover, stock symbol и regular Check anchors, compile preflight до discovery, late receipt и неподтверждённый reap. Первый suite до стабилизации воспроизвёл известный отказ escaped-descendant `REAP_UNVERIFIED` в синтетическом тесте. Повтор до стабилизации прошёл 110/110 на каждой из четырёх шкал.

### Принятая стабилизация supervisor self-tests

После решения координатора R2 GO в g0 `423f971b2ed273eec9ea20d08fc44aaf8f848ca2` принят ровно `ch8-cal1/test_supervisor.py` из `637387c038e5e3b4f68c2868e9b3376504c105ac`. Перед заменой blob `5f7889280b9cac99471eda153a2477bfa49313c4` совпал у FIX1, control четырёх слотов и базы w15 `6a599af76402e61eef6746c32d7500b6ac101945`. Новый blob `df63a457c3adf648d360f3d559d5d40ef00a9427` совпал с принятым. `git diff-tree` показал один файл в коммите `8e1603eef`. Production-код, workflow и три входных SHA-256 совпадают с родителем. R2 GO распространяется на включённый test-only diff. [Ревью R2](REV2-SUPERVISOR-SELFTEST-REVIEW.md)

Полный синтетический suite выполнен последовательно из финального detached trigger по командам workflow, с watchdog 90 с и запасом KILL 5 с на каждую копию.

| Шкала monotonic | Тесты | Время unittest, с |
| --- | ---: | ---: |
| Обычная | 110/110 | 23,825 |
| 60 с + elapsed | 110/110 | 23,685 |
| 5 с + elapsed | 110/110 | 23,369 |
| 1 с + elapsed | 110/110 | 23,058 |

Финальный detached trigger на шкале от 1 с прошёл `pins` и `finish` с синтетическим push payload. Итоговые записи содержат четыре `NOT_STARTED`, `PROVIDERS_OPEN`, `proof_credit=NONE`, три проверенных входных SHA-256 и восемь проверенных членов артефакта. `pins`, `sources` и `finish` отклонили tree базы FIX1, tree control до стабилизации, посторонний tree, прежнее имя переменной и неверный payload SHA. `sources` и `finish` отдельно отклонили изменённый первичный receipt. Всего 17 ожидаемых отказов.

## Открытые рёбра

У всех четырёх новых пар исход остаётся открытым до нативного результата и ревью. При заметном удорожании N32 первым делом сверяются новый и исторический FIX3 shape, cfg и native anchors. При прошедшем N32 и ресурсной отсечке отдельного N следующий кандидат ограничивается разбиением этой геометрии на up/down. Пять ранее завершённых опор N20/N21, включая exact odd center N21, и старые N18/N19 receipts сохраняют свои пины и статус. Odd center N31, actual copy-back и сквозные consumer roots остаются отдельными обязательствами.

Внешняя индукция по рангам `(byte, исходный индекс)` связывает пару с циклом actual merge. При k заполнены ранги `[0,k)` и `[N−k,N)`, а пара добавляет ранги k и `N−1−k`. Tie-side совпадает с порядком рангов. После m пар чётный случай исчерпывает обе половины, в нечётном случае остаётся единственный ранг m для odd center. Из этого и поста центра выводятся равенства концов перед actual guard. Copy-back использует непрерывный инициализированный префикс длины N после успешного guard. Переход к целому merge и consumer требует собственных связок и допуска. Уровни B1/B2, исходный отчёт инструмента и независимый proof credit учитываются раздельно. [Правило композиции](REV2-COMPOSITION-RULE.md) · [Граф N18–N31](REV2-N18-N31-PLAN.md)

Все коммиты пакета локальные, с `[skip ci]`, автор Tiramisu-Cake <igkharin@gmail.com>. Проверки этого этапа статические и синтетические. Push, CI, изменения Actions variables и локальный запуск cargo, rustc, Kani или CBMC отсутствуют.
