# REV2 · диагностический пакет `u64` N13

**`READY_FOR_REVIEW` · `go=NOT_GRANTED` · `proof_credit=NONE`.** w13, будущий учёт — Item 2. Пакет содержит три последовательных холодных singleton на Ubuntu X64. Компиляция, фактический discovery, нативные результаты и измерения остаются открытыми до независимого ревью и отдельного GO координатора. [Задание](REV2-U64-N13-TASK.md) · [Лимиты](OWNER-DECISION-LIMITS-20261125.md)

## Пины и worktrees

| Объект | Commit | Tree | Единственный parent кандидата |
| --- | --- | --- | --- |
| База Std | `ee9eccad17d08988300e5b9e9e18d821889cdc92` | `b242e0d68a9666e2f6c965656cb9b27c6475df4a` | |
| [Std](/root/verify-rust-std-rev2-u64-n13-w13), `work/rev2-u64-n13-std-w13` | `79030c96c86f6bae0ef3498e3323a5ba919925c0` | `e40eeb1347f75ab9a3dcbf4659c6aed1f887b3fb` | `ee9eccad17d08988300e5b9e9e18d821889cdc92` |
| База Control | `17d0184168945306f80352c70993c215bef40c92` | `16daa4eabbb186bd4822fbe79a3d56dfb74d89a7` | |
| [Control](/root/kani-rev2-u64-n13-control-w13), `work/rev2-u64-n13-control-w13` | `027f81e0712dcc106266fd1af577af388bace5bc` | `794c9c5bb6872053a581d85731f4bd4e10772477` | `17d0184168945306f80352c70993c215bef40c92` |
| [Review-trigger](/root/kani-rev2-u64-n13-trigger-w13/control), detached; локальный ref `review/rev2-u64-n13-trigger-w13` | `87888742f89bd464d1b4438f1a63e7e0f3e727a2` | `794c9c5bb6872053a581d85731f4bd4e10772477` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Std CI-base для загрузки bundle — `dab03cf510df5c35141cde49f1368b1242f5035e` / tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani — `9834c96ce90ff57d8495416530b080dc3d52ce25` / tree `938e9932cb2127239afb4f093f6302652c053398`. Handoff идёт в g0 на `experiment/kani-k1-kani3300g0-20261111`, задание закреплено на `dde94ee726`. Параллельные коммиты g0 сохранены. Все новые коммиты используют `Tiramisu-Cake <igkharin@gmail.com>` для author и committer и имеют `[skip ci]`.

| Замороженный вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/CI-REQUEST.json) | `ac3d0a81d4c74247e04d4e99d260007f5f7737643f2612a8459240dcc7dd4ce9` |
| Exact roster | `4d174160b04b7f6e0bd2d25d62103a78a6d18df73aa3ff70ad5a338f98f8e5b4` |
| Source bindings | `208f5b04840ce320840f772e358169d11f472b5d78da40ac94766b4e1793a738` |
| [std-overlay.bundle](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/std-overlay.bundle), 58 542 байта | `dc662c5485d3e1156718d3a80b7355ec3e1f0e4575ba3ace1b88f7537e12c008` |

Хэши roster и source bindings считаются от canonical JSON с сортировкой ключей и разделителями `(",", ":")`. Исторические roster сохранены в source bindings с прежними SHA-256 — copy-back `6206fc1d9f76cc8e84129c1aecb99e36ab8b38ddd41d7f9152a9a0591a82ecbd`, consumer `b6709c5d920e4ac4621fc10e6a4a3056a7fa7c52ca6b9ff8d399eb04e45129dc`, merge `47cd94f3d07647f62ce26e0e0f1f8451545775e45d46f985a8f1759adbc059db`.

| Исходник | Git blob в Std |
| --- | --- |
| `verify/rev2_u64_n13.rs` | `a69b9501be6139be78af3d6df569b3d32d39d76c` |
| `smallsort/verify.rs` | `4376bfc6a08ee44a48911c9ab5d93ad2741afaee` |
| `core/Cargo.toml` | `ff9d0aef21e8abe4244e269cb8ec8bf7b192c9d8` |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `verify/network.rs` | `e36ed1630ed740410eea0ca100b831276d0dea4b` |
| `verify/rev2_provider_cost.rs` | `c1f34296a2ff77b5cfe4b1e045c70d28bb50e6de` |
| `verify/cal1_q_merge_model.rs` | `d3c2a137f7332d79e7ce8596a517fd8b5f2dbe19` |
| `core/src/ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |

Std-дельта содержит модуль, регистрацию в `smallsort/verify.rs:301–302` под `cfg(kani_smallsort_rev2_u64_n13)` внутри существующей области `cfg(kani)` и check-cfg в `core/Cargo.toml:68`. Удаление двух новых деклараций восстанавливает базовые blobs. Source gate проверяет этот delta, цепочку до CI-base, исторические blobs, точное расписание `sort13_optimal` и ожидаемые координаты.

Workflow проверяет `Tiramisu-Cake/kani`, push `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, exact `HEAD == GITHUB_SHA == payload.after`, сохранённый ref, `payload.deleted == false`, чистый detached checkout и единственный parent. Независимая Actions variable `CH8_REV2_U64_N13_TRIGGER_TREE` должна указывать на tree Control из таблицы. `pins` пишет admission receipt, `sources` и `finish` сверяют его перед последующими действиями. [Workflow](/root/kani-rev2-u64-n13-trigger-w13/control/.github/workflows/ch8-q-pilot.yml) · [Trigger gate](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/request.py)

## Exact roster и нативные якоря

| Слот | Exact selector | Root | Ожидаемый исход / exit | Latest start |
| --- | --- | --- | --- | --- |
| `U64-N13-SWAP` | `slice::sort::shared::smallsort::verify::rev2_u64_n13::u64_n13_swap` | `15:1` | `VERIFIED` / 0 | 55:00 |
| `U64-N13-S13-BITS` | `slice::sort::shared::smallsort::verify::rev2_u64_n13::u64_n13_s13_bits` | `47:1` | `VERIFIED` / 0 | 58:25 |
| `U64-N13-S13-CORRUPT` | `slice::sort::shared::smallsort::verify::rev2_u64_n13::u64_n13_s13_corrupt` | `53:1` | `FAILED` / 1 | 61:50 |

Координаты относятся к `core/src/slice/sort/shared/smallsort/verify/rev2_u64_n13.rs`. В таблице к каждому имени функции добавляется префикс `slice::sort::shared::smallsort::verify::rev2_u64_n13::`, к каждой метке — `REV2_U64_N13_`. [Модуль](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n13.rs)

| Метка | Функция | Line:column | Класс | Статус |
| --- | --- | --- | --- | --- |
| `COMPARATOR_CALLED` | `u64_less` | `9:5` | cover | `SATISFIED` у всех трёх |
| `SWAP_GREATER_INPUT` | `u64_n13_swap` | `24:5` | cover | `SATISFIED` |
| `SWAP_LESS_INPUT` | `u64_n13_swap` | `25:5` | cover | `SATISFIED` |
| `SWAP_EQUAL_INPUT` | `u64_n13_swap` | `26:5` | cover | `SATISFIED` |
| `SWAP_RETURNED` | `u64_n13_swap` | `32:5` | cover | `SATISFIED` |
| `SWAP_MIN` | `u64_n13_swap` | `35:5` | assertion | `SUCCESS` |
| `SWAP_MAX` | `u64_n13_swap` | `36:5` | assertion | `SUCCESS` |
| `SWAP_V34_FRAME` | `u64_n13_swap` | `42:5` | assertion | `SUCCESS` |
| `S13_MIXED_INPUT` | `check_s13::<false>` / `check_s13::<true>` | `65:5` | cover | `SATISFIED` у обоих |
| `S13_INPUT_INVERSION` | `check_s13::<false>` / `check_s13::<true>` | `66:5` | cover | `SATISFIED` у обоих |
| `S13_RETURNED` | `check_s13::<false>` / `check_s13::<true>` | `69:5` | cover | `SATISFIED` у обоих |
| `S13_V34_FRAME` | `check_s13::<false>` / `check_s13::<true>` | `74:5` | assertion | `SUCCESS` у обоих |
| `S13_CANONICAL_OUTPUT` | `check_s13::<false>` / `check_s13::<true>` | `81:5` | assertion | `SUCCESS` у обоих |
| `S13_SORTED_POPCOUNT` | `check_s13::<false>` / `check_s13::<true>` | `82:5` | assertion | `SUCCESS` / единственный `FAILURE` |

`copy_back=false` для всех трёх. Гейт требует один regular property на каждый ожидаемый якорь и согласованные ID, статусы и итоговые счётчики regular и stock в доступном объёме. Stock RFC 0015 агрегирует успешные checks, поэтому их точные координаты и ID берутся из regular, а число и статусы сверяются по stock. Обязательные covers требуют `SATISFIED` в обоих каналах, все выведенные unwind assertions — `SUCCESS` при `unwinding=ON`. Контроль требует единственного `FAILURE` класса assertion на `REV2_U64_N13_S13_SORTED_POPCOUNT`, согласованного в обоих каналах. [Гейт результатов](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/results.py)

Фиксируются доступные regular свойства `ptr::copy::<u64>` и `ptr::copy_nonoverlapping::<u64>` с ID, классом, статусом и координатой. В теле swap это `smallsort.rs:517:9` и `:518:9`, число элементов 1. В теле `ptr` intrinsic-координаты `core/src/ptr/mod.rs:682:9` и `:587:14`. Решение для этого первого пакета — собирать наблюдения для офлайн-привязки без заранее назначенных сгенерированных ID или числа grouped properties, которые могут зависеть от оптимизации, в том числе у константного контроля. Нативную привязку к actual swap предстоит проверить после прогона.

## Рёбра составного аргумента

Область — живой инициализированный `[u64; 34]` с базой `v[1..14]`, размер и выравнивание элемента по 8 байт на Ubuntu X64. У листа единственное `assume` ограничивает два индексных значения `0 ≤ a < b < 13`. Все 34 входных значения произвольны. Указатели `base.add(a)` и `base.add(b)` указывают на `v[1+a]` и `v[1+b]`. Вызов swap на строке 31 и min/max/frame проверяют полные `u64`. Остальные 32 элемента сравниваются со снимком.

Решение о компараторе — один function item `u64_less` без захватов и записей, с verification cover и полным `a < b` на `&u64`. Он сохраняет состояние и наблюдаемо совпадает с числовым `strict_less::<u64>`. Точное ребро от листа к sort13 использует один и тот же тип function item. Эквивалентность с `strict_less` относится к ответам и эффектам и используется отдельным внешним шагом. На stock-пине `contracts.rs:583–598` выбирает `ContractMode::Original` для обычного вызова с `--no-assert-contracts`. Все корни plain Proof, unwind36. Предикаты FIX3 для swap и CAL1 для S13 допускают моделирование только при специализации `u8, KeyLess<u8>`. Для `u64` они ложны и в этих корнях не вычисляются. [strict_less](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort/verify/network.rs:735) · [FIX3](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_provider_cost.rs:90) · [Precedent режима](REV2-S13-BINDING-DESIGN.md)

S13 получает тот же тип, срез и компаратор. Битовый positive отображает `kani::any::<u16>() & 0x1fff` в 13 независимых `0u64/1u64`. Оракул сравнивает каждый полный элемент с 0 и 1 и собирает маску через `item == 1`. Ожидаемая маска — `0x1fff ^ (0x1fff >> input_mask.count_ones())`. В контрольном корне вход `0x0001` даёт `0x1000` перед порчей по статической модели. После actual возврата и cover XOR на строке 71 меняет читаемый тем же оракулом `v[1]`, давая `0x1001` с каноническими элементами и прежним внешним frame. [Общий helper](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_u64_n13.rs:57)

Все 45 actual вызовов используют `v_base` от `smallsort.rs:605:18`, тот же `is_less` и адреса `v[1+a]`/`v[1+b]`, с `0 ≤ a < b < 13`. Каждая пара в таблице соответствует следующей строке исходника, столбец 9. [Actual расписание](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort.rs:612)

| Строки | Пары в порядке исходника |
| --- | --- |
| 612–620 | (0,12), (1,10), (2,9), (3,7), (5,11), (6,8), (1,6), (2,3), (4,11) |
| 621–629 | (7,9), (8,10), (0,4), (1,2), (3,6), (7,8), (9,10), (11,12), (4,6) |
| 630–638 | (5,9), (8,11), (10,12), (0,5), (3,8), (4,7), (6,11), (9,10), (0,1) |
| 639–647 | (2,5), (6,9), (7,8), (10,11), (1,3), (2,4), (5,6), (9,10), (1,2) |
| 648–656 | (3,4), (5,7), (6,8), (2,3), (4,5), (6,7), (8,9), (3,4), (5,6) |

При успешном листе для каждого `t: u64` проекция `P_t(x) = [x ≥ t]` переводит min/max в AND/OR. После каждого вызова actual расписания проекции совпадают с результатом такого же шага на битах, а значения вне пары сохраняются. Успешный битовый корень даёт порядок и исходный popcount для любой проекции. Соседняя убывающая пара `x > y` дала бы инверсию при `t = x`. Для `t < u64::MAX` кратность `t` получается как `count(≥t) - count(≥t+1)`. Порог `u64::MAX` даёт свою кратность напрямую. Frame вне среза следует из frame листа на каждом шаге.

У `small_sort_network` с N13 `no_merge=true` на `smallsort.rs:386`, регион с той же базой и длиной 13 создаётся на `:389–391`. Actual вызов S13 на `:396` возвращает управление к `insertion_sort_shift_left(region, 13, is_less)` на `:405`. Вставки имеют нулевое число итераций, поскольку указатели `tail` и `v_end` равны на `:759–761`. Путь возвращается на `:407–408` до второй половины, merge и copy-back. Это внешний перенос для ровно N13. Для допуска требуются нативные опоры и ревью рёбер. Для `stub_verified` и штатной матрицы pr752 действуют отдельные условия. [Actual ветка](/root/verify-rust-std-rev2-u64-n13-w13/library/core/src/slice/sort/shared/smallsort.rs:386) · [Правило композиции](REV2-COMPOSITION-RULE.md) · [Прецедент N13](REV2-N13-ADMISSION-APPROVAL.md)

## Профиль и часы

Один job `ubuntu-24.04`, 90 мин. Stock Kani, CBMC 6.11.0/CaDiCaL, OB12, unwind36. Для одного корня — 120 с VT, 4 GiB group RSS, 180 с cold wall и 2 GiB системного резерва. Safety, overflow, unwinding, undefined-function и assertion-reach включены, uninit/validity выключены. Отдельные CWD, Cargo/Kani targets, TMPDIR и stock export для каждого корня.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

`RUSTFLAGS` строится из exact `cfg` строки roster в исходном порядке. Все исторические флаги сохраняются, новый `--cfg=kani_smallsort_rev2_u64_n13` добавляется последним. `KANI_JOBS=1`, `CARGO_TARGET_DIR=$slot/cargo-target`, временные пути `$slot/tmp`. До discovery отдельный cfg-on compile preflight с `--no-assert-contracts --no-codegen --only-codegen --quiet`, максимум 180 с и первые структурированные сообщения rustc при отказе. Discovery сравнивает cfg-off с cfg-on по kind, selector, file и targets, проверяет закреплённые Check targets и отсутствие contract target у каждого plain. Ожидается 94 исторических REV2 записей плюс ровно три новых `standard-harnesses`. [Runner](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/run.py)

| Стадия | Граница от monotonic epoch | Внешний timeout |
| --- | --- | --- |
| Prepare | 54:00 | 56 мин |
| Входной gate measure | до 55:00 и до 60 с от входа | В составе measure |
| Три окна по 205 с | 55:00 / 58:25 / 61:50, конец 65:15 | Внутренний measure 13:20, внешний 15 мин |
| Финальная аттестация | 67:15 | В составе measure |
| Finish и upload-gate | общий cutoff 72:10, до 5 мин finish от его входа | 6 мин и 1 мин |
| Upload и полный план | upload до 79:15, план до 85:15 с резервом 6 мин | Upload 7 мин, job 90 мин |

Окно слота — 180 с cold wall + 10 с reap + 5 с receipt + 10 с launch headroom. Ранний вход в measure может сдвинуть latest starts раньше в пределах внутреннего бюджета. Абсолютные latest starts остаются верхними границами. Supervisor записывает checkpoint нативного исхода и reap до проекции, finish ограничивает retry записи своим cutoff. Следующий слот после остановки измерения возможен при подтверждённом reap и в его окне. Пределы проекции и артефакта 4/96 MiB. Linux group RSS может недоучитывать память при смене worker TID. [Supervisor и часы базы](REV2-N27-N29-N30-N31-COMPOSITE-HANDOFF.md#профиль-и-часы)

`U64_N13_WITHIN_PROFILE` требует все три exact исхода, полные опубликованные проекции, якоря, covers, timely receipts, подтверждённый reap, соблюдение лимитов и своевременную финальную аттестацию `COMPLETE`. Иной пакет имеет `U64_N13_OPEN` с профилем каждой роли. [Отчёт](/root/kani-rev2-u64-n13-control-w13/ch8-cal1/report.py)

## Локальная сверка

- Видимость `crate::kani`, actual helper имён, `Arbitrary` для массивов и `From<bool>` для `u16` проверена по исходникам. Pinned rustfmt `nightly-2026-11-19` прошёл на новом модуле и registry с сохранением исторического порядка деклараций. TOML, YAML без дубликатов, `bash -n` для 8 блоков, 15 Python AST и `git diff --check` прошли.
- Shallow bare Std depth 2 без alternates прошёл `bundle verify/list-heads/unbundle`. Prerequisite — CI-base, единственный объявленный ref — HEAD Std кандидата. HEAD, refs и shallow boundary сохранены. Сверены 21 commit/tree/sole-parent, 23 текущих source blobs с историческими привязками, 335 текстовых и 288 нативных якорей. Отдельные сдвиги столбца либо замены функции/класса отклонены во всех 66 мутациях 22 новых якорей.
- Из actual тела извлечены все 45 пар, совпали с `SWAP_PAIRS` базы. Статический перебор 8 192/8 192 масок дал ожидаемую отсортированную маску для каждой. Контроль подтвердил `0x0001 → 0x1000 → 0x1001`.
- Синтетический discovery дал 94 + 3 записи. Гейты отклонили чужое дерево или payload, прежнее имя Actions variable, лишний selector/target, смещённый или чужой native anchor, потерю cover, второй отказ контроля, неверный exit, поздний receipt, превышение VT/RSS, отсутствие reap или аттестации.
- `test_supervisor.py` имеет blob `df63a457c3adf648d360f3d559d5d40ef00a9427` в Control и review-trigger. На чистом detached review-trigger suite прошёл последовательно по 124/124 теста на обычной и свежих шкалах 1/5/60 с. Время — 40,611 / 47,999 / 55,170 / 42,356 с соответственно.
- Синтетический detached trigger принял `pins` при +2 с, `finish` при +4300 с, `upload-gate` при +4330 с и `upload-check` при +4755 с. Смещение на 0,01 с за соответствующие cutoff отклонено. `finish` отклонил изменённый admission receipt. В синтетическом индексе сверены размеры и SHA-256 7 членов, 3 роли `NOT_STARTED`/`OPEN`, `proof_credit=NONE`.

## Открытые обязательства

1. Независимое ревью пинов, контрольных гейтов и доказательных рёбер. Затем отдельный GO координатора на один диагностический прогон Item 2.
2. Compile preflight, нативный cfg-off/on discovery и результаты трёх корней. Нативные ID, фактические статусы и ресурсные значения ожидают CI. После него сверить ptr-наблюдения с двумя actual swap call sites и запас времени на проекцию/receipt.
3. После успешной диагностики отдельно решить исследовательский допуск N13 на заявленной области. Перенос на соседние длины и заявления о покрытии pr752 требуют своих оснований.

Локально выполнены Git, статическая проверка и Python/shell синтетика. Cargo, rustc, Kani, CBMC и CI не запускались. Push, изменения Actions variables и учёт в действующем ledger отсутствуют.
