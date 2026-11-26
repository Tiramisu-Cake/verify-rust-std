# REV2 · actual N17 и четвёртая вставка

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** Готов один локальный Ubuntu-пакет для `small_sort_network::<u8, KeyLess<u8>>` на инициализированном V34, активном `v[1..18]` и независимом `q: u8`. Для составного вывода о полных байтах готова привязка S13 и подготовлен exact байтовый корень для всего driver. Результаты всех трёх новых слотов, независимое ревью и отдельный GO остаются открыты. [Задание](REV2-N17-TASK.md) · [Правило композиции](REV2-COMPOSITION-RULE.md) · [Допуск N32](REV2-N32-ADMISSION.md)

## Граф actual вызова

| Ребро | Exact привязка и статус |
| --- | --- |
| Dispatch и reborrow | При `len=17` условия `len < 2` и `len > 32` ложны. На `smallsort.rs:386` истинно `no_merge`. В :388–391 base указывает на абсолютный индекс 1, а `initial_region_len=17`. Срез региона имеет ту же геометрию и эксклюзивный доступ к этим 17 инициализированным байтам. |
| S13 и пороговый перенос | На :395–397 `region.len() >= 13`, поэтому actual `sort13_optimal` получает весь `v[1..18]`. Guard :601 пропускает длину 17. Все 45 вызовов на :612–656 имеют base 1 и `0 <= a < b < 13`. Exact `S13-B01-L17-BITS` и полнобайтовый FIX3 `S13-SWAP-LEAF` дают принятый внешний вывод о numeric order и сохранении кратностей в `v[1..14]`. Хвост `v[14..18]`, весь внешний frame и q сохранены. |
| Actual driver | На :405 вызывается `insertion_sort_shift_left(region, 13, is_less)`. На :748 guard `offset == 0 || offset > len` ложен. На :758–764 `v_end=v_base.add(17)` имеет абсолютный индекс 18. `tail` стартует с `v_base.add(13)`. Пока `tail != v_end`, actual `insert_tail` вызывается на rel13, 14, 15, 16, то есть на абсолютных 14–17. После rel16 выполняется :767, `tail == v_end` и следующий тест :761 завершает цикл. |
| Последняя вставка и native byte post | На :705–708 четвёртый вызов читает `v[17]` и предыдущий элемент `v[16]`. При `v[17] < v[16]` actual ветка копирует predecessor :722, опускает gap и останавливается на `sift == begin` (:725) или первом неудовлетворённом `tmp < *sift` (:731). `CopyOnDrop::drop` (:357–362) заполняет gap одним сохранённым initialized байтом. Проход касается только `v[1..18]`. Exact `N17-INSERT-BYTES` должен подтвердить весь driver, включая rel16, числовой пост, `count(<q)` и frame. |
| Выход сети | Сразу после driver :407–408 возвращает управление. Второй регион (:411–416), merge (:424) и copy-back (:425) на этом пути недостижимы. `N17-ACTUAL-BITS` должен подтвердить normal return и общий пост на 17 независимых битах. `N17-WITNESS-CORRUPT` проверяет чувствительность этого же поста на конкретном пути. |

Первым трём вызовам driver передаётся очередной неизменённый байт и уже упорядоченный префикс. Если новый байт не меньше последнего, :706–708 сохраняет префикс и наращивает его на байт. При сдвиге каждый скопированный элемент больше сохранённого байта, а последний gap получает именно этот байт. В обоих случаях расширенный префикс упорядочен, сохраняет своё мультимножество, включая прежний максимум, и оставляет дальнейший хвост. Поэтому перед rel16 predecessor является максимумом расширенного префикса и не меньше `before[13]`, максимума входного prefix13. Условие `before[17] < before[13]` в byte cover гарантирует строгий сдвиг именно на rel16. N32 даёт прецедент трёх вставок на len16. Здесь необходим exact пост driver на len17. [Actual сеть](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort.rs:367) · [Driver](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort.rs:742) · [Вставка](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort.rs:701) · [Byte Proof](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n17.rs:16)

На каждом S13-листе `Pₜ(x)=[x >= t]` переводит min/max в AND/OR. Индукция по 45 actual парам даёт ту же выходную проекцию для входных байтов и их пороговых битов. Инверсия обнаруживается при пороге, равном большему байту. Разности сохранённых пороговых счётчиков дают все кратности. Пары работают на двух различных живых байтах с выравниванием 1 внутри одного V34, а leaf frame сохраняет каждую нецелевую ячейку. После S13 это даёт byte precondition driver с четырьмя неизменёнными хвостовыми байтами. [Принятый пороговый вывод](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md#покрытие-по-длинам-сети) · [Сопоставление 45 вызовов](REV2-S13-GEOMETRIES-HANDOFF.md#привязка-байтового-листа-и-пороговый-перенос)

`KeyLess<u8>::call_mut` исполняет cover и числовое `a < b`. Инициализированный `q` хранится отдельно, компаратор его не читает и не меняет. Для фиксированного байтового входа actual результат driver един для всех q. Если byte Proof проходит, равенство `C(q)=count(byte<q)` для всех q даёт кратность `b<255` как `C(b+1)-C(b)`, а кратность 255 как `17-C(255)`. Композиция с S13 даёт на нормальном возврате numeric order, полное входное мультимножество и сохранение q и 17 внешних байтов. Сохранение инициализации следует из семантики actual записей и отсутствия чтений неинициализированного scratch при `no_merge`, при инструментальных `uninit/validity OFF`. Составной пакет использует plain Proof, все actual вызовы исполняются без stubs, Replace или новых loop contracts. Предположение byte harness ограничено numeric order входного prefix13. [Компаратор](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:26)

### Идентичность источников и исторические anchors

| Источник в Std candidate | Git blob | Роль |
| --- | --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` | Dispatch, S13, swap, driver, tail, drop. Идентичен FIX3, exact геометрии S13 и N32. |
| `verify/cal1_model.rs` | `236394dcfb1ff571ee6f816391f7b2e00cc9e630` | `KeyLess<u8>`, независимый q и actual comparator cover. Идентичен на обеих исторических опорах. |
| `verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` | FIX3 leaf, домен :144–157 и post/frame :159–169. |
| `verify/rev2_s13_geometries.rs` | `c403b343270752fb03fc087a101b55d8dc20a7ab` | Exact `check_bits::<1, 17, false>`, actual S13 :51. |
| `verify/rev2_n17.rs` | `54012b888edc7580a5ee028c2b08e70d98c6ae45` | Новый byte driver :23, actual network :67, общий битовый пост :87:5. |

В сохранённых структурированных результатах сверены SHA-256 индекса, размера и SHA-256 обоих членов по индексу. Обе опоры имеют Ubuntu X64, attempt 1, один stock SHA, CBMC 6.11.0/CaDiCaL, OB12, exact singleton, unwind36 и uninit/validity OFF. У обоих нативный `VERIFIED`, exit 0. [Результаты S13](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md) · [FIX3](REV2-NETWORK-PROVIDERS-RESULTS-ANALYSIS.md)

| Нативная опора | Std commit / tree | Успешные anchors |
| --- | --- | --- |
| `45688753097` · `S13-B01-L17-BITS` · plain Proof `rev2_s13_geometries::s13_b01_l17_bits` | `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` / `ff2563b5867b8327b95db909262ddf80e3ed9c03` | `check_bits::<1, 17, false>.assertion.` 5/8/11/12 на :53:5/:54:5/:64:5/:69:5, q, V34 frame, canonical, sorted popcount. 4/4 covers. |
| `45661535099` · `S13-SWAP-LEAF` · Check `rev2_provider_cost::s13_swap_leaf` для `swap_if_less` | `32129c149a15fb1b60a7314e738f3cb466d076e5` / `1b0cc32c571b370178e64f2b8c79773d2ce27051` | `s13_swap_leaf.assertion.` 1/14/19 на :159:5/:160:5/:166:9, q, full-byte min/max, V34 byte frame и native DFCC write set. 6/6 covers. |

| Слот | SHA-256 индекса | SHA-256 receipt | SHA-256 projection |
| --- | --- | --- | --- |
| `S13-B01-L17-BITS` | `e575daf8b20bab3c3023b8809e61cc21ea1a4bf9be85153d572368e6bbf663b7` | `119b822970d1386f3d15e5edefefaf847d4ee63a5358610f0bd9e22880c63c79` | `6c37276170ebe94470fa4a1d17b92bc09e05e5ac6b66d22aadd21508f255696a` |
| `S13-SWAP-LEAF` | `31209be8cb8d2c0f3f770e56aca354eeecaf4ad3feae8e0d2078797fa6aba4be` | `a90892f50538caf129a77f8dfd9be920280a6952c30b67401e1aadc7483d1c9c` | `3f81b2c134cdba1348d9720fafb5569dbc37195693e47485c8bb1b80fe28d596` |

## Exact roster и контроль

Имена ниже даны в порядке слотов. У каждого native kind `Proof` (`standard-harnesses`), unwind36. Все три требуют cover `CAL1 q actual comparator executed` из actual `KeyLess`. [Frozen request](/root/kani-rev2-n17-control-w14/ch8-cal1/CI-REQUEST.json)

| Слот и exact selector | Нативный ожидаемый исход | Обязательные метки |
| --- | --- | --- |
| `N17-INSERT-BYTES` · `slice::sort::shared::smallsort::verify::rev2_n17::n17_insert_bytes` | `VERIFIED`, exit 0 | Assertions `REV2_N17_INSERT_NUMERIC_ORDER`, `REV2_N17_INSERT_COUNT_BELOW_Q`, `REV2_N17_INSERT_Q_FRAME`, `REV2_N17_INSERT_V34_FRAME`. Дополнительные covers `REV2_N17_INSERT_FOURTH_SHIFT`, `REV2_N17_INSERT_NORMAL_RETURN`. |
| `N17-ACTUAL-BITS` · `slice::sort::shared::smallsort::verify::rev2_n17::n17_actual_bits` | `VERIFIED`, exit 0 | Assertions `REV2_N17_ACTUAL_Q_FRAME`, `REV2_N17_ACTUAL_V34_FRAME`, `REV2_N17_ACTUAL_CANONICAL_SORTED_POPCOUNT`. Дополнительные covers `REV2_N17_ACTUAL_MIXED_INPUT`, `REV2_N17_ACTUAL_FOURTH_SHIFT`, `REV2_N17_ACTUAL_NORMAL_RETURN`. |
| `N17-WITNESS-CORRUPT` · `slice::sort::shared::smallsort::verify::rev2_n17::n17_witness_corrupt` | `FAILED`, exit 1 | Те же covers и успешные q/V34 frame. Единственный `FAILURE` на `REV2_N17_ACTUAL_CANONICAL_SORTED_POPCOUNT`. |

Положительный корень передаёт независимый `u32`, из которого используются ровно младшие 17 бит. Ожидаемая маска `((1 << 17) - 1) ^ (((1 << 17) - 1) >> popcount)` размещает единицы в старших позициях. Проверка маски вместе с каноничностью каждого байта устанавливает порядок и исходный popcount. Cover четвёртого сдвига требует хотя бы одну единицу в rel0–12 и четыре нуля в rel13–16. S13 оставляет максимум 1 на rel12, каждый нулевой хвостовой байт заставляет actual вставку сдвигать максимум на следующий правый край.

Контроль передаёт `0x0000_0001` в общий `check_network::<true>`. После actual normal return маска `0x0001_0000`, после `v[1] ^= 1` маска `0x0001_0001`. Сдвиг, mixed input и normal return проверяются до порчи. q и внешние `v[0]`, `v[18..34]` произвольны. Координата общего поста на Std `49811849392302943d45b02beb4b0403509b9447` — `core/src/slice/sort/shared/smallsort/verify/rev2_n17.rs:87:5` в `slice::sort::shared::smallsort::verify::rev2_n17::check_network::<true>` для regular. Stock export должен дать тот же ID, label, class `assertion` и совместимый file/line. Числовой суффикс ID устанавливается по будущим native каналам. [Общий пост](/root/verify-rust-std-rev2-n17-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n17.rs:87) · [Сверка каналов](/root/kani-rev2-n17-control-w14/ch8-cal1/results.py:164)

Report сохраняет native outcome, `MATCHED` и ресурсную оценку раздельно. `COMPOSITE_WITHIN_PROFILE` требует exact roster, полные anchors и попадание в профиль у всех трёх слотов и успешную финальную аттестацию. `PAIR_WITHIN_PROFILE` относится к двум битовым слотам и оставляет byte driver самостоятельным обязательством. Timeout/RSS остаются незавершёнными. [Классификация](/root/kani-rev2-n17-control-w14/ch8-cal1/report.py:107)

## Локальные пины и бюджеты

| Роль и worktree | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| Вход задания в g0 | `f5778cc360354eee90c2a523cdd231516e3f014a` | `8b082c7411c2fab13bac9b814e795c92a045697c` | `37dc780cecb6929ed241b387fcd4f1fa55bed08d` |
| [Std](/root/verify-rust-std-rev2-n17-w14), `work/rev2-n17-w14` | `49811849392302943d45b02beb4b0403509b9447` | `642b76724b9a702ec7f600059a615ad3438d6719` | `9a8bb36e3b85d9f5729bdfa3b02e434d26c16470` |
| [Control](/root/kani-rev2-n17-control-w14), `work/rev2-n17-control-w14` | `ee6156445c9cdd30912d1b3a41f9e4b2444caf25` | `750951a6f4c627e06f0934b2bcc8a35cab92f86e` | `3e5c0508fdfa1a460906cb461a890eb2914bd295` |
| [Review-trigger](/root/kani-rev2-n17-trigger-w14/control), detached, `review/rev2-n17-trigger-w14` | `a93dc1887c62823dc914fb9eaddc6e3123ddc254` | `750951a6f4c627e06f0934b2bcc8a35cab92f86e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`. Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Будущий workflow сверяет fork `Tiramisu-Cake/kani`, push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact event SHA, clean detached checkout, sole parent и фактический `HEAD^{tree}`. Независимая Actions variable `CH8_REV2_N17_TRIGGER_TREE` передаётся в `REV2_N17_TRIGGER_TREE`. Ожидаемое значение для ревью — `750951a6f4c627e06f0934b2bcc8a35cab92f86e`. `pins`, `sources` и `finish` читают pin извне, последние два сверяют сохранённый admission receipt. Upload требует успешные `pins` и `finish`. Review-trigger локальный, Actions variables не менялись. [Workflow](/root/kani-rev2-n17-control-w14/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n17-control-w14/ch8-cal1/request.py:161)

| Вход | SHA-256 |
| --- | --- |
| [Frozen request](/root/kani-rev2-n17-control-w14/ch8-cal1/CI-REQUEST.json) | `b44ea1a5fde848213fa2380a411a2cd3d03e5e7b90240f174be9d58655c938a7` |
| Canonical roster, JSON с сортированными ключами и разделителями `(",", ":")` | `51592c9e98bf9102cd314cda4351db2c619319d0bbb4e808ff5701778a3ddcdf` |
| [Std overlay bundle](/root/kani-rev2-n17-control-w14/ch8-cal1/std-overlay.bundle), 22 164 байта | `7a82f45f516cc29f498831809524f400ee9f6d13d8237eb28ea3d67893b4be5f` |

Одна job Ubuntu 24.04, CBMC 6.11.0/CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, штатные safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Перед discovery ранний preflight до 180 с ищет compile witness `core` с восемью флагами и сохраняет первые compiler errors при отказе. Discovery сравнивает `selector/kind/file` при семи унаследованных cfg и при добавлении `kani_smallsort_rev2_n17`, требует ровно три новых plain Proof и сохранение остального инвентаря. Для каждого exact слота выделяются отдельные cwd, Cargo/Kani targets, TMPDIR и export. Caps проекции и артефакта составляют 4 MiB и 96 MiB. [Runner](/root/kani-rev2-n17-control-w14/ch8-cal1/run.py)

| Стадия | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup, compile, discovery | 45:00 | 45:00 |
| Три слота | 10:15 | 55:15 |
| Финальная аттестация | 2:00 | 57:15 |
| Finish | 5:00 | 62:15 |
| Upload | 7:00 | 69:15 |
| Резерв | 9:00 | 78:15 |
| Job | 90:00 | 90:00 |

Последние старты в порядке roster — **45:00, 48:25, 51:50** от epoch. На слот даются 180 с cold wall, 10 с reap, 5 с receipt и 10 с запаса для запуска. Отбор требует VT ≤120 с, пик группы ≤4 GiB и резерв памяти 2 GiB. Таймауты шагов workflow по порядку — 1, 2, 4, 5, 4, 3, 15, 46, 14, 6 и 7 мин. `pins` до 45 с и два последовательных self-test watchdog по 70+5 с занимают не более 195 с из 240 с. `sources` ограничен 120 с. `measure` от входа в CLI ограничен 800 с из 840 с, включая 60 с для входных проверок и 5 с для журнала. Если шаговое окно короче глобального, latest starts сдвигаются раньше с сохранением полного бюджета слота. `finish` использует более раннюю из 62:15 от epoch и 290 с от входа в CLI при внешнем таймауте 360 с.

После возврата supervisor checkpoint с наблюдённым исходом процесса и reap атомарно записывается перед проекцией. Deadline receipt — минимум из конца слота и `supervisor_return + 5s`, проекция обрывается на секунду раньше. Просроченный receipt получает late, прерванная запись сохраняется для ограниченного по времени повтора в `finish`. Следующий слот требует подтверждённый reap предыдущего и собственное открытое окно. При потере reap запуск блокируется. Для засчитанного результата требуются полные обязательные anchors и сохранённая проекция. [Receipt и исполнение](/root/kani-rev2-n17-control-w14/ch8-cal1/run.py:473) · [Финализация](/root/kani-rev2-n17-control-w14/ch8-cal1/report.py:186)

Ресурсы N17 пока оценены по ориентирам. Byte driver N32 с тремя вставками имел VT 8,39 с, cold wall 35,73 с и 2,11 GiB. Exact S13 base1/len17 имел 13,65 с, 41,73 с и 2,10 GiB. У сквозного битового N32 были 125,58 с, 151,56 с и 3,83 GiB. В N17 один S13 и четыре вставки, путь короче. Реальное время решателя и пик группы на новых трёх корнях остаются неизвестны до измерения. [N32](REV2-N32-CONSUMER-RESULTS-ANALYSIS.md) · [S13](REV2-S13-GEOMETRIES-RESULTS-ANALYSIS.md) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

## Локальная проверка

- Видимость новых Rust-имён сверена от мест использования. `verify` находится под `cfg(kani)`, `rev2_n17` под конъюнкцией восьми cfg. `super::super` указывает на `smallsort` и даёт дочернему модулю доступ к обоим actual функциям. `super::cal1_model` виден соседнему модулю, `with_q/q` доступны в `verify`, `u8: FreezeMarker` через `Freeze`. `core::kani` создаётся `kani_core::kani_lib!(core)` и предоставляет используемые macros/observers. Остальные имена определены в новом модуле или берутся из core prelude. Целый runtime diff пуст. Восстановление cfg-off убирает только lint и opt-in регистрацию и даёт исходные blobs.
- `rustfmt --check --edition 2024 --config use_small_heuristics=Max` прошёл указанным nightly-2026-11-19 на обоих Rust-файлах с `skip_children=true,reorder_modules=false` для сохранения прежнего порядка module registry. `git diff --check` прошёл на Std, control, review-trigger относительно его родителя и handoff. Cold argv и 12 непересекающихся target/export/tmp путей проверены синтетически. Извлечённые 45 пар и модель четырёх вставок дали ожидаемую маску на всех 131 072 входах и подтвердили четвёртый сдвиг для всех 8 191 масок, удовлетворяющих предикату. Этот локальный перебор проверяет привязку формулы и witness.
- Полный suite последовательно прошёл **106/106** на обычной шкале (23,117 с, wall 23,623 с) и **106/106** при `monotonic() = 60 + elapsed` (23,243 с, wall 23,778 с). Проверены exact roster/gate, два положительных исхода и ожидаемый контроль, посторонние отказы, несовместимые ID и координаты, отсутствие anchors, compile/discovery failures, медленная проекция и запись receipt, поздняя финализация, потеря reap и поздний старт. Зависимые чтения, включая `finish`, используют шкалу соответствующего теста.
- `git bundle verify`, `list-heads` и `unbundle` прошли на отдельной bare shallow базе depth 2 через локальный Git transport без alternates. До импорта новый overlay отсутствовал. После импорта сверены восемь commit/tree/sole-parent и layout, base HEAD, refs и shallow boundary сохранены. YAML разобран, все shell-блоки проверены `bash -n`, встроенные Python-блоки проверены на синтаксис, сроки и upload gate сверены.
- Exact локальный review-trigger с синтетическим push payload прошёл `pins` и `finish`. Индекс содержит три `NOT_STARTED` и `proof_credit=NONE`. Старый tree, неверный tree, одно старое имя pin и подменённый payload SHA отклонены в `pins`, `sources` и `finish`.

Реальные compile/discovery, native anchors и ресурсы новых Proof остаются за будущим запуском после независимого ревью и GO. На подготовке Cargo, rustc, Kani и CBMC локально не выполнялись. Push, CI и публикация не выполнялись.
