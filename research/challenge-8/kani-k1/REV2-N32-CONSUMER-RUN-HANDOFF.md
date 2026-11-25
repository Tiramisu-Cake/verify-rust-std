# REV2 N32 · пакет запуска на ревью

`READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Локальный пакет готов для независимого ревью control. Разрешение `f345942a4c` относится к подготовке четырёх exact singleton. Dispatch требует отдельного GO. Нативные результаты и составной допуск N32 остаются открыты. [Ревью Std](REV2-N32-CONSUMER-REVIEW.md) · [Исходный handoff](REV2-N32-CONSUMER-HANDOFF.md)

## Идентичности

| Роль | Pin |
| --- | --- |
| Входной g0 | `f345942a4c1950c05a2b265d5bdef981f1e65741` |
| Локальный control | `b3b6b42b845e2a590149d6d0d2e430c3a2f95427`, tree `adda4d22098a1bbf99e77ac674b9eaa3c95cee61`, единственный parent FIX1 `efaf43d82324fd4d76d07e6bf77bbc7a78434700` |
| Checkout | Sparse worktree `/root/kani-rev2-n32-consumer-control-w14`, ветка `work/rev2-n32-consumer-control-w14` |
| Std CI-base / tree | `dab03cf510df5c35141cde49f1368b1242f5035e` / `7fd542ad59723ff2beeacb9632fb0568e81b0655` |
| Std overlay / tree / parent | `b93859fb447a39c0c8c7d854f70dedf9a47b263f` / `562a2fac5ed349a9fc09097789d0816f200c3819` / `217b8efaa6c9c0d6e5d44f77e98d74bd5493360a` |
| Stock Kani / tree | `9834c96ce90ff57d8495416530b080dc3d52ce25` / `938e9932cb2127239afb4f093f6302652c053398`, launcher 0.68.0 |
| Frozen request SHA-256 | `5cefc5d2e4985f188775888018c18f6d33ed8b1f9c66afa32afe00dfd57e78a2`, 7 052 байта |
| Canonical roster SHA-256 | `b8b7a67b996a9cad5a51b278d64cea75189dfb9f8b7e91bb41c3e06940f7a037`, JSON-массив в порядке исполнения, ключи отсортированы, разделители `(",", ":")` |
| Bundle SHA-256 | `21dda5581b93962535d440766567a734a2f413e0df1dc76507fcd89d4c29f046`, 19 596 байт |
| Будущий trigger | Fork `Tiramisu-Cake/kani`, push в `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, единственный parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`, tree `adda4d22098a1bbf99e77ac674b9eaa3c95cee61` |
| Независимый Actions pin после отдельного GO | `CH8_REV2_N32_CONSUMER_TRIGGER_TREE=adda4d22098a1bbf99e77ac674b9eaa3c95cee61` |

В рабочий пакет входит один [bundle](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/std-overlay.bundle), объявляющий только `b93859fb447a39c0c8c7d854f70dedf9a47b263f HEAD`. `sources` проверяет Std и Kani checkout, импортирует объекты, сверяет цепочку tree/sole parent CAL1 → CAL2 → FIX3 → S13-binding → S13-geometries → N32 consumer и проверяет точный cfg-off layout. Последняя дельта — opt-in регистрация, запись check-cfg и новый файл. Actual `smallsort.rs` имеет blob `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`, корни — `7c7823d549dbd2203f3dd8f0b1307b618c474f53`. [Frozen request](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/CI-REQUEST.json) · [Layout gate](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/request.py)

`pins`, `sources` и `finish` вычисляют Git tree clean detached checkout и сравнивают его с независимым Actions pin, отдельно от SHA, event payload, ref и sole parent. После `pins` сохраняется admission receipt. Последующие шаги сверяют его с повторной аттестацией. Upload требует успешного `pins`, `trigger_admitted=true` и успешного `finish`. Actions variable и remote refs остались вне локальной подготовки. [Workflow](/root/kani-rev2-n32-consumer-control-w14/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/request.py)

## Roster и нативные условия

| Слот | Exact selector | Ожидаемый исход | Latest start от epoch |
| --- | --- | --- | ---: |
| `N32-INSERT-LEFT-BYTES` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_insert_left_bytes` | `VERIFIED`, exit 0, numeric/count/q/frame, 3 covers | 2700 с |
| `N32-INSERT-RIGHT-BYTES` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_insert_right_bytes` | `VERIFIED`, exit 0, numeric/count/q/frame, 3 covers | 2905 с |
| `N32-ACTUAL-BITS` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_actual_bits` | `VERIFIED`, exit 0, mask/q/frame, 5 covers | 3110 с |
| `N32-ACTUAL-CORRUPT` | `slice::sort::shared::smallsort::verify::rev2_n32_consumer::n32_actual_corrupt` | `FAILED`, exit 1, q/frame, 5 covers и ровно один ожидаемый родной отказ | 3315 с |

Профиль — одна job Ubuntu 24.04, четыре последовательных `--harness … --exact --jobs=1`, OB12, unwind36 из атрибутов, CBMC 6.11.0/CaDiCaL, `--no-assert-contracts`, проверки memory safety/overflow/unwind/undefined-function/assertion-reach ON, uninit/validity OFF. Режим четырёх корней — plain Proof с пустыми stubs и Replace. К пяти унаследованным cfg добавлен `kani_smallsort_rev2_n32_consumer`. Атрибут merge loop invariant отсутствует в pinned Std. Preflight требует cfg-on compile witness для `core` и сравнивает две полные discovery-выдачи по selector/kind/file. При включении opt-in допустимо ровно четыре новых Proof из этого модуля, унаследованные Check/Replace остаются на своих местах. Roster исполнения берётся из request. Stock export каждого слота проверяет kind и отсутствие stubs/Replace. [Runner](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/run.py) · [Область ревью](REV2-N32-CONSUMER-REVIEW.md#rust-и-границы-пакета)

Контроль принимает один `assertion FAILURE` на `REV2_N32_ACTUAL_CANONICAL_SORTED_POPCOUNT` в `…::rev2_n32_consumer::check_network::<true>` на `rev2_n32_consumer.rs:54:5` в regular. В stock обязателен тот же фактический native ID, класс, метка, файл и строка 54. Native ordinal определяется по результату. Два frame asserts и все пять обязательных covers должны пройти на каждой стороне пары. Для вставок проверяются их четыре assertion-метки и три cover-метки на слот. Несогласованные каналы, лишний отказ, неполные результаты или отсутствующие anchors исключают совпадение. Сгруппированные safety-свойства и достижимость выходов сверяются по pinned call sites при приёмке. [Oracle](/root/verify-rust-std-rev2-n32-consumer-w14/library/core/src/slice/sort/shared/smallsort/verify/rev2_n32_consumer.rs:54) · [Парсер](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/results.py)

## Время, ресурсы и receipts

На слот выделено 180 с cold wall, 10 с reap и 5 с receipt, плюс 10 с запаса в расчёте latest start. Отбор — VT ≤120 с, RSS группы ≤4 GiB, резерв Ubuntu 2 GiB. Каждому слоту выделены отдельные cwd, cargo/kani target, TMPDIR и export. При cutoff сохраняются наблюдавшийся exit, причина остановки, reap, последний подтверждённый этап и имеющиеся resource/native anchors. Следующий слот требует подтверждённый reap и своё доступное окно. Профиль setup отдельно использует унаследованный cap 10 GiB. Приёмка по ресурсам учитывает все четыре строки через `roster_within_profile`, битовая пара также имеет собственную диагностическую классификацию. [Модель ресурсов](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/report.py)

| Бюджет от epoch первого шага | Время / отсечка |
| --- | --- |
| Setup вместе с preflight и discovery | 45:00 |
| Четыре слота с запасом | +13:40 → 58:40 |
| Итоговая аттестация | +2:00 → 60:40 |
| Finish / публикация receipt | +5:00 → 65:40 |
| Upload | +7:00 → 72:40 |
| Резерв / внешний job limit | +9:00 → 81:40 / 90:00 |

Пределы Actions по шагам, в порядке workflow — 1, 2, 3, 5, 4, 3, 15, 46, 22, 5 и 7 минут. Внутренние бюджеты `pins` 45 с плюс две suite с watchdog по 50 с и 5 с до kill, `sources` 120 с, setup/prepare до 45 минут, `measure` ≤21 минуты от входа в CLI с сохранением глобальной отсечки и лимита отдельного слота. `finish` захватывает повторный Git gate и отчёт до более ранней границы — общего publication deadline или 290 с от входа в CLI. Так остаётся 10 с до таймаута шага. Паузы между ранними шагами после epoch расходуют общий бюджет setup. [Границы CLI](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/run.py)

Receipt deadline — минимум из `supervisor_return + 5s` и конца окна слота. Checkpoint сохраняет процесс, cleanup и фазу до проекции. Проекция получает отсечку на секунду раньше receipt. После исходного окна просроченный receipt остаётся с отметкой просрочки, даже если его удалось дописать. `finish` очищает partial files через `partial_path`, отдельно от `pending`. Ошибка записи журнала измерений сохраняет исходное исключение. Итоговый index хэширует структурированные receipts и присутствующие проекции. [Receipt path](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/run.py) · [Финализация](/root/kani-rev2-n32-consumer-control-w14/ch8-cal1/report.py)

## Локальная проверка кандидата

- Python 3.12.3 suite — **104/104 за 23,075 с** на обычных часах и **104/104 за 23,948 с** при `time.monotonic() = 60 + elapsed`. Проверены cfg-off/on дельта, wrong category/file, missing/partial/wrong-type результаты, mismatch функции/колонки/native ID, stale trigger, gates под дедлайном, поздние и повторные receipts, partial рядом с pending, отклонение при неподтверждённом reap.
- На точном tree control в отдельном временном shallow detached fixture с синтетическим событием старый pin отклонён в `pins`, `sources` и `finish`. С новым pin прошли `pins` и `finish`, итоговый index содержит четыре `NOT_STARTED` и `proof_credit=NONE`. Синтетический commit жил только в fixture.
- `git bundle verify`, `list-heads` и `unbundle` прошли в отдельной bare shallow-базе depth 2 от локального Git-источника. До импорта overlay отсутствовал, alternates отсутствовали. После импорта совпали все шесть commit/tree/parent, cfg-off layout и два ключевых blob. HEAD, refs и shallow boundary сохранились.
- YAML разобран и сверен по всем 11 timeout, env и условиям upload. `bash -n` прошёл для всех shell-блоков workflow. `git diff --check` прошёл для control и Std. Указанный `nightly-2026-11-19/bin/rustfmt` прошёл для нового Rust-файла с `use_small_heuristics=Max` и для реестра адресно с `skip_children=true,reorder_modules=false`, сохраняя унаследованный порядок.

Cargo, rustc, Kani и CBMC локально не запускались. CI, push и изменение Actions variables не выполнялись. Открытые пункты после ревью — реальный core compile/discovery, четыре нативных исхода и ресурсный профиль на Ubuntu.
