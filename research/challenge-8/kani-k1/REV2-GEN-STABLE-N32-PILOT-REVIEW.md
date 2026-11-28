# REV2 пилот general Wide и stable u64 на N32 · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-28. **GO_WITH_NITS**, блокеров и should-fix нет. Пины: Std `88d05a138c4bca054de4ec1215ceb7f54087c3df` / tree `7dd117f525`, parent `93d0c4a18d`; Control `ec27bc206c745ac6babd6acd4862f7ac9282fea5` / tree `9fda6b9c8ee8565fe7f18a0de9e4a1429b391ed2`, parent `bfc6f20a86`; review-trigger `df269de44349399bc16f703d70ed4a5faa8ee56a`, тот же tree, sole parent `467af9cb8d`. CI-REQUEST `eddd1856…`, bundle `c806269c…` (98 035 байт, один HEAD `88d05a1`, prerequisite `dab03cf510`, 37 коммитов, `git bundle verify` проходит), relay `c8b4c070…` без изменений, roster `5845e394…` — пересчитаны. Задание g0 `e9c072be34`, handoff `67fd79cc23`.

1. Nit. `request.py:1775–1781`: цикл `for p in range(16): for j in range(16)` в `check_n32_pilot_source` — чистая арифметика, от исходника не зависит и ни одну мутацию не отвергает. Гарантию дают побайтный рендер и bounds checks Kani; handoff называет цикл gate («Индексы ограничены статически»). Удалить цикл или описать как инвариант.
2. Nit. Шаг pins `.github/workflows/ch8-q-pilot.yml:46` — timeout 8 мин на четыре последовательных suite; локально 82–101 с на прогон, итого 5,5–6,7 мин. Раннер на 20 % медленнее провалит pins (fail closed, потерянный прогон). Предложено 10 мин.
3. Nit (не воспроизведено). На свежем clone trigger первый прогон suite дал `FAILED (failures=1, errors=12)`, имена не сохранены; следующие три прогона на том же clone — 181/181. Возможен тест, чувствительный ко времени или состоянию; в CI сработает fail closed на pins.
4. Nit (текст handoff): фикстура `n32_pilot_module.fixture` равна срезу модуля от `:1943` до конца, а не всему blob `16c8b858…`; `wide_n12_n14` импортирует ещё `UnstableSmallSortTypeImpl`; `:35:5` — в `rev2_gen_stable_n16_pilot.rs` (`GEN_N16_WIDE_COMPARATOR_CALLED`), а не в `rev2_u64_n13.rs`.

Проверено и в порядке: Std — старый файл побайтный префикс (78 086 → 104 752 байт), правки только хвост модуля и `core/Cargo.toml:82`, blob `smallsort.rs` `0b77c3db` без изменений, вероятных ошибок rustc нет. Правый S8 совпадает с `smallsort.rs:300–305` при len=32 (`s+16`, `d+16`, `d+40`), выходы стартуют неинициализированными, frame V34/D[0..16)/D[24..40). Fill rel15 — `:329–330`, единственный `assume` — отсортированный префикс ключей, позиция вставки точная (`:701–735`), frame D[0..16)/D[32..48)/V34. Четыре Check — базы курсоров `:1004–1012` при m=16, tie-правила `:883–888`/`:916–921`, достижимые состояния в домене, выход up на `d+32` внутри D48, down через `wrapping_sub`, scoped `modifies`, `assume` = `requires`, семь covers достижимы. N32 чётна, ветка нечётного центра не исполняется — тексты верны. Control: семь строк, все `STOCK_PIPE`, `RELAY_SLOT_ID=None`, лимиты 120 с VT / 180 с cold / 4 GiB / резерв 2 GiB, job 110 мин, measure 29 мин, старты 3300+205·i до 4530, 34 флага cfg, индекс `smallsort-rev2-gen-stable-n32-pilot-artifact-v1`, guards trigger. Render gate отверг четыре мутации ревьюера. Гигиена пяти коммитов в порядке. Номера строк handoff совпадают с кодом.

NOT_RUN: rustc/Cargo/Kani/CBMC/rustfmt (компиляция, discovery 186/193, нативные координаты, ресурсы N32), YAML, `bash -n`, прогоны со сдвигом часов, shallow fetch bundle.

Решение координатора: GO откладывается до раунда правок. Nit 3 — ровно сценарий CI (первый прогон на свежем checkout); причину выяснить и устранить. Nit 2 — поднять timeout pins до 10 мин. Nit 1 и 4 — в том же раунде.

## R2 · FIX1 (handoff 0e40b67200)

Тот же `smallsort-reviewer`, 2026-11-28. **GO**, новых замечаний нет. Пины пересчитаны: Control `79a5ec2fb89f643559e44bdab0f534d6e827ec08` / tree `c1bbb6dbe41ce69c93a65b42fb45655d78da2aac`, sole parent `ec27bc206c` (fast-forward); review-trigger `e9206385e8d02e62af407ce568db253683ce4215`, тот же tree, sole parent `467af9cb8d`. Без изменений: Std `88d05a138c`, CI-REQUEST `eddd1856…`, bundle `c806269c…`, relay `c8b4c070…`, roster `5845e394…` и bindings `623ae996…` (внутри неизменного CI-REQUEST, константы `request.py` не правились). Гигиена двух новых коммитов в порядке.

- Diff `ec27bc2`→`79a5ec2`: три файла, +7/−9. `ch8-q-pilot.yml:46` — timeout pins 8 → 10 мин (nit 2). `request.py:1774–1777` — арифметический цикл заменён комментарием об инварианте рендера, побайтное сравнение и `fill.count(...)` сохранены (nit 1). `test_relay.py:124–127` — cap тестовой фикстуры `RelayFixture` 64 → 24 MiB, `disk_reserve_bytes` 1 MiB и `term_grace` 0,5 без изменений.
- Nit 3: объяснение исполнителя согласуется с кодом. `stdout_relay.py:112–113` требует свободного места ≥ cap + reserve; для прежней фикстуры это 68 157 440 байт — ровно число из ошибки; корень сервера был заполнен почти на 100 %. Крупнейший синтетический поток 22 260 361 байт (≈21,23 MiB) < 24 MiB. Смысл тестов сохранён: нижняя граница 16 MiB (`:164`), собственный cap 1 MiB в тесте остановки (`:246`), тест резерва (`:306`), тесты spill-prefix 17 MiB не зависят от cap. Боевые значения (chunk 64 KiB, cap 4 GiB, reserve 2 GiB) проверяются в `:826–827`; frozen-request по-прежнему отвергает relay на любом слоте и cap 8 GiB; в N32 relay ни на одном слоте.
- Nit 4: три правки текста handoff внесены (`:74`, `:38`, comparator cover `rev2_gen_stable_n16_pilot.rs:35:5`).
- Свежий depth-2 clone trigger `e9206385e8`, около 1,3 GiB свободно: suite 181/181 за 93,2 с с первого прогона.

NOT_RUN: rustc/Cargo/Kani/CBMC; воспроизведение нехватки места на ext4-образе 100 MiB; шаг pins с четырьмя шкалами (исполнитель сообщает 361 с), CLI trigger, YAML, `bash -n`. Выводы R1 по модулю Std и runner сохраняются: Std, CI-REQUEST, roster, bindings, bundle и лимиты побайтно те же.

Решение координатора: GO, [REV2-GEN-STABLE-N32-PILOT-GO.md](REV2-GEN-STABLE-N32-PILOT-GO.md).
