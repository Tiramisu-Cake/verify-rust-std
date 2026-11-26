# REV2 · нативные контроли N14–N16

`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`. Пакет содержит три exact отрицательных слота для открытых контролей N14–N16. Ревью g0 `b4d1371043f595924d783af2b5ada0d9c1b16eff` приняло функциональные рёбра всех трёх длин. Статус их контролей остаётся `OPEN` до получения и ревью нативных результатов. N13 утверждён отдельно в g0 `ef67ae56eae496c45902b08b75e60bebbef09efa`. [Офлайн-ревью](REV2-N13-N16-OFFLINE-REVIEW.md#минимальный-нативный-контроль-для-открытых-строк) · [Утверждение N13](REV2-N13-ADMISSION-APPROVAL.md)

## Общий helper и exact roster

Каждый plain `Proof` вызывает один `check_network::<N>()`. Он берёт инициализированный V34, независимый `q: u8` и произвольный внешний frame, задаёт активные байты `1,0,…,0` и вызывает actual `small_sort_network::<u8, KeyLess<u8>>` на `v[1..1+N]` в строке 41. После нормального возврата cover на 43 предшествует записи `v[1] ^= 1` на 44. Затем проверяются q, все внешние байты `v[0]` и `v[1+N..34]`, каноничность и маска. Маска имеет bit0 на младшем адресе и сравнивается с `1u32 << (N-1)`. [Helper](/root/verify-rust-std-rev2-n14-n16-control-w15/library/core/src/slice/sort/shared/smallsort/verify/rev2_n14_n16_control.rs:30)

В actual caller `N < 18` ведёт в единственный S13, driver с offset 13 и возврат по `no_merge`. S13 переносит единственную единицу в rel12. Каждый следующий ноль вызывает `0 < 1` на `smallsort.rs:706`, копирует единицу вправо на 722 и возвращает ноль через `CopyOnDrop` на 362. Предыдущий ноль останавливает сдвиг. На `smallsort.rs:761` driver останавливается на первом `tail == v_end`. Эта привязка сдвигов дана по исходнику и witness. Обязательные native covers — actual компаратор `CAL1 q actual comparator executed` на `cal1_model.rs:28:9` и `REV2_N14_N16_NORMAL_RETURN` на 43:5. [Caller](/root/verify-rust-std-rev2-n14-n16-control-w15/library/core/src/slice/sort/shared/smallsort.rs:367) · [Вставка](/root/verify-rust-std-rev2-n14-n16-control-w15/library/core/src/slice/sort/shared/smallsort.rs:701) · [Компаратор](/root/verify-rust-std-rev2-n14-n16-control-w15/library/core/src/slice/sort/shared/smallsort/verify/cal1_model.rs:28)

| Слот | Селектор без общего префикса | Сдвиги / end (abs) | Ожидаемая маска → после записи |
| --- | --- | --- | --- |
| `N14-WITNESS-CORRUPT` | `n14_witness_corrupt` | 14 / 15 | `0x2000` → `0x2001` |
| `N15-WITNESS-CORRUPT` | `n15_witness_corrupt` | 14, 15 / 16 | `0x4000` → `0x4001` |
| `N16-WITNESS-CORRUPT` | `n16_witness_corrupt` | 14, 15, 16 / 17 | `0x8000` → `0x8001` |

Префикс каждого exact selector и функции matcher — `slice::sort::shared::smallsort::verify::rev2_n14_n16_control::`. Common failure anchor — `REV2_N14_N16_SORTED_POPCOUNT`, класс `assertion`, `core/src/slice/sort/shared/smallsort/verify/rev2_n14_n16_control.rs:58:5` в `check_network::<14>`, `check_network::<15>` и `check_network::<16>` соответственно. Matcher требует ровно один `FAILURE` в regular и ровно один в stock export с одинаковыми native ID, классом и меткой. В regular сверяются файл, строка, колонка и специализация. В stock RFC 0015 сверяются файл и строка. Числовой суффикс property ID берётся из будущих согласованных native каналов. [Frozen request](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/CI-REQUEST.json) · [Matcher](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/results.py:164)

Для `FAILED` / exit 1 с `MATCHED` обязательны `SUCCESS` на `REV2_N14_N16_Q_FRAME` (45:5), `REV2_N14_N16_V34_FRAME` (46:5), `REV2_N14_N16_CANONICAL` (57:5) и оба covers `SATISFIED` в regular и stock. Matcher сверяет суммы проверок и buckets в двух каналах, включая служебные `UNREACHABLE`. Неожиданный отказ, неполная проекция или потеря обязательных anchors исключают принятие слота. Report хранит наблюдённый исход отдельно от `MATCHED` и оценки профиля. `COMPOSITE_CONTROL_WITHIN_PROFILE` требует все три exact слота в порядке таблицы, своевременные полные receipts, подтверждённые reap/sampler, финальную аттестацию и соблюдение лимитов. Индекс привязывает размер и SHA-256 сохранённых receipt и projection к слоту. [Отчёт](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/report.py:105)

## Пины и хэши

| Роль | Commit | Tree | Sole parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-n14-n16-control-w15), `work/rev2-n14-n16-control-w15` | `5c24f5bc963e654b02ab28d166ca46c83538c3ba` | `1824e63f160f31afb0e589cb9e0970942938b03f` | `9a8bb36e3b85d9f5729bdfa3b02e434d26c16470` |
| [Control](/root/kani-rev2-n14-n16-control-w15), `work/rev2-n14-n16-control-w15` | `9de17e15a840c2fe8288f8b1f4f2443043587890` | `1ae3500db291b1a2eecf41a5a346755882b54361` | `3e5c0508fdfa1a460906cb461a890eb2914bd295` |
| [Local review-trigger](/root/kani-rev2-n14-n16-trigger-w15/control), `review/rev2-n14-n16-trigger-w15` | `537278cd3da8943f3f3c542af68f56425f471880` | `1ae3500db291b1a2eecf41a5a346755882b54361` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`. Std CI-base `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Bundle объявляет только HEAD нового Std-overlay с указанной CI-base как prerequisite. Runtime `smallsort.rs` побайтно совпадает с parent, blob `0b77c3dbb3b767ba35281a2a686aa477ff1344c5`. `cal1_model.rs` совпадает, blob `236394dcfb1ff571ee6f816391f7b2e00cc9e630`. Дельта Std ограничена check-cfg в `library/core/Cargo.toml` (blob `362532de4ed68c31c12a9b7c78a50a2ad6a068d3`), регистрацией в `smallsort/verify.rs` (blob `be00299a13379e890332b8a2309828b4d5dbe1f3`) и новым `rev2_n14_n16_control.rs` (blob `0bd73ed7ac93e5e0b36d11c855aae4f11580b976`). [Layout guard](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/request.py:292)

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/CI-REQUEST.json), 6 787 байт | `fcd15d0319643ef4e053cfe0ac421d6c853d5addd79029783558b2dda1c42e73` |
| Canonical roster, UTF-8 JSON с сортированными ключами и разделителями `(",", ":")` | `a76d7078973ed15225a031200f235e85a4b56b82071908cea6ddbae99fc24b89` |
| [std-overlay.bundle](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/std-overlay.bundle), 21 769 байт | `5babf8a4e550286c2169d8137cbf035cb0f38880138249d849f7594a0dc3f617` |

Workflow получает ожидаемый tree из отдельной Actions variable `CH8_REV2_N14_N16_CONTROL_TRIGGER_TREE` через `REV2_N14_N16_CONTROL_TRIGGER_TREE`. Значение для ревью — `1ae3500db291b1a2eecf41a5a346755882b54361`. Проверяются `Tiramisu-Cake/kani`, push ref `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact checkout SHA и payload `after`, clean detached checkout, указанный sole parent и фактический `HEAD^{tree}`. `sources` и `finish` повторяют gate и сверяют receipt из `pins`. Upload требует успешных `pins`, `trigger_admitted=true` и успешный `finish`. Actions variable не выставлялась. [Workflow](/root/kani-rev2-n14-n16-control-w15/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/request.py:161)

## Профиль и бюджеты

Одна job Ubuntu 24.04 X64, CBMC 6.11.0 / CaDiCaL, OB12, unwind36, `--exact --jobs=1 --no-assert-contracts`, штатные safety/overflow/unwind/undefined function/assertion reach ON, uninit/validity OFF. Plain Proof без stubs, Replace, loop contracts и `should_panic`. Compile preflight до 180 с ищет witness компиляции `core` со всеми восемью cfg, сохраняет первые ошибки компилятора при отказе. Discovery сравнивает инвентарь с семью унаследованными cfg и с добавленным `kani_smallsort_rev2_n14_n16_control`. Допустимая дельта — ровно три указанных plain Proof с точными файлами. Cold cwd, tmp, Cargo/Kani targets и export изолированы для каждого слота. Setup cap 10 GiB, cap группы каждого слота 4 GiB с резервом 2 GiB, отбор VT ≤120 с. Лимиты проекции и артефакта 4 и 96 MiB. [Runner](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/run.py) · [Лимиты владельца](OWNER-DECISION-LIMITS-20261125.md)

| Стадия | Бюджет | Отсечка от epoch |
| --- | ---: | ---: |
| Setup и discovery | 45:00 | 45:00 |
| Три слота с запасом старта | 10:15 | 55:15 |
| Финальная аттестация | 2:00 | 57:15 |
| Finish | 5:00 | 62:15 |
| Upload | 7:00 | 69:15 |
| Резерв | 9:00 | 78:15 |
| Job | 90:00 | 90:00 |

Слот занимает 180 с cold wall + 10 с reap + 5 с receipt. На планирование старта добавлены 10 с на слот. Latest starts от epoch в порядке roster — 45:00, 48:25, 51:50. Следующий слот требует подтверждённого reap и открытого окна, потеря reap или исправности supervisor блокирует оставшиеся старты. Таймауты Actions по порядку шагов — 1, 2, 4, 5, 4, 3, 15, 46, 14, 6 и 7 мин. `pins` до 45 с и два последовательных suite с watchdog 70 с + 5 с до kill занимают максимум 195 из 240 с. `sources` ограничен 120 с из 180 с, внутренний `measure` 800 с из 840 с. При более коротком шаговом окне latest starts сдвигаются раньше с сохранением полного окна слота. `finish` ограничен минимумом из epoch +62:15 и 290 с от входа в CLI, внешний таймаут 360 с. [Часы и отсечки](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/run.py:99)

Фактический outcome/exit и reap атомарно записываются в checkpoint перед проекцией. Deadline receipt равен `min(slot_deadline, supervisor_return + 5s)`, проекция останавливается на секунду раньше. Поздняя или прерванная запись сохраняет исход в журнале для ограниченного повтора в `finish` с флагом late. При очистке частичных файлов `partial_path` отделён от словаря `pending`. Тесты с подменённым временем сохраняют одну шкалу на запись и зависимые чтения, включая `finish`. [Запись receipt](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/run.py:473) · [Повтор записи](/root/kani-rev2-n14-n16-control-w15/ch8-cal1/report.py:182)

## Офлайн-проверки

- Полный Python suite последовательно прошёл **106/106** на обычной шкале (27,334 с, wall 28,013 с) и **106/106** на `monotonic() = 60 + elapsed` (25,778 с, wall 26,350 с). Были проверены exact roster, изоляция argv, каждый кандидат на `MATCHED`, подмена специализации на другую длину, посторонние и лишние отказы, несовпадение ID/Location, обязательные anchors, поздний старт, compile/discovery failures, потеря reap, медленная проекция и receipt, запись рядом с частичным `.tmp` и обе границы `finish`. Запас до watchdog составил не менее 41 с на suite по измеренным wall.
- `rustfmt --check` прошёл указанным nightly-2026-11-19 с `--config use_small_heuristics=Max`, для реестра с сохранением порядка модулей и без обхода дочерних файлов. Проверены `git diff --check`, cfg-off восстановление blobs, 45 упорядоченных пар S13 и три конкретных witness с указанными сдвигами и координатами отказа. YAML разобран с запретом повторных ключей, шесть shell-блоков прошли `bash -n`, встроенный Python проверен на синтаксис, бюджеты и upload gate сверены.
- Bundle прошёл `verify`, `list-heads` и `unbundle` на отдельной bare shallow базе depth 2 по локальному Git transport без alternates. Сверены восемь commit/tree/sole-parent и layout, base HEAD, refs и shallow boundary сохранились.
- Exact локальный review-trigger прошёл `pins` и `finish` с синтетическим payload. Индекс содержит три `NOT_STARTED` и `proof_credit=NONE`, размеры и SHA-256 его членов совпали. Старый и неверный tree, только старая переменная и подменённый `after` отклонены в `pins`, `sources` и `finish`.

Реальные compile/discovery, native ID и статусы свойств на трёх новых roots, ресурсы и будущие хэши receipt/projection подлежат проверке после отдельного GO. Cargo, rustc, Kani, CBMC, CI, push и публикация на подготовке не запускались.
