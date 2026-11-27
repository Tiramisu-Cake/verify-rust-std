# REV2 · Ubuntu-пилот general/stable на N16

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

Пакет измеряет шесть локальных опор на Ubuntu X64. Компиляция с cfg и нативные измерения остаются на будущий запуск после независимого ревью и отдельного GO координатора. [Задание](REV2-GEN-STABLE-N16-PILOT-TASK.md)

## Пины пакета

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std](/root/verify-rust-std-rev2-gen-stable-n16-pilot-w13) | `14a5a7322a050c7d5028054acc5825172d43c14c` | `bf379fc6b403e9caa51e549cc53956d66549ef3c` | `727137f7efd6f5feb05eb7b3db4f3875c8699675` |
| [Control](/root/kani-rev2-gen-stable-n16-pilot-control-w13) | `046b1e0f8457390b1e6ffea9dd779a0a4acc053e` | `9021966b36dcbbf0a7f36d9065bd0dae580a4e98` | `5d58830f278d18a9080c61b4d791f94101e0c4c4` |
| [Review-trigger, detached](/root/kani-rev2-gen-stable-n16-pilot-trigger-w13/control) | `2783b10ee6ed6f32bdc3595703119109ac6ffba1` | `9021966b36dcbbf0a7f36d9065bd0dae580a4e98` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Основание задания g0 `b3614058e71f408cff5c778e468b9c7047d147ab`, ветка `experiment/kani-k1-kani3300g0-20261111`. Исходные деревья Std и Control `50089d49d2be1058df3f271abef7d0bfc9ee57d4` и `4e4a20091835954aa9ff6847b11b7a572c9fc277`. Bundle объявляет единственный `HEAD` и содержит 29 последовательных overlay-коммитов поверх `dab03cf510df5c35141cde49f1368b1242f5035e`, tree `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25`, tree `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n16-pilot-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `c105664a8cb5abc24eebe9710422252bbc77d62ccd06b692cf169816ba4d0e17` |
| Exact roster, канонический JSON | `e9b522a49fc5bf72723c043d581cdf9c8625a612d4034f05ada08fb2f943b674` |
| Source bindings, канонический JSON | `04e5df7a92044846d54bb6efa8fe5869a1392e9f03b05f4c6d0a4d9a8198bddd` |
| [Std bundle](/root/kani-rev2-gen-stable-n16-pilot-trigger-w13/control/ch8-cal1/std-overlay.bundle), 83 842 байта | `c11285e32bc8d4e4e3faddf43c8422aafcbb51a49fc5be21f3128f3a622e7fc1` |

Независимый tree pin `CH8_REV2_GEN_STABLE_N16_PILOT_TRIGGER_TREE=9021966b36dcbbf0a7f36d9065bd0dae580a4e98` проверяется в `pins`, `sources`, `prepare`, `measure`, `finish` и `upload-gate`. Допуск связывает чистый detached HEAD, `GITHUB_SHA`, payload `after`, единственного parent и дерево с fork `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1. Схема индекса `smallsort-rev2-gen-stable-n16-pilot-artifact-v1` связывает admission receipt, четыре SHA-256 и инвентарь файлов. Upload-gate повторно сверяет admission receipt, request и индекс. [Workflow](/root/kani-rev2-gen-stable-n16-pilot-trigger-w13/control/.github/workflows/ch8-q-pilot.yml)

## Exact roster и нативные привязки

Префикс selector и Check target `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::`. Discovery проверяет 163 исторические записи управляемого roster с source, kind и targets и добавляет ровно шесть новых. Каждый root ожидает `VERIFIED`, exit 0. Root указывает на атрибут proof в модуле. [Модуль Std](/root/verify-rust-std-rev2-gen-stable-n16-pilot-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs)

| Слот | Суффикс selector | Root | Kind и суффикс target | Latest start |
| --- | --- | --- | --- | --- |
| `GEN-N16-S8-R32-FULL` | `gen_n16_s8_r32_full` | 85:1 | Proof, targets ∅ | 55:00 |
| `GEN-N16-S8-R32-BITS` | `gen_n16_s8_r32_bits` | 91:1 | Proof, targets ∅ | 58:25 |
| `GEN-N16-WIDE-S4-R48` | `gen_n16_wide_s4_r48` | 165:1 | Proof, targets ∅ | 61:50 |
| `GEN-N16-WIDE-FILL-R48-REL4` | `gen_n16_wide_fill_r48_rel4` | 241:1 | Proof, targets ∅ | 65:15 |
| `GEN-N16-U64-S32-MERGE-PAIR` | `gen_n16_u64_s32_merge_pair` | 365:1 | ProofForContract, `actual_merge_pair_u64_s32` (304:1) | 68:40 |
| `GEN-N16-WIDE-S48-MERGE-PAIR` | `gen_n16_wide_s48_merge_pair` | 485:1 | ProofForContract, `actual_merge_pair_wide_s48` (424:1) | 72:05 |

| Привязка | Координаты |
| --- | --- |
| Обе sort8 | Actual вызов 115:5. Общий оракул 154–159, колонка 5. Covers инверсии смешанного входа, равных ключей и возврата 160–162, колонка 5. Компаратор `rev2_u64_n13.rs:9:5` с full-width `<`. |
| Wide sort4 | Actual вызов 189:5. Scalar order, records-by-tag, стабильность равных ключей и оба frame 217–221, колонка 5. Covers равных ключей с разными метками, входной инверсии и возврата 225–227, колонка 5. |
| Wide fill | Локальная копия 236:9 транскрибирует `smallsort.rs:329:17`. Actual вставка вызвана с 237:9 по геометрии `smallsort.rs:330`. Exact upper-bound и два frame 292–294, колонка 5. Covers без сдвига, со сдвигом, distinct tie и возврата 298–301, колонка 5. |
| U64 pair | Восемь assertions read/write/disjoint/cursors в Check на 322:9, 326:9, 327:9, 334:9, 344:9, 348:9, 349:9 и 356:9. Выбранные слова 398–399, frame 411–412, covers 413–421, колонка 5. |
| Wide pair | Восемь assertions read/write/disjoint/cursors в Check на 442:9, 446:9, 447:9, 454:9, 464:9, 468:9, 469:9 и 476:9. Все поля выбранных записей 521–522, frame 538–539, covers 540–544, 548, 552–554, колонка 5. |
| Wide comparator | Cover `GEN_N16_WIDE_COMPARATOR_CALLED` на 35:5. Числовой `a.key < b.key`. |

В обоих sort8 `copy_sites` привязаны к actual `smallsort.rs:832–835` и `:885:9`/`:918:9`. У Wide sort4 это `:832–835`, у Wide fill собственный 236:9 с полем `transcribes` и actual `:722:13`/`:362:13`. У обеих пар это actual `:885:9`/`:918:9`. Каждый слот требует шесть сгруппированных typed-copy свойств на `ptr/mod.rs:587:14` для `ptr::copy_nonoverlapping::<u64>` или `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>`. Обе Check-привязки требуют exact stock target, `single_top_level_call`, `no_recursive_call`, scoped `memcpy.assigns.1/.2` и все assertions той же обёртки. Все выведенные unwind checks должны иметь `SUCCESS` при stock `unwinding=ON`. [Решение о группировке](item2-audit-response-20261120/GROUPED-PROPERTY-DECISION.md)

| Исходник | Git blob |
| --- | --- |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |
| `rev2_u64_n13.rs` | `47c129a11d6cd0d0adce0be450b91eca84a25c0c` |
| `rev2_gen_stable_n16_pilot.rs` | `027b71ea2726e8a89047da497a9b297455448be5` |
| `verify.rs`, две добавленные строки 315–316 | `10e8612240fa99cfd5c6e2c4b1908450f4d15f3a` |
| `core/Cargo.toml`, check-cfg на 75 | `1be550ce208eee155a8b7c4b50d26bb0c9f19fa9` |

## Маршруты и переходы инициализации

`S=v[1..17].as_mut_ptr()` из V18, `D` из всего отдельного scratch. Stable Freeze `u64` получает внешний scratch на `smallsort.rs:81`. У N16 проверка `:286` требует минимум 32 слова, `:297–307` выбирает sort8. `Wide` состоит из трёх `u64`, `repr(C)`, Copy+Freeze, размер 24 и выравнивание 8. При `size_of::<T>() <= 8` на `:1071` Wide минует network в Copy+Freeze специализации `:189–225`. Его 1152 байта укладываются в 4096, поэтому `:221–222` ведёт к private general. На `:261–273` создаётся и передаётся scratch48, а `:308–313` выбирает sort4. Маршруты сверены по исходникам и свойствам типа. Вход через целый trait-метод остаётся предметом композиции. [Actual Std](/root/verify-rust-std-rev2-gen-stable-n16-pilot-w13/library/core/src/slice/sort/shared/smallsort.rs)

| Ребро | Запись и следующее чтение | Открытая предпосылка |
| --- | --- | --- |
| Stable u64, правый sort8 | `S[8..16]` → два actual sort4 на `:850–851` пишут изначально uninit `D[24..28]` и `D[28..32]`. Actual merge на `:857` после обеих записей читает эти четвёрки и пишет uninit `D[8..16]`. При возврате оракул читает tmp и dst. Диапазоны dst/tmp в одной живой D32 имеют байтовые границы `[64,128)` и `[192,256)`. | Привязка реального левого вызова и других backing. При cutoff FULL открыты order, кратность, tmp-order и frame для полных слов. BITS имеет тот же оракул, восемь независимых `0u64/1u64` и произвольный полный probe. |
| Stable u64, левый sort8 | `:299` читает `S[0..8]`, пишет `D[16..24]` и затем `D[0..8]`. | Отдельная привязка `D[0..8]`/`D[16..24]`, совместный frame двух вызовов. |
| Wide, правый sort4 → rel4 | Actual `:311` читает `S[8..12]` и пишет uninit `D[8..12]`. Правый rel4 принимает эти четыре упорядоченные инициализированные записи, локальная копия переносит `S[12]` в uninit `D[12]`, затем actual insert_tail читает хвост и префикс. Возврат даёт пять инициализированных слов `D[8..13]` с точным порядком по upper bound. | Переходы rel5, rel6 и rel7, каждый со своей длиной префикса и точным постом. |
| Wide, левая половина | `:310` читает `S[0..4]` и пишет `D[0..4]`. Цикл `:321–330` переносит `S[4..8]` последовательно и достраивает `D[0..8]`. | Привязка левого sort4 и всех четырёх шагов. |
| Внешний merge обеих линий | `:342–346` передаёт инициализированные `D[0..16]` в merge со scratch → V. При `m=8`, `k<8`, `a,c<=k`, `b=k−a`, `d=k−c`, шаг читает `D[a], D[8+b], D[7−c], D[15−d]`, пишет ровно `S[k]` и `S[15−k]`. Для up tie-left, для down tie-right. Проверяются курсоры, записи и frame обеих аллокаций. | Порядок обеих половин, инвариант связи счётчиков и границ на следующих шагах, полное потребление и терминальный пост N16. |

Для `uninit OFF` цепочка инициализации опирается на фактические записи, точные посты и нормальный возврат. Frame читает только заранее заполненные слова. Непересечение внутри одной D выводится из интервалов и выравнивания. Локальные свойства Wide разделены по вызовам. Sort4 сохраняет порядок меток равных записей, вставка кладёт новую запись после равных, а пара проверяет выбор стороны при равенстве. Сквозная устойчивость, восстановление при панике, оформление для pr752 и `stub_verified` открыты.

## Запуск и отчёт

Одна `ubuntu-24.04` X64 job, внешний предел 100 мин. Stock CBMC 6.11.0/CaDiCaL, OB12, unwind36, `KANI_JOBS=1`. Safety, overflow, unwinding, undefined-function и assertion-reach ON, uninit/validity OFF. Actual тела в Original. Две локальные обёртки в Check. Состав Replace, stubs и loop contracts пуст. На слот 120 с VT, 180 с cold wall, 4 GiB group RSS, резерв ОС 2 GiB. Холодные CWD, Cargo/Kani targets, tmp и export раздельны. Порядок 27 cfg закреплён в request.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Cfg-on compile preflight до обоих list использует те же verify `-Z` без export-json и `--no-assert-contracts --no-codegen --only-codegen --quiet --target-dir "$preflight/kani-target" "$std/library"`, предел 180 с. При сбое сохраняются первые rustc diagnostics. Discovery использует `"$tool/scripts/kani" list -Z function-contracts -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing "$std/library" --std --format json` для cfg-off и cfg-on.

| Стадия | Граница от начала job | Окно |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Measure identity gate | 55:00 | До 60 с от входа в measure |
| Шесть слотов | 75:30 | Каждый 205 с, включая cold wall 180 с, reap 10 с, receipt 5 с и запас старта 10 с |
| Финальная аттестация | 77:30 | Measure 23:35 внутренний, 25 мин внешний |
| Finish и upload-gate | 82:25 | Внешние 6 и 1 мин, 5 с резерва запуска upload |
| Upload | 89:30 | Внешние 7 мин |
| План с резервом | 95:30 | Job 100 мин |

`GEN_STABLE_N16_PILOT_WITHIN_PROFILE` требует 6/6 `VERIFIED/MATCHED`, полных своевременных receipts/projections, нужных covers, валидного sampler, подтверждённого reap, соблюдения лимитов и своевременной аттестации `COMPLETE`. Checkpoint исхода и reap сохраняется перед проекцией. Повтор receipt ограничен абсолютным дедлайном и сохраняет флаг late. Неподтверждённый reap блокирует дальнейшие слоты. Caps 4 MiB на проекцию и 96 MiB на публикацию. Отчёт показывает последнюю фазу, первую CNF, VT, cold wall и group/CBMC RSS. Доступный CBMC PSS привязан к PID и к пику group/CBMC RSS либо ближайшей выборке. Смена Linux TID может занизить RSS при неатомарном чтении. При cutoff любой пары сначала сопоставить фазу и CNF до решения о раздельных измерениях up/down. При успехе опор второй пакет замыкает обе половины и терминальный пост N16.

## Локальная валидация

- Rustfmt `nightly-2026-11-19 --edition 2024 --config use_small_heuristics=Max` применён до фиксации координат. Затем прошёл `--check`. SHA-256 бинарника `0cb21861860ae07c03b7097b099ea3e28dfb3857a9b09acce0df6b165f25cc70`. Сверены видимость Rust-имён, TOML, cfg, actual dispatch и геометрия. Вычитание строк cfg восстанавливает исходные registry и manifest. Runtime, контракты и прежние модули побайтно совпадают.
- Явные проходы не длиннее 32 итераций, включая инициализацию и frame scratch48. Внутрисортовый merge8 выполняет четыре пары, `insert_tail` rel4 делает до четырёх сдвигов. Массив `[u64; 18]` использует stock `any_raw_array` с одним nondet для массива. Kani переводит typed copy в CBMC `memcpy`, где реализация на теге 6.11.0 использует `__CPROVER_array_copy` и `__CPROVER_array_replace` без побайтового цикла. Сравнения записей выполняются по трём полям, сравнения frame скалярные. Эти границы укладываются в unwind36. Для сгенерированных проверок развёртки применяется нативный gate.
- Статическая модель проверила 204/204 состояния адресов для обеих геометрий, 256 битовых входов sort8, 256 комбинаций ключей sort4 и 175 сценариев вставки. Пример с переставленными метками соседних равных ключей сохраняет ключи и записи и отклоняется отдельным stability постом.
- Source gate сверил 29 commit/tree/parent overlay, 30 текущих blobs, 1104 координаты и определения нативных свойств. Шаблон historical layout с устаревшим manifest и подмена координаты транскрипции отклонены. Depth-2 Std checkout без alternates принял bundle, сохранил HEAD базы и shallow boundary.
- На точном review-trigger прошёл self-test workflow с Python 3.12.3. Штатная шкала 135/135 за 52,689 с, старт от 1 с 135/135 за 54,830 с, от 5 с 135/135 за 53,596 с и от 60 с 135/135 за 53,646 с. Проверены discovery 163 → 169, чужой selector/Check target, потеря стабильности, frame, typed-copy, scoped assigns, cursor и return anchors, выход из профиля, поздний receipt, потеря reap и аттестации. Проверены уникальные ключи YAML, восемь блоков `bash -n`, синтаксис Python и `git diff --check`.
- На detached review-trigger пройдены `pins`, `sources`, `finish`, `upload-gate` и `upload-check` с синтетическим push. Для Std и tool `sources` сверял чистые detached checkout и точные commit/tree, подменив рекурсивную проверку submodules для локальных shallow копий. Синтетический finish сформировал шесть `NOT_STARTED` receipts и диагноз `GEN_STABLE_N16_PILOT_OPEN`. Неверные tree и payload отклонены четырьмя входами. Upload-gate отклонил подмену admission receipt, схемы индекса и индексированного receipt. Просроченные upload-gate и upload-check отклонены.
- `test_supervisor.py` сохранён с blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Std, Control, review-trigger и g0 коммиты записаны от `Tiramisu-Cake <igkharin@gmail.com>` с `[skip ci]`. Для пакета выполнялись локальные статические и синтетические проверки без Cargo, rustc, Kani, CBMC, CI, push или изменения Actions variables.

## FIX1 · раздельные Wide merge_up и merge_down

**READY_FOR_REVIEW · Item 2 · `go=NOT_GRANTED` · `proof_credit=NONE`.**

FIX1 содержит два Check с полным доменом своего направления. Нативная компиляция и измерения этого пакета относятся к стадии после независимого ревью и отдельного GO. [Задание FIX1](REV2-GEN-STABLE-N16-PILOT-TASK.md#fix1--раздельные-wide-merge_up-и-merge_down)

### Сверка опор 46054351048/1

Индекс SHA-256 `3e856c127e21aebd3e37a9a8a909b36aba2e922cd22b6e1066a80139d9ecd7d9`. Сверены размеры и SHA-256 26/26 структурированных файлов, исходные blobs и координаты, request, roster, bindings и bundle. Фактический trigger `9e57088dade0aa932b83bca98d97fe02ae4963f5` имеет дерево `9021966b36dcbbf0a7f36d9065bd0dae580a4e98` и единственного parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Std и stock tool совпадают с пинами исходного пилота. Аттестация `COMPLETE`. [Индекс исторического запуска](/root/ch8-artifacts/run-46054351048/ch8-rev2-gen-stable-n16-pilot-Linux-X64-46054351048-1/index.json)

| Исторический слот | Исход в индексе | VT / cold wall, с | Covers |
| --- | --- | --- | --- |
| `GEN-N16-S8-R32-FULL` | VERIFIED/MATCHED в профиле | 61,478 / 104,168 | 4/4 |
| `GEN-N16-S8-R32-BITS` | VERIFIED/MATCHED в профиле | 37,174 / 79,564 | 4/4 |
| `GEN-N16-WIDE-S4-R48` | VERIFIED/MATCHED в профиле | 34,052 / 76,557 | 4/4 |
| `GEN-N16-WIDE-FILL-R48-REL4` | VERIFIED/MATCHED в профиле | 19,990 / 62,452 | 5/5 |
| `GEN-N16-U64-S32-MERGE-PAIR` | VERIFIED/MATCHED в профиле | 93,489 / 140,479 | 10/10 |
| `GEN-N16-WIDE-S48-MERGE-PAIR` | TIMEOUT в CBMC, неполная проекция | неизвестно / 180,000 | итоговые нативные covers отсутствуют |

В проекциях исторических Wide S4 и fill подтверждены шесть typed-copy свойств с полным именем Wide-инстанса, используемым в FIX1. Пара Wide имела первую CNF 1 533 969 переменных / 7 656 396 дизъюнктов и пик группы 2 906 460 KiB. Эти числа служат ориентиром при чтении двух будущих receipts. Исходный Wide pair сохраняется в discovery с историческим TIMEOUT. Успешные опоры, включая u64 pair, сохраняют исходные selectors, координаты, профиль и receipts. [Сводка исторического запуска](/root/ch8-artifacts/run-46054351048/ch8-rev2-gen-stable-n16-pilot-Linux-X64-46054351048-1/SUMMARY.md)

### Пины FIX1

| Роль | Commit | Tree | Единственный parent |
| --- | --- | --- | --- |
| [Std FIX1](/root/verify-rust-std-rev2-gen-stable-n16-pilot-fix1-w13) | `5a8702f59ae309b8069d380b1e3887fd48c2564b` | `76ff14e1811ae4115aa1aeef2ae42986d21d3c50` | `14a5a7322a050c7d5028054acc5825172d43c14c` |
| [Control FIX1](/root/kani-rev2-gen-stable-n16-pilot-fix1-control-w13) | `bcf4fd366d1fc3fe4e045bb8c6f3b54189a92435` | `981944277c90a3ed6d9667967d8ed2494109ee4e` | `046b1e0f8457390b1e6ffea9dd779a0a4acc053e` |
| [Review-trigger FIX1, detached](/root/kani-rev2-gen-stable-n16-pilot-fix1-trigger-w13/control) | `f3b6b688630a4ea6f777fded2be151217c50815a` | `981944277c90a3ed6d9667967d8ed2494109ee4e` | `467af9cb8dba0e3be78a8d7d07672a1943c4806b` |

Основание g0 `86e0c6a5a1a90a372e12d2a77302c9b576df8f73`, ветка `experiment/kani-k1-kani3300g0-20261111`. Bundle FIX1 содержит одну ссылку `HEAD` и 30 overlay-коммитов поверх CI-base `dab03cf510df5c35141cde49f1368b1242f5035e` / `7fd542ad59723ff2beeacb9632fb0568e81b0655`. Stock Kani `9834c96ce90ff57d8495416530b080dc3d52ce25` / `938e9932cb2127239afb4f093f6302652c053398`.

| Вход | SHA-256 |
| --- | --- |
| [CI-REQUEST.json](/root/kani-rev2-gen-stable-n16-pilot-fix1-trigger-w13/control/ch8-cal1/CI-REQUEST.json) | `83e332c97f9ce196447f44caf05b878d74f066935c9c543b6d23a75e5dcabce7` |
| Exact roster, канонический JSON | `a5949152efec39e80362507c3a07a8d5b6b51ec0521e31f9a981cee33d3d29ff` |
| Source bindings, канонический JSON | `33318eebbe632b9afee1719c1db4b83523733171482bfcf6cf581f2e4913db76` |
| [Std bundle](/root/kani-rev2-gen-stable-n16-pilot-fix1-trigger-w13/control/ch8-cal1/std-overlay.bundle), 83 486 байтов | `ded7e86e5d42644ac00f9c555a3b97d8aaa0585ec653d7809fa251e39d6fc704` |

Независимый tree pin `CH8_REV2_GEN_STABLE_N16_PILOT_FIX1_TRIGGER_TREE=981944277c90a3ed6d9667967d8ed2494109ee4e`. Допуск требует fork `Tiramisu-Cake/kani`, push на `refs/heads/uninit-ci/ch8-q-pilot-v1`, attempt 1, совпадение чистого detached HEAD, `GITHUB_SHA` и payload `after`. Индекс `smallsort-rev2-gen-stable-n16-pilot-fix1-artifact-v1` связывает четыре хэша, точные source pins, admission receipt и инвентарь. Upload-gate повторно сверяет индекс и admission receipt. [Workflow FIX1](/root/kani-rev2-gen-stable-n16-pilot-fix1-trigger-w13/control/.github/workflows/ch8-q-pilot.yml)

### Roster, координаты и композиция

Префикс selector и exact target `slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::fix1::`. Discovery сохраняет 169 исторических записей и добавляет два ProofForContract с одной точной целью каждый. Только эти два корня входят в измерительный roster, ожидаемый исход обоих `VERIFIED/MATCHED`, exit 0. [Модуль Std FIX1](/root/verify-rust-std-rev2-gen-stable-n16-pilot-fix1-w13/library/core/src/slice/sort/shared/smallsort/verify/rev2_gen_stable_n16_pilot.rs)

| Слот | Суффикс selector и root | Суффикс Check target и cfg_attr | Actual copy site | Latest start |
| --- | --- | --- | --- | --- |
| `GEN-N16-WIDE-S48-MERGE-UP` | `gen_n16_wide_s48_merge_up`, 599:5 | `actual_merge_up_wide_s48`, 561:5 | `smallsort.rs:885:9` | 55:00 |
| `GEN-N16-WIDE-S48-MERGE-DOWN` | `gen_n16_wide_s48_merge_down`, 696:5 | `actual_merge_down_wide_s48`, 658:5 | `smallsort.rs:918:9` | 58:25 |

| Привязка в Rust-модуле | Up | Down |
| --- | --- | --- |
| Actual вызов | 588:13 | 685:13 |
| Read / write / disjoint / три курсора | 578:13, 582:13, 583:13, 590:13 | 675:13, 679:13, 680:13, 687:13 |
| Value / V frame / scratch frame | 627:9, 645:9, 646:9 | 725:9, 743:9, 744:9 |
| Covers left, right, tie с разными метками, k=0, k=7, возврат | 647:9, 648:9, 649:9, 653:9, 654:9, 655:9 | 745:9, 746:9, 747:9, 751:9, 752:9, 753:9 |
| Cover actual компаратора `GEN_N16_WIDE_COMPARATOR_CALLED` | 35:5 | 35:5 |

Оба корня требуют stock target, `single_top_level_call`, `no_recursive_call`, scoped `memcpy.assigns.1/.2` и шесть typed-copy свойств `ptr::copy_nonoverlapping::<slice::sort::shared::smallsort::verify::rev2_gen_stable_n16_pilot::Wide>` на `ptr/mod.rs:587:14`. Один actual copy site закреплён за каждым Check. Все выведенные unwind checks должны иметь `SUCCESS` при stock `unwinding=ON`.

| Исходник | Git blob |
| --- | --- |
| `rev2_gen_stable_n16_pilot.rs`, cfg на 557, `mod fix1` на 558 | `fc42d3e4977443e4a01e0bdf4394ba2303d17e0f` |
| `core/Cargo.toml`, check-cfg на 76 | `21f3b4d868a8d124b68cd78560875ab9b7f2ff7d` |
| `verify.rs` | `10e8612240fa99cfd5c6e2c4b1908450f4d15f3a` |
| `smallsort.rs` | `0b77c3dbb3b767ba35281a2a686aa477ff1344c5` |
| `ptr/mod.rs` | `9220ac5ab6cb3a09bb91e28c9cc8c83cfe06b1e6` |

| Шаг | Домен и назначения | Точный локальный пост |
| --- | --- | --- |
| Up | `S=v[1..17].as_mut_ptr()`, отдельный scratch48, `D[0..16]` инициализирован. `0≤a≤k<8`, `b=k−a`. Чтения `D[a],D[8+b]`, единственная цель `S[k]`, `modifies(s.wrapping_add(k))`. | Сравнивает ключи и копирует все три поля выбранной записи. При tie выбирает левую. Инкрементируется выбранный курсор, конечный dst `S+k+1`. Scratch48 и остальная V18 сохраняются. |
| Down | Та же геометрия, произвольная начальная V18. `0≤c≤k<8`, `d=k−c`. Чтения `D[7−c],D[15−d]`, единственная цель `S[15−k]`, `modifies(s.wrapping_add(15 - k))`. | При tie копирует все три поля правой записи. Выбранный курсор двигается на wrapping −1, конечный dst `S+14−k`. Scratch48 и остальная V18 сохраняются. |

При фиксированном k допустимые a и c образуют декартово произведение. Внешняя композиция применяет два поста к 204 комбинациям пары из 36 состояний up и 36 down. Up сохраняет D, поэтому down получает исходный scratch. Его произвольная V18 допускает уже записанный up результат. Назначения `k∈[0,7]` и `15−k∈[8,15]` различны, поэтому down сохраняет запись up. Вместе получаются два точных значения, обе тройки курсоров и frame пары. Actual цикл на `smallsort.rs:1022–1025` вызывает up затем down. Общий компаратор читает ключи и сравнивает их числовым `<`. Ребро опирается на будущую приёмку обоих Check, отдельный инвариант цикла и терминальный пост N16 остаются открыты. [Actual цикл](/root/verify-rust-std-rev2-gen-stable-n16-pilot-fix1-w13/library/core/src/slice/sort/shared/smallsort.rs:1022)

### Профиль и локальная валидация

Одна `ubuntu-24.04` X64 job до 90 мин. CBMC 6.11.0/CaDiCaL, OB12, unwind36, `KANI_JOBS=1`. Каждый слот получает 120 с VT, 180 с cold wall, 4 GiB RSS группы, резерв ОС 2 GiB. Safety, overflow, unwinding, undefined-function, assertion-reach ON. Uninit и validity OFF. Actual helpers в Original, две локальные обёртки в Check, пустые Replace/stubs/loop contracts. Холодные CWD, Cargo/Kani targets, tmp и export разделены. В request закреплены 28 cfg.

```bash
"$tool/scripts/kani" verify-std -Z unstable-options -Z function-contracts \
  -Z mem-predicates -Z float-lib -Z c-ffi -Z loop-contracts -Z quantifiers -Z stubbing \
  --no-assert-contracts --harness "$selector" --exact --jobs=1 --output-format=regular \
  -Z export-json --export-json "$slot/export.json" --verbose \
  --target-dir "$slot/kani-target" "$std/library" --cbmc-args --object-bits 12
```

Ранний cfg-on compile preflight с `--no-assert-contracts --no-codegen --only-codegen --quiet` до обоих list, предел 180 с. Первые rustc diagnostics сохраняются при ошибке. Аргументы list и `-Z` совпадают с основной стадией пилота.

| Стадия | Граница от старта | Окно |
| --- | --- | --- |
| Prepare | 54:00 | Внешний timeout 56 мин |
| Measure identity gate | 55:00 | До 60 с от входа в measure |
| Два слота | 61:50 | По 205 с. 180 с cold wall, 10 с reap, 5 с receipt, 10 с запаса старта |
| Аттестация | 63:50 | Measure 9:55 внутренний, 12 мин внешний |
| Finish и upload-gate | 68:45 | Внешние 6 и 1 мин, 5 с запаса старта upload |
| Upload | 75:50 | Внешние 7 мин |
| План с резервом | 81:50 | Job 90 мин |

`GEN_STABLE_N16_PILOT_FIX1_WITHIN_PROFILE` требует двух своевременных `VERIFIED/MATCHED` с полными нативными свойствами и covers, sampler/reap и аттестацией `COMPLETE`. Checkpoint исхода и reap сохраняется до проекции. Неустановленный reap блокирует следующий слот. Повтор receipt ограничен окном и сохраняет late. Caps 4 MiB на проекцию и 96 MiB на публикацию. По каждому слоту отчёт хранит первую CNF, до семи последующих маркеров на поток и число опущенных маркеров, VT, cold wall, фазу, group/CBMC RSS, доступные CBMC PSS и covers. Неатомарная выборка Linux может занизить RSS при смене TID. Снижение CNF служит диагностикой.

- Проверены rustfmt `nightly-2026-11-19` с `use_small_heuristics=Max` до снятия координат, TOML и Rust-видимость. Исходный модуль сохранён точным байтовым префиксом, check-cfg добавлен одной строкой. Сравнения скалярные. Scratch48 инициализируется и проверяется литеральными интервалами `0..32` и `32..48`. Остальные проходы по 18 элементам. Stock Kani понижает повтор `[MaybeUninit::uninit(); 48]` в константу массива, typed copy использует тот же CBMC `memcpy` из исходного пилота. Source-level циклы укладываются в unwind36. Сгенерированные unwind checks проверяет нативный gate.
- Статическая модель прошла 36/36 up, 36/36 down и 204/204 сочетания пары, проверила адреса, непересечение назначений, tie на различимых записях и сохранение записи up после down.
- Source gate сверил 30 commit/tree/parent, 30 текущих blobs и 1115 координат. Исторические строки и bindings сохранены. Подмены исходного layout и направления typed copy отклонены. Depth-2 Std без alternates принял bundle, сохранил HEAD базы и shallow boundary.
- На точном detached review-trigger прошёл self-test workflow с Python 3.12.3. Штатная шкала 137/137 за 52,964 с, старт от 1 с 137/137 за 53,323 с, от 5 с 137/137 за 52,006 с и от 60 с 137/137 за 52,252 с. Синтетика проверила discovery 169 → 171, чужой selector/target, потерю typed-copy и scoped assigns, подмену направления, обязательные посты и unwind, лимиты, поздний receipt, reap и аттестацию. Проверены YAML с уникальными ключами, восемь блоков `bash -n`, синтаксис Python и `git diff --check`.
- С синтетическим push на точном review-trigger пройдены `pins`, `sources`, `finish`, `upload-gate` и `upload-check`. В `sources` рекурсивная проверка submodules заменена локальной проверкой чистых detached Std/tool и их точных commit/tree. Синтетический finish сформировал два `NOT_STARTED` receipts. Старое дерево, неверный payload, подмены admission receipt, схемы индекса и индексированного receipt, поздний upload-gate и upload-check отклонены.
- `test_supervisor.py` сохранил blob `df63a457c3adf648d360f3d559d5d40ef00a9427`. Пакет подготовлен локально без Cargo, rustc, Kani, CBMC, CI, push и изменения Actions variables. Все четыре локальных коммита имеют `[skip ci]` и авторство `Tiramisu-Cake <igkharin@gmail.com>`.
